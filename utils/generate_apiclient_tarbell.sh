#!/usr/bin/env bash

# Copyright 2012-2013 John Sullivan
# Copyright 2012-2013 Other contributors as noted in the CONTRIBUTORS file
#
# This file is part of Galah.
#
# Galah is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Galah is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Galah.  If not, see <http://www.gnu.org/licenses/>.

# This will ensure that the script exits if a failure occurs
set -e

# This will ensure the user is visually prompted upon failure
trap "echo FAILURE: An error has occured! >&2" EXIT

STARTING_DIR=`pwd`

# Create a temporary build directory that we'll construct the contents of our
# tarbell within.
BUILD_DIR=`mktemp -d`
echo "Created build directory at $BUILD_DIR"

# Copy the actual api client to the directory
cp ./api_client.py $BUILD_DIR/
echo "Copied api_client.py into build directory."

# Build all of the man pages for the api commands
MAN_DIR=`mktemp -d`
sphinx-build -q -b man ../docs/src/galah.api/ $MAN_DIR
cd $MAN_DIR
for f in `ls`
do
	gzip $f
done
mkdir -p $BUILD_DIR/man/man1/
mv *.gz $BUILD_DIR/man/man1/
cd $BUILD_DIR
rm -rf $MAN_DIR
echo "Built all of the man pages."

# Download the required requests package and move it into the build directory
REQUESTS_DIR=`mktemp -d`
cd $REQUESTS_DIR
wget -qO - https://github.com/kennethreitz/requests/tarball/develop | tar xz
mv `find . -name requests` $BUILD_DIR/
cd $BUILD_DIR
rm -rf $REQUESTS_DIR
echo "Downloaded and untarred requests package"

# Create the final tarbell
cd $BUILD_DIR
tar -zcf $STARTING_DIR/api_client.tar.gz *
echo "Created tarbell api_client.tar.gz in $STARTING_DIR"

# Clean up anything left over
rm -rf $BUILD_DIR


# Unset the trap so we don't freak the user out by telling them an error has
# occured when everything went fine.
trap - EXIT
