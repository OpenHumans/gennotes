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
        response = self.verify_request('/b37-1-883516-G-A/')

        self.assertEqual(response.data, {
            'b37_id': '1-883516-G-A',
            'tags': {
                'chrom_b37': '1',
                'pos_b37': '883516',
                'ref_allele_b37': 'G',
                'var_allele_b37': 'A',
            },
            'relation_set': [
                {
                    'tags': {
                        'gene:name': 'nucleolar complex associated 2 homolog (S. cerevisiae)',
                        'citations': '',
                        'record_status': 'current',
                        'clinvar-accession:disease-name': 'Malignant melanoma',
                        'xml:hash': 'c37662731c8b5810157415f85f762232',
                        'gene:symbol': 'NOC2L',
                        'clinvar-accession:significance': 'not provided',
                        'clinvar-accession:id': 'RCV000064926',
                        'clinvar-accession:version': '2',
                        'type': 'clinvar-accession',
                        'num_submissions': '1',
                    }
                }
            ]
        })

        # TODO: should be 405, method not allowed
        self.verify_request('/b37-1-883516-G-A/', status=403, method='delete')
        self.verify_request('/b37-1-883516-G-A/', method='post', status=403,
                            data={'tags': '{"a": "b"}'})

        self.verify_request('/garbage/', status=404)
