#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-dataset-contributors
# Created by the Natural History Museum in London, UK

import json

from ckanext.dataset_contributors.model.crud import ContributorQ

from ckan.plugins import toolkit


def is_serialised_list(value):
    ''' Make sure value can be deserialised into a list.'''
    if value is None or value == u'':
        return
    try:
        if not isinstance(value, (str, unicode)):
            raise toolkit.Invalid(toolkit._(u'The value should be a serialised list.'))
        if not isinstance(json.loads(value), list):
            raise toolkit.Invalid(toolkit._(u'The value should be a serialised list.'))
    except ValueError as e:
        raise toolkit.Invalid(toolkit._(u'Could not deserialise JSON list.'))
    return value


def from_contributor_ids(value):
    '''Get the associated contributors.'''
    if value is None or value == u'':
        return
    if isinstance(value, list):
        ids = value
    else:
        try:
            ids = json.loads(value)
        except ValueError:
            raise toolkit.Invalid(toolkit._(u'The value should be a list or serialised list.'))
    contributors = {}
    for ix, i in enumerate(ids):
        row = ContributorQ.read(i)
        if row is not None:
            row_dict = row.as_dict()
            row_dict[u'order'] = ix
            contributors[i] = row_dict
    return contributors


def to_contributor_ids(value):
    '''Get contributor ids from the dictionary.'''
    if not isinstance(value, list):
        raise toolkit.Invalid(toolkit._(u'This is not a list.'))
    if len(value) == 0 or isinstance(value[0], str) or isinstance(value[0], unicode):
        return json.dumps(value)
    if isinstance(value[0], dict):
        try:
            return json.dumps([c[u'id'] for c in value])
        except KeyError as e:
            raise toolkit.Invalid(toolkit._(u'Item does not have "id" attribute.'))
    else:
        raise toolkit.Invalid(toolkit._(u'Incorrect format.'))
