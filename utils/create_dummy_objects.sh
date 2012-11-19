#!/usr/bin/env bash

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
