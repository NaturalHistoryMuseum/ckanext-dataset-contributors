#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-orcid-datasets
# Created by the Natural History Museum in London, UK

from ckan.authz import is_sysadmin


def contributor_update(context, data_dict):
    '''
    Only allow for sysadmins (who usually skip this method, except in tests).
    '''
    return {
        u'success': is_sysadmin(context.get(u'user'))
        }


def contributor_orcid_update(context, data_dict):
    '''
    Allow for logged-in users.
    '''
    return {
        u'success': True
        }