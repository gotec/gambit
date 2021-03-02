#!/usr/bin/env python
# -*- coding: utf-8 -*-

import setuptools
from gambit import __version__

with open("README.md", "r") as f:
    long_description = f.read()

with open('requirements.txt') as f:
    install_requirements = f.read().splitlines()

setuptools.setup(
    name="gambit-disambig",
    version=__version__,
    author="Christoph Gote",
    author_email="cgote@ethz.ch",
    license='AGPL-3.0+',
    description="An Open Source name disambiguation tool for version control systems",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/gotec/gambit',
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Operating System :: OS Independent"
    ],
    keywords='alias disambiguation repository mining version control system',
    install_requires=install_requirements,
)
