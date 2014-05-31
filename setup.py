#! /usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

# List of python package dependancies availables on pypi repository
apps_pypi = []

# Tests requirements
# Note : not installed automatically
tests_requires = ['coverage']


setup(
    name='cgroups',
    version='0.1.0',  # 3 numbers notation major.minor.bugfix_or_security
    description='Python module to manage cgroups',
    author='Francis Bouvier - Cloud Orchestra',
    author_email='francis.bouvier@cloudorchestra.io',
    license='New BSD',
    url='http://www.xerus-technologies.fr',
    platforms='Linux',
    packages=find_packages(exclude=['ez_setup']),
    zip_safe=False,
    include_package_data=True,
    install_requires=apps_pypi,
    entry_points={
        'console_scripts': [
            'user_cgroups = cgroups.user:main',
        ]
    },
)
