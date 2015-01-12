#!/usr/bin/env bash

cd /home/vagrant/debexpo/
sudo apt-get update
sudo apt-get install python-lxml libapt-pkg-dev python-pip python-dev python-virtualenv --yes
sudo apt-get build-dep python-lxml --yes
virtualenv venv
. venv/bin/activate
pip install https://launchpad.net/python-apt/main/0.7.8/+download/python-apt-0.8.5.tar.gz
pip install --editable .
python setup.py develop
paster setup-app development.ini
python setup.py compile_catalog
