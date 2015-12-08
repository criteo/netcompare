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

import pytest

from netcompare import netcompare


@pytest.fixture
def data_dir():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')


def pytest_generate_tests(metafunc):
    dir = os.listdir(data_dir())
    metafunc.parametrize("directory", dir)


def test_assert(capsys, directory, data_dir):
    origin = os.path.join(data_dir, directory, 'origin.conf')
    target = os.path.join(data_dir, directory, 'target.conf')
    vendor = directory.split('_', 1)[0]
    result = os.path.join(data_dir, directory, 'result.txt')
    netcompare.main(
                     ["--origin", origin,
                      "--target", target,
                      "--vendor", vendor]
                   )
    with open(result) as file_opened:
        result = file_opened.read()
    out, err = capsys.readouterr()
    assert result == out
