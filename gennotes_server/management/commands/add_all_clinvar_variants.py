import codecs
import fileinput
from ftplib import FTP
import gzip
from optparse import make_option
import os
import re
import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
import reversion
from vcf2clinvar.clinvar import ClinVarVCFLine

from gennotes_server.models import Variant
from gennotes_server.utils import map_chrom_to_index


try:
    # faster implementation using bindings to libxml
    from lxml import etree as ET
except ImportError:
    print 'Falling back to default ElementTree implementation'
    from xml.etree import ElementTree as ET

CV_VCF_DIR = 'pub/clinvar/vcf_GRCh37'
CV_XML_DIR = 'pub/clinvar/xml'

CV_VCF_REGEX = r'^clinvar_[0-9]{8}.vcf.gz$'
CV_XML_REGEX = r'^ClinVarFullRelease_[0-9]{4}-[0-9]{2}.xml.gz$'

SPLITTER = re.compile('[,|]')

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
    
    def _get_elements(self, fp, tag):
        '''
            Convenience and memory management function that iterates required tags
        '''
        context = iter(ET.iterparse(fp, events=('start', 'end')))
        _, root = next(context) # get root element
        for event, elem in context:
            if event == 'end' and elem.tag == tag:
                yield elem
                root.clear() # preserve memory
    
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
        cv_xml_w_date = sorted([f for f in ftp.nlst() if re.match(CV_XML_REGEX, f)])
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
    def handle(self, local_vcf=None, local_xml=None, *args, **options):
        print get_user_model().objects.all()
        clinvar_user = get_user_model().objects.get(
            username='clinvar-variant-importer')
        print clinvar_user
        tempdir = tempfile.mkdtemp()
        print "Created tempdir {}".format(tempdir)
        if local_vcf:
            clinvar_fp, clinvar_filename = local_vcf, os.path.split(local_vcf)[-1]
        else:
            clinvar_fp, clinvar_filename = self._download_latest_clinvar(tempdir)
        print "Downloaded latest Clinvar, stored at {}".format(clinvar_fp)
        
        # speed optimization
        variant_map = {(
                        v.tags['chrom_b37'], 
                        v.tags['pos_b37'], 
                        v.tags['ref_allele_b37'], 
                        v.tags['var_allele_b37']): v.pk for v in Variant.objects.all()}
        rcv_map = {}
        
        print 'Reading VCF'
        clinvar_vcf = self._open(clinvar_fp)
        
        for line in clinvar_vcf:
            if line.startswith('#'):
                continue
            
            cvvl = ClinVarVCFLine(vcf_line=line).as_dict()
            
            data = line.rstrip('\n').split('\t')
            chrom = map_chrom_to_index(data[0])
            pos = data[1]
            ref_allele = data[3]
            var_alleles = data[4].split(',')
            all_alleles = [ref_allele] + var_alleles
            info_dict = {v[0]: v[1] for v in
                         [x.split('=') for x in data[7].split(';')]
                         if len(v) == 2}
            
            for allele in info_dict['CLNALLE'].split(','):
                var_allele = all_alleles[int(allele)]
                var_key = (chrom, pos, ref_allele, var_allele)
                if var_key not in variant_map:
                    print 'Inserting new Variant {}, {}, {}, {}'.format(*var_key)
                    variant = Variant(tags={
                        'chrom_b37': chrom,
                        # Check pos is a valid int before adding.
                        'pos_b37': str(int(pos)),
                        'ref_allele_b37': ref_allele,
                        'var_allele_b37': var_allele})
                    variant.save()
                    variant_map[var_key] = variant.pk
                    reversion.set_user(user=clinvar_user)
                    reversion.set_comment(
                        'Variant added based on presence in ClinVar file: ' +
                        clinvar_filename)
                
                for record in cvvl['alleles'][int(allele)].get('records', []):
                    rcv, rcv_ver = record['acc'].split('.')
                    rcv_map.setdefault((rcv, rcv_ver), set()).add(variant_map[var_key])
                
        clinvar_vcf.close()
        
        print 'Multiple variants for single RCV#:'
        for k, v in rcv_map.iteritems():
            if len(v) > 1:
                print '\t', k[0], k[1], Variant.objects.filter(pk__in=list(v))
        
        if local_xml:
            clinvar_fp, clinvar_filename = local_xml, os.path.split(local_xml)[-1]
        else:
            clinvar_fp, clinvar_filename = self._download_latest_clinvar_xml(tempdir)
        print "Downloaded latest Clinvar XML, stored at {}".format(clinvar_fp)
        
        print 'Reading XML'
        clinvar_xml = self._open(clinvar_fp)
        i = 0
        for ele in self._get_elements(clinvar_xml, 'ClinVarSet'):
            rcva = ele.find('ReferenceClinVarAssertion')
            i+= 1
            
            ref_acc = rcva.find('ClinVarAccession')
            rcv, rcv_ver = ref_acc.get('Acc'), ref_acc.get('Version')
            
            if (rcv, rcv_ver) not in rcv_map:
                # We do not have a record of this RCV from VCF, skip parsing...
                continue
            
            val_store = {"type": "clinvar-accession", "clinvar-accession:id": rcv, "clinvar-accession:version": rcv_ver}
            val_store["clinvar-accession:significance"] = rcva.findtext('ClinicalSignificance/Description')
            val_store["clinvar-accession:disease-name"] = rcva.findtext('TraitSet[@Type="Disease"]/Trait[@Type="Disease"]/Name/ElementValue[@Type="Preferred"]')
            
            val_store['num_submissions'] = len(ele.findall('ClinVarAssertion'))
            val_store['record_status'] = rcva.findtext('RecordStatus')
            
            ch = rcva.find('MeasureSet/Measure/MeasureRelationship[@Type="variant in gene"]')
            if ch is not None:
                val_store['gene:name'] = ch.findtext('Name/ElementValue')
                val_store['gene:symbol'] = ch.findtext('Symbol/ElementValue')
            
            citations = rcva.findall('MeasureSet/Measure/Citation/ID[@Source="PubMed"]')
            if citations:
                val_store['citations'] = ';'.join(['PMID%s' % c.text for c in citations])
            
            print i, rcv, rcv_ver, rcv_map.get((rcv, rcv_ver))
            for k, v in sorted(val_store.iteritems()):
                print '\t %s := %s' % (k, v)
            
            if i == 100: break
        
        clinvar_xml.close()
        
        shutil.rmtree(tempdir)
