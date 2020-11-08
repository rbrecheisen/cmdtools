#!/usr/bin/env bash

export PYTHONPATH=${HOME}/dev/cmdtools:${PYTHONPATH}

cd cmdtools/${1}/test

pytest
