#!/usr/bin/env bash

export PYTHONPATH=${HOME}/dev/cmdtools:${PYTHONPATH}

cd cmdtools/${1}

python ${1}.py
