#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
from typing import List

from invoke import run, Context

TEMPLATE_KEEP_PATH = os.path.abspath(os.path.dirname(__file__))
TEMPLATE_KEEP_PATH = os.path.abspath(os.path.join(
    TEMPLATE_KEEP_PATH, '../resources/templates/keepalived'))


def cp_keepalived(dst_path):
    if dst_path is None:
        raise RuntimeError('Destination path is required!')

    run(f'cp -r {TEMPLATE_KEEP_PATH}/files {dst_path}/')
    run(f'chmod +x {dst_path}/files/etc/uci-defaults/99_keepalived.sh')


def copy_func(dst_path):
    cp_keepalived(dst_path)


# need kmod-ipt-ipset, provide by default
def get_packages() -> List[str]:
    with open(f"{TEMPLATE_KEEP_PATH}/config.json", 'r') as load_f:
        config = json.load(load_f)
    return config['packages']


def get_disabled_services() -> List[str]:
    with open(f"{TEMPLATE_KEEP_PATH}/config.json", 'r') as load_f:
        config = json.load(load_f)
    return config['disabled_services']