#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-dataset-contributors
# Created by the Natural History Museum in London, UK

from ckanext.dataset_contributors.logic.common import parse_contributors
from ckanext.dataset_contributors.model.crud import ContributorQ

from ckan.plugins import toolkit


@toolkit.chained_action
def package_create(next_action, context, data_dict):
    data_dict[u'contributors'] = parse_contributors(context, data_dict)
    return next_action(context, data_dict)


def contributor_create(context, data_dict):
    '''

    :param context:
    :param data_dict:
    :return:
    '''
    toolkit.check_access(u'contributor_create', context, data_dict)
    try:
        del data_dict[u'id']
    except KeyError:
        pass
    return ContributorQ.create(**data_dict).as_dict()
