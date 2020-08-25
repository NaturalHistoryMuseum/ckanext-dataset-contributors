#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-orcid-datasets
# Created by the Natural History Museum in London, UK


from ckanext.orcid_datasets.lib.orcid_api import OrcidApi
from ckanext.orcid_datasets.model.contributor import Contributor
from ckanext.orcid_datasets.model.crud import ContributorQ
from sqlalchemy import and_
from sqlalchemy.orm.attributes import InstrumentedAttribute

from ckan.model import Session
from ckan.plugins import toolkit


def contributor_show(context, data_dict):
    contributor_id = data_dict.get(u'id', None)
    if contributor_id is None or contributor_id == u'':
        raise toolkit.ObjectNotFound(toolkit._(u'Contributor ID not supplied.'))
    contributor = ContributorQ.read(contributor_id)
    if contributor is not None:
        return contributor.as_dict()
    else:
        raise toolkit.ObjectNotFound(toolkit._(u'Contributor ID not found.'))


def contributor_autocomplete(context, data_dict):
    include_orcid = data_dict.pop('include_orcid', False)

    filters = []
    for k, v in data_dict.items():
        if v is not None and hasattr(Contributor, k) and isinstance(getattr(Contributor, k),
                                                                    InstrumentedAttribute):
            filters.append(getattr(Contributor, k).ilike(u'%' + v + u'%'))

    portal_results = Session.query(Contributor).filter(and_(*filters)).limit(10).all()
    orcid_results = []
    orcid_remaining = 0

    if include_orcid:
        api = OrcidApi()
        _orcid_search = api.search(data_dict.get(u'surname', None), data_dict.get(u'orcid', None))
        n = _orcid_search.get(u'num-found', 0)
        records = _orcid_search.get('result', [])
        orcid_ids = []
        for r in records:
            _id = r.get(u'orcid-identifier', {}).get(u'path', None)
            if _id is not None and _id not in orcid_ids:
                try:
                    orcid_record = api.as_contributor_record(api.read(_id))
                    orcid_results.append(orcid_record)
                    orcid_ids.append(_id)
                except AttributeError as e:
                    # probably a malformed orcid record
                    continue
        if n > len(orcid_results):
            orcid_remaining = n - len(orcid_results)

    return {
        'portal': [r.as_dict() for r in portal_results],
        'orcid': orcid_results,
        'orcid_remaining': orcid_remaining
        }
