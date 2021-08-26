#!/usr/bin/env python3

import os
from setuptools import setup
from unpoly import get_version

HERE = os.path.abspath(os.path.dirname(__file__))


def make_readme(root_path):
    consider_files = ("README.md", "LICENSE", "CHANGELOG")
    for filename in consider_files:
        filepath = os.path.realpath(os.path.join(root_path, filename))
        if os.path.isfile(filepath):
            with open(filepath, mode="r") as f:
                yield f.read()


LICENSE = "MIT License"
URL = "https://github.com/thinkwelltwd/unpoly_django"
LONG_DESCRIPTION = "\r\n\r\n----\r\n\r\n".join(make_readme(HERE))
SHORT_DESCRIPTION = "An app for Django to implement the Unpoly v2 Server Protocol"
KEYWORDS = (
    "django",
    "unpoly",
)

setup(
    name="unpoly_django",
    version=get_version(),
    author="Dave Burkholder",
    author_email="dave@thinkwelldesigns.com",
    description=SHORT_DESCRIPTION[0:200],
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    packages=[
        "unpoly",
    ],
    include_package_data=True,
    install_requires=[
        "Django>=3.1",
    ],
    tests_require=[
        "django-crispy-forms",
    ],
    zip_safe=False,
    keywords=" ".join(KEYWORDS),
    license=LICENSE,
    url=URL,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: {}".format(LICENSE),
        "Natural Language :: English",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Framework :: Django",
        "Framework :: Django :: 3.1",
    ],
)
