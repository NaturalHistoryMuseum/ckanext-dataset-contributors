#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-orcid-datasets
# Created by the Natural History Museum in London, UK

def choice(prompt, default=True):
    yn_prompt = u' [Y/n] ' if default else u' [y/N] '
    answer = raw_input(prompt + yn_prompt).lower()
    if answer not in [u'y', u'n', u'']:
        print(u'That wasn\'t an option.')
        return choice(prompt, default)
    elif answer == u'':
        return default
    else:
        return answer == u'y'


def multi_choice(prompt, options, default=0):
    print(prompt)
    for i, o in enumerate(options):
        print(u'\t({0}) {1}'.format(i+1, o))
    answer = raw_input(u'Choose an option: [{0}] '.format(default+1))
    if answer == '':
        return options[default]
    try:
        answer = int(answer)
        return options[answer - 1]
    except:
        print(u'That wasn\'t an option.')
        return multi_choice(prompt, options)
