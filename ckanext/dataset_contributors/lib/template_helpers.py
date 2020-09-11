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


def convert_to_contributor_details(id_list):
    '''
    Ensures that the contributors field is loaded in the correct format for rendering in a
    template (i.e. with full details rather than just a list of IDs). This is useful for when
    there is a validation error and the page reloads with the package_update schema rather than
    package_show.
    :param id_list:
    :return:
    '''
    try:
        id_list = json.loads(id_list)
    except:
        pass
    if isinstance(id_list, dict):
        return id_list
    if not isinstance(id_list, list):
        return {}
    contributor_show = toolkit.get_action(u'contributor_show')
    contributors = {}
    for ix, _id in enumerate(id_list):
        row = contributor_show({}, {
            u'id': _id
            })
        row[u'order'] = ix
        contributors[_id] = row
    return contributors


def can_edit():
    '''
    Check editing permissions for updating contributors directly.
    :return:
    '''
    try:
        permitted = toolkit.check_access(u'contributor_update', {}, {})
        return permitted
    except toolkit.NotAuthorized:
        return False
