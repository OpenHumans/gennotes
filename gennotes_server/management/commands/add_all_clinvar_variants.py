from ftplib import FTP
import gzip
import os
import re
import shutil
import tempfile

import reversion

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from gennotes_server.models import Variant
from gennotes_server.utils import map_chrom_to_index

CV_VCF_DIR = 'pub/clinvar/vcf_GRCh37'
CV_VCF_REGEX = r'^clinvar_[0-9]{8}.vcf.gz$'


class Command(BaseCommand):
    help = 'Download latest ClinVar VCF, import variants not already in db.'

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

    @transaction.atomic()
    @reversion.create_revision()
    def handle(self, *args, **options):
        print get_user_model().objects.all()
        clinvar_user = get_user_model().objects.get(
            username='clinvar-variant-importer')
        print clinvar_user
        tempdir = tempfile.mkdtemp()
        print "Created tempdir {}".format(tempdir)
        clinvar_fp, clinvar_filename = self._download_latest_clinvar(tempdir)
        print "Downloaded latest Clinvar, stored at {}".format(clinvar_fp)
        clinvar_vcf = gzip.open(clinvar_fp)
        for line in clinvar_vcf:
            if line.startswith('#'):
                continue
            data = line.rstrip('\n').split('\t')
            chrom = map_chrom_to_index(data[0])
            pos = data[1]
            ref_allele = data[3]
            var_alleles = data[4].split(',')
            all_alleles = [ref_allele] + var_alleles
            info_dict = {v[0]: v[1] for v in
                         [x.split('=') for x in data[7].split(';')]
                         if len(v) == 2}
            all_variants = Variant.objects.all()
            for allele in info_dict['CLNALLE'].split(','):
                var_allele = all_alleles[int(allele)]
                matched_var = all_variants.filter(
                    tags__chrom_b37=chrom,
                    tags__pos_b37=pos,
                    tags__ref_allele_b37=ref_allele,
                    tags__var_allele_b37=var_allele)
                if not matched_var.exists():
                    variant = Variant(tags={
                        'chrom_b37': chrom,
                        # Check pos is a valid int before adding.
                        'pos_b37': str(int(pos)),
                        'ref_allele_b37': ref_allele,
                        'var_allele_b37': var_allele})
                    variant.save()
                    reversion.set_user(user=clinvar_user)
                    reversion.set_comment(
                        'Variant added based on presence in ClinVar file: ' +
                        clinvar_filename)
        shutil.rmtree(tempdir)
