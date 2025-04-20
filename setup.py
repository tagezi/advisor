#!/usr/bin/env python
#     This code is a part of program Advisor
#     Copyright (C) 2022 contributors Advisor
#     The full list is available at the link
#     https://github.com/tagezi/advisor/blob/master/contributors.txt
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""This module contains setup instructions for MIL."""
import codecs
import os

from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

with open(os.path.join(here, "advisor", "version.py")) as fp:
    exec(fp.read())

setup(
    name="Advisor",
    version=__version__,  # noqa: F821
    author="Valerii Goncharuk",
    author_email="lera.goncharuk@gmail.com",
    packages=["advisor"],
    package_data={"": ["LICENSE"]},
    url="https://github.com/tagezi/advisor",
    license="GPL 3.0",
    entry_points={
        "console_scripts": [
            "advisor = advisor:__main__"]},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: X11 Applications :: Qt",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GPL 3.0",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python",
        "Topic :: Database",
        "Topic :: Education",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Scientific/Engineering",
        "Topic :: Utilities",
    ],
    description="Python 3 program to help analyze of the securities market.",
    include_package_data=True,
    long_description_content_type="text/markdown",
    long_description=long_description,
    zip_safe=True,
    python_requires=">=3.10",
    project_urls={
        "Bug Reports": "https://github.com/tagezi/advisor/issues",
        "Read the Docs": "https://github.com/tagezi/advisor",
    },
    keywords=["market", "analyze", "business", "advisor"],
)
