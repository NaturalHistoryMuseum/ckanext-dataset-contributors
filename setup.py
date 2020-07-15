#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-orcid-datasets
# Created by the Natural History Museum in London, UK

from setuptools import find_packages, setup

__version__ = u'1.0.0-alpha'

with open(u'README.md', u'r') as f:
    __long_description__ = f.read()

setup(
    name=u'ckanext-orcid-datasets',
    version=__version__,
    description=u'A CKAN extension that connects ORCID identifiers to dataset authors.',
    long_description=__long_description__,
    classifiers=[
        u'Development Status :: 3 - Alpha',
        u'Framework :: Flask',
        u'Programming Language :: Python :: 2.7'
    ],
    keywords=u'CKAN data orcid_datasets',
    author=u'Natural History Museum',
    author_email=u'data@nhm.ac.uk',
    url=u'https://github.com/NaturalHistoryMuseum/ckanext-orcid-datasets',
    license=u'GNU GPLv3',
    packages=find_packages(exclude=[u'tests']),
    namespace_packages=[u'ckanext', u'ckanext.orcid_datasets'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        u'orcid'
        ],
    entry_points= \
        u'''
        [ckan.plugins]
            orcid_datasets=ckanext.orcid_datasets.plugin:OrcidDatasetsPlugin

        [paste.paster_command]
            orcid-sync=ckanext.orcid_datasets.commands.orcid_sync:OrcidSyncCommand
        ''',
    )
