#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['porerefiner >= 0.9.0',]

setup_requirements = [ ]

test_requirements = [ ]

setup(
    author="Justin Payne",
    author_email='justin.payne@fda.hhs.gov',
    python_requires='>=3.7',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="A Porerefiner plugin that supports metadata in the PHA4GE format and ontologies",
    entry_points={
        'porerefiner.plugins': '.prfr_pha4ge = prfr_pha4ge',
    },
    install_requires=requirements,
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='prfr_pha4ge',
    name='prfr_pha4ge',
    packages=find_packages(include=['prfr_pha4ge', 'prfr_pha4ge.*']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/crashfrog/prfr_pha4ge',
    version='0.1.0',
    zip_safe=False,
)
