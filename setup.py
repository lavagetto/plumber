#!/usr/bin/python

from setuptools import setup, find_packages

setup(
    name='plumber',
    version='0.0.1-alpha',
    description='simple, mundane script to build and publish containers to marathon/mesos',
    author='Giuseppe Lavagetto',
    author_email='glavagetto@wikimedia.org',
    url='https://github.com/lavagetto/plumber',
    install_requires=['argparse', 'Flask', 'jinja2'],
    setup_requires=[],
    zip_safe=True,
    packages=find_packages(),
    entry_points={
        'console_scripts': [
              'plumber-run =  plumber.main:run',
            ],
          },
)
