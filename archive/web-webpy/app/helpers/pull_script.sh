#!/bin/bash

git init
git remote add student_repo $1
git fetch student_repo
git add --all
git commit -m "Uploaded from Web Interface"
git merge -s ours student_repo/master
git push student_repo

# Hack to delete the current working directory
pwd | xargs rm -r
