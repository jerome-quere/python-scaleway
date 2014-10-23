# -*- coding: utf-8 -*-

import json
import unittest
import urlparse
import uuid

from ocs_sdk.apis import MetadataAPI

from . import FakeAPITestCase


class TestMetadataAPI(FakeAPITestCase, unittest.TestCase):

    def setUp(self):
        super(TestMetadataAPI, self).setUp()
        self.api = MetadataAPI()

    def make_fake_metadata_api(self):
        """ Fakes the Metadata API.
        """
        # Response returned by fake_route_conf
        json_response = {
            'id': str(uuid.uuid4()),
            'name': 'super name',
        }

        def fake_route_conf(_, uri, headers):
            """ Fakes the /conf route.

            Returns metadata of a running server. Our tests don't need to have
            all the metadata of a server, so only a few values are returned.

            If ?format=json is set, return a JSON dict with a application/json
            content
            type.

            If no format is given, return a text/plain response with a "shell"
            format.
            """
            querystring = urlparse.parse_qs(urlparse.urlparse(uri).query)

            if 'json' in querystring.get('format', []):
                return 200, headers, json.dumps(json_response)

            headers['content-type'] = 'text/plain'
            return 200, headers, '\n'.join(
                '%s="%s"' % (key, value)
                for key, value in json_response.items()
            )

        self.fake_endpoint(self.api, 'conf/', body=fake_route_conf)
        return json_response

    def test_get(self):
        expected_response = self.make_fake_metadata_api()
        self.assertEqual(self.api.get(), expected_response)

        shell_response = self.api.get(as_shell=True)
        self.assertIn('id="%(id)s"' % expected_response, shell_response)
        self.assertIn('name="%(name)s"' % expected_response, shell_response)
