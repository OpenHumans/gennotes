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

    def test_get_specified_variant_list(self):
        """
        Ensure we can get a Variant with no credentials.
        """
        response = self.verify_request('/?variant_list=' +
                                       '%5B%22b37-1-883516-G-A%22%2C+' +
                                       '%22b37-1-891344-G-A%22%2C+' +
                                       '%22b37-1-906168-G-A%22%5D')

        self.assertEqual(response.data, {
            "count": 3, "next": None, "previous": None,
            "results": [
                {"b37_id": "1-883516-G-A",
                 "tags": {"ref_allele_b37": "G",
                          "pos_b37": "883516",
                          "chrom_b37": "1",
                          "var_allele_b37": "A"},
                 "relation_set": [{
                     "tags": {
                         "gene:name": "nucleolar complex associated 2 homolog (S. cerevisiae)",
                         "citations": "",
                         "record_status": "current",
                         "clinvar-accession:disease-name": "Malignant melanoma",
                         "xml:hash": "c37662731c8b5810157415f85f762232",
                         "gene:symbol": "NOC2L",
                         "clinvar-accession:significance": "not provided",
                         "clinvar-accession:id": "RCV000064926",
                         "clinvar-accession:version": "2",
                         "type": "clinvar-accession",
                         "num_submissions": "1"}}]},
                {"b37_id": "1-891344-G-A",
                 "tags": {"ref_allele_b37": "G",
                          "pos_b37": "891344",
                          "chrom_b37": "1",
                          "var_allele_b37": "A"},
                 "relation_set": [{
                     "tags": {
                         "gene:name": "nucleolar complex associated 2 homolog (S. cerevisiae)",
                         "citations": "",
                         "record_status": "current",
                         "clinvar-accession:disease-name": "Malignant melanoma",
                         "xml:hash": "7cb953c00c3283f2f0918ce62abee4dd",
                         "gene:symbol": "NOC2L",
                         "clinvar-accession:significance": "not provided",
                         "clinvar-accession:id": "RCV000064927",
                         "clinvar-accession:version": "2",
                         "type": "clinvar-accession",
                         "num_submissions": "1"}}]},
                {"b37_id": "1-906168-G-A",
                 "tags": {"ref_allele_b37": "G",
                          "pos_b37": "906168",
                          "chrom_b37": "1",
                          "var_allele_b37": "A"},
                 "relation_set": [{
                     "tags": {
                         "gene:name": "pleckstrin homology domain containing, family N member 1",
                         "citations": "",
                         "record_status": "current",
                         "clinvar-accession:disease-name": "Malignant melanoma",
                         "xml:hash": "50e62113f35bfeea8ae1e4bc1039c0a6",
                         "gene:symbol": "PLEKHN1",
                         "clinvar-accession:significance": "not provided",
                         "clinvar-accession:id": "RCV000064940",
                         "clinvar-accession:version": "2",
                         "type": "clinvar-accession",
                         "num_submissions": "1"}}]}]
        })
