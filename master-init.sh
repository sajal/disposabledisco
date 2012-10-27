#!/bin/bash
# == Fresh install script (Master)==

apt-get -y update
apt-get -y upgrade


apt-get -y install --PACKAGES--

echo "
deb http://discoproject.org/debian /
" >> /etc/apt/sources.list

apt-get -y update
apt-get -y --force-yes install disco-master python-disco

--PIP--

#Run these as disco user
su - disco -c "ssh-keygen -N '' -f ~/.ssh/id_dsa"
su - disco -c "cat ~/.ssh/id_dsa.pub >> ~/.ssh/authorized_keys"
#Add management key so we can ssh in
su - disco -c "echo \"--PUBKEY--\" >> ~/.ssh/authorized_keys"

#accpet and add key
su - disco -c "ssh -oStrictHostKeyChecking=no localhost uptime"

#back to root
mkdir /mnt/disco
chown disco:disco /mnt/disco

#edit config...
disco stop

echo "
DISCO_ROOT = \"/mnt/disco\"

DISCO_DATA = \"/mnt/disco/data\"
DISCO_LOG_DIR = \"/mnt/disco/log\"
DISCO_GC_AFTER = 6400
DISCO_PROXY_ENABLED = \"on\"
" >> /etc/disco/settings.py

disco start
#restart....

#post init...

--POST_INIT--