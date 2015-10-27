netcompare
==========
netcompare is a python script that compares two Cisco IOS style's configuration files for a single network device (one origin and one target). It returns an ordered list of commands that can be applied to the network equipment in order to achieve the target configuration state.
It's like a "diff" on steroids, which takes care of command's parent / child relationships.
This script has been written with network configuration automation in mind, for crappy network equipments that does not support atomic changes.

[![Build Status](https://travis-ci.org/criteo/netcompare.png?branch=master)](https://travis-ci.org/criteo/netcompare) [![codecov.io](https://codecov.io/github/criteo/netcompare/coverage.svg?branch=master)](https://codecov.io/github/criteo/netcompare?branch=master)

Known to work with
------------------
 * Cisco IOS
 * Cisco ASA
 * Dell FTOS
 * Huawei VRP
 * F5 BigIP LTM

It can also work with these platforms (but they support -at least partially- atomic changes, so there's a better way):
 * Arista EOS (configuration sessions with commit supported in modern EOS releases)
 * Cisco NXOS (you can implement pseudo atomic methods with configuration checkpoints and "rollback-patch" command)
 * Cisco IOS XR (supports commit with limitations on object renaming)

It should work with all Cisco IOS style kind of configuration files.

Comparison algorithm
--------------------
The script does the work in two pass:

1. For each line of the origin configuration file, check if this line is present in the target file. If not, we assume that we need to prefix this line with "no" and add it in our resulting command list.
2. For each line of the target configuration file, check if this line is present in the origin file. If not, we assume that we need this line in our resulting command list.

Then, we sort the two resulting lists to be sure that "no" commands are placed before new commands.

That's the basics. We'll do a detailed diagram to explain everything in a near future.

Limitations
-----------
There's no black magic in this script, it can't invent commands, so be careful with implicit configurations.

Don't forget to yell at your favorite vendor's representatives about their bad CLI and lack of API.

How-to
======
That's quite simple, call netcompare.py with 3 arguments:
 * The origin configuration file
 * The target configuration file
 * The OS/Vendor of the equipment's configuration file. It can be for now:
  * ios: for Cisco IOS-style configurations (Cisco IOS, Dell)
  * vrp: for Huawei VRP-style configurations
  * f5: for F5 BigIP LTM-style configurations

```
    python netcompare.py tests/data/ios_1/origin.conf tests/data/ios_1/target.conf ios
```

The script returns an ordered list of commands that can be applied to the network equipment in order to achieve the target configuration state.

Requirements
============
netcompare uses the awesome David Michael Pennington's CiscoConfParse library to parse the configuration files.
More information in [CiscoConfParse](http://www.pennington.net/py/ciscoconfparse/) documentation.
It also uses pyyaml library.
Be sure to install these before using netcompare:

```
    pip install ciscoconfparse
    pip install pyyaml
```

Documentation
=============
(Minimalist) documentation will be available on [Read the Docs](http://netcompare.readthedocs.org) soon.

Todo
=============
A lot of things !
 * Ansible library and playbook example
 * Find a way to do changes in one command instead of two (like ip address or hostname changes)
 * Handle banner changes (and all multiline commands with delimiters)

Pull requests are warmly welcome :)

Authors
=======
 * François Fanuel ([f.fanuel@criteo.com](mailto:f.fanuel@criteo.com))
 * Cédric Paillet ([c.paillet@criteo.com](mailto:c.paillet@criteo.com))
