#! /usr/bin/bash



echo "Starting init script"

./manage.py init_setup

echo "Starting ropon wagtail server"

./manage.py runserver 0.0.0.0:8000
