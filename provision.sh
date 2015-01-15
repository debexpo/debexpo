#!/usr/bin/env bash

# For some reasons the tests want this.
set -e
mkdir -p ~/.gnupg
cd /home/vagrant/debexpo/
if ! grep -q backports /etc/apt/sources.list; then
    echo 'deb http://http.debian.net/debian/ wheezy-backports main contrib non-free' | sudo sh -c 'cat >> /etc/apt/sources.list'
fi
export DEBIAN_FRONTEND=noninteractive
sudo debconf-set-selections <<< "postfix postfix/main_mailer_type string 'Internet Site'"
sudo debconf-set-selections <<< "postfix postfix/mailname string debexpo-dev"
sudo apt-get update
sudo apt-get install postfix python-lxml libapt-pkg-dev python-pip python-dev python-virtualenv --yes
sudo apt-get install --yes python-fedmsg -t wheezy-backports
sudo apt-get build-dep --yes python-lxml
echo '* discard:' | sudo sh -c 'cat > /etc/postfix/discard-transport'
if ! grep -q transport_maps /etc/postfix/main.cf; then
    echo 'transport_maps = hash:/etc/postfix/discard-transport' | sudo sh -c 'cat >> /etc/postfix/main.cf'
fi
sudo postmap /etc/postfix/discard-transport
sudo service postfix restart
virtualenv venv
. venv/bin/activate
pip install https://launchpad.net/python-apt/main/0.7.8/+download/python-apt-0.8.5.tar.gz
pip install --editable .
paster setup-app development.ini
python setup.py compile_catalog
