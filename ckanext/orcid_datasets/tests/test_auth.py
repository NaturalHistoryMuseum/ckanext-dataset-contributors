#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-orcid-datasets
# Created by the Natural History Museum in London, UK


import nose
from ckantest.models import TestBase

from ckan.plugins import toolkit


class TestAuthBase(TestBase):
    plugins = [u'orcid_datasets']
    persist = {
        u'ckanext.orcid_datasets.debug': True
        }

    @classmethod
    def setup_class(cls):
        super(TestAuthBase, cls).setup_class()
        cls.data_factory().user(name=u'normalnorman', password=u'password')
        cls.sysadmin_context = {
            u'user': cls.data_factory().sysadmin[u'name']
            }
        cls.user_context = {
            u'user': u'normalnorman'
            }
        cls.anon_context = {}


class TestCreateAuth(TestAuthBase):
    def test_contributor_create_auth(self):
        with nose.tools.assert_raises(toolkit.NotAuthorized):
            toolkit.check_access(u'contributor_create', self.anon_context, {})
        toolkit.check_access(u'contributor_create', self.user_context, {})
        toolkit.check_access(u'contributor_create', self.sysadmin_context, {})


class TestGetAuth(TestAuthBase):
    def test_contributor_show_auth(self):
        toolkit.check_access(u'contributor_show', self.anon_context, {})
        toolkit.check_access(u'contributor_show', self.user_context, {})
        toolkit.check_access(u'contributor_show', self.sysadmin_context, {})

    def test_contributor_autocomplete_auth(self):
        toolkit.check_access(u'contributor_autocomplete', self.anon_context, {})
        toolkit.check_access(u'contributor_autocomplete', self.user_context, {})
        toolkit.check_access(u'contributor_autocomplete', self.sysadmin_context, {})


class TestUpdateAuth(TestAuthBase):
    def test_contributor_update(self):
        with nose.tools.assert_raises(toolkit.NotAuthorized):
            toolkit.check_access(u'contributor_update', self.anon_context, {})
        with nose.tools.assert_raises(toolkit.NotAuthorized):
            toolkit.check_access(u'contributor_update', self.user_context, {})
        toolkit.check_access(u'contributor_update', self.sysadmin_context, {})

    def test_contributor_update_orcid(self):
        with nose.tools.assert_raises(toolkit.NotAuthorized):
            toolkit.check_access(u'contributor_update_orcid', self.anon_context, {})
        toolkit.check_access(u'contributor_update_orcid', self.user_context, {})
        toolkit.check_access(u'contributor_update_orcid', self.sysadmin_context, {})