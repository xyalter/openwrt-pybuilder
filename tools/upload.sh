#!/usr/bin/env bash

rm -rf dist/*
# python3 setup.py sdist bdist_wheel
python3 -m build
#twine upload dist/*
