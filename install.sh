#!/bin/bash

set -e

# Install package requirements
sudo -H pip install --ignore-installed -U -r requirements.txt
