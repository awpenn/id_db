#!/bin/bash
#This script will install all the dependencies required to run the adsp id generation and database loading script.
parentdir="$(dirname "$(pwd)")"

sudo apt-get install python-pip
sudo apt-get install python3-pip

pip install -U pip
pip install setuptools
pip install virtualenv

cd $parentdir/id_db
virtualenv -p python3 .venv 
source $parentdir/id_db/.venv/bin/activate

pip install -r requirements.txt
deactivate

echo "Installation complete.  Please create a .env file with database connection information, and configure input/output directory information in adspid-csv.py before running the script."