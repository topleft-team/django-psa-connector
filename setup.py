#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import djpsa

LONG_DESCRIPTION = open('README.md').read()

setup(
    name="django-psa",
    version=djpsa.__version__,
    description='Django app for working with '
                'various PSA REST API. Defines '
                'models (tickets, companies, '
                'etc.) and callbacks. ',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    keywords='django connectwise halo autotask rest api python',
    packages=find_packages(),
    author='TopLeft Technologies Ltd.',
    author_email='sam@topleft.team',
    url="https://github.com/topleft-team/django-psa",
    include_package_data=True,
    license='MIT',
    install_requires=[
        'requests',
        'django',
        'setuptools',
        'python-dateutil',
    ],
    test_suite='runtests.suite',
    tests_require=[
        'names',
        'coverage',
        'flake8',
        'django-test-plus',
        'mock',
        'freezegun',
        'responses',
        'model-mommy',
        'django-coverage',
        'names',
    ],
    # Django likes to inspect apps for /migrations directories, and can't if
    # package is installed as an egg. zip_safe=False disables installation as
    # an egg.
    zip_safe=False,
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Development Status :: 3 - Alpha',
    ],
)
