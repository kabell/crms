#!/bin/bash

export PYTHONPATH=/app
export FLASK_APP="crms.app:create_app()"

if [[ "$1" = 'api' ]]
then
  flask db upgrade
  set -- "gunicorn --workers 1 --bind :8080 crms.app:create_app()"
fi
exec $@
