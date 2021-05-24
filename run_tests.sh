#!/bin/bash

echo $#
echo $0
echo $1

if [ $# -lt 1 ];
then
    python3 -m unittest discover "./tests/"
else
    python3 -m unittest $1
fi