#!/bin/bash

DIR=$(dirname "$(readlink -f "$0")")

# Setup environment
source "$DIR/setup.sh"

# Execute command
flask "$@"
