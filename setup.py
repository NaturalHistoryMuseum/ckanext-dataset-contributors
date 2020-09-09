#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-dataset-contributors
# Created by the Natural History Museum in London, UK

from setuptools import find_packages, setup

__version__ = u'1.0.0-alpha'

with open(u'README.md', u'r') as f:
    __long_description__ = f.read()

setup(
    name=u'ckanext-dataset-contributors',
    version=__version__,
    description=u'A CKAN extension that connects ORCID identifiers to dataset authors.',
    long_description=__long_description__,
    classifiers=[
        u'Development Status :: 3 - Alpha',
        u'Framework :: Flask',
        u'Programming Language :: Python :: 2.7'
    ],
    keywords=u'CKAN data dataset_contributors',
    author=u'Natural History Museum',
    author_email=u'data@nhm.ac.uk',
    url=u'https://github.com/NaturalHistoryMuseum/ckanext-dataset-contributors',
    license=u'GNU GPLv3',
    packages=find_packages(exclude=[u'tests']),
    namespace_packages=[u'ckanext', u'ckanext.dataset_contributors'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        u'orcid',
        u'spacy',
        u'unidecode'
        ],
    entry_points= \
        u'''
        [ckan.plugins]
            dataset_contributors=ckanext.dataset_contributors.plugin:DatasetContributorsPlugin

        [paste.paster_command]
            orcid-sync=ckanext.dataset_contributors.commands.orcid_sync:OrcidSyncCommand
            contributor-migrate=ckanext.dataset_contributors.commands.migrate:ContributorMigrateCommand
        ''',
    )
