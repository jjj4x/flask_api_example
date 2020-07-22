#!/bin/bash

pwd

if [ -d "./src" ]; then
  find ./src -regex '^.*\(__pycache__\|\.py[co]\)$' -delete
fi

exec "$@"
