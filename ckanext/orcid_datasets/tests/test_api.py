#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-orcid-datasets
# Created by the Natural History Museum in London, UK

import nose
from ckanext.orcid_datasets.lib.orcid_api import OrcidApi
from ckanext.orcid_datasets.tests import helpers
from ckantest.models import TestBase
from ckantest.helpers.mocking import Response
import mock


class TestOrcidApi(TestBase):
    plugins = [u'orcid_datasets']
    persist = {
        u'ckanext.orcid_datasets.debug': True
        }

    def _set_config_value(self, key, has_var, test_value=None):
        if has_var:
            self.config.update({
                u'ckanext.orcid_datasets.' + key: test_value
                })
        else:
            self.config.remove(u'ckanext.orcid_datasets.' + key)

    def test_gets_credentials_when_present(self):
        test_key = u'test-key-value'
        test_secret = u'test-secret-value'
        self._set_config_value(u'key', True, test_key)
        self._set_config_value(u'secret', True, test_secret)
        api = OrcidApi()
        nose.tools.assert_equal(test_key, api.key)
        nose.tools.assert_equal(test_secret, api.secret)
        self.config.reset()

    def test_gets_no_credentials_when_absent(self):
        self._set_config_value(u'key', False)
        self._set_config_value(u'secret', False)
        api = OrcidApi()
        nose.tools.assert_is_none(api.key)
        nose.tools.assert_is_none(api.secret)
        self.config.reset()

    def test_gets_debug_value_when_present(self):
        test_value = False
        self._set_config_value(u'debug', True, test_value)
        api = OrcidApi()
        nose.tools.assert_equal(test_value, api._debug)
        self.config.reset()

    def test_gets_debug_default_when_absent(self):
        default_value = True
        self._set_config_value(u'debug', False)
        api = OrcidApi()
        nose.tools.assert_equal(default_value, api._debug)
        self.config.reset()

    def test_cannot_authenticate_without_credentials(self):
        self._set_config_value(u'key', False)
        self._set_config_value(u'secret', False)
        with nose.tools.assert_raises(Exception):
            api_conn = OrcidApi().conn
        self.config.reset()

    def test_can_authenticate(self):
        # NB: this requires an actual key/secret to test properly.
        api = helpers.skip_without_credentials()
        api_conn = api.conn

    def test_read_token(self):
        api = helpers.skip_without_credentials()
        nose.tools.assert_is_not_none(api.read_token)

    @mock.patch('ckanext.orcid_datasets.lib.orcid_api.requests.post', return_value=Response(ok=False))
    def test_read_token_is_none_if_response_bad(self, mock_request):
        api = helpers.skip_without_credentials()
        nose.tools.assert_is_none(api.read_token)

    def test_read_token_fails_without_credentials(self):
        self._set_config_value(u'key', False)
        with nose.tools.assert_raises(Exception):
            api_conn = OrcidApi().read_token
        self.config.reset()

    def test_search_surname(self):
        api = helpers.skip_without_credentials()
        results = api.search(surname_q=u'Portal')
        records = results[u'result']
        nose.tools.assert_less_equal(len(records), 10)
        nose.tools.assert_less_equal(len(records), results[u'num-found'])
        if len(records) <= 10:
            # only bother checking this if the number of results is small, which it should be
            # (but this is beyond our control)
            orcids = [r[u'orcid-identifier'][u'path'] for r in records]
            nose.tools.assert_in(helpers.sandbox_portal_orcid, orcids)

    def test_search_orcid(self):
        api = helpers.skip_without_credentials()
        results = api.search(orcid_q=helpers.sandbox_portal_orcid)
        records = results[u'result']
        nose.tools.assert_equal(len(records), 1)
        nose.tools.assert_less_equal(len(records), results[u'num-found'])
        orcids = [r[u'orcid-identifier'][u'path'] for r in records]
        nose.tools.assert_in(helpers.sandbox_portal_orcid, orcids)

    def test_search_surname_and_orcid(self):
        api = helpers.skip_without_credentials()
        results = api.search(surname_q=u'Portal', orcid_q=helpers.sandbox_portal_orcid)
        records = results[u'result']
        nose.tools.assert_equal(len(records), 1)
        nose.tools.assert_less_equal(len(records), results[u'num-found'])
        orcids = [r[u'orcid-identifier'][u'path'] for r in records]
        nose.tools.assert_in(helpers.sandbox_portal_orcid, orcids)

    def test_read_orcid_record(self):
        api = helpers.skip_without_credentials()
        record = api.read(helpers.sandbox_portal_orcid)
        nose.tools.assert_equal(record[u'orcid-identifier'][u'path'],
                                helpers.sandbox_portal_orcid)
        nose.tools.assert_equal(record[u'person'][u'name'][u'given-names'][u'value'],
                                u'Data')

    def test_orcid_record_as_contributor(self):
        api = helpers.skip_without_credentials()
        record = api.read(helpers.sandbox_portal_orcid)
        contrib_record = api.as_contributor_record(record)
        nose.tools.assert_equal(contrib_record[u'orcid'], helpers.sandbox_portal_orcid)
        nose.tools.assert_equal(contrib_record[u'orcid'], record[u'orcid-identifier'][u'path'])
