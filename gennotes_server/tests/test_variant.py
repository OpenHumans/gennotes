import json

from test_helpers import APITestCase

ERR_NO_DELETE = {'detail': 'Method "DELETE" not allowed.'}
ERR_NO_POST = {'detail': 'Method "POST" not allowed.'}
ERR_NOAUTH = {'detail': 'Authentication credentials were not provided.'}
ERR_CHR_CHNG = {'detail': "Updates (PUT or PATCH) must not attempt to change "
                          "the values for special tags. Your request "
                          "attempts to change the value for tag 'chrom_b37' "
                          "from '1' to '2'"}
ERR_REL_INC = {'detail': "Edits must update the 'tags' field of a Variant or "
                         "Relation, and no other object fields. Your request "
                         "includes the following object fields: "
                         "[u'relation_set', u'tags']"}


class VariantTests(APITestCase):
    """
    Test the Variant API.
    """
    base_path = '/variant'
    fixtures = ['gennotes_server/fixtures/test-data.json']

    def test_post_variant(self):
        """
        Test Variant POST responses.
        """
        data = {'tags': {'chrom_b37': '1', 'pos_b37': '123456',
                         'ref_allele_b37': 'A', 'var_allele_b37': 'G'}}
        # Unauthenticated
        self.verify_request(path='/b37-1-883516-G-A/', method='post',
                            expected_data=ERR_NOAUTH, expected_status=401,
                            data=data, format='json')
        # Authenticated
        self.client.login(username='testuser', password='password')
        self.verify_request(path='/b37-1-883516-G-A/', method='post',
                            expected_data=ERR_NO_POST, expected_status=405,
                            data=data, format='json')
        self.client.logout()

    def test_delete_variant(self):
        """
        Test Variant DELETE responses.
        """
        # Unauthenticated
        self.verify_request(path='/b37-1-883516-G-A/', method='delete',
                            expected_data=ERR_NOAUTH, expected_status=401)
        # Authenticated
        self.client.login(username='testuser', password='password')
        self.verify_request(path='/b37-1-883516-G-A/', method='delete',
                            expected_data=ERR_NO_DELETE, expected_status=405)
        self.client.logout()

    def test_get_variant(self):
        """
        Test getting data for a single Variant.
        """
        with open('gennotes_server/tests/expected_data/variant.json') as f:
            expected_data = json.load(f)

        # Look up by primary key.
        self.verify_request(path='/1/', method='get',
                            expected_data=expected_data, expected_status=200)

        # Look up by build 37 information.
        self.verify_request(path='/b37-1-883516-G-A/', method='get',
                            expected_data=expected_data, expected_status=200)

    def test_get_specified_variant_list(self):
        """
        Test getting data for a specified list of Variants.
        """
        data = {'variant_list': json.dumps(
            ['b37-1-883516-G-A', 'b37-1-891344-G-A', '3'])}

        with open('gennotes_server/tests/expected_data/'
                  'specified_variant_list.json') as f:
            expected_data = json.load(f)

        self.verify_request(path='/', method='get',
                            expected_data=expected_data, expected_status=200,
                            data=data)

    def test_get_variant_list(self):
        """
        Test getting full list of Variant data.
        """
        with open('gennotes_server/tests/expected_data/'
                  'variant_list.json') as f:
            expected_data = json.load(f)

        self.verify_request(path='/', method='get',
                            expected_data=expected_data, expected_status=200)

    def test_put_variant(self):
        """
        Test Variant PUT responses.
        """
        good_data = {"tags": {"chrom_b37": "1", "pos_b37": "883516",
                              "ref_allele_b37": "G", "var_allele_b37": "A",
                              "test_tag": "test_value"},
                     "edited-version": 1}
        with open('gennotes_server/tests/expected_data/'
                  'variant_put_patch1.json') as f:
            expected_data = json.load(f)

        # Test unauthorized.
        self.verify_request(path='/b37-1-883516-G-A/', method='put',
                            expected_data=ERR_NOAUTH, expected_status=401,
                            data=good_data, format='json')

        # Test bad data.
        # Should only have tags field, and all special tags included unchanged.
        bad_data_1 = {"tags": {"chrom_b37": "1", "pos_b37": "883516",
                               "ref_allele_b37": "G", "var_allele_b37": "A",
                               "test_tag": "test_value"},
                      "relation_set": [{
                          "tags": {"type": "test-relation"},
                          "variant": "http://testserver/api/variant/1/"}],
                      "edited-version": 1}
        err_1 = ERR_REL_INC
        bad_data_2 = {"tags": {"chrom_b37": "2", "pos_b37": "883516",
                               "ref_allele_b37": "G", "var_allele_b37": "A",
                               "test_tag": "test_value"},
                      "edited-version": 1}
        err_2 = ERR_CHR_CHNG
        bad_data_3 = {"tags": {"chrom_b37": "1", "test_tag": "test_value"},
                      "edited-version": 1}
        err_3 = {'detail': "PUT requests must retain all special tags. Your "
                           "request is missing the tag: pos_b37"}

        self.client.login(username='testuser', password='password')

        # Test disallowed field 'relation_set'.
        self.verify_request(path='/b37-1-883516-G-A/', method='put',
                            expected_data=err_1, expected_status=400,
                            data=bad_data_1, format='json')
        # Test changing special tag.
        self.verify_request(path='/b37-1-883516-G-A/', method='put',
                            expected_data=err_2, expected_status=400,
                            data=bad_data_2, format='json')
        # Test missing special tags.
        self.verify_request(path='/b37-1-883516-G-A/', method='put',
                            expected_data=err_3, expected_status=400,
                            data=bad_data_3, format='json')

        # Test good request.
        self.verify_request(path='/b37-1-883516-G-A/', method='put',
                            expected_data=expected_data, expected_status=200,
                            data=good_data, format='json')

        self.client.logout()

    def test_patch_variant(self):
        """
        Test Variant PATCH responses.
        """
        good_data_1 = {"tags": {"chrom_b37": "1", "test_tag": "test_value"},
                       "edited-version": 1}
        good_data_2 = {"tags": {"test_tag": "test_value_2"},
                       "edited-version": 21}
        with open('gennotes_server/tests/expected_data/'
                  'variant_put_patch1.json') as f:
            expected_data_1 = json.load(f)
        with open('gennotes_server/tests/expected_data/'
                  'variant_patch2.json') as f:
            expected_data_2 = json.load(f)

        # Test unauthorized.
        self.verify_request(path='/b37-1-883516-G-A/', method='patch',
                            expected_data=ERR_NOAUTH, expected_status=401,
                            data=good_data_1, format='json')

        # Test bad data.
        # Should only have tags field. If included, special tags unchanged.
        bad_data_1 = {"tags": {"chrom_b37": "1", "pos_b37": "883516",
                               "ref_allele_b37": "G", "var_allele_b37": "A",
                               "test_tag": "test_value"},
                      "relation_set": [{
                          "tags": {"type": "test-relation"},
                          "variant": "http://testserver/api/variant/1/"}],
                      "edited-version": 1}
        err_1 = ERR_REL_INC
        bad_data_2 = {"tags": {"chrom_b37": "2", "test_tag": "test_value"},
                      "edited-version": 1}
        err_2 = ERR_CHR_CHNG

        self.client.login(username='testuser', password='password')

        # Test disallowed field 'relation_set'.
        self.verify_request(path='/b37-1-883516-G-A/', method='patch',
                            expected_data=err_1, expected_status=400,
                            data=bad_data_1, format='json')
        # Test changing special tag.
        self.verify_request(path='/b37-1-883516-G-A/', method='patch',
                            expected_data=err_2, expected_status=400,
                            data=bad_data_2, format='json')

        # Test good request #1.
        self.verify_request(path='/b37-1-883516-G-A/', method='patch',
                            expected_data=expected_data_1, expected_status=200,
                            data=good_data_1, format='json')

        # Test good request #2.
        self.verify_request(path='/b37-1-883516-G-A/', method='patch',
                            expected_data=expected_data_2, expected_status=200,
                            data=good_data_2, format='json')

        self.client.logout()
