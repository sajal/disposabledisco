disposabledisco
===============

Helper scripts to launch disposable Disco clusters for map/reduce tasks using EC2 spot instances

Project Scope
=============

1. Ability to launch/reconfigure Disco clusters on the whim.
2. Use cheaper AWS spot instances.
3. Don't care about permanent storage in DDFS. Instead we use S3 or something else.
4. Being able to (re)configure number of slaves and instance types.
5. Using only Official Ubuntu Cloud Guest Amazon Machine Images (AMIs) - http://cloud.ubuntu.com/ami/
6. Probably will use Instance store, since Map/Reduce is supposed to be more CPU bound than IO bound.

Dependencies
============

1. boto
2. paramiko

Usage
=====

1. Create config file with some defaults

```bash
   $ python create_config.py > config.json
```
2. Edit config file based on Appendix below

3. Run this script many times to take care of pending tasks.

```bash
   $ python create_cluster.py config.json
```

Appendix
========

<table>
<tr><td>Name</td><td>Required?</td><td>Note</td></tr>
<tr><td>BASE_PACKAGES</td><td>Yes</td><td>Do not override.</td></tr>
<tr><td>ADDITIONAL_PACKAGES</td><td>Yes</td><td>Additional packages to be installed using apt-get</td></tr>
<tr><td>PIP_REQUIREMENTS</td><td>Yes</td><td>Packages installed via pip. run after all apt-get tasks</td></tr>
<tr><td>AWS_ACCESS</td><td>Yes</td><td>REQUIRED. Your AWS access key</td></tr>
<tr><td>AWS_SECRET</td><td>Yes</td><td>REQUIRED. Your AWS secret key</td></tr>
<tr><td>AMI</td><td>Yes</td><td>What AMI to use. Hint: http://cloud.ubuntu.com/ami/ </td></tr>
<tr><td>MAX_BID</td><td>Yes</td><td>How much to bid for each instance.</td></tr>
<tr><td>INSTANCE_TYPE</td><td>Yes</td><td>What instance type to use?</td></tr>
<tr><td>MASTER_INSTANCE_TYPE</td><td>No</td><td>Defaults to INSTANCE_TYPE</td></tr>
<tr><td>SLAVE_INSTANCE_TYPE</td><td>No</td><td>Defaults to INSTANCE_TYPE</td></tr>
<tr><td>KEY_NAME</td><td>Yes</td><td>The key name in EC2 console. To be able to login as ubuntu user for debugging</td></tr>
<tr><td>SECURITY_GROUPS</td><td>Yes</td><td>At-least 1 security group needed. Settings example next section.</td></tr>
<tr><td>MGMT_KEY</td><td>Yes</td><td>Public key(s) that is added on instances. Set this as your public keys. Multiple seperated by newline.</td></tr>
<tr><td>TAG_KEY</td><td>Yes</td><td>key used for tagging. If you are making multiple clusters, then make these ubique</td></tr>
<tr><td>NUM_SLAVES</td><td>Yes</td><td>Number of slaves</td></tr>
<tr><td>MASTER_MULTIPLIER</td><td>No</td><td>Ratio of workers compared to cores in master</td></tr>
<tr><td>SLAVE_MULTIPLIER</td><td>No</td><td>Ratio of workers compared to cores in each slave</td></tr>
<tr><td>POST_INIT</td><td>No</td><td>Bash scripts, runs as root after rest of the initialization</td></tr>
</table>

Security Group
==============

1. Allow all udp, tcp traffic from within the group on all ports.
2. Allow ssh from 0.0.0.0/0 ... or atleast from your workstation.


TODO
====

1. Ability to select region. Currently it is hardcoded to default (us-east)
2. Specify different instance types with counts for slaves.
3. Ability to stop unresponsive slaves.
4. Ability to scale down cluster based on config changes. It can already scale up.
5. Make pip installable, so that we can install it globally, and keep config file inside relavent project directories.
