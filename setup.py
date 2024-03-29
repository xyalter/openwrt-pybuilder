import sys

from setuptools import find_packages
from setuptools import setup
from setuptools.command.test import test as TestCommand

version = '0.2.0'

install_requires = [
    'invoke',
    'setuptools'
]

docs_extras = [
    'Sphinx>=1.0',  # autodoc_member_order = 'bysource', autodoc_default_flags
    'sphinx_rtd_theme',
]

setup(
    name='openwrt-pybuilder',
    version=version,
    description="OpenWrt build tools by Python3",
    url='https://github.com/xxy1991/openwrt-pybuilder',
    author="xxy1991",
    author_email='xxy1991@gmail.com',
    license='AGPL 3.0',
    python_requires='>=3.7',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Plugins',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Security',
        'Topic :: System :: Installation/Setup',
        'Topic :: System :: Networking',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities',
    ],

    packages=find_packages(exclude=['tests', 'private*']),
    package_data={'openwrt_pybuilder': ['resources/templates/**/*']},
    include_package_data=True,
    install_requires=install_requires,
    extras_require={
        'docs': docs_extras,
    },
    test_suite='openwrt_pybuilder',
)
