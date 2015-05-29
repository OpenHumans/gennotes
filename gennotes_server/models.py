from collections import OrderedDict

from django.conf import settings
from django.contrib.postgres.fields import HStoreField
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
    # This is roughly equivalent to a "node" in OSM.
    chrom = models.PositiveSmallIntegerField(choices=CHROMOSOMES.items())
    pos = models.PositiveIntegerField()
    ref_allele = models.CharField(max_length=255)
    var_allele = models.CharField(max_length=255)
    tags = HStoreField()


class Relation(models.Model):
    # Is Relation the best name?
    #
    # In OSM, a relation has an ordered list of member elements (node, way,
    # and/or relation). The equivalent member elements for us would be variant
    # and relation. I think it could be done with two fields, but would we take
    # an efficiency hit on searching? (I don't know enough about dbs.) -mpb
    # e.g.
    # member_types = ArrayField(ForeignKey(ContentType))
    # member_ids = ArrayField(PositiveIntegerField())
    # Instead of ...
    variant = models.ForeignKey(Variant)
    # Example relations:
    #  - "type": "ClinVar accession", a relation to a single Variant member,
    #    with tags regarding associated data from ClinVar, and tags from
    #    Genevieve.
    #  - "type": "ExAC variant", a relation to a single Variant member, with
    #    tags regarding associated data from ExAC.
    #
    # I'm having trouble imagining Relations that aren't to a single Variant.
    #
    # "When should something be a relation, and when should it be a tag?"
    # Some thoughts...
    # - There can only be one tag for a given key. If a given 'type' (e.g. a
    #   ClinVar accession) could have multiple valid values for a given item
    #   (e.g. multiple accessions for a given Variant) then it doesn't make
    #   sense to try to store it as tags (where the 'type' is the key).
    # - If there's multiple related data to associate with the item, e.g. ExAC
    #   data, it may make sense to store these as tags on a relation to the
    #   item rather than tags on the item itself?

    # Type stored as 'type' tag in OSM - should it be a hardcoded field? -mpb
    tags = HStoreField()


class EditSet(models.Model):
    # Roughly equivalent to OSM's Changeset?
    # Note that EditSets are not themselves editable, they are logs.
    # While OSM stores user as a tag on the EditSet, maybe we should hardcode
    # it, make sure we always have a legit user associated with edits? -mpb
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    timestamp = models.DateTimeField()
    # EditSet comments stored as a 'comments' tag.
    tags = HStoreField()


class VariantEdit(models.Model):
    # VariantEdit comments stored as a 'comments' tag.
    # Note that VariantEdits are not themselves editable, they are logs.
    tags = HStoreField()
    edit_set = models.ForeignKey(EditSet)
    variant = models.ForeignKey(Variant)
    # Values for this relation tags as of this edit?
    variant_chrom = models.PositiveSmallIntegerField(
        choices=CHROMOSOMES.items())
    variant_pos = models.PositiveIntegerField()
    variant_ref_allele = models.CharField(max_length=255)
    variant_var_allele = models.CharField(max_length=255)
    variant_tags = HStoreField()


class RelationEdit(models.Model):
    # RelationEdit comments stored as a 'comments' tag.
    # Note that RelationEdits are not themselves editable, they are logs.
    tags = HStoreField()
    edit_set = models.ForeignKey(EditSet)
    relation = models.ForeignKey(Relation)
    # Values for this relation tags as of this edit?
    relation_variant = models.ForeignKey(Variant)
    relation_tags = HStoreField()
