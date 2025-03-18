#!/bin/bash
pip install -r beacon_project/requirements.txt
python beacon_project/beacon_project/manage.py collectstatic --noinput
python beacon_project/beacon_project/manage.py migrate