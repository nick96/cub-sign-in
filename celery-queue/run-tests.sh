#!/usr/bin/env bash
pip install -q -r requirements.txt
celery worker --loglevel=ERROR -A tasks
