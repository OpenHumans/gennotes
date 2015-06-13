import codecs
import fileinput
from ftplib import FTP
import gzip
import json
import logging
import md5
from optparse import make_option
import os
import re
import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction, connection
import reversion
from vcf2clinvar.clinvar import ClinVarVCFLine

from gennotes_server.models import Variant, Relation
from gennotes_server.utils import map_chrom_to_index


try:
    # faster implementation using bindings to libxml
    from lxml import etree as ET
except ImportError:
    logging.debug('Falling back to default ElementTree implementation')
    from xml.etree import ElementTree as ET

CV_VCF_DIR = 'pub/clinvar/vcf_GRCh37'
CV_XML_DIR = 'pub/clinvar/xml'

CV_VCF_REGEX = r'^clinvar_[0-9]{8}.vcf.gz$'
CV_XML_REGEX = r'^ClinVarFullRelease_[0-9]{4}-[0-9]{2}.xml.gz$'

SPLITTER = re.compile('[,|]')

# Keep track of tags used for ReferenceClinVarAssertion data. Tags are keys.
# Values are tuples of (variable-type, function); during parsing the function
# is applied to that variable type to retrieve corresponding data from the XML.
RCVA_DATA = {
    'type':
        (None, lambda: 'clinvar-rcva'),
    'clinvar-rcva:accession':
        ('rcva', lambda rcva: rcva.find('ClinVarAccession').get('Acc')),
    'clinvar-rcva:version':
        ('rcva', lambda rcva: rcva.find('ClinVarAccession').get('Version')),
    'clinvar-rcva:disease-name':
        ('rcva', lambda rcva: rcva.findtext(
            'TraitSet[@Type="Disease"]/Trait[@Type="Disease"]/'
            'Name/ElementValue[@Type="Preferred"]')),
    'clinvar-rcva:significance':
        ('rcva', lambda rcva: rcva.findtext(
            'ClinicalSignificance/Description')),
    'clinvar-rcva:num-submissions':
        ('ele', lambda ele: str(len(ele.findall('ClinVarAssertion')))),
    'clinvar-rcva:record-status':
        ('rcva', lambda rcva: rcva.findtext('RecordStatus')),
    'clinvar-rcva:gene-name':
        ('rcva', lambda rcva: rcva.find(
            'MeasureSet/Measure/MeasureRelationship'
            '[@Type="variant in gene"]').findtext('Name/ElementValue')),
    'clinvar-rcva:gene-symbol':
        ('rcva', lambda rcva: rcva.find(
            'MeasureSet/Measure/MeasureRelationship'
            '[@Type="variant in gene"]').findtext('Symbol/ElementValue')),
    'clinvar-rcva:citations':
        ('rcva', lambda rcva:
            ';'.join(['PMID%s' % c.text for c in rcva.findall(
                'MeasureSet/Measure/Citation/ID[@Source="PubMed"]')])),
    }


class Command(BaseCommand):
    help = 'Download latest ClinVar VCF, import variants not already in db.'

    option_list = BaseCommand.option_list + (
        make_option('-c', '--local-vcf',
                    dest='local_vcf',
                    help='Open local ClinVar VCF file'),
        make_option('-x', '--local-xml',
                    dest='local_xml',
                    help='Open local ClinVar XML file'),
        )

    def _hash_xml_dict(self, d):
        return md5.md5(json.dumps(
            [(k, d.get(k, '')) for k in RCVA_DATA.keys()])).hexdigest()

    def _get_elements(self, fp, tag):
        '''
            Convenience and memory management function
            that iterates required tags
        '''
        context = iter(ET.iterparse(fp, events=('start', 'end')))
        _, root = next(context)  # get root element
        for event, elem in context:
            if event == 'end' and elem.tag == tag:
                yield elem
                root.clear()  # preserve memory

    def _open(self, fp):
        if 'xml' in fp:
            return fileinput.hook_compressed(fp, 'r')

        if fp.endswith('.gz'):
            reader = codecs.getreader("utf-8")
            return reader(gzip.open(fp))
        return codecs.open(fp, encoding='utf-8', mode='r')

    def _download_latest_clinvar(self, dest_dir):
        ftp = FTP('ftp.ncbi.nlm.nih.gov')
        ftp.login()
        ftp.cwd(CV_VCF_DIR)
        cv_vcf_w_date = [f for f in ftp.nlst() if re.match(CV_VCF_REGEX, f)]
        if len(cv_vcf_w_date) != 1:
            raise CommandError('ClinVar reporting more than one VCF matching' +
                               ' regex: \'{0}\' in directory {1}'.format(
                                   CV_VCF_REGEX, CV_VCF_DIR))
        ftp_vcf_filename = cv_vcf_w_date[0]
        dest_filepath = os.path.join(dest_dir, ftp_vcf_filename)
        with open(dest_filepath, 'w') as fh:
            ftp.retrbinary('RETR {0}'.format(ftp_vcf_filename), fh.write)
        return dest_filepath, ftp_vcf_filename

    def _download_latest_clinvar_xml(self, dest_dir):
        ftp = FTP('ftp.ncbi.nlm.nih.gov')
        ftp.login()
        ftp.cwd(CV_XML_DIR)
        # sort just in case the ftp lists the files in random order
        cv_xml_w_date = sorted(
            [f for f in ftp.nlst() if re.match(CV_XML_REGEX, f)])
        if len(cv_xml_w_date) == 0:
            raise CommandError('ClinVar reporting zero XML matching' +
                               ' regex: \'{0}\' in directory {1}'.format(
                                   CV_XML_REGEX, CV_XML_DIR))
        ftp_xml_filename = cv_xml_w_date[-1]
        dest_filepath = os.path.join(dest_dir, ftp_xml_filename)
        with open(dest_filepath, 'w') as fh:
            ftp.retrbinary('RETR {0}'.format(ftp_xml_filename), fh.write)
        return dest_filepath, ftp_xml_filename


    @transaction.atomic()
    @reversion.create_revision()
    def _save_as_revision(self, object_list, user, comment):
        for object in object_list:
            object.save()
            reversion.set_user(user=user)
            reversion.set_comment(comment=comment)

    @transaction.atomic()
    def handle(self, local_vcf=None, local_xml=None, *args, **options):
        # The clinvar_user will be recorded as the editor by reversion.
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s - %(message)s')
        clinvar_user = get_user_model().objects.get(
            username='clinvar-variant-importer')

        # Store objects that need to be saved (created or updated) to db.
        # These are saved in a separate function so they're represented as
        # different Revisions (sets of changes) in django-reversion.
        variants_new = []
        relations_new = []
        relations_updated = []

        # Load ClinVar VCF.
        logging.debug('Loading ClinVar VCF file...')
        if not (local_vcf and local_xml):
            tempdir = tempfile.mkdtemp()
            logging.debug('Created tempdir {}'.format(tempdir))
        if local_vcf:
            cv_fp, vcf_filename = local_vcf, os.path.split(local_vcf)[-1]
        else:
            cv_fp, vcf_filename = self._download_latest_clinvar(tempdir)
        logging.debug('Loaded Clinvar VCF, stored at {}'.format(cv_fp))

        logging.debug('Caching existing variants with build 37 lookup info.')
        variant_map = {(
            v.tags['chrom-b37'],
            v.tags['pos-b37'],
            v.tags['ref-allele-b37'],
            v.tags['var-allele-b37']): v for v in Variant.objects.all()}

        # Dict to track ClinVar RCV records in VCF and corresponding Variants.
        # Key: RCV accession number. Value: set of tuples of values for Variant
        # tags: ('chrom-b37', 'pos-b37', 'ref-allele-b37', 'var-allele-b37')
        rcv_map = {}

        logging.debug('Done caching variants. Reading VCF.')
        clinvar_vcf = self._open(cv_fp)

        # Add Variants if they have ClinVar data. Variants are initially added
        # only with the build 37 position information from the VCF.
        for line in clinvar_vcf:
            if line.startswith('#'):
                continue

            # Parse ClinVar information using vcf2clinvar.
            cvvl = ClinVarVCFLine(vcf_line=line).as_dict()
            data = line.rstrip('\n').split('\t')

            # Get build 37 position information.
            chrom = map_chrom_to_index(data[0])
            pos = data[1]
            ref_allele = data[3]
            var_alleles = data[4].split(',')
            all_alleles = [ref_allele] + var_alleles
            info_dict = {v[0]: v[1] for v in
                         [x.split('=') for x in data[7].split(';')]
                         if len(v) == 2}

            for allele in info_dict['CLNALLE'].split(','):
                # Check if we already have this Variant. If not, add it.
                var_allele = all_alleles[int(allele)]
                var_key = (chrom, pos, ref_allele, var_allele)
                if var_key not in variant_map:
                    # logging.debug('Inserting new Variant'
                    #               '{}, {}, {}, {}'.format(*var_key))
                    variant = Variant(tags={
                        'chrom-b37': chrom,
                        # Check pos is a valid int before adding.
                        'pos-b37': str(int(pos)),
                        'ref-allele-b37': ref_allele,
                        'var-allele-b37': var_allele})
                    variants_new.append(variant)
                    variant_map[var_key] = variant

                # Keep track of RCV Assertion IDs we encounter, we'll add later
                for record in cvvl['alleles'][int(allele)].get('records', []):
                    rcv_acc, _ = record['acc'].split('.')
                    rcv_map.setdefault(
                        rcv_acc, set()).add(var_key)

        # Close VCF, save these new variants to db as a revision.
        clinvar_vcf.close()
        self._save_as_revision(
            object_list=variants_new,
            user=clinvar_user,
            comment='Variant added based on presence in ClinVar ' +
                    'VCF file: {}'.format(vcf_filename))

        # print 'Multiple variants for single RCV Assertion ID:'
        # for k, v in rcv_map.iteritems():
        #     if len(v) > 1:
        #         print '\t', k[0], v

        # Load ClinVar XML file.
        logging.debug('Loading latest ClinVar XML...')
        if local_xml:
            cv_fp, xml_filename = local_xml, os.path.split(local_xml)[-1]
        else:
            cv_fp, xml_filename = self._download_latest_clinvar_xml(tempdir)
        logging.debug('Loaded latest Clinvar XML, stored at {}'.format(cv_fp))

        logging.debug('Caching existing clinvar-rcva Relations by accession')
        rcv_hash_cache = {
            rel.tags['clinvar-rcva:accession']:
                (rel.id, self._hash_xml_dict(rel.tags)) for
            rel in Relation.objects.filter(
                **{'tags__type': RCVA_DATA['type'][1]()})}

        logging.debug('Reading XML, parsing each ClinVarSet')
        clinvar_xml = self._open(cv_fp)

        for ele in self._get_elements(clinvar_xml, 'ClinVarSet'):
            # Retrieve Reference ClinVar Assertion (RCVA) data.
            # Each RCV Assertion is intended to represent a single phenotype,
            # and may contain multiple Submitter ClinVar Assertions.
            # Each Variant may have multiple associated RCVA accessions.
            # Discrepencies in phenotype labeling by SCVAs can lead to multiple
            # RCVAs which should theoretically be merged.
            rcva = ele.find('ReferenceClinVarAssertion')
            rcv_acc = rcva.find('ClinVarAccession').get('Acc')

            if rcv_acc not in rcv_map:
                # We do not have a record of this RCV from VCF, skip parsing...
                continue

            if len(rcv_map[rcv_acc]) != 1:
                # either no or too many variations for this RCV
                continue

            # Use the functions in RCVA_DATA to retrieve data for tags.
            val_store = dict()
            for rcva_key in RCVA_DATA:
                variable_type = RCVA_DATA[rcva_key][0]
                try:
                    if not variable_type:
                        value = RCVA_DATA[rcva_key][1]()
                    elif variable_type == 'ele':
                        value = RCVA_DATA[rcva_key][1](ele)
                    elif variable_type == 'rcva':
                        value = RCVA_DATA[rcva_key][1](rcva)
                except AttributeError:
                    # Some retrieval functions are chained and the parent elem
                    # isn't present. In that case, the data doesn't exist.
                    value = None
                if value:
                    val_store[rcva_key] = value

            # Get the hash of this data.
            xml_hash = self._hash_xml_dict(val_store)

            if rcv_acc not in rcv_hash_cache:
                # We got a brand new record
                rel = Relation(variant=variant_map[list(rcv_map[rcv_acc])[0]],
                               tags=val_store)
                relations_new.append(rel)
                rcv_hash_cache[rcv_acc] = (rel.pk, xml_hash)

                # TODO: set HGVS tag in Variant

                # logging.debug('Added new RCVA, accession: {}, {}'.format(
                #     rcv_acc, str(rcv_map[rcv_acc])))
            elif rcv_hash_cache[rcv_acc][1] != xml_hash:
                # XML parameters have changed, update required
                # logging.debug('Need to update accession: {}'.format(rcv_acc))
                rel = Relation.objects.get(**{
                    'tags__clinvar-accession:id': rcv_acc,
                    "tags__type": "clinvar-accession"})
                rel.tags.update(val_store)
                relations_updated.append(rel)
            else:
                # nothing to do here, move along
                pass

        self._save_as_revision(
            object_list=relations_new,
            user=clinvar_user,
            comment='Relation added based on presence in ClinVar ' +
                    'XML file: {}'.format(xml_filename))
        self._save_as_revision(
            object_list=relations_updated,
            user=clinvar_user,
            comment='Relation updated based on updated data detected in ' +
                    'ClinVar XML file: {}'.format(xml_filename))

        clinvar_xml.close()

        if not (local_vcf and local_xml):
            shutil.rmtree(tempdir)
            logging.debug('Removed tempdir {}'.format(tempdir))
