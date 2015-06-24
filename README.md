netcompare
==========
netcompare is a python script that compares two Cisco IOS style's configuration files for a single network device (one origin and one target). It returns an ordered list of commands that can be applied to the network equipment in order to achieve the target configuration state.
It's like a "diff" on steroids, which takes care of command's parent / child relationships.
This script has been written with network configuration automation in mind, for crappy network equipments that does not support atomic changes.

Known to work with
------------------
 * Cisco IOS
 * Cisco NXOS
 * Cisco ASA
 * Dell FTOS
 * Huawei VRP

It can also work with these platforms (but they support -at least partially- atomic changes, so there's a better way):
 * Arista EOS
 * Cisco IOS XR

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
 * The negation keyword used by your platform. Cisco IOS, NXOS, IOS-XR, ASA uses "no", Huawei uses "undo" for example
 ``
    python netcompare.py tests/sample1.conf tests/sample2.conf no
 ``
The script returns an ordered list of commands that can be applied to the network equipment in order to achieve the target configuration state.

Requirements
============
netcompare uses the awesome David Michael Pennington's CiscoConfParse library to parse the configuration files.
More information in [CiscoConfParse](http://www.pennington.net/py/ciscoconfparse/) documentation.
Be sure to install it before using netcompare:
``
   pip install ciscoconfparse
``

Documentation
=============
(Minimalist) documentation is available on [Read the Docs](http://netcompare.readthedocs.org)

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
