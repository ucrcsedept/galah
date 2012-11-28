#!/usr/bin/env bash

# Copyright 2012 John Sullivan
# Copyright 2012 Other contributers as noted in the CONTRIBUTERS file
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

API_CLIENT=./api_client.py

mkdir -p ./user-files/data/

echo "email,password" > ./user-files/data/test_users.csv

# Create the test class
$API_CLIENT create_class "test_class"

# Create the requested assignments
for (( i=1; i <= $2; i++ ))
do
    $API_CLIENT create_assignment "test_assignment_$i" "10/20/2014 10:09:00" "test_class"
done

# Create the requested users
for (( i=1; i <= $1; i++ ))
do
    $API_CLIENT create_user "test_student_$i@testing.edu" "muffin"
    $API_CLIENT enroll_student "test_student_$i@testing.edu" "test_class"
    echo "test_student_$i@testing.edu,muffin" >> ./user-files/data/test_users.csv
done

# Unset the trap so we don't freak the user out by telling them an error has
# occured when everything went fine.
trap - EXIT
