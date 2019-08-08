#!/usr/bin/env python
from setuptools import setup, find_packages

import re
import sys
import os

BASE_LOCATION = os.path.abspath(os.path.dirname(__file__))

VERSION_FILE = os.path.join(BASE_LOCATION, "src", "ustubby", "__init__.py")
REQUIRES_FILE = 'requirements.txt'
DEPENDENCIES_FILE = None


def filter_comments(fd):
    no_comments = list(filter(lambda l: l.strip().startswith("#") is False, fd.readlines()))
    return list(filter(lambda l: l.strip().startswith("-") is False, no_comments))


def readfile(filename, func):
    try:
        with open(os.path.join(BASE_LOCATION, filename)) as f:
            data = func(f)
    except (IOError, IndexError):
        sys.stderr.write(u"""
Can't find '%s' file. This doesn't seem to be a valid release.
""" % filename)
        sys.exit(1)
    return data


def get_version():
    with open(VERSION_FILE, 'r') as f:
        data = f.read()
        m = re.search(r"__version__ ?= ?\"[\d.]+\"", data)
    res = m.group(0)
    if res:
        ret = re.search(r"(?<=\")[\d\.]+", res).group(0)
        if ret:
            return ret
    raise ValueError("No version for ustubby found")


def get_requires():
    return readfile(REQUIRES_FILE, filter_comments)


def get_dependencies():
    return readfile(DEPENDENCIES_FILE, filter_comments)


setup(
    name="ustubby",
    author="Ryan Parry-Jones",
    author_email="ryanspj+github@gmail.com",
    description="Micropython c stub generator",
    long_description=open("README.md").read(),
    package_dir={'': 'src'},
    packages=find_packages('src'),
    url="https://github.com/pazzarpj/micropython-ustubby",
    version=get_version(),
    python_requires='>=3.6',
    dependency_links=[],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Manufacturing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
)
