"""
Models for GenNotes Variant and Relation elements.

## About Tags
Most data in GenNotes is stored as key/value tags related to these elements.
Users aren't constrained by database design to particular keys or values, but
for now, I recommend tag keys match this regex format (it may be important for
later optimizing with db indexing and Django): `^[a-z][a-z0-9]*(_[a-z0-9]+)*`.
    -- Madeleine
"""
from django.contrib.postgres.fields import HStoreField
from django.db import models

import reversion


class Variant(models.Model):
    """
    Gennotes Variant element model.

    ## Special Tags
    The following keys are currently special/protected. They're used to find a
    variant based on location and sequence and are indexed in our db to
    optimize searches:
    'chrom-b37', 'pos-b37', 'ref-allele-b37', 'var-allele-b37'
    """
    tags = HStoreField()
    special_tags = ['chrom-b37', 'pos-b37', 'ref-allele-b37', 'var-allele-b37']

    def __unicode__(self):
        return u'; '.join([u'%s=%s' % (k, v) for k, v in self.tags.iteritems()])


class Relation(models.Model):
    """
    Gennotes Relation element model.

    ## Special Tags
    The following key is special/protected; it's used to identify a relation
    and is indexed in our db to optimize searches:
    'type'
    """
    variant = models.ForeignKey(Variant)
    tags = HStoreField()

    def __unicode__(self):
        return 'Relation: {}, Type: {}'.format(str(self.pk), self.tags['type'])


reversion.register(Variant)
reversion.register(Relation)
