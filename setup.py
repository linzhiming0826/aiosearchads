#!/usr/bin/env python

import re
from os import path
from setuptools import setup, find_packages


requirements = [
    'aiohttp>=3.6.2',
    'pyjwt>=1.7.1'
]

with open("README.md", "r") as fh:
    long_description = fh.read()

version_file = path.join(
    path.dirname(__file__),
    'aiosearchads',
    '__version__.py'
)
with open(version_file, 'r') as fp:
    m = re.search(
        r"^__version__ = ['\"]([^'\"]*)['\"]",
        fp.read(),
        re.M
    )
    version = m.groups(1)[0]


setup(
    name='aiosearchads',
    version=version,
    license='MIT',
    url='https://github.com/linzhiming0826/aiosearchads',
    author='TuoX',
    author_email='120549827@qq.com',
    description='Asynchronous apple searchads framework for asyncio and Python',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'License :: OSI Approved :: MIT License',
    ],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=requirements
)
