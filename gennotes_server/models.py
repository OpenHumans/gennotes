from django.contrib.postgres.fields import HStoreField
from django.db import models

import reversion


class Variant(models.Model):
    # This is roughly equivalent to a "node" in OSM.
    # Expected/protected tags:
    # 'chrom-b37', 'pos-b37', 'ref-allele-b37', 'var-allele-b37'
    # Chromosome values should be integers, with X=24, Y=25, MT=26.
    tags = HStoreField()


class Relation(models.Model):
    # Example relations:
    #  - "type": "ClinVar accession", a relation to a single Variant member,
    #    with tags regarding associated data from ClinVar, and tags from
    #    Genevieve.
    #  - "type": "ExAC variant", a relation to a single Variant member, with
    #    tags regarding associated data from ExAC.
    #
    # I'm having trouble imagining Relations that aren't to a single Variant.
    #
    # "When should something be a relation vs. a tag on the variant?"
    # Some thoughts...
    # - There can only be one tag for a given key. If a given 'type' (e.g. a
    #   ClinVar accession) could have multiple valid values for a given item
    #   (e.g. multiple accessions for a given Variant) then it doesn't make
    #   sense to try to store it as tags (where the 'type' is the key).
    # - If there's multiple related data to associate with the variant, e.g.
    #   ExAC data, it makes sense to store these as tags on a relation to the
    #   variant rather than tags on the item itself.
    variant = models.ForeignKey(Variant)

    # Expected/protected tags: 'type'
    tags = HStoreField()


reversion.register(Variant)
reversion.register(Relation)
