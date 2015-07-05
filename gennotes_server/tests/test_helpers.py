import json
import logging

from rest_framework.test import APITestCase as BaseAPITestCase

logger = logging.getLogger(__name__)


class APITestCase(BaseAPITestCase):
    """
    A helper for writing tests.
    """
    base_path = ''
    fixtures = ['gennotes_server/fixtures/test-data.json']

    def verify_request(self, path, method='get',
                       expected_status=200, expected_data=None,
                       **kwargs):
        args = ['/api' + self.base_path + path]

        logger.debug('%s %s', method.upper(), args[0])

        response = getattr(self.client, method)(*args, **kwargs)

        self.assertEqual(response.status_code, expected_status)

        if expected_data:
            if hasattr(response.data, 'keys'):
                compare_response_dict(response.data, expected_data)
            elif hasattr(response.data, '__iter__'):
                compare_response_list(response.data, expected_data)
            # Doing this too in case the above didn't catch a difference.
            self.assertEqual(response.data, expected_data)

        return response


def compare_response_list(response, expected, path_pre=''):
    """
    Compare lists, helps determine test failure in responses.
    """
    if not hasattr(expected, '__iter__'):
        raise AssertionError(
            'List in response not expected at path: {}'.format(path_pre))
    for i in range(len(response)):
        my_path = path_pre + ' [{}] ->'.format(str(i))
        if hasattr(response[i], 'keys'):
            compare_response_dict(response[i], expected[i], path_pre=my_path)
        elif hasattr(response[i], '__iter__'):
            compare_response_list(response[i], expected[i], path_pre=my_path)
        elif response[i] != expected[i]:
            raise AssertionError(
                'Values in list not equal at path:{0}\n'
                'response: {1}\nexpected: {2}'.format(
                    my_path, response[i], expected[i]))
    if len(expected) > len(response):
        raise AssertionError(
            'Expected list longer than response at:{0}\n'
            'response length: {1}\nexpected length: {2}.'.format(
                path_pre, str(len(expected)), str(len(response))))


def compare_response_dict(response, expected, path_pre=''):
    """
    Compare dicts, helps determine test failure in responses.
    """
    if not hasattr(expected, 'keys'):
        raise AssertionError(
            'Dict in response not expected at path: {}'.format(path_pre))
    for k in response.keys():
        my_path = path_pre + ' ["{}"] ->'.format(k)
        if k not in expected:
            raise AssertionError(
                'Unexpected key at path:{}\n'
                '"{}" in response is not in expected data.'.format(
                    my_path, k))
        elif hasattr(response[k], 'keys'):
            compare_response_dict(response[k], expected[k], my_path)
        elif hasattr(response[k], '__iter__'):
            compare_response_list(response[k], expected[k], my_path)
        elif response[k] != expected[k]:
            raise AssertionError(
                'Values not equal at path:{}\n'
                'response: {}\nexpected: {}'.format(
                    my_path, response[k], expected[k]))
    for k in expected.keys():
        my_path = path_pre + ' ["{}"] ->'.format(k)
        if k not in response:
            raise AssertionError(
                'Missing key at path:{}\n'
                '"{}" in expected data, but not in response.'.format(
                    my_path, k))
