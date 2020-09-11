#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-dataset-contributors
# Created by the Natural History Museum in London, UK

import json

from ckanext.dataset_contributors.lib import template_helpers, validators
from ckanext.dataset_contributors.model import contributor as contributor_model
from paste.deploy.converters import asbool
try:
    from ckanext.doi.interfaces import IDoi
    doi_available = True
except ImportError:
    doi_available = False

from ckan.plugins import PluginImplementations, SingletonPlugin, implements, interfaces, toolkit


class DatasetContributorsPlugin(SingletonPlugin, toolkit.DefaultDatasetForm):
    '''A CKAN extension that connects ORCID identifiers to dataset authors.'''

    implements(interfaces.IActions, inherit=True)
    implements(interfaces.IAuthFunctions, inherit=True)
    implements(interfaces.IConfigurable)
    implements(interfaces.IConfigurer)
    implements(interfaces.IDatasetForm)
    implements(interfaces.IFacets, inherit=True)
    implements(interfaces.IPackageController, inherit=True)
    implements(interfaces.ITemplateHelpers)
    implements(interfaces.IValidators)
    if doi_available:
        implements(IDoi)

    # IActions
    def get_actions(self):
        from ckanext.dataset_contributors.logic.action import create, get, update
        actions = {
            u'contributor_create': create.contributor_create,
            u'package_create': create.package_create,
            u'contributor_show': get.contributor_show,
            u'contributor_autocomplete': get.contributor_autocomplete,
            u'contributor_update': update.contributor_update,
            u'contributor_orcid_update': update.contributor_orcid_update,
            u'package_update': update.package_update
            }
        return actions

    # IAuthFunctions
    def get_auth_functions(self):
        from ckanext.dataset_contributors.logic.auth import create, get, update
        auth = {
            u'contributor_create': create.contributor_create,
            u'contributor_show': get.contributor_show,
            u'contributor_autocomplete': get.contributor_autocomplete,
            u'contributor_update': update.contributor_update,
            u'contributor_orcid_update': update.contributor_orcid_update
            }
        return auth

    # IConfigurable
    def configure(self, config):
        '''
        Called at the end of CKAN setup.
        '''
        contributor_model.check_for_table()

    # IConfigurer
    def update_config(self, config):
        '''
        :param config:
        '''
        toolkit.add_template_directory(config, u'theme/templates')
        toolkit.add_resource(u'theme/fanstatic', u'ckanext-dataset-contributors')

    # IDatasetForm
    def is_fallback(self):
        idataset_plugins = [p for p in PluginImplementations(interfaces.IDatasetForm) if
                            p.name != 'dataset_contributors']
        no_idataset = len(idataset_plugins) == 0
        if not no_idataset:
            for p in idataset_plugins:
                def _create_schema_wrapper(original_schema_method):
                    return lambda: self.create_package_schema(original_schema_method())

                def _show_schema_wrapper(original_schema_method):
                    return lambda: self.show_package_schema(original_schema_method())

                def _update_schema_wrapper(original_schema_method):
                    return lambda: self.update_package_schema(original_schema_method())

                p.create_package_schema = _create_schema_wrapper(p.create_package_schema)
                p.show_package_schema = _show_schema_wrapper(p.show_package_schema)
                p.update_package_schema = _update_schema_wrapper(p.update_package_schema)
        return no_idataset

    def package_types(self):
        return []

    # IDoi
    def build_metadata(self, pkg_dict, metadata_dict):
        if not doi_available:
            return metadata_dict
        contributors = pkg_dict.get(u'contributors', None)
        if contributors:
            found_contributors = []
            if isinstance(contributors, (str, unicode)):
                try:
                    contributors = json.loads(contributors)
                except ValueError:
                    pass
            if isinstance(contributors, list):
                get_contributor = toolkit.get_action(u'contributor_show')
                for contributor_id in contributors:
                    contributor = get_contributor({}, {
                        u'id': contributor_id
                        })
                    _surname = contributor.get(u'surname', u'').encode(u'unicode-escape')
                    _given = contributor.get(u'given_names', u'').encode(u'unicode-escape')
                    _affiliations = contributor.get(u'affiliations', [])
                    _orcid = contributor.get(u'orcid', None)
                    contrib_metadata = {
                        u'contributorName': u'{0}, {1}'.format(_surname, _given),
                        u'affiliation': _affiliations,
                        }
                    if _orcid is not None and _orcid != '':
                        contrib_metadata[u'nameIdentifier'] = _orcid
                    found_contributors.append(contrib_metadata)
                metadata_dict[u'contributors'] = found_contributors
        return metadata_dict

    def metadata_to_xml(self, xml_dict, metadata):
        if not doi_available:
            return xml_dict
        if u'contributors' in metadata:
            contributor_xml = []

            for contributor in metadata[u'contributors']:
                contributor[u'@contributorType'] = u'Researcher'
                if u'nameIdentifier' in contributor:
                    contributor[u'nameIdentifier'] = {
                        u'#text': contributor[u'nameIdentifier'],
                        '@schemeURI': 'http://orcid.org',
                        '@nameIdentifierScheme': 'ORCID'
                        }
                contributor_xml.append(contributor)
            xml_dict[u'resource'][u'contributors'] = {
                u'contributor': contributor_xml,
                }
        return xml_dict

    # IFacets
    def dataset_facets(self, facets_dict, package_type):
        enable_faceting = toolkit.config.get(u'ckanext.dataset_contributors.enable_faceting',
                                             'false').lower() == 'true'
        if enable_faceting:
            facets_dict[u'contributors'] = toolkit._(u'Contributors')
        return facets_dict

    # IPackageController
    def before_index(self, pkg_dict):
        enable_faceting = asbool(toolkit.config.get(u'ckanext.dataset_contributors.enable_faceting',
                                                    False))
        if enable_faceting:
            from_contributor_ids = toolkit.get_validator(u'from_contributor_ids')
            contributors = pkg_dict.get(u'contributors', [])
            try:
                contrib_dict = from_contributor_ids(contributors)
                pkg_dict[u'contributors'] = [u'{0}, {1}'.format(c[u'surname'], c['given_names'])
                                             for c in contrib_dict.values()]
            except toolkit.Invalid:
                pass
        return pkg_dict

    # IValidators
    def get_validators(self):
        return {
            u'is_serialised_list': validators.is_serialised_list,
            u'from_contributor_ids': validators.from_contributor_ids
            }

    # ITemplateHelpers
    def get_helpers(self):
        return {
            u'as_string': template_helpers.as_string,
            u'convert_to_contributor_details': template_helpers.convert_to_contributor_details,
            u'can_edit': template_helpers.can_edit
            }

    # DefaultDatasetForm
    def create_package_schema(self, schema=None):
        ignore_missing = toolkit.get_validator(u'ignore_missing')
        convert_to_extras = toolkit.get_converter(u'convert_to_extras')
        is_serialised_list = toolkit.get_validator(u'is_serialised_list')
        if schema is None:
            schema = super(DatasetContributorsPlugin, self).create_package_schema()
        schema[u'contributors'] = [ignore_missing, is_serialised_list, convert_to_extras]
        return schema

    def show_package_schema(self, schema=None):
        ignore_missing = toolkit.get_validator(u'ignore_missing')
        convert_from_extras = toolkit.get_converter(u'convert_from_extras')
        is_serialised_list = toolkit.get_validator(u'is_serialised_list')
        from_contributor_ids = toolkit.get_validator(u'from_contributor_ids')
        if schema is None:
            schema = super(DatasetContributorsPlugin, self).show_package_schema()
        schema[u'contributors'] = [convert_from_extras, ignore_missing, is_serialised_list,
                                   from_contributor_ids]
        return schema

    def update_package_schema(self, schema=None):
        ignore_missing = toolkit.get_validator(u'ignore_missing')
        convert_to_extras = toolkit.get_converter(u'convert_to_extras')
        is_serialised_list = toolkit.get_validator(u'is_serialised_list')
        if schema is None:
            schema = super(DatasetContributorsPlugin, self).update_package_schema()
        schema[u'contributors'] = [ignore_missing, is_serialised_list, convert_to_extras]
        return schema
