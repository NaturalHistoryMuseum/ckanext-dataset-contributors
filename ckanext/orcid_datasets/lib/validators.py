#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-orcid-datasets
# Created by the Natural History Museum in London, UK


import json

from ckan.plugins import toolkit


def is_serialised_list(value):
    ''' Make sure value can be deserialised into a list.'''
    if value is None or value == u'':
        return
    try:
        if not isinstance(value, str):
            raise toolkit.Invalid(toolkit._(u'The value should be a serialised list.'))
        if not isinstance(json.loads(value), list):
            raise toolkit.Invalid(toolkit._(u'The value should be a serialised list.'))
    except ValueError as e:
        raise toolkit.Invalid(toolkit._(u'Could not deserialise JSON list.'))
    return value
