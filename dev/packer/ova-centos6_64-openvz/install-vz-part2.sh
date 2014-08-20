#!/usr/bin/env bash

# This will echo every line
set -x

yum -y remove kernel
yum -y update
yum -y clean all
