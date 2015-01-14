#!/usr/bin/env bash

# For some reasons the tests want this.
mkdir -p ~/.gnupg
cd /home/vagrant/debexpo/
sudo apt-get update
sudo apt-get install postfix python-lxml libapt-pkg-dev python-pip python-dev python-virtualenv --yes
sudo apt-get build-dep python-lxml --yes
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
