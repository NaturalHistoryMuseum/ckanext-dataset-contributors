#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-orcid-datasets
# Created by the Natural History Museum in London, UK

import json

from ckanext.orcid_datasets.model.crud import ContributorQ

from ckan.plugins import toolkit


def parse_contributors(context, data_dict):
    contributors = json.loads(data_dict.get(u'contributors', u'{}'))
    if isinstance(contributors, list):
        return data_dict.get(u'contributors')
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
            if in_database is not None:
                new_contributor = in_database.as_dict()
        if new_contributor is None:
            new_contributor = toolkit.get_action(u'contributor_create')(context, c)
        new_contributor[u'order'] = c.get(u'order', len(package_contributors))
        package_contributors.append(new_contributor)

    contributor_ids = [c[u'id'] for c in
                       sorted(package_contributors, key=lambda x: x.get(u'order', 0))]
    return json.dumps(contributor_ids)