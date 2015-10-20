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

import argparse
from ciscoconfparse import CiscoConfParse
import sys
import re
import os
import yaml
import pprint


def cli_parser():
    parser = argparse.ArgumentParser(
        description=('Generating configuration commands by finding differences'
                     ' between two Cisco IOS style configuration files'))
    parser.add_argument('origin', metavar='origin',
                        type=str, help='Origin configuration file')
    parser.add_argument('target', metavar='target',
                        type=str, help='Target configuration file')
    parser.add_argument('vendor', metavar='vendor',
                        type=str, help='vendor')
    return parser.parse_args()

def clean_file(file, vendor):
    with open(file) as file_opened:
        list = file_opened.readlines()

    list_clean = []

    if vendor == 'huawei':
        line_parent_sharp = False
        for line in list:
            line_clean = line.rstrip(' \t\r\n\0')
            if line_parent_sharp is False:
                if line_clean == '#' or line_clean == '!':
                    line_parent_sharp = True
                elif re.match('^!.*$', line_clean) or re.match(
                  '^#.*$', line_clean):
                    pass
                elif line_clean == 'return' or line_clean == 'exit':
                    pass
                elif line_clean == '':
                    pass
                else:
                    list_clean.append(line_clean)
            else:
                if line_clean == '#' or line_clean == '!':
                    line_parent_sharp = True
                elif re.match('^!.*$', line_clean) or re.match(
                  '^#.*$', line_clean):
                    pass
                elif line_clean == 'return' or line_clean == 'exit':
                    pass
                elif re.match('^\s.*$', line_clean):
                    line_without_space = re.match('^\s(.*)$', line_clean)
                    list_clean.append(line_without_space.group(1))
                elif line_clean == '':
                    pass
                else:
                    list_clean.append(line_clean)
                    line_parent_sharp = False
    else:
        for line in list:
            for dont_compare in config[vendor]['dont_compare']:
                if dont_compare in line:
                    break
            else:
                f5_curly_bracket = re.search('^(?P<space>\s*)(?P<begin>.*)\{(?P<inside>.*)\}(?P<end>.*)$', line)
                if vendor == 'f5' and f5_curly_bracket:
                    list_clean.append(f5_curly_bracket.group('space')+f5_curly_bracket.group('begin')+"{")
                    list_clean.append(f5_curly_bracket.group('space')+"  "+f5_curly_bracket.group('inside'))
                    list_clean.append(f5_curly_bracket.group('space')+"}"+f5_curly_bracket.group('end').rstrip(' \t\r\n\0'))
                else:
                    list_clean.append(line.rstrip(' \t\r\n\0'))
    return list_clean

def print_line(d,depth=0):
    for k,v in sorted(d.items(),key=lambda x: x[0]):
        if isinstance(v, dict):
            print ("%s" % k)
            print_line(v,depth+1)
        else:
            print "%s %s" % (k, v)

def netcompare(origin, target, vendor):
    origin_file = CiscoConfParse(origin, syntax=config[vendor]['CiscoConfParse_syntax'], factory=False)
    target_file = CiscoConfParse(target, syntax=config[vendor]['CiscoConfParse_syntax'], factory=False)
    result = {}
    for line_origin in origin_file.objs:
        find = 0
        for line_target in target_file.objs:
            if line_origin.geneology_text == line_target.geneology_text:
		find = find + 1
	if find == 0:
            pointer = result
            for cmd in line_origin.geneology_text:
                if not cmd in pointer:
                    pointer[cmd] = {}
                pointer = pointer.get(cmd)
    for line_target in target_file.objs:
        find = 0
        for line_origin in origin_file.objs:
            if line_origin.geneology_text == line_target.geneology_text:
		find = find + 1
	if find == 0:
            pointer = result
            size = len(line_target.geneology_text)
            for cmd in line_target.geneology_text:
                size = size - 1
                if re.match("(\s*)(.*)", cmd):
                	line_text_without_no = re.match("^(\s*)(.*)", cmd)
                        cmd_no = line_text_without_no.group(1) + config[vendor]['no_command'] + " " + line_text_without_no.group(2)
                        if cmd_no in pointer:
                        	break
                if not cmd in pointer and size == (len(line_target.geneology_text) - 1):
                        pointer[cmd] = {}
                if not cmd in pointer:
                     	if not re.match(config[vendor]['no_command'] + "\s.*", cmd):
                        	line_text_without_no = re.match("^(\s*)(.*)", cmd)
                     		cmd = line_text_without_no.group(1) + config[vendor]['no_command'] + " " + line_text_without_no.group(2)
                     	elif re.match(config[vendor]['no_command'] + "\s.*", cmd):
                        	line_text_without_no = re.match(config[vendor]['no_command'] + "\s(.*)", cmd)
                        	cmd = line_text_without_no.group(1)
                        pointer[cmd] = {}
                pointer = pointer.get(cmd)
    return result


def main():
    args = cli_parser()
    global config
    with open('netcompare.yml', 'r') as f:
        config = yaml.load(f)

    origin_list = clean_file(args.origin, args.vendor)
    target_list = clean_file(args.target, args.vendor)

    display_commands = netcompare(origin_list, target_list, args.vendor)
    print_line(display_commands)
    

if __name__ == '__main__':
    main()
