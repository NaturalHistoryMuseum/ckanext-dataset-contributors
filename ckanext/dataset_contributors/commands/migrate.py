#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-dataset-contributors
# Created by the Natural History Museum in London, UK

import json

from ckanext.dataset_contributors.model.contributor import check_for_table
from ckanext.dataset_contributors.model.crud import ContributorQ

from ckan.model import Session
from ckan.model.package_extra import PackageExtra
from ckan.plugins import toolkit
from ._migrate_helpers import Combiner, Parser
from .helpers import choice


class ContributorMigrateCommand(toolkit.CkanCommand):
    '''
    Paster functions for manipulating the database when first installing the extension.

    Commands:
        paster contributor-migrate existing -c /etc/ckan/default/development.ini
    '''
    summary = __doc__.split(u'\n')[0]
    usage = __doc__

    def command(self):
        if not self.args or self.args[0] in [u'--help', u'-h', u'help']:
            print(self.summary)
            return

        self._load_config()

        cmd = self.args[0]
        if cmd == u'existing':
            self.existing()
        else:
            print(u'{0} not recognised'.format(cmd))

    def existing(self):
        # TODO
        print(
            u'\nAttempting to migrate contributors. It is HIGHLY recommended that you back up '
            u'your database before running this.')
        if not choice('Continue?', False):
            print(u'Cancelling. Nothing has been changed.')
            return
        check_for_table()
        pkgs_with_contribs = Session.query(PackageExtra).filter(
            PackageExtra.key == u'contributors').all()
        print(u'{0} values found.'.format(len(pkgs_with_contribs)))
        all_found_contribs = []
        for pkg in pkgs_with_contribs:
            if pkg.value is None:
                continue
            for parser_group in Parser.run(pkg.value, pkg):
                all_found_contribs += parser_group.contribs

        for i, c in enumerate(all_found_contribs):
            c['name'] = ' '.join([n.strip() for n in c['name']]).strip()
            all_found_contribs[i] = c

        combined = Combiner(all_found_contribs).run()
        by_package = {}
        for contributor in combined:
            c_obj = None
            if 'orcid' in contributor:
                c_obj = ContributorQ.read_orcid(contributor['orcid'])
            if c_obj is None:
                c_obj = ContributorQ.create(**contributor)
            for package_id in contributor['packages']:
                by_package[package_id] = by_package.get(package_id, []) + [c_obj.id]
        for package_id, contributor_ids in by_package.items():
            package_extra = Session.query(PackageExtra).filter(
                PackageExtra.package_id == package_id, PackageExtra.key == u'contributors')
            package_extra.update({
                'value': json.dumps(contributor_ids)
                })
            Session.commit()

        print(u'Added {0} new contributors.'.format(len(combined)))
        for c in combined:
            print(c)
