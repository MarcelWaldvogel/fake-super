#!/usr/bin/python3
import re

import setuptools


def extract_version(filename):
    with open(filename, 'r') as fh:
        for line in fh:
            match = re.match(
                    r'''VERSION\s*=\s*["']([-_.0-9a-z]+)(\+?)["']''', line)
            if match:
                if match[2] == '':
                    return match[1]
                else:
                    return match[1] + '.post'
    exit("Cannot extract version number from %s" % filename)


with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name="fake-super",
    version=extract_version('fake_super/version.py'),
    author="Marcel Waldvogel",
    author_email="marcel.waldvogel@trifence.ch",
    description="Handle information for `rsync --fake-super`",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/trifence/fake-super",
    license='MIT',
    packages=setuptools.find_packages(),
    install_requires=['setuptools', 'xattr'],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'fake-super=fake_super:main',
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Information Technology",
        "Programming Language :: Python",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Natural Language :: English",
        "Topic :: Utilities",
        "Topic :: System :: Archiving :: Backup",
        "Topic :: System :: Archiving :: Mirroring",
    ],
)
