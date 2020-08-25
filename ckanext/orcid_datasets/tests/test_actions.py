#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-orcid-datasets
# Created by the Natural History Museum in London, UK


import json

import nose
from ckanext.orcid_datasets.model.crud import ContributorQ
from ckanext.orcid_datasets.tests import helpers
from ckantest.models import TestBase

from ckan.plugins import toolkit


class TestCreateActions(TestBase):
    plugins = [u'orcid_datasets']
    persist = {
        u'ckanext.orcid_datasets.debug': True
        }

    @classmethod
    def setup_class(cls):
        super(TestCreateActions, cls).setup_class()
        cls.action_context = {
            u'user': cls.data_factory().sysadmin[u'name']
            }

    def test_create_actions_registered(self):
        toolkit.get_action(u'contributor_create')

    def test_contributor_create(self):
        new_contributor = toolkit.get_action(u'contributor_create')(self.action_context, {
            u'surname': u'Contributor1',
            u'given_names': u'A'
            })
        nose.tools.assert_is_instance(new_contributor, dict)
        nose.tools.assert_equal(new_contributor[u'surname'], u'Contributor1')

    def test_contributor_create_does_not_use_id(self):
        new_contributor = toolkit.get_action(u'contributor_create')(self.action_context, {
            u'id': u'dont-use-an-id',
            u'surname': u'Contributor2',
            u'given_names': u'B'
            })
        nose.tools.assert_is_instance(new_contributor, dict)
        nose.tools.assert_equal(new_contributor[u'surname'], u'Contributor2')
        nose.tools.assert_not_equal(new_contributor[u'id'], u'dont-use-an-id')


class TestGetActions(TestBase):
    plugins = [u'orcid_datasets']
    persist = {
        u'ckanext.orcid_datasets.debug': True
        }

    @classmethod
    def setup_class(cls):
        super(TestGetActions, cls).setup_class()
        cls.action_context = {
            u'user': cls.data_factory().sysadmin[u'name']
            }
        cls.contributor1 = ContributorQ.create(**helpers.contributor1)
        cls.contributor2 = ContributorQ.create(**helpers.contributor2)

    def test_get_actions_registered(self):
        toolkit.get_action(u'contributor_show')
        toolkit.get_action(u'contributor_autocomplete')

    def test_contributor_show(self):
        contributor_show = toolkit.get_action(u'contributor_show')
        valid_contributor = contributor_show(self.action_context, {
            u'id': self.contributor1.id
            })
        nose.tools.assert_dict_equal(valid_contributor, self.contributor1.as_dict())
        with nose.tools.assert_raises(toolkit.ObjectNotFound):
            invalid_contributor = contributor_show(self.action_context, {
                u'id': u'not-a-real-id'
                })
        with nose.tools.assert_raises(toolkit.ObjectNotFound):
            empty_contributor = contributor_show(self.action_context, {})

    def test_contributor_autocomplete_database(self):
        contributor_autocomplete = toolkit.get_action(u'contributor_autocomplete')
        results = contributor_autocomplete(self.action_context, {
            u'surname': u'Contributor'
            })
        nose.tools.assert_equal(len(results[u'portal']), 2)
        nose.tools.assert_equal(len(results[u'orcid']), 0)

    def test_contributor_autocomplete_orcid(self):
        contributor_autocomplete = toolkit.get_action(u'contributor_autocomplete')
        results1 = contributor_autocomplete(self.action_context, {
            u'include_orcid': True,
            u'orcid': helpers.sandbox_portal_orcid
            })
        nose.tools.assert_equal(len(results1[u'portal']), 1)
        nose.tools.assert_equal(len(results1[u'orcid']), 1)
        results2 = contributor_autocomplete(self.action_context, {
            u'include_orcid': True,
            u'surname': u'c'
            })
        nose.tools.assert_equal(len(results2[u'portal']), 2)
        nose.tools.assert_greater_equal(len(results2[u'orcid']), 1)
        nose.tools.assert_less_equal(len(results2[u'orcid']), 10)


class TestUpdateActions(TestBase):
    plugins = [u'orcid_datasets']
    persist = {
        u'ckanext.orcid_datasets.debug': True
        }

    @classmethod
    def setup_class(cls):
        super(TestUpdateActions, cls).setup_class()
        cls.action_context = {
            u'user': cls.data_factory().sysadmin[u'name'],
            u'ignore_auth': True
            }

    def setUp(self):
        self.data_factory().refresh()
        self.contributor1 = ContributorQ.create(**helpers.contributor1)
        self.contributor2 = ContributorQ.create(**helpers.contributor2)
        self.pkg = self.data_factory().package(u'testpackage', contributors=[self.contributor1.id])

    def test_update_actions_registered(self):
        toolkit.get_action(u'package_update')
        toolkit.get_action(u'contributor_update')
        toolkit.get_action(u'contributor_orcid_update')

    def test_package_update_updates_existing(self):
        package_update = toolkit.get_action(u'package_update')
        name_before = ContributorQ.read(self.contributor1.id).given_names
        update_dict = {
            self.contributor1.id: {
                u'update': True,
                u'id': self.contributor1.id,
                u'given_names': u'X',
                u'order': 0
                }
            }
        self.pkg[u'contributors'] = json.dumps(update_dict)
        package_update(self.action_context, self.pkg)
        name_after = ContributorQ.read(self.contributor1.id).given_names
        nose.tools.assert_not_equal(name_before, name_after)

    def test_package_update_only_updates_when_told(self):
        package_update = toolkit.get_action(u'package_update')
        name_before = ContributorQ.read(self.contributor1.id).given_names
        update_dict = {
            self.contributor1.id: {
                u'update': False,
                u'id': self.contributor1.id,
                u'given_names': u'X',
                u'order': 0
                }
            }
        self.pkg[u'contributors'] = json.dumps(update_dict)
        package_update(self.action_context, self.pkg)
        name_after = ContributorQ.read(self.contributor1.id).given_names
        nose.tools.assert_equal(name_before, name_after)

    def test_package_update_creates_new(self):
        package_update = toolkit.get_action(u'package_update')
        update_dict = {
            self.contributor1.id: {
                u'id': self.contributor1.id,
                u'order': 0
                },
            'a-random-id': {
                u'new': True,
                u'order': 1,
                u'surname': u'D',
                u'given_names': u'C',
                u'orcid': u'this-is-not-a-valid-orcid'
                },
            'delete-this-one': {
                u'new': True,
                u'delete': True,
                u'order': 2,
                u'surname': u'F',
                u'given_names': u'E',
                u'orcid': u'another-invalid-orcid'
                }
            }
        self.pkg[u'contributors'] = json.dumps(update_dict)
        package_update(self.action_context, self.pkg)
        new1 = ContributorQ.read_orcid(u'this-is-not-a-valid-orcid')
        nose.tools.assert_is_not_none(new1)
        nose.tools.assert_equal(u'D', new1.surname)
        new2 = ContributorQ.read_orcid(u'another-invalid-orcid')
        nose.tools.assert_is_none(new2)

    def test_package_update_deduplicate_orcids(self):
        package_update = toolkit.get_action(u'package_update')
        update_dict = {
            self.contributor1.id: {
                u'id': self.contributor1.id,
                u'order': 0
                },
            'a-random-id': {
                u'new': True,
                u'order': 1,
                u'surname': u'D',
                u'given_names': u'C',
                u'orcid': self.contributor2.orcid
                }
            }
        self.pkg[u'contributors'] = json.dumps(update_dict)
        package_update(self.action_context, self.pkg)
        new_contribs = ContributorQ.search(ContributorQ.m.surname == u'D')
        nose.tools.assert_equal(len(new_contribs), 0)

    def test_package_update_adds_to_extras(self):
        # FIXME: unskip when package_show is fixed
        raise nose.SkipTest('package_show is broken, skipping for now')
        package_update = toolkit.get_action(u'package_update')
        package_show = toolkit.get_action(u'package_show')
        update_dict = {
            self.contributor1.id: {
                u'id': self.contributor1.id,
                u'order': 1
                },
            self.contributor2.id: {
                u'id': self.contributor2.id,
                u'order': 0
                }
            }
        self.pkg[u'contributors'] = json.dumps(update_dict)
        package_update(self.action_context, self.pkg)
        # this will fail if package_show does not use the updated schema
        nose.tools.assert_list_equal([self.contributor2.id, self.contributor1.id],
                                     package_show(self.action_context, {
                                         u'id': self.pkg[u'id']
                                         }).get(u'contributors', []))

    def test_package_update_removes(self):
        # FIXME: unskip when package_show is fixed
        raise nose.SkipTest('package_show is broken, skipping for now')
        package_update = toolkit.get_action(u'package_update')
        package_show = toolkit.get_action(u'package_show')
        update_dict = {
            self.contributor1.id: {
                u'delete': True,
                u'id': self.contributor1.id
                },
            self.contributor2.id: {
                u'id': self.contributor2.id,
                u'order': 0
                }
            }
        self.pkg[u'contributors'] = json.dumps(update_dict)
        package_update(self.action_context, self.pkg)
        # this will fail if package_show does not use the updated schema
        nose.tools.assert_list_equal([self.contributor2.id],
                                     package_show(self.action_context, {
                                         u'id': self.pkg[u'id']
                                         }).get(u'contributors', []))

    def test_contributor_update(self):
        contributor_update = toolkit.get_action(u'contributor_update')
        name_before = ContributorQ.read(self.contributor1.id).given_names
        update_dict = {
            u'id': self.contributor1.id,
            u'given_names': u'X'
            }
        updated1 = contributor_update(self.action_context, update_dict)
        name_after = ContributorQ.read(self.contributor1.id).given_names
        nose.tools.assert_not_equal(name_before, name_after)
        nose.tools.assert_equal(u'X', name_after)
        nose.tools.assert_is_instance(updated1, dict)
        updated2 = contributor_update(self.action_context, {u'given_names': u'Y'})
        nose.tools.assert_is_none(updated2)

    def test_contributor_orcid_update(self):
        helpers.skip_without_credentials()
        contributor_orcid_update = toolkit.get_action(u'contributor_orcid_update')
        name_before = ContributorQ.read(self.contributor1.id).given_names
        update_dict = {
            u'id': self.contributor1.id
            }
        updated1 = contributor_orcid_update(self.action_context, update_dict)
        name_after = ContributorQ.read(self.contributor1.id).given_names
        nose.tools.assert_not_equal(name_before, name_after)
        nose.tools.assert_equal(helpers.sandbox_portal_given, name_after)
        updated2 = contributor_orcid_update(self.action_context, {
            u'orcid': helpers.sandbox_portal_orcid
            })
        nose.tools.assert_is_none(updated2)
