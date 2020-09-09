#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-orcid-datasets
# Created by the Natural History Museum in London, UK

from ckanext.orcid_datasets.logic.common import parse_contributors
from ckanext.orcid_datasets.model.crud import ContributorQ

from ckan.plugins import toolkit


@toolkit.chained_action
def package_update(next_action, context, data_dict):
    '''
    Modify or add new contributors to the dataset before continuing with the package update.
    '''
    data_dict[u'contributors'] = parse_contributors(context, data_dict)
    return next_action(context, data_dict)


def contributor_update(context, data_dict):
    '''
    Manually update a contributor.
    :param context:
    :param data_dict: a dictionary containing the update values
    :return: the updated contributor, as a dict
    '''
    toolkit.check_access(u'contributor_update', context, data_dict)

    contributor_id = data_dict.get(u'id', None)
    if contributor_id is None:
        return
    return ContributorQ.update(contributor_id, **data_dict).as_dict()


def contributor_orcid_update(context, data_dict):
    '''
    Force a refresh of a contributor's data from ORCID.
    :param context:
    :param data_dict: a dictionary containing the contributor's id
    :return: the updated contributor, as a dict
    '''
    toolkit.check_access(u'contributor_orcid_update', context, data_dict)
    if u'id' not in data_dict:
        return
    updated_entry = ContributorQ.update_from_api(data_dict[u'id'])
    return updated_entry.as_dict()
