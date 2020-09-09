#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-dataset-contributors
# Created by the Natural History Museum in London, UK

from ckanext.dataset_contributors.model.contributor import Contributor, contributor_table
from ckanext.dataset_contributors.lib.orcid_api import OrcidApi
from requests import HTTPError

from ckan.model import Session
from ckan.plugins import toolkit


class ContributorQ(object):
    # model, for convenience
    m = Contributor

    @classmethod
    def _columns(cls, **kwargs):
        return {c.name: kwargs.get(c.name) for c in contributor_table.c if c.name in kwargs}

    @classmethod
    def create(cls, **kwargs):
        contributor_dict = cls._columns(**kwargs)
        new_contributor = Contributor(**contributor_dict)
        Session.add(new_contributor)
        Session.commit()
        return new_contributor

    @classmethod
    def read(cls, contributor_id):
        return Session.query(Contributor).get(contributor_id)

    @classmethod
    def read_orcid(cls, orcid):
        return Session.query(Contributor).filter(Contributor.orcid == orcid).first()

    @classmethod
    def search(cls, query):
        return Session.query(Contributor).filter(query).all()

    @classmethod
    def update(cls, contributor_id, **kwargs):
        Session.query(Contributor).filter(Contributor.id == contributor_id).update(
            cls._columns(**kwargs))
        Session.commit()
        return Session.query(Contributor).get(contributor_id)

    @classmethod
    def update_from_api(cls, contributor_id, api=None):
        if api is None:
            api = OrcidApi()
        current_entry = cls.read(contributor_id)
        if current_entry.orcid is None:
            return
        try:
            orcid_record = api.read(current_entry.orcid)
        except HTTPError:
            orcid_results = api.search(orcid_q=current_entry.orcid)
            if orcid_results[u'num-found'] == 0:
                raise Exception(toolkit._(u'This ORCID does not exist.'))
            else:
                orcid_record = orcid_results[u'result'][0]
        updated_entry = api.as_contributor_record(orcid_record)
        return cls.update(contributor_id, **updated_entry)

    @classmethod
    def delete(cls, contributor_id):
        to_delete = Session.query(Contributor).get(contributor_id)
        if to_delete is not None:
            Session.delete(to_delete)
            Session.commit()
