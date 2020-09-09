#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-dataset-contributors
# Created by the Natural History Museum in London, UK

from ckan.plugins import toolkit
from ckanext.dataset_contributors.lib.orcid_api import OrcidApi
from ckanext.dataset_contributors.model.crud import ContributorQ
from ckanext.dataset_contributors.model.contributor import Contributor


class OrcidSyncCommand(toolkit.CkanCommand):
    '''
    Paster functions to communicate with the ORCID API.

    Commands:
        paster orcid-sync pull -c /etc/ckan/default/development.ini
    '''
    summary = __doc__.split(u'\n')[0]
    usage = __doc__

    def command(self):
        if not self.args or self.args[0] in [u'--help', u'-h', u'help']:
            print(self.summary)
            return

        self._load_config()

        cmd = self.args[0]
        if cmd == u'pull':
            self.pull()
        else:
            print(u'{0} not recognised'.format(cmd))

    def pull(self):
        orcids = self.args[1:] if len(self.args) > 1 else []
        api = OrcidApi()
        if len(orcids) > 0:
            records = ContributorQ.search(Contributor.orcid.in_(orcids))
        else:
            records = ContributorQ.search(Contributor.orcid.isnot(None))
        print(u'Found {0} ORCID record(s).'.format(len(records)))
        success = 0
        failure = 0
        for r in records:
            try:
                ContributorQ.update_from_api(r.id, api=api)
                success += 1
            except Exception as e:
                print(u'Error ({0}): {1}'.format(r.orcid, e))
                failure += 1
        print(u'Updated {0}/{1} ({2} failed)'.format(success, len(records), failure))
