#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-orcid-datasets
# Created by the Natural History Museum in London, UK

from ckanext.orcid_datasets.lib import template_helpers, validators
from ckanext.orcid_datasets.model import contributor as contributor_model

from ckan import model
from ckan.plugins import SingletonPlugin, implements, interfaces, toolkit


class OrcidDatasetsPlugin(SingletonPlugin, toolkit.DefaultDatasetForm):
    '''A CKAN extension that connects ORCID identifiers to dataset authors.'''

    implements(interfaces.IActions, inherit=True)
    implements(interfaces.IAuthFunctions, inherit=True)
    implements(interfaces.IConfigurable)
    implements(interfaces.IConfigurer)
    implements(interfaces.IPluginObserver, inherit=True)
    implements(interfaces.ITemplateHelpers)
    implements(interfaces.IValidators)

    # IActions
    def get_actions(self):
        from ckanext.orcid_datasets.logic.action import create, get, update
        actions = {
            u'contributor_create': create.contributor_create,
            u'contributor_show': get.contributor_show,
            u'contributor_autocomplete': get.contributor_autocomplete,
            u'contributor_update': update.contributor_update,
            u'contributor_orcid_update': update.contributor_orcid_update,
            u'package_update': update.package_update
            }
        return actions

    # IAuthFunctions
    def get_auth_functions(self):
        from ckanext.orcid_datasets.logic.auth import create, get, update
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
        if model.package_table.exists():
            contributor_model.contributor_table.create(checkfirst=True)

    # IConfigurer
    def update_config(self, config):
        '''
        :param config:
        '''
        toolkit.add_template_directory(config, u'theme/templates')
        toolkit.add_resource(u'theme/fanstatic', u'ckanext-orcid-datasets')

    # IPluginObserver
    def before_load(self, plugin):
        '''
        Modifies the show/update package schemas to include a 'contributors' field.
        '''
        if interfaces.IDatasetForm.implemented_by(type(plugin)):
            def _create_schema_wrapper(original_schema_method):
                return lambda: self.create_package_schema(original_schema_method())

            def _show_schema_wrapper(original_schema_method):
                return lambda: self.show_package_schema(original_schema_method())

            def _update_schema_wrapper(original_schema_method):
                return lambda: self.update_package_schema(original_schema_method())

            plugin.create_package_schema = _create_schema_wrapper(plugin.create_package_schema)
            plugin.show_package_schema = _show_schema_wrapper(plugin.show_package_schema)
            plugin.update_package_schema = _update_schema_wrapper(plugin.update_package_schema)
        return plugin

    # IValidators
    def get_validators(self):
        return {
            'is_serialised_list': validators.is_serialised_list
            }

    # ITemplateHelpers
    def get_helpers(self):
        return {
            u'as_string': template_helpers.as_string,
            u'contributor_details': template_helpers.contributor_details,
            u'can_edit': template_helpers.can_edit
            }

    # DefaultDatasetForm
    def create_package_schema(self, schema=None):
        ignore_missing = toolkit.get_validator(u'ignore_missing')
        convert_to_extras = toolkit.get_converter(u'convert_to_extras')
        is_serialised_list = toolkit.get_validator(u'is_serialised_list')
        if schema is None:
            schema = super(OrcidDatasetsPlugin, self).create_package_schema()
        schema[u'contributors'] = [ignore_missing, is_serialised_list, convert_to_extras]
        return schema

    def show_package_schema(self, schema=None):
        ignore_missing = toolkit.get_validator(u'ignore_missing')
        convert_from_extras = toolkit.get_converter(u'convert_from_extras')
        is_serialised_list = toolkit.get_validator(u'is_serialised_list')
        if schema is None:
            schema = super(OrcidDatasetsPlugin, self).show_package_schema()
        schema[u'contributors'] = [convert_from_extras, ignore_missing, is_serialised_list]
        return schema

    def update_package_schema(self, schema=None):
        ignore_missing = toolkit.get_validator(u'ignore_missing')
        convert_to_extras = toolkit.get_converter(u'convert_to_extras')
        is_serialised_list = toolkit.get_validator(u'is_serialised_list')
        if schema is None:
            schema = super(OrcidDatasetsPlugin, self).update_package_schema()
        schema[u'contributors'] = [ignore_missing, is_serialised_list, convert_to_extras]
        return schema
