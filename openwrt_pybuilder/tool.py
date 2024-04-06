#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Time    : 2020-10-23 14:17
@Author  : xxy1991
@Email   : xxy1991@gmail.com
"""

import sys

from invoke import run


def build():
    run('docker build -t xxy1991/openwrt:imagebuilder .')


def get_package():
    run('docker pull xxy1991/openwrt:imagebuilder')
    run('docker run -d -i --name openwrt-imagebuilder xxy1991/openwrt:imagebuilder')

    FILE_NAME = 'openwrt-imagebuilder-19.07.7-x86-64.Linux-x86_64.tar.xz'

    run(f'docker cp openwrt-imagebuilder:"/data/{FILE_NAME}" .')
    run('docker container stop openwrt-imagebuilder')
    run('docker container rm openwrt-imagebuilder')


def info():
    print('Please execute with a option:')
    print('build - manual build at local.')
    print('getpack - download openwrt-imagebuilder package in docker image.')


if __name__ == "__main__":
    if sys.argv[1] is 'build':
        build()
    elif sys.argv[1] is 'getpack':
        get_package()
    else:
        info()
