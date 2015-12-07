#!/usr/bin/env python

from setuptools import setup

setup(
      name='netcompare',
      version='0.2',
      description='compares two Network Configuration',
      author='Criteo',
      url='https://github.com/criteo/netcompare',
      packages=['netcompare'],
      install_requires=['CiscoConfParse==1.2.39'],
      data_files=[('etc/', ['etc/netcompare.yml'])],
      entry_points={
        'console_scripts': [
            'netcompare = netcompare.netcompare:main',
        ],
      },
      classifiers=(
        # 'Development Status :: 1 - Planning',
        # 'Development Status :: 2 - Pre-Alpha',
        # 'Development Status :: 3 - Alpha',
        'Development Status :: 4 - Beta',
        # 'Development Status :: 5 - Production/Stable',
        # 'Development Status :: 6 - Mature',
        # 'Development Status :: 7 - Inactive',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'License :: License Apache2',
        'Environment :: Console',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7'
        # 'Programming Language :: Python :: 3',
        # 'Programming Language :: Python :: 3.3',
        # 'Programming Language :: Python :: 3.4',
       )
      )
