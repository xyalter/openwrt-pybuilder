#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Time    : 2020-08-31 21:52
@Author  : xxy1991
@Email   : xxy1991@gmail.com
"""

from __future__ import annotations

import argparse
import copy
import json
import logging
from functools import cmp_to_key
from pathlib import Path
from typing import Callable, List

from invoke import run


def __cmp_func(src: List[str]) -> Callable[[str, str], int]:
    def func(x: str, y: str) -> int:
        # if x.startswith('-') and not y.startswith('-'):
        #     return -1
        # if y.startswith('-') and not x.startswith('-'):
        #     return 1
        return src.index(x) - src.index(y)

    return func


def _merge(x: List[str], y: List[str]) -> List[str]:
    merged = x + y
    return sorted(set(merged), key=cmp_to_key(__cmp_func(merged)))


def _remove_reverse(x: List[str]) -> List[str]:
    result = list(x)
    remove_items = []
    for item in result:
        if item.startswith('-'):
            remove_items.append(item[1:])
    for item in remove_items:
        if item in result:
            result.remove(item)
            result.remove('-' + item)
    return result


class Config(object):
    def __init__(self, path: Path = None):
        """Constructor"""
        data = dict(
            name=None,
            version='23.05.3',
            arch='x86',
            board='64',
            env_list=None,
            includes=[],
            packages=[],
            files=[],
            disabled_services=[]
        )
        self._data = data
        self.load(path)

    def load(self, path: Path):
        if path is None:
            return
        if not path.is_file():
            return
        json_doc = json.loads(path.read_text())
        if 'name' in json_doc:
            self._data['name_'] = json_doc['name']
        if 'version' in json_doc:
            self._data['version'] = json_doc['version']
        if 'arch' in json_doc:
            self._data['arch'] = json_doc['arch']
        if 'board' in json_doc:
            self._data['board'] = json_doc['board']
        if 'env-file' in json_doc:
            self._data['env_file'] = json_doc['env-file']
        if 'includes' in json_doc:
            self._data['includes'] = json_doc['includes']
        if 'packages' in json_doc:
            self._data['packages'] = _remove_reverse(_merge(self.packages,
                                                            json_doc['packages']))
        if 'files' in json_doc:
            self._data['files'] = _merge(self.files, json_doc['files'])
        if 'disabled_services' in json_doc:
            self._data['disabled_services'] = _merge(self.disabled_services,
                                                     json_doc['disabled_services'])
        if len(self.includes) <= 0:
            return

        def map_files(root_path: Path, sub_path: Path) -> Callable[[str], str]:
            def _(x: str) -> str:
                if x.startswith(str(root_path)):
                    return x
                new_path = str(sub_path.joinpath(x))
                if x.endswith('/') and not new_path.endswith('/'):
                    new_path += '/'
                return new_path

            return _

        templates_path = Path(__file__).parent.joinpath('resources/templates')
        templates_config = Config()
        for template in self.includes:
            template_path = templates_path.joinpath(f'{template}')
            template_json_path = template_path.joinpath('config.json')
            if template_json_path.exists():
                template_config = Config(template_json_path)
                template_config.files = list(map(
                    map_files(templates_path, template_path),
                    template_config.files))
                templates_config.merge(template_config)
                logging.debug(f'{template}:{templates_config.packages}')
        self.merge(templates_config, True)
        logging.debug(f'self:{self.packages}')

    def merge(self, other: Config, reverse=False) -> None:
        prior = self
        next_ = other
        if reverse:
            prior = other
            next_ = self
        self.packages = _remove_reverse(_merge(prior.packages,
                                               next_.packages))
        self.files = _merge(prior.files, next_.files)
        self.disabled_services = _merge(prior.disabled_services,
                                        next_.disabled_services)

    def __add__(self, other: Config) -> Config:
        config = copy.deepcopy(self)
        config.merge(other)
        return config

    @property
    def name(self) -> str:
        return self._data['name_']

    @name.setter
    def name(self, value: str) -> None:
        self._data['name_'] = value

    @property
    def version(self) -> str:
        return self._data['version']

    @version.setter
    def version(self, value: str) -> None:
        self._data['version'] = value

    @property
    def arch(self) -> str:
        return self._data['arch']

    @arch.setter
    def arch(self, value: str) -> None:
        self._data['arch'] = value

    @property
    def board(self) -> str:
        return self._data['board']

    @board.setter
    def board(self, value: str) -> None:
        self._data['board'] = value

    @property
    def env_file(self) -> str:
        return self._data['env_file']

    @env_file.setter
    def env_file(self, value: str) -> None:
        self._data['env_file'] = value

    @property
    def includes(self) -> List[str]:
        return self._data['includes']

    @includes.setter
    def includes(self, value: List[str]) -> None:
        self._data['includes'] = value

    @property
    def packages(self) -> List[str]:
        return self._data['packages']

    @packages.setter
    def packages(self, value: List[str]) -> None:
        self._data['packages'] = value

    @property
    def files(self) -> List[str]:
        return self._data['files']

    @files.setter
    def files(self, value: List[str]) -> None:
        self._data['files'] = value

    @property
    def disabled_services(self) -> List[str]:
        return self._data['disabled_services']

    @disabled_services.setter
    def disabled_services(self, value: List[str]) -> None:
        self._data['disabled_services'] = value

    def to_dict(self) -> dict:
        return self._data


class OpenwrtImageBuilder(object):
    def __init__(self, config: Config):
        """Constructor"""
        if config is None:
            raise RuntimeError('Config is required!')
        self._config = config

    @property
    def config(self) -> Config:
        return self._config

    def _check_image_name(self) -> None:
        if self.config.name is None:
            raise RuntimeError("Image name is required!")

    def copy_files(self, dst_path: str) -> None:
        if dst_path is None:
            raise RuntimeError('Destination path is required!')
        for src_path in self.config.files:
            src_path_obj = Path(src_path)
            if not src_path_obj.exists():
                raise RuntimeError(f'Source path: {src_path} must exists!')
            if src_path_obj.is_dir():
                run(f'cp -r {src_path} {dst_path}/')
            elif src_path_obj.is_file():
                run(f'cp {src_path} {dst_path}/')

    def build_docker(self):
        self._check_image_name()
        image_name = self.config.name
        run(f'docker build -t openwrt:{image_name} ./{image_name}-temp')

    def build_image(self):
        self._check_image_name()
        image_name = self.config.name
        if self.config.env_file is None:
            raise RuntimeError("Env file is required!")
        env_file = self.config.env_file

        packages = f"PACKAGES={' '.join(self.config.packages)}"
        files = 'FILES=files/'
        disabled_services = f"DISABLED_SERVICES={' '.join(self.config.disabled_services)}"
        args = f'"{packages}" "{files}" "{disabled_services}"'

        bin_path = Path(f'./{image_name}-bin')
        if not bin_path.exists():
            bin_path.mkdir()

        cache_path = Path('./cache')
        if not cache_path.exists():
            cache_path.mkdir()

        run(f'docker run --name openwrt-{image_name} '
            + f'--env-file {env_file} '
            + f'--mount type=bind,source="$(pwd)"/{image_name}-bin,target=/home/build/openwrt/bin '
            + f'--mount type=bind,source="$(pwd)"/cache,target=/home/build/openwrt/dl '
            + f'openwrt:{image_name} {args}')

    @property
    def base_dir(self) -> str:
        base_dir = f'/home/build/openwrt'
        return f'{base_dir}/bin/targets/{self.config.arch}/{self.config.board}'

    @property
    def file_name(self) -> str:
        return f'openwrt-{self.config.version}-{self.config.arch}-{self.config.board}'

    @property
    def rootfs_name(self) -> str:
        return f'{self.file_name}-generic-rootfs.tar.gz'

    @property
    def squashfs_name(self) -> str:
        return f'{self.file_name}-combined-squashfs.img.gz'

    @property
    def ext4_vmdk_name(self) -> str:
        return f'{self.file_name}-combined-ext4.vmdk'

    def cp_target(self, remote_path: str = None, file_path: str = None):
        self._check_image_name()
        image_name = self.config.name
        if remote_path is None:
            raise RuntimeError("Remote path is required!")
        if file_path is None:
            raise RuntimeError("File path is required!")
        run(f'docker cp openwrt-{image_name}:"{remote_path}" "{file_path}"')

    def cp_rootfs(self, file_path: str = None):
        self._check_image_name()
        image_name = self.config.name
        remote_path = f'{self.base_dir}/{self.rootfs_name}'
        if file_path is None:
            file_path = f'{image_name}.tar.gz'
        self.cp_target(remote_path, file_path)

    def cp_squashfs_img(self, file_path: str = None):
        self._check_image_name()
        image_name = self.config.name
        remote_path = f'{self.base_dir}/{self.squashfs_name}'
        if file_path is None:
            file_path = f'{image_name}-squashfs-combined.img.gz'
        self.cp_target(remote_path, file_path)

    def cp_squashfs_qcow2(self):
        self._check_image_name()
        image_name = self.config.name
        self.cp_squashfs_img()
        file_name = f'{image_name}-squashfs-combined.img.gz'
        run(f'gunzip {file_name}')
        file_name = Path(file_name).stem
        run(f'qemu-img resize -f raw {file_name} 300M')
        run(f'qemu-img convert -f raw -O qcow2 {file_name} {image_name}.qcow2')
        run(f'mv {file_name} {image_name}.img')
        run(f'rm -f {image_name}.img.gz')
        run(f'gzip {image_name}.img')

    def cp_ext4_img(self, file_path: str = None):
        self._check_image_name()
        image_name = self.config.name
        remote_path = f'{self.base_dir}/{self.squashfs_name}'
        if file_path is None:
            file_path = f'{image_name}-ext4.img.gz'
        self.cp_target(remote_path, file_path)

    def cp_ext4_vmdk(self, file_path: str = None):
        self._check_image_name()
        image_name = self.config.name
        remote_path = f'{self.base_dir}/{self.ext4_vmdk_name}'
        if file_path is None:
            file_path = f'{image_name}-ext4.vmdk'
        self.cp_target(remote_path, file_path)

    def cp_all(self):
        self._check_image_name()
        image_name = self.config.name
        remote_path = self.base_dir
        file_path = f'{image_name}-output/'
        self.cp_target(remote_path, file_path)

    def remove_instance(self):
        self._check_image_name()
        image_name = self.config.name
        run(f'docker container stop openwrt-{image_name}')
        run(f'docker container rm openwrt-{image_name}')


def get_args(args=None):
    parser = argparse.ArgumentParser(description='OpenWRT image builder.')
    parser.add_argument('image name', help="the image's name")
    parser.add_argument('-V', help="the distribution's major version")
    parser.add_argument('-C', '--config', help='config file path')
    parser.add_argument('-M', '--manual', action="store_true", help='manual mode')

    if args is not None:
        return parser.parse_args(args)
    return parser.parse_args()
