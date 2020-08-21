#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-orcid-datasets
# Created by the Natural History Museum in London, UK

from unittest import SkipTest

import os
from ckanext.orcid_datasets.lib.orcid_api import OrcidApi

from ckan.plugins import toolkit

sandbox_portal_orcid = u'0000-0002-6856-1627'


def skip_without_credentials():
    api = OrcidApi()
    missing = api.key is None or api.secret is None
    if missing:
        env_key = os.environ.get('ORCID_KEY', None)
        env_secret = os.environ.get('ORCID_SECRET', None)
        if env_key is not None and env_secret is not None:
            missing = False
            api.key = env_key
            api.secret = env_secret
    message = toolkit._(u'ORCID API credentials not supplied.')
    if missing:
        raise SkipTest(message)
    else:
        return api
