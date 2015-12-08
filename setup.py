#!/usr/bin/env python

from os.path import join

from setuptools import setup, find_packages


NAME = 'netcompare'
PACKAGE = NAME.replace('-', '_')
CLASSIFIERS = """\
Development Status :: 4 - Beta
Environment :: Console
Intended Audience :: Information Technology
Intended Audience :: Network Administrators
License :: OSI Approved :: Apache Software License
Operating System :: OS Independent
Programming Language :: Python :: 2.7
"""


def get_version():
    with open(join(PACKAGE, '__init__.py')) as fileobj:
        for line in fileobj:
            if line.startswith('__version__ ='):
                return line.split('=', 1)[1].strip()[1:-1]
        else:
            raise Exception(
                '__version__ is not defined in %s.__init__' % PACKAGE)


setup(
    name=NAME,
    version=get_version(),
    author='Criteo Network team',
    author_email='prod-network@criteo.com',
    description='Compare network equipment configurations',
    packages=find_packages(),
    install_requires=['CiscoConfParse==1.2.39'],
    data_files=[('etc/', ['etc/netcompare.yml'])],
    entry_points={
        'console_scripts': [
            'netcompare = netcompare.netcompare:main',
        ],
    },
    classifiers=CLASSIFIERS,
    include_package_data=True,
)
