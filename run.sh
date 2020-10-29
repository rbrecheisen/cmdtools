#!/usr/bin/env bash

export PYTHONPATH=${HOME}/dev/cmdtools:${PYTHONPATH}

export PYTHON=${HOME}/.virtualenvs/research/bin/python

cd cmdtools/${1}

${PYTHON} ${1}.py
