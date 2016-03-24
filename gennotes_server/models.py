"""
Models for GenNotes Variant and Relation elements.

## About Tags
Most data in GenNotes is stored as key/value tags related to these elements.
Users aren't constrained by database design to particular keys or values, but
for now, I recommend tag keys match this regex format (it may be important for
later optimizing with db indexing and Django): `^[a-z][a-z0-9]*(_[a-z0-9]+)*`.
    -- Madeleine
"""
from django.contrib.postgres.fields import HStoreField, JSONField
from django.db import models

from oauth2_provider.models import AbstractApplication

from reversion import revisions as reversion
from reversion.models import Revision


class Variant(models.Model):
    """
    Gennotes Variant element model.

    ## Special Tags
    The following keys are currently special/protected. They're used to find a
    variant based on location and sequence and are indexed in our db to
    optimize searches:
    'chrom_b37', 'pos_b37', 'ref_allele_b37', 'var_allele_b37'
    """
    ALLOWED_CHROMS = [str(i) for i in range(1, 25)]
    tags = HStoreField()
    special_tags = ['chrom_b37', 'pos_b37', 'ref_allele_b37', 'var_allele_b37']
    required_tags = special_tags

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
    tags = JSONField()
    special_tags = ['type']
    required_tags = ['type']

    def __unicode__(self):
        return 'Relation: {}, Type: {}'.format(str(self.pk), self.tags['type'])


class CommitDeletion(models.Model):
    revision = models.ForeignKey(Revision)
    deletion = models.BooleanField(default=True)


reversion.register(Variant)
reversion.register(Relation)


class EditingApplication(AbstractApplication):
    """
    OAuth2 provider application for submitting edits on behalf of users.

    (Putting notes here for now on how to get token...)
    1) send user to:
        /oauth2-app/authorize?client_id=[client-id-here]&response_type=code
    2) your default redirect_uri will receive the following:
        yourdomain.com/path/to/redirect_uri?code=[grant-code]
    3) exchange that grant code for a token immediately. example w/ requests:
        Set this up with your client_id and client_secret:
            client_auth = requests.auth.HTTPBasicAuth(client_id, client_secret)
        Set code:
            code = [the grant-code you just received]
        Set redirect_uri (required by our framework...):
            redirect_uri = [a redirect uri you registered]
        Set the GenNotes receiving uri... e.g. for local testing I use:
            token_uri = 'http://localhost:8000/oauth2-app/token/'
        POST to this:
            response_token = requests.post(token_uri, data={
                'grant_type': 'authorization_code',
                'code': code, 'redirect_uri': redirect_uri}, auth=client_auth)
        The response should contain an access token, e.g.:
            {'access_token': '1hu94IRBX3da0euOiX0u3E9h',
             'token_type': 'Bearer',
             'expires_in': 36000,
             'refresh_token': 'WSuwoeBO0e9JFHqY7TnpDi7jUjgAex',
             'scope': 'commit-edit'}
        To use the refresh token to get new tokens:
            refresh_token = response_token.json()['refresh_token']
            response_refresh = requests.post(token_uri, data={
                'grant_type': 'refresh_token',
                'refresh_token': refresh_token}, auth=client_auth)
    """
    description = models.CharField(max_length=300)
