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
