#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-orcid-datasets
# Created by the Natural History Museum in London, UK

from ckanext.orcid_datasets.model.crud import ContributorQ

from ckan.plugins import toolkit


def contributor_create(context, data_dict):
    '''

    :param context:
    :param data_dict:
    :return:
    '''
    toolkit.check_access(u'contributor_create', context, data_dict)
    del data_dict[u'id']
    return ContributorQ.create(**data_dict).as_dict()
