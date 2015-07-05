import json

from test_helpers import APITestCase

ERR_NO_DELETE = {'detail': 'Method "DELETE" not allowed.'}
ERR_NO_POST = {'detail': 'Method "POST" not allowed.'}
ERR_UNAUTH = {'detail': 'Authentication credentials were not provided.'}


class VariantTests(APITestCase):
    """
    Test the Variant API.
    """
    base_path = '/variant'
    fixtures = ['gennotes_server/fixtures/test-data.json']

    def test_post_variant(self):
        """
        Test POST responses.
        """
        data = {'tags': {'chrom-b37': '1', 'pos-b37': '123456',
                         'ref-allele-b37': 'A', 'var-allele-b37': 'G'}}
        # Unauthenticated
        self.verify_request(path='/b37-1-883516-G-A/', method='post',
                            expected_data=ERR_UNAUTH, expected_status=403,
                            data=data, format='json')
        # Authenticated
        self.client.login(username='testuser', password='password')
        self.verify_request(path='/b37-1-883516-G-A/', method='post',
                            expected_data=ERR_NO_POST, expected_status=405,
                            data=data, format='json')
        self.client.logout()

    def test_delete_variant(self):
        """
        Test DELETE responses.
        """
        # Unauthenticated
        self.verify_request(path='/b37-1-883516-G-A/', method='delete',
                            expected_data=ERR_UNAUTH, expected_status=403)
        # Authenticated
        self.client.login(username='testuser', password='password')
        self.verify_request(path='/b37-1-883516-G-A/', method='delete',
                            expected_data=ERR_NO_DELETE, expected_status=405)
        self.client.logout()

    def test_get_variant(self):
        """
        Ensure we can get a Variant with no credentials.
        """
        response = self.client.get('/api/variant/b37-1-883516-G-A/')

        expected_data = {
            'url': 'http://testserver/api/variant/1/',
            'b37_id': 'b37-1-883516-G-A',
            'tags': {
                'chrom-b37': '1',
                'pos-b37': '883516',
                'ref-allele-b37': 'G',
                'var-allele-b37': 'A',
            },
            'relation_set': [
                {
                    'url': 'http://testserver/api/relation/8/',
                    'variant': 'http://testserver/api/variant/1/',
                    'tags': {
                        'clinvar-rcva:record-status': 'current',
                        'clinvar-rcva:num-submissions': '1',
                        'clinvar-rcva:trait-type': 'Disease',
                        'clinvar-rcva:trait-name': 'Malignant melanoma',
                        "clinvar-rcva:preferred-name": "NM_015658.3(NOC2L):c.1654C>T (p.Leu552=)",
                        'clinvar-rcva:significance': 'not provided',
                        'clinvar-rcva:version': '2',
                        'clinvar-rcva:gene-name': 'nucleolar complex associated 2 homolog (S. cerevisiae)',
                        'clinvar-rcva:accession': 'RCV000064926',
                        'clinvar-rcva:gene-symbol': 'NOC2L',
                        'type': 'clinvar-rcva',
                    }
                }
            ]
        }
        self.verify_request(path='/b37-1-883516-G-A/', method='get',
                            expected_data=expected_data, expected_status=200)

    def test_get_specified_variant_list(self):
        """
        Ensure we can get a Variant with no credentials.
        """
        data = {'variant_list': json.dumps(
            ['b37-1-883516-G-A', 'b37-1-891344-G-A', '3'])}

        expected_data = {
            "count": 3, "next": None, "previous": None,
            "results": [
                {"url": "http://testserver/api/variant/1/",
                 "b37_id": "b37-1-883516-G-A",
                 "tags": {"ref-allele-b37": "G",
                          "pos-b37": "883516",
                          "chrom-b37": "1",
                          "var-allele-b37": "A"},
                 "relation_set": [{
                     "url": "http://testserver/api/relation/8/",
                     "tags": {
                         "clinvar-rcva:record-status": "current",
                         "clinvar-rcva:num-submissions": "1",
                         "clinvar-rcva:trait-type": "Disease",
                         "clinvar-rcva:trait-name": "Malignant melanoma",
                         "clinvar-rcva:preferred-name": "NM_015658.3(NOC2L):c.1654C>T (p.Leu552=)",
                         "clinvar-rcva:significance": "not provided",
                         "clinvar-rcva:version": "2",
                         "clinvar-rcva:gene-name": "nucleolar complex associated 2 homolog (S. cerevisiae)",
                         "clinvar-rcva:accession": "RCV000064926",
                         "clinvar-rcva:gene-symbol": "NOC2L",
                         "type": "clinvar-rcva"},
                     "variant": "http://testserver/api/variant/1/"}]},
                {"url": "http://testserver/api/variant/2/",
                 "b37_id": "b37-1-891344-G-A",
                 "tags": {"ref-allele-b37": "G",
                          "pos-b37": "891344",
                          "chrom-b37": "1",
                          "var-allele-b37": "A"},
                 "relation_set": [{
                     "url": "http://testserver/api/relation/9/",
                     "tags": {
                         "clinvar-rcva:record-status": "current",
                         "clinvar-rcva:num-submissions": "1",
                         "clinvar-rcva:trait-type": "Disease",
                         "clinvar-rcva:trait-name": "Malignant melanoma",
                         "clinvar-rcva:preferred-name": "NM_015658.3(NOC2L):c.657C>T (p.Leu219=)",
                         "clinvar-rcva:significance": "not provided",
                         "clinvar-rcva:version": "2",
                         "clinvar-rcva:gene-name": "nucleolar complex associated 2 homolog (S. cerevisiae)",
                         "clinvar-rcva:accession": "RCV000064927",
                         "clinvar-rcva:gene-symbol": "NOC2L",
                         "type": "clinvar-rcva"},
                     "variant": "http://testserver/api/variant/2/"}]},
                {"url": "http://testserver/api/variant/3/",
                 "b37_id": "b37-1-906168-G-A",
                 "tags": {"ref-allele-b37": "G",
                          "pos-b37": "906168",
                          "chrom-b37": "1",
                          "var-allele-b37": "A"},
                 "relation_set": [{
                     "url": "http://testserver/api/relation/10/",
                     "tags": {
                         "clinvar-rcva:record-status": "current",
                         "clinvar-rcva:num-submissions": "1",
                         "clinvar-rcva:trait-type": "Disease",
                         "clinvar-rcva:trait-name": "Malignant melanoma",
                         "clinvar-rcva:preferred-name": "NM_001160184.1(PLEKHN1):c.484+30G>A",
                         "clinvar-rcva:significance": "not provided",
                         "clinvar-rcva:version": "2",
                         "clinvar-rcva:gene-name": "pleckstrin homology domain containing, family N member 1",
                         "clinvar-rcva:accession": "RCV000064940",
                         "clinvar-rcva:gene-symbol": "PLEKHN1",
                         "type": "clinvar-rcva"},
                     "variant": "http://testserver/api/variant/3/"}]}]
        }

        self.verify_request(path='/', method='get',
                            expected_data=expected_data, expected_status=200,
                            data=data)
