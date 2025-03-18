#!/bin/bash
pip install -r requirements.txt
python beacon_project/manage.py collectstatic --noinput
python beacon_project/manage.py migrate