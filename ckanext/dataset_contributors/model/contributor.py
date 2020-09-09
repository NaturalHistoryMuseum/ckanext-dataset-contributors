#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-dataset-contributors
# Created by the Natural History Museum in London, UK

from sqlalchemy import (Column, ForeignKey, Table, UnicodeText)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import backref, relation

from ckan.model import DomainObject, User, meta, package_table
from ckan.model.types import make_uuid

# this table stores contributors
contributor_table = Table(
    u'contributors',
    meta.metadata,
    Column(u'id', UnicodeText, primary_key=True, default=make_uuid),
    Column(u'surname', UnicodeText, nullable=False, index=True),
    Column(u'given_names', UnicodeText, nullable=False),
    Column(u'affiliations', JSONB, nullable=True),
    Column(u'orcid', UnicodeText, nullable=True, unique=True),
    Column(u'user_id', UnicodeText,
           ForeignKey(u'user.id', onupdate=u'CASCADE', ondelete=u'CASCADE'), nullable=True)
    )


class Contributor(DomainObject):
    '''
    Object for a contributor row.
    '''
    pass


meta.mapper(Contributor, contributor_table, properties={
    u'dataset': relation(User,
                         backref=backref(u'contributor', cascade=u'all, delete-orphan'),
                         primaryjoin=contributor_table.c.user_id.__eq__(User.id)
                         )
    })


def check_for_table():
    if package_table.exists():
        contributor_table.create(checkfirst=True)