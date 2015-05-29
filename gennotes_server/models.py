from collections import OrderedDict

from django.db import models

CHROMOSOMES = OrderedDict([
    (1, 'chr1'),
    (2, 'chr2'),
    (3, 'chr3'),
    (4, 'chr4'),
    (5, 'chr5'),
    (6, 'chr6'),
    (7, 'chr7'),
    (8, 'chr8'),
    (9, 'chr9'),
    (10, 'chr10'),
    (11, 'chr11'),
    (12, 'chr12'),
    (13, 'chr13'),
    (14, 'chr14'),
    (15, 'chr15'),
    (16, 'chr16'),
    (17, 'chr17'),
    (18, 'chr18'),
    (19, 'chr19'),
    (20, 'chr20'),
    (21, 'chr21'),
    (22, 'chr22'),
    (23, 'chrX'),
    (24, 'chrY'),
    (25, 'chrM'),
    ])


def map_chrom_to_index(chrom_str):
    if chrom_str.startswith('chr' or 'Chr'):
        chrom_str = chrom_str[3:]
    if chrom_str.startswith('ch' or 'Ch'):
        chrom_str = chrom_str[2:]
    try:
        return int(chrom_str)
    except ValueError:
        if chrom_str == 'X':
            return 23
        elif chrom_str == 'Y':
            return 24
        elif chrom_str in ['M', 'MT']:
            return 25
    raise ValueError("Can't determine chromosome for {0}".format(chrom_str))


class Variant(models.Model):
    chrom = models.PositiveSmallIntegerField(choices=CHROMOSOMES.items())
    pos = models.PositiveIntegerField()
    ref_allele = models.CharField(max_length=255)
    var_allele = models.CharField(max_length=255)
