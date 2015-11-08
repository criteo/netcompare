#!/usr/bin/env python
# Copyright 2015 Criteo. All rights reserved.
#
# The contents of this file are licensed under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with the
# License. You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

import os
import sys
import re

import argparse
import yaml

from ciscoconfparse import CiscoConfParse


def cli_parser(argv=None):
    parser = argparse.ArgumentParser(
        description=('Generating configuration commands by finding differences'
                     ' between two Cisco IOS style configuration files'))
    parser.add_argument('origin', metavar='origin',
                        type=str, help='Origin configuration file')
    parser.add_argument('target', metavar='target',
                        type=str, help='Target configuration file')
    parser.add_argument('vendor', metavar='Vendor or OS definition',
                        type=str, help='vendor')
    return parser.parse_args(argv)


def clean_line(line, vendor):
    cleaned_lines = []
    f5_curly_bracket = re.search('^(?P<space>\s*)(?P<begin>.*)\{(?'
                                 'P<inside>.*)\}(?P<end>.*)$',
                                 line)
    if vendor == 'f5' and f5_curly_bracket:
        cleaned_lines.append(f5_curly_bracket.group('space') +
                             f5_curly_bracket.group('begin') + "{")
        cleaned_lines.append(f5_curly_bracket.group('space') +
                             "  " + f5_curly_bracket.group('inside'))
        cleaned_lines.append(f5_curly_bracket.group('space') + "}" +
                             f5_curly_bracket.group('end').
                             rstrip(' \t\r\n\0'))
    else:
        cleaned_lines.append(line.rstrip(' \t\r\n\0'))
    return cleaned_lines


def clean_file(file, vendor, config):
    with open(file) as file_opened:
        list = file_opened.readlines()

    list_clean = []

    try:
        config[vendor]['dont_compare']
        for line in list:
            for dont_compare in config[vendor]['dont_compare']:
                if dont_compare in line:
                    break
            else:
                list_clean = list_clean + clean_line(line, vendor)
        return list_clean
    except:
        for line in list:
            list_clean = list_clean + clean_line(line, vendor)
        return list_clean


def print_one_line(line, vendor, config):
    if line[0] == 'NO':
        line_text_no = re.match("^(\s*)" +
                                config[vendor]['no_command'] +
                                " (.*)", line[1])
        if line_text_no:
            cmd = (line_text_no.group(1) + line_text_no.group(2))
        else:
            line_text_without_no = re.match("^(\s*)(.*)", line[1])
            cmd = (line_text_without_no.group(1) +
                   config[vendor]['no_command'] + " " +
                   line_text_without_no.group(2))
        print ("%s" % cmd)
    else:
        print ("%s" % line[1])


def print_line(d, vendor, config, depth=0):
    for k, v in sorted(d.items(), key=lambda x: x[0]):
        print_one_line(k, vendor, config)
        print_line(v, vendor, config, depth+1)


def netcompare(origin, target, vendor, config):
    origin_file = (CiscoConfParse(origin,
                   syntax=config[vendor]['CiscoConfParse_syntax'],
                   factory=False))
    target_file = (CiscoConfParse(target,
                   syntax=config[vendor]['CiscoConfParse_syntax'],
                   factory=False))

    result = {}

    for line_origin in origin_file.objs:
        eq_lines = (target_file.find_objects(
                    '^' + re.escape(line_origin.text) + '$'))
        for line_target in eq_lines:
            if line_origin.geneology_text == line_target.geneology_text:
                break
        else:   # Delete needed
            pointer = result
            index = len(line_origin.geneology_text)
            for cmd in line_origin.geneology_text:
                index = index - 1
                if ('NO', cmd) in pointer:
                    break
                if ('_CR', cmd) in pointer:
                    pointer = pointer.get(('_CR', cmd))
                elif index == 0:
                    pointer[('NO', cmd)] = {}
                    pointer = pointer.get(('NO', cmd))
                else:
                    pointer[('_CR', cmd)] = {}
                    pointer = pointer.get(('_CR', cmd))

    for line_target in target_file.objs:
        find = 0
        eq_lines = (origin_file.find_objects(
                    '^' + re.escape(line_target.text) + '$'))
        for line_origin in eq_lines:
            if line_origin.geneology_text == line_target.geneology_text:
                find = 1
        if find == 0:  # Create needed
            pointer = result
            for cmd in line_target.geneology_text:
                if not ('_CR', cmd) in pointer:
                    pointer[('_CR', cmd)] = {}
                pointer = pointer.get(('_CR', cmd))
    return result


def main(argv=None):
    args = cli_parser(argv)
    with open('netcompare.yml', 'r') as f:
        config = yaml.load(f)

    origin_list = clean_file(args.origin, args.vendor, config)
    target_list = clean_file(args.target, args.vendor, config)

    display_commands = netcompare(origin_list,
                                  target_list, args.vendor, config)
    print_line(display_commands, args.vendor, config)


if __name__ == '__main__':
    main()
