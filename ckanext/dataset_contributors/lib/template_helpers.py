#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-dataset-contributors
# Created by the Natural History Museum in London, UK

import json
from ckan.plugins import toolkit


def as_string(value):
    if isinstance(value, (str, unicode)):
        return value
    elif isinstance(value, (list, dict)):
        try:
            return json.dumps(value)
        except:
            return ''
    else:
        return str(value)


def contributor_details(id_list):
    try:
        id_list = json.loads(id_list)
    except:
        pass
    if not isinstance(id_list, list):
        raise TypeError(u'Value is not a list and could not be converted to one.')
    contributor_show = toolkit.get_action(u'contributor_show')
    contributors = {}
    for ix, _id in enumerate(id_list):
        row = contributor_show({}, {u'id': _id})
        row[u'order'] = ix
        contributors[_id] = row
    return contributors


def can_edit():
    try:
        permitted = toolkit.check_access(u'contributor_update', {}, {})
        return permitted
    except toolkit.NotAuthorized:
        return False