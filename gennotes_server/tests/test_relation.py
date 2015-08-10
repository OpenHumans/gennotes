import json
import logging

from test_helpers import APITestCase

ERR_NOAUTH = {'detail': 'Authentication credentials were not provided.'}
ERR_TYPE_CHNG = {'detail': "Updates (PUT or PATCH) must not attempt to change "
                           "the values for special tags. Your request "
                           "attempts to change the value for tag 'type' "
                           "from 'clinvar-rcva' to 'test-type'"}
ERR_VAR_INC = {'detail': "Edits should include the 'tags' field, and only "
                         "this field. Your request is attempting to edit the"
                         " following fields: [u'variant', u'tags']"}

logger = logging.getLogger(__name__)


class RelationTests(APITestCase):
    """
    Test the Relation API.
    """
    base_path = '/relation'
    fixtures = ['gennotes_server/fixtures/test-data.json']

    def test_get_relation(self):
        """
        Test getting data for a single Relation.
        """
        with open('gennotes_server/tests/expected_data/relation.json') as f:
            expected_data = json.load(f)

        self.verify_request(path='/1/', method='get',
                            expected_data=expected_data, expected_status=200)

    def test_get_relation_list(self):
        """
        Test getting full list of Relation data.
        """
        with open('gennotes_server/tests/expected_data/'
                  'relation_list.json') as f:
            expected_data = json.load(f)

        self.verify_request(path='/', method='get',
                            expected_data=expected_data, expected_status=200)

    def test_post_relation(self):
        """
        Test creating a new Relation.
        """
        good_data = {"tags": {"type": "test-relation",
                              "other-test-tag": "some-value"},
                     "variant": "http://testserver/api/variant/1/"}
        bad_data_1 = {"tags": {"type": "test-relation",
                               "other-test-tag": "some-value"}}
        err_1 = {'detail': "Create (POST) should include the 'tags' and "
                           "'variant' fields. Your request contains the "
                           "following fields: [u'tags']"}
        bad_data_2 = {"tags": {"test-tag": "some-value"},
                      "variant": "http://testserver/api/variant/1/"}
        err_2 = {"detail": "Create (POST) tag data must include all required "
                           "tags: ['type']"}

        with open('gennotes_server/tests/expected_data/'
                  'relation_create.json') as f:
            expected_data = json.load(f)

        # Test unauthenticated.
        self.verify_request(path='/', method='post',
                            expected_data=ERR_NOAUTH, expected_status=401,
                            data=good_data, format='json')

        self.client.login(username='testuser', password='password')

        # Test missing variant data.
        self.verify_request(path='/', method='post',
                            expected_data=err_1, expected_status=400,
                            data=bad_data_1, format='json')

        # Test missing "type" tag.
        self.verify_request(path='/', method='post',
                            expected_data=err_2, expected_status=400,
                            data=bad_data_2, format='json')

        # Test good request.
        self.verify_request(path='/', method='post',
                            expected_data=expected_data, expected_status=201,
                            data=good_data, format='json')

    def test_delete_relation(self):
        """
        Test deleting an existing Relation.
        """
        # Test unauthenticated.
        self.verify_request(path='/1/', method='delete',
                            expected_data=ERR_NOAUTH, expected_status=401)

        self.client.login(username='testuser', password='password')

        # Test good request.
        self.verify_request(path='/1/', method='delete',
                            expected_status=204)

    def test_put_relation(self):
        """
        Test editing an existing Relation via PUT.
        """
        good_data = {"tags": {"type": "clinvar-rcva",
                              "comment": "All other tags deleted!"}}
        bad_data_1 = {"tags": {"type": "clinvar-rcva",
                               "comment": "All other tags deleted!"},
                      "variant": "http://testserver/api/variant/10/"}
        err_1 = ERR_VAR_INC
        bad_data_2 = {"tags": {"type": "test-type",
                               "comment": "All other tags deleted!"}}
        err_2 = ERR_TYPE_CHNG
        bad_data_3 = {"tags": {"comment": "All other tags deleted!"}}
        err_3 = {'detail': "PUT requests must retain all special tags. Your "
                           "request is missing the tag: type"}

        with open('gennotes_server/tests/expected_data/'
                  'relation_put.json') as f:
            expected_data = json.load(f)

        # Test unauthenticated
        self.verify_request(path='/1/', method='put',
                            expected_data=ERR_NOAUTH, expected_status=401,
                            data=good_data, format='json')

        self.client.login(username='testuser', password='password')

        # Test bad request (attempting to edit variant field).
        self.verify_request(path='/1/', method='put',
                            expected_data=err_1, expected_status=400,
                            data=bad_data_1, format='json')

        # Test bad request (attempting to edit special 'type' tag).
        self.verify_request(path='/1/', method='put',
                            expected_data=err_2, expected_status=400,
                            data=bad_data_2, format='json')

        # Test bad request (failing to retain special 'type' tag).
        self.verify_request(path='/1/', method='put',
                            expected_data=err_3, expected_status=400,
                            data=bad_data_3, format='json')

        # Test good request.
        self.verify_request(path='/1/', method='put',
                            expected_data=expected_data, expected_status=200,
                            data=good_data, format='json')

        self.client.logout()

    def test_patch_relation(self):
        """
        Test editing an existing Relation via PATCH.
        """
        good_data_1 = {"tags": {"comment": "All other tags preserved."}}
        good_data_2 = {"tags": {"type": "clinvar-rcva",
                                "comment": "All other tags preserved."}}
        bad_data_1 = {"tags": {"type": "clinvar-rcva",
                               "comment": "All other tags preserved."},
                      "variant": "http://testserver/api/variant/10/"}
        err_1 = ERR_VAR_INC
        bad_data_2 = {"tags": {"type": "test-type",
                               "comment": "All other tags preserved."}}
        err_2 = ERR_TYPE_CHNG

        with open('gennotes_server/tests/expected_data/'
                  'relation_patch.json') as f:
            expected_data = json.load(f)

        # Test unauthenticated
        self.verify_request(path='/1/', method='patch',
                            expected_data=ERR_NOAUTH, expected_status=401,
                            data=good_data_1, format='json')

        self.client.login(username='testuser', password='password')

        # Test bad request (attempting to edit variant field).
        self.verify_request(path='/1/', method='patch',
                            expected_data=err_1, expected_status=400,
                            data=bad_data_1, format='json')

        # Test bad request (attempting to edit special 'type' tag).
        self.verify_request(path='/1/', method='patch',
                            expected_data=err_2, expected_status=400,
                            data=bad_data_2, format='json')

        # Test good request ('type' tag not included).
        self.verify_request(path='/1/', method='patch',
                            expected_data=expected_data, expected_status=200,
                            data=good_data_1, format='json')

        # Test good request ('type' tag included and unchanged).
        self.verify_request(path='/1/', method='patch',
                            expected_data=expected_data, expected_status=200,
                            data=good_data_2, format='json')

        self.client.logout()
