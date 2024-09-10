# -*- coding: utf-8 -*-

import os
import io

from setuptools import setup, find_packages


def read_file(filename):
    with io.open(filename) as fp:
        return fp.read().strip()


root = os.path.abspath(os.path.dirname(__file__))
version = read_file(os.path.join(root, "VERSION"))
requirements = [
    line.strip()
    for line in read_file(os.path.join(root, "requirements.txt")).splitlines()
    if not line.startswith("#")
]

setup(
    name="apo-health-spiders",
    version=version,
    description="em apo-health spiders",
    keywords="scrapy web-scraping",
    license="New BSD License",
    author="Sky",
    author_email="newkbsky@gmail.com",
    url="https://github.com/VG-IT/apo-health",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: Scrapy",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
    ],
    packages=find_packages(exclude=["*test"]),
    install_requires=requirements,
    entry_points={
        "scrapy": [
            "settings = apo_health.settings",
        ],
    },
)
