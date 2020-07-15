#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-orcid-datasets
# Created by the Natural History Museum in London, UK

from unittest import SkipTest

from ckanext.orcid_datasets.lib.orcid_api import OrcidApi

from ckan.plugins import toolkit


sandbox_portal_orcid = u'0000-0002-6856-1627'

def skip_without_credentials():
    api = OrcidApi()
    missing = api.key is None or api.secret is None
    message = toolkit._(u'ORCID API credentials not supplied.')
    if missing:
        raise SkipTest(message)
    else:
        return api