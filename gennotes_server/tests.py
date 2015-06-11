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
                'chrom-b37': '1',
                'pos-b37': '883516',
                'ref-allele-b37': 'G',
                'var-allele-b37': 'A',
            },
            'relation_set': [
                {
                    'tags': {
                        'clinvar-rcva:record-status': 'current',
                        'clinvar-rcva:num-submissions': '1',
                        'clinvar-rcva:disease-name': 'Malignant melanoma',
                        'clinvar-rcva:significance': 'not provided',
                        'clinvar-rcva:citations': '',
                        'clinvar-rcva:version': '2',
                        'clinvar-rcva:gene-name': 'nucleolar complex associated 2 homolog (S. cerevisiae)',
                        'clinvar-rcva:accession': 'RCV000064926',
                        'clinvar-rcva:gene-symbol': 'NOC2L',
                        'type': 'clinvar-rcva',
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
                 "tags": {"ref-allele-b37": "G",
                          "pos-b37": "883516",
                          "chrom-b37": "1",
                          "var-allele-b37": "A"},
                 "relation_set": [{
                     "tags": {
                         "clinvar-rcva:record-status": "current",
                         "clinvar-rcva:num-submissions": "1",
                         "clinvar-rcva:disease-name": "Malignant melanoma",
                         "clinvar-rcva:significance": "not provided",
                         "clinvar-rcva:citations": "",
                         "clinvar-rcva:version": "2",
                         "clinvar-rcva:gene-name": "nucleolar complex associated 2 homolog (S. cerevisiae)",
                         "clinvar-rcva:accession": "RCV000064926",
                         "clinvar-rcva:gene-symbol": "NOC2L",
                         "type": "clinvar-rcva"}}]},
                {"b37_id": "1-891344-G-A",
                 "tags": {"ref-allele-b37": "G",
                          "pos-b37": "891344",
                          "chrom-b37": "1",
                          "var-allele-b37": "A"},
                 "relation_set": [{
                     "tags": {
                         "clinvar-rcva:record-status": "current",
                         "clinvar-rcva:num-submissions": "1",
                         "clinvar-rcva:disease-name": "Malignant melanoma",
                         "clinvar-rcva:significance": "not provided",
                         "clinvar-rcva:citations": "",
                         "clinvar-rcva:version": "2",
                         "clinvar-rcva:gene-name": "nucleolar complex associated 2 homolog (S. cerevisiae)",
                         "clinvar-rcva:accession": "RCV000064927",
                         "clinvar-rcva:gene-symbol": "NOC2L",
                         "type": "clinvar-rcva"}}]},
                {"b37_id": "1-906168-G-A",
                 "tags": {"ref-allele-b37": "G",
                          "pos-b37": "906168",
                          "chrom-b37": "1",
                          "var-allele-b37": "A"},
                 "relation_set": [{
                     "tags": {
                         "clinvar-rcva:record-status": "current",
                         "clinvar-rcva:num-submissions": "1",
                         "clinvar-rcva:disease-name": "Malignant melanoma",
                         "clinvar-rcva:significance": "not provided",
                         "clinvar-rcva:citations": "",
                         "clinvar-rcva:version": "2",
                         "clinvar-rcva:gene-name": "pleckstrin homology domain containing, family N member 1",
                         "clinvar-rcva:accession": "RCV000064940",
                         "clinvar-rcva:gene-symbol": "PLEKHN1",
                         "type": "clinvar-rcva"}}]}]
        })
