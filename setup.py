#!/usr/bin/python
"""Docstrings"""
from setuptools import setup, find_packages

VERSION = "0.1.65"

setup(
    name="ramrodbrain",
    version=VERSION,
    packages=find_packages(),
    description='RethinkDB Wrapper functions',
    author='Dan Bauman',
    maintainer='Dan Bauman',
    maintainer_email='dan@bauman.space',
    license='MIT',
    url='https://github.com/ramrod-project/database-brain',
    download_url='https://github.com/ramrod-project/python-brain/archive/ramrodbrain-{}.tar.gz'.format(VERSION),
    install_requires=[
        'rethinkdb',
        "protobuf",
        "dict-to-protobuf",
        "decorator",
        "python-magic"
    ],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ],
)
