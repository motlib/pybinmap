#!/usr/bin/env python

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='pybinmap',
    version='0.0-dev1',
    description='PyBinMap helps to interpret binary data blobs.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Andreas Schroeder',
    author_email='andreas@a-netz.de',
    url='https://github.com/motlib/pybinmap',
    packages=['pybinmap'],
)
