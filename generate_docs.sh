#!/usr/bin/env bash

# This will ensure that the script exits if a failure occurs
set -e

# This will ensure the user is visually prompted upon failure
trap "echo FAILURE: An error has occured! >&2" EXIT

# The directory that will contain all of the generated documentation
DOCS_PATH=./docs

## Create the API documentation for shell users ################################
echo Building API documentation...

sphinx-build -q -a -b man ./docs/src/galah.api/ $DOCS_PATH

echo "SUCCESS: MAN page 'galah.api.commands.1' created in $DOCS_PATH"

# Unset the trap so we don't freak the user out by telling them an error has
# occured when everything went fine.
trap - EXIT