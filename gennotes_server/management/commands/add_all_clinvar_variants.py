from ftplib import FTP
import gzip
import os
import re
import shutil
import tempfile

from django.core.management.base import BaseCommand, CommandError

from gennotes_server.models import map_chrom_to_index, Variant

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
        return dest_filepath

    def handle(self, *args, **options):
        tempdir = tempfile.mkdtemp()
        print "Created tempdir {}".format(tempdir)
        clinvar_fp = self._download_latest_clinvar(tempdir)
        print "Downloaded latest Clinvar, stored at {}".format(clinvar_fp)
        clinvar_vcf = gzip.open(clinvar_fp)
        new_variants = []
        for line in clinvar_vcf:
            if line.startswith('#'):
                continue
            data = line.rstrip('\n').split('\t')
            chrom = map_chrom_to_index(data[0])
            pos = int(data[1])
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
                    chrom=chrom,
                    pos=pos,
                    ref_allele=ref_allele,
                    var_allele=var_allele)
                if not matched_var.exists():
                    variant = Variant(chrom=chrom,
                                      pos=pos,
                                      ref_allele=ref_allele,
                                      var_allele=var_allele)
                    new_variants.append(variant)
        print "Adding {0} new variants to database".format(len(new_variants))
        Variant.objects.bulk_create(new_variants)
        shutil.rmtree(tempdir)
