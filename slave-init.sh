#!/bin/bash
# == Fresh install script (Master)==

apt-get -y update
apt-get -y upgrade


apt-get -y install --PACKAGES--

echo "
deb http://discoproject.org/debian /
" >> /etc/apt/sources.list

apt-get -y update
apt-get -y --force-yes install disco-node python-disco

--PIP--

#Run these as disco user
su - disco -c "ssh-keygen -N '' -f ~/.ssh/id_dsa"
su - disco -c "cat ~/.ssh/id_dsa.pub >> ~/.ssh/authorized_keys"

#Add management key so we can ssh in
su - disco -c "echo \"--PUBKEY--\" >> ~/.ssh/authorized_keys"

#back to root
mkdir /mnt/disco
chown disco:disco /mnt/disco

#Add Master's key so it can ssh in
su - disco -c "echo \"--MASTERPUBKEY--\" >> ~/.ssh/authorized_keys"

#status checks...