#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
from typing import List

from invoke import run, Context

TEMPLATE_BASE_PATH = os.path.abspath(os.path.dirname(__file__))
TEMPLATE_BASE_PATH = os.path.abspath(os.path.join(
    TEMPLATE_BASE_PATH, '../resources/templates/base'))


def cp_base(dst_path):
    if dst_path is None:
        raise RuntimeError('Destination path is required!')

    run(f'cp -r {TEMPLATE_BASE_PATH}/files {dst_path}/')
    run(f'cp {TEMPLATE_BASE_PATH}/custom-*.sh {dst_path}/')
    run(f'chmod +x {dst_path}/files/etc/board.d/99-custom_*.sh \
                {dst_path}/files/etc/uci-defaults/99_custom-*.sh \
                {dst_path}/custom-base.sh')


def copy_func(dst_path):
    cp_base(dst_path)


def get_packages() -> List[str]:
    with open(f"{TEMPLATE_BASE_PATH}/config.json", 'r') as load_f:
        config = json.load(load_f)
    return config['packages']


def get_disabled_services() -> List[str]:
    with open(f"{TEMPLATE_BASE_PATH}/config.json", 'r') as load_f:
        config = json.load(load_f)
    return config['disabled_services']
