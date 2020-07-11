#!/bin/bash

pwd
ls

if [ "${DEBUG}x" != "x" ]; then
  echo '*******************************DEBUG mode*******************************'
  pip uninstall -y myapp
  pip install -e .
fi

# TODO: cleanup pyc

gosu myapp "$@"
