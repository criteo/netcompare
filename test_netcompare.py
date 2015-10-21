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

import py.test
from netcompare import *
import os

def compare(test_dir, vendor, capsys):
    with open('netcompare.yml', 'r') as f:
        config = yaml.load(f)

    origin_list = clean_file(test_dir + 'origin.conf', vendor, config)
    target_list = clean_file(test_dir + 'target.conf', vendor, config)

    display_commands = netcompare(origin_list, target_list, vendor, config)

    with open(test_dir + 'result.txt') as file_opened:
        result = file_opened.read()
    print_line(display_commands, vendor, config)
    out, err = capsys.readouterr()
    assert result == out

def test(capsys):
    test_directories = next(os.walk('tests/'))[1]

    for directory in test_directories:
        test_dir = 'tests/' + directory + '/'
        vendor = re.search('^([a-zA-Z0-9]*)_.*', directory).group(1)
        compare(test_dir, vendor, capsys)
