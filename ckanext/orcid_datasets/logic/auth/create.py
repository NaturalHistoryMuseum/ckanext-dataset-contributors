#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-orcid-datasets
# Created by the Natural History Museum in London, UK


def contributor_create(context, data_dict):
    '''
    Allow for logged-in users.
    '''
    return {
        u'success': True
        }
