#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-dataset-contributors
# Created by the Natural History Museum in London, UK
from __future__ import division
import itertools
from collections import Counter

import re
import spacy
from ckanext.dataset_contributors.lib.orcid_api import OrcidApi
from unidecode import unidecode

from .helpers import choice, multi_choice

nlp = spacy.load("en_core_web_sm")


def manual_add(pkg_id):
    new_name = raw_input(u'Name (leave blank to delete): ')
    if new_name == '':
        return
    affiliations = []
    while True:
        new_aff = input(
            u'Affiliation {0} (leave blank to stop adding): '.format(len(affiliations) + 1))
        if new_aff != '':
            affiliations.append(new_aff.strip())
        else:
            break
    return {
        u'name': [new_name],
        u'affiliations': affiliations,
        u'packages': [pkg_id]
        }


class Parser(object):
    def __init__(self, line, pkg):
        self.pkg = pkg
        self.contribs = self.extract(line)

    @classmethod
    def run(cls, txt, pkg):
        for line in txt.split('\n'):
            sublines = cls.prepare_line(line)
            for subline in sublines:
                if subline == '':
                    continue
                yield cls(subline, pkg)

    @classmethod
    def prepare_line(cls, line):
        line = line.replace('\\r', '')
        parsed = nlp(line)
        # check that it has a lot of proper nouns and doesn't just look like a sentence
        tokens = [t for t in parsed]
        pos = Counter([t.pos_ for t in tokens])
        if len(tokens) == 0:
            print(line)
            return []
        pc_proper_nouns = pos.get('PROPN', 0) / len(tokens)
        if pc_proper_nouns < 0.5:
            print('\nThis text doesn\'t look right:')
            print(line)
            if not choice('Try to parse it anyway?', False):
                return []
        sublines = []

        if ' and ' in line:
            sublines = cls._sep_split(' and ', line)
        elif ';' in line:
            sublines = cls._sep_split(';', line)
        if len(sublines) == 0:
            sublines = [line]

        # remove dangling punctuation
        return [re.sub('[,;.]$', '', subline.strip()) for subline in sublines]

    @staticmethod
    def _sep_split(sep, line):
        # try to split items on the same line
        sublines = []
        opening = re.compile('\(')
        closing = re.compile('\)')
        # do parentheses match in each segment
        while line != '':
            sublines += [s for s in line.split(sep) if
                         len(opening.findall(s)) == len(closing.findall(s))]
            splits = [s for s in line.split(sep) if
                      len(opening.findall(s)) != len(closing.findall(s))]
            line = sep.join(splits) if len(splits) > 0 else ''
            if len(splits) <= 2:
                sublines.append(line)
                break
        return [s.strip() for s in sublines]

    def extract(self, line):
        line = line.strip()
        # hopefully there's only one person here, so check if it matches regexes first
        with_affiliation = re.match('^([^()]+)\((.+)\)$', line)
        just_a_name = re.match('^([^(),;]+)$', line)
        if with_affiliation is not None:
            parsed_line_contribs = [{
                'name': [with_affiliation.groups()[0]],
                'affiliations': self.split_affiliations(with_affiliation.groups()[1]),
                'packages': [self.pkg.package_id]
                }]
        elif just_a_name is not None:
            parsed_line_contribs = [{
                'name': [just_a_name.groups()[0]],
                'affiliations': [],
                'packages': [self.pkg.package_id]
                }]
        else:
            parsed_line_contribs = self.extract_with_spacy(line)
        return parsed_line_contribs

    def extract_with_spacy(self, line):
        parsed_line_contribs = []
        return_line_contribs = []
        parsed = nlp(line)
        for entity in parsed.ents:
            if entity.label_ == 'PERSON':
                parsed_line_contribs.append({
                    'name': [entity.text],
                    'affiliations': [],
                    'packages': [self.pkg.package_id]
                    })
            elif len(parsed_line_contribs) == 0:
                continue
            else:
                parsed_line_contribs[-1]['affiliations'].append(entity.text)
        print('\n{0}'.format(line))
        more_contributors = None
        if ',' in line:
            more_contributors = choice('Is there more than one contributor in this line?', False)
            if more_contributors:
                for s in line.split(','):
                    return_line_contribs += self.extract(s)
                return return_line_contribs
            else:
                name, aff = line.split(',', 1)
                parsed_line_contribs = [{
                    'name': [name],
                    'affiliations': [aff],
                    'packages': [self.pkg.package_id]
                    }]
        print('\nFound {0} possible contributors in line:'.format(len(parsed_line_contribs)))
        for i, c in enumerate(parsed_line_contribs):
            c['affiliations'] = self.split_affiliations(' '.join(c['affiliations']))
            print(c)
            if choice('[{0}/{1}] Does this look correct?'.format(i + 1, len(parsed_line_contribs))):
                return_line_contribs.append(c)
            else:
                corrected = manual_add(self.pkg.package_id)
                if corrected is not None:
                    return_line_contribs.append(corrected)
        if more_contributors is None and choice('Did I miss any contributors from that line?',
                                                False):
            cont_adding = True
            while cont_adding:
                new_contrib = manual_add(self.pkg.package_id)
                if new_contrib is not None:
                    return_line_contribs.append(new_contrib)
                cont_adding = choice('Add another?', False)
        return return_line_contribs

    def split_affiliations(self, a_line):
        if ' and ' in a_line:
            affiliations = self._sep_split(' and ', a_line)
        elif ';' in a_line:
            affiliations = self._sep_split(';', a_line)
        elif ',' in a_line:
            # estimate if it's one institution + location or multiple
            parsed = nlp(a_line)
            if any([e.label_ == 'GPE' for e in parsed.ents]):
                # if there's a geopolitical entity (GPE), assume it's one institution
                affiliations = [a_line.strip()]
            else:
                # otherwise assume it's multiple comma-separated institutions
                affiliations = [a.strip() for a in a_line.split(',')]
        else:
            affiliations = [a_line]
        return affiliations


class Combiner(object):
    def __init__(self, contributor_list):
        self._input = contributor_list

    def _name_key(self, contributor):
        '''
        Generate an (initial, surname) key for grouping contributors.
        :param contributor:
        :return:
        '''
        n = unidecode(contributor['name'])
        # remove some common titles
        if n.split(' ')[0].replace('.', '').lower() in ['prof', 'professor', 'dr']:
            n = n.split(' ', 1)[-1]
        surname = n.split(' ')[-1]
        initial = n[0]
        return ' '.join([initial, surname])

    def _filter_diacritics(self, name_list):
        '''
        If any have diacritics etc, return only those, otherwise return the original list
        :param name_list:
        :return:
        '''
        filtered = [n for n in name_list if unidecode(n) != n]
        if len(filtered) > 0:
            return filtered
        else:
            return name_list

    @property
    def grouped(self):
        '''
        Group the input list of contributors by the (initial, surname) key.
        :return: dict
        '''
        return {k: list(v) for k, v in itertools.groupby(sorted(self._input, key=self._name_key),
                                                         key=self._name_key)}

    def _combine_names(self, c_group):
        '''
        Attempt to combine the names within a set of contributors grouped using self._name_key.
        :return:
        '''
        all_names = [x['name'] for x in c_group]
        unique_names = list(set(all_names))
        # split into parts
        first_rgx = re.compile('^[^. ]+')
        last_rgx = re.compile('[^. ]+$')
        middle_rgx = re.compile('^[^. ]+(.+?)[^. ]+$')
        first = []
        last = []
        middle = []
        for n in unique_names:
            first += first_rgx.findall(n)
            last += last_rgx.findall(n)
            middle_matches = middle_rgx.match(n)
            if middle_matches is not None:
                middle += [m.replace('.', ' ').strip() for m in middle_matches.groups()]
        first = list(set(first))
        last = list(set(last))
        # choose the longest version of each name
        combined = {
            'surname': sorted(self._filter_diacritics(last), key=lambda x: -len(x))[0],
            'given_names': sorted(self._filter_diacritics(first), key=lambda x: -len(x))[0]
            }

        # middle names are more complicated
        # remove empty strings and split into parts
        middle = [re.split('\s+', m) for m in list(set(middle)) if m != '']
        middle_parts = {}
        for m in middle:
            for i, x in enumerate(m):
                middle_parts[i] = middle_parts.get(i, []) + [x]
        middle_names = ' '.join(
            [sorted(self._filter_diacritics(p), key=lambda x: -len(x))[0] for p in
             middle_parts.values()])
        if middle_names != '':
            combined['given_names'] += ' ' + middle_names

        return combined

    def run(self, use_orcid=True):
        _combined = []
        if use_orcid:
            api = OrcidApi()
        else:
            api = None
        for key, g in self.grouped.items():
            name = self._combine_names(g)
            packages = [p for x in g for p in x['packages']]
            affiliations = list(set([a for x in g for a in x['affiliations']]))
            if use_orcid:
                results = api.search(surname_q=name['surname'], given_q=name['given_names']).get(u'result', [])
                display_name = ' '.join([name['given_names'], name['surname']])
                if len(results) > 0:
                    results = [api.as_contributor_record(api.read(r[u'orcid-identifier'][u'path'])) for r in results]
                    selection = multi_choice(
                        'Do any of these ORCID results match "{0}"?'.format(display_name),
                        results + ['No'], default=len(results))
                    if selection != 'No':
                        d = selection
                        d['packages'] = packages
                        _combined.append(d)
                        continue
                print(u'No results found for "{0}".'.format(display_name))
            d = name
            d['affiliations'] = affiliations
            d['packages'] = packages
            _combined.append(d)
        return _combined
