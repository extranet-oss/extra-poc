#!/bin/bash

DIR=$(dirname "$(readlink -f "$0")")

# Try to execute a `return` statement,
# but do it in a sub-shell and catch the results.
# If this script isn't sourced, that will raise an error.
$(return >/dev/null 2>&1)
if ! [ "$?" -eq "0" ]; then
  echo "Please type: source $0"
  exit 1
fi

# load virtual environment
if ! [ -v VIRTUAL_ENV ]; then
  source "$DIR/venv/bin/activate"
else
  echo "VirtualEnv already activated."
fi

# setup environment variables
export FLASK_DEBUG=1
export FLASK_APP="$DIR/app.py"
