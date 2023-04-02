#!/bin/bash

export PYTHONPATH=/app

if [[ "$1" = 'api' ]]
then
  set -- "gunicorn --workers 1 --bind :8080 crms.app:create_app()"
fi
exec $@
