#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-orcid-datasets
# Created by the Natural History Museum in London, UK

import json

from ckanext.orcid_datasets.model.crud import ContributorQ

from ckan.plugins import toolkit


@toolkit.chained_action
def package_update(next_action, context, data_dict):
    '''
    Modify or add new contributors to the dataset before continuing with the package update.
    '''
    contributors = json.loads(data_dict.get(u'contributors', u'{}'))
    new_contributors = [c for _, c in contributors.items() if c.get('new', False)]
    existing_contributors = [c for _, c in contributors.items() if not c.get('new', False)]
    package_contributors = []
    for c in existing_contributors:
        if c.get(u'delete', False):
            continue
        if c.get(u'update', False):
            toolkit.get_action(u'contributor_update')(context, c)
        package_contributors.append(c)
    for c in new_contributors:
        if c.get(u'delete', False):
            continue
        new_contributor = None
        if c.get(u'orcid', None) is not None:
            # if that orcid already exists in the database, just add that
            in_database = ContributorQ.read_orcid(c.get(u'orcid'))
            if len(in_database) > 0:
                new_contributor = in_database[0].as_dict()
        if new_contributor is None:
            new_contributor = toolkit.get_action(u'contributor_create')(context, c)
        new_contributor[u'order'] = c.get(u'order', len(package_contributors))
        package_contributors.append(new_contributor)

    contributor_ids = [c[u'id'] for c in sorted(package_contributors, key=lambda x: x[u'order'])]
    data_dict[u'contributors'] = json.dumps(contributor_ids)

    return next_action(context, data_dict)


def contributor_update(context, data_dict):
    '''
    Manually update a contributor.
    :param context:
    :param data_dict: a dictionary containing the update values
    :return: the updated contributor, as a dict
    '''
    toolkit.check_access(u'contributor_update', context, data_dict)

    contributor_id = data_dict.pop(u'id', None)
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
