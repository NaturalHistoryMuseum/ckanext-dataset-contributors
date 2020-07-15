#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-orcid-datasets
# Created by the Natural History Museum in London, UK


def contributor_update(context, data_dict):
    '''
    Only allow for sysadmins (who skip this method, so just return False).
    '''
    return {
        u'success': False
        }


def contributor_orcid_update(context, data_dict):
    '''
    Allow for logged-in users.
    '''
    return {
        u'success': True
        }