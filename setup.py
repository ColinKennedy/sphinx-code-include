#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""The main module that sets up this repository as a Python/PyPI package."""

from __future__ import absolute_import
from __future__ import print_function

import io
import re
from glob import glob
from os.path import basename
from os.path import dirname
from os.path import join
from os.path import splitext

from setuptools import find_packages
from setuptools import setup


def read(*names, **kwargs):
    """str: Get the text of whatever file path is given."""
    with io.open(
        join(dirname(__file__), *names), encoding=kwargs.get("encoding", "utf8")
    ) as handler:
        return handler.read()


setup(
    name="sphinx-code-include",
    version="1.1.1",
    license="BSD-2-Clause",
    description="Include source code from any Sphinx project using only its import path",
    long_description="%s\n%s"
    % (
        re.compile("^.. start-badges.*^.. end-badges", re.M | re.S).sub(
            "", read("README.rst")
        ),
        re.sub(":[a-z]+:`~?(.*?)`", r"``\1``", read("CHANGELOG.rst")),
    ),
    author="Colin Kennedy",
    author_email="colinvfx@gmail.com",
    url="https://github.com/ColinKennedy/sphinx-code-include",
    packages=find_packages("src"),
    package_dir={"": "src"},
    py_modules=[splitext(basename(path))[0] for path in glob("src/*.py")],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        # complete classifier list: http://pypi.python.org/pypi?%3Aaction=list_classifiers
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: Unix",
        "Operating System :: POSIX",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Utilities",
    ],
    project_urls={
        "Documentation": "https://sphinx-code-include.readthedocs.io/",
        "Changelog": "https://sphinx-code-include.readthedocs.io/en/latest/changelog.html",
        "Issue Tracker": "https://github.com/ColinKennedy/sphinx-code-include/issues",
    },
    keywords=[
        "Sphinx", "code-include", "source-code", "source code", "include",
    ],
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*",
    install_requires=[
        read("requirements.txt").splitlines(),
    ],
    extras_require={
    },
)
