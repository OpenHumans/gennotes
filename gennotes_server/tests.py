from .test_helpers import APITestCase


class VariantTests(APITestCase):
    """
    Test the Variant API.
    """

    base_url = '/variant'

    def test_get_variant(self):
        """
        Ensure we can get a Variant with no credentials.
        """
        response = self.verify_request('/1-883516-G-A/')

        self.assertEqual(response.data, {
            'tags': {
                'chrom_b37': '1',
                'pos_b37': '883516',
                'ref_allele_b37': 'G',
                'var_allele_b37': 'A',
            },
        })

        # TODO: should be 405, method not allowed
        self.verify_request('/1-883516-G-A/', status=403, method='delete')
        self.verify_request('/1-883516-G-A/', method='post', status=403,
                            data={'tags': '{"a": "b"}'})

        self.verify_request('/garbage/', status=404)
