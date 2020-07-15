#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-orcid-datasets
# Created by the Natural History Museum in London, UK


import mock
import nose
from ckanext.orcid_datasets.lib import template_helpers
from ckanext.orcid_datasets.model.crud import ContributorQ
from ckantest.models import TestBase

from ckan.plugins import toolkit


class TestTemplateHelpers(TestBase):
    plugins = [u'orcid_datasets']
    persist = {
        u'ckanext.orcid_datasets.debug': True
        }

    def test_as_string(self):
        test_string = 'test string'
        nose.tools.assert_equal(test_string, template_helpers.as_string(test_string))
        test_dict = {
            'k': 'v'
            }
        nose.tools.assert_equal('{"k": "v"}', template_helpers.as_string(test_dict))
        test_list = [1, 2]
        nose.tools.assert_equal('[1, 2]', template_helpers.as_string(test_list))
        test_unserialisable_dict = {
            'k': lambda x: x + 1
            }
        nose.tools.assert_equal('', template_helpers.as_string(test_unserialisable_dict))
        test_int = 1
        nose.tools.assert_equal('1', template_helpers.as_string(test_int))

    def test_contributor_details(self):
        contributor = ContributorQ.create(surname='A', given_names='B', affiliations=['C', 'D'])
        from_list = template_helpers.contributor_details([contributor.id])
        from_json = template_helpers.contributor_details('["' + contributor.id + '"]')
        with nose.tools.assert_raises(TypeError):
            template_helpers.contributor_details(contributor.id)
        nose.tools.assert_in(contributor.id, from_list)
        nose.tools.assert_equal(from_list[contributor.id][u'surname'], 'A')

    def test_can_edit(self):
        toolkit_access = toolkit.check_access

        def _as_sysadmin(auth_name, context, data_dict):
            context[u'user'] = self.data_factory().sysadmin[u'name']
            return toolkit_access(auth_name, context, data_dict)

        def _as_user(auth_name, context, data_dict):
            self.data_factory().user(name=u'normalnorman', password=u'password')
            context[u'user'] = u'normalnorman'
            return toolkit_access(auth_name, context, data_dict)

        def _as_anon(auth_name, context, data_dict):
            try:
                del context[u'user']
            except KeyError:
                pass
            return toolkit_access(auth_name, context, data_dict)

        with mock.patch('ckanext.orcid_datasets.lib.template_helpers.toolkit.check_access',
                        _as_sysadmin):
            nose.tools.assert_true(template_helpers.can_edit())

        with mock.patch('ckanext.orcid_datasets.lib.template_helpers.toolkit.check_access',
                        _as_user):
            nose.tools.assert_false(template_helpers.can_edit())

        with mock.patch('ckanext.orcid_datasets.lib.template_helpers.toolkit.check_access',
                        _as_anon):
            nose.tools.assert_false(template_helpers.can_edit())
