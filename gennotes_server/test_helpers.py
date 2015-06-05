import logging

from rest_framework.test import APITestCase as BaseAPITestCase

logger = logging.getLogger(__name__)


class APITestCase(BaseAPITestCase):
    """
    A helper for writing study tests.
    """

    base_url = ''
    fixtures = ['gennotes_server/fixtures/test-data.json']

    def verify_request(self, url, method='get', data=None, status=200):
        args = ['/api' + self.base_url + url]

        if method == 'post':
            args.append(data)

        logger.debug('%s %s', method.upper(), args[0])

        response = getattr(self.client, method)(*args)

        self.assertEqual(response.status_code, status)

        return response
