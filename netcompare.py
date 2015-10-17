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


def cli_parser():
    parser = argparse.ArgumentParser(
        description=('Generating configuration commands by finding differences'
                     ' between two Cisco IOS style configuration files'))
    parser.add_argument('origin', metavar='origin',
                        type=str, help='Origin configuration file')
    parser.add_argument('target', metavar='target',
                        type=str, help='Target configuration file')
    parser.add_argument('no_command', metavar='no_command',
                        type=str, help='Negation command keyword')
    return parser.parse_args()


def clean_file(file, no_command):
    with open(file) as file_opened:
        list = file_opened.readlines()

    list_clean = []

    if no_command == 'undo':
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
            if 'Current Configuration ...' in line:
                pass
            else:
                list_clean.append(line.rstrip(' \t\r\n\0'))

    return list_clean


def compare_children_prefix_no(obj_origin, obj_target, no_command):
    command_list = [obj_origin.text]
    for child in obj_origin.children:
        match = obj_target.find_objects_w_parents(
            obj_origin.text,
            '^'+re.escape(child.text)+'$')
        if len(match) == 0 and not re.match(
          "\s*" + no_command + "\s.*", child.text):
            line_text_without_indent = re.match("(\s*)(.*)", child.text)
            command_list.append(
                line_text_without_indent.group(1) +
                no_command +
                " " +
                line_text_without_indent.group(2))
        elif len(match) == 0 and re.match(
          "\s*" + no_command + "\s.*", child.text):
            line_text_without_no = re.match(
              "(\s*)" + no_command + "\s(.*)", child.text)
            command_list.append(
                line_text_without_no.group(1) +
                line_text_without_no.group(2))
        elif len(child.children) > 0:
            for result_recursive in compare_children_prefix_no(
                    child, obj_target, no_command):
                command_list.append(result_recursive)
    if len(command_list) > 1:
        return command_list
    else:
        return []


def compare_children(obj_origin, obj_target):
    command_list = [obj_origin.text]
    for child in obj_origin.children:
        match = obj_target.find_objects_w_parents(
            obj_origin.text,
            '^'+re.escape(child.text)+'$')
        if len(child.children) > 0:
            for result_recursive in compare_children(child, obj_target):
                command_list.append(result_recursive)
        elif len(match) == 0:
            command_list.append(child.text)
    if len(command_list) > 1:
        return command_list
    else:
        return []


def merge_commands(list1, list2):
    command_list = []
    for line_list1 in list1:
        if isinstance(line_list1, list) is True:
            for line_children_list1 in line_list1:
                command_list.append(line_children_list1)
            for line_list2 in list2:
                if isinstance(line_list2, list) is True:
                    if line_list1[0] == line_list2[0]:
                        for line_children_list2 in line_list2[1:]:
                            command_list.append(line_children_list2)
                        list2.remove(line_list2)
        else:
            command_list.append(line_list1)
    for line_list2 in list2:
        if isinstance(line_list2, list) is True:
            for line_children_list2 in line_list2:
                command_list.append(line_children_list2)
        else:
            command_list.append(line_list2)
    return command_list


def netcompare(origin, target, no_command):
    origin_file = CiscoConfParse(origin, syntax='ios', factory=False)
    target_file = CiscoConfParse(target, syntax='ios', factory=False)
    diff_add_no_commands = []
    for line in origin_file.objs:
        if line.parent.linenum == line.linenum and line.is_config_line is True:
            parent_match = target_file.find_objects(
                '^'+re.escape(line.text)+'$',
                exactmatch=True, ignore_ws=False)
            if len(parent_match) == 0 and not re.match(
              no_command + "\s.*", line.text):
                diff_add_no_commands.append(no_command + ' ' + line.text)
            elif len(parent_match) == 0 and re.match(
              no_command + "\s.*", line.text):
                line_text_without_no = re.match(
                  no_command + "\s(.*)", line.text)
                diff_add_no_commands.append(line_text_without_no.group(1))
            if len(line.children) > 0 and len(parent_match) != 0:
                result_comparison = compare_children_prefix_no(
                    line, target_file, no_command)
                if len(result_comparison) > 0:
                    diff_add_no_commands.append(result_comparison)
    diff_add_commands = []
    for line in target_file.objs:
        if line.parent.linenum == line.linenum and line.is_config_line is True:
            parent_match = origin_file.find_objects(
                '^'+re.escape(line.text)+'$',
                exactmatch=True, ignore_ws=False)
            if len(parent_match) == 0:
                parent_with_children = target_file.find_all_children(
                    '^'+re.escape(line.text)+'$')
                for line_in_parent_with_children in parent_with_children:
                    diff_add_commands.append(line_in_parent_with_children)
            if len(line.children) > 0 and len(parent_match) != 0:
                result_comparison = compare_children(line, origin_file)
                if len(result_comparison) > 0:
                    diff_add_commands.append( result_comparison )
    return merge_commands(diff_add_no_commands, diff_add_commands)


def main():
    args = cli_parser()

    origin_list = clean_file(args.origin, args.no_command)
    target_list = clean_file(args.target, args.no_command)

    display_commands = netcompare(origin_list, target_list, args.no_command)
    for line in display_commands:
        print line

if __name__ == '__main__':
    main()
