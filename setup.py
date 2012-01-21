#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from distutils.core import setup

data_files = [("share/icons/", ["vault/data/vault.png"]),
              ("share/applications/", ["vault/data/vault.desktop"])]

setup(
    name = "vault",
    packages = ["vault"],
    scripts = ["vault/vault"],
    data_files = data_files,
    version = "1.0.0",
    description = "GUI application for creating and managing encrypted folders.",
    author = "Chris Triantafillis",
    author_email = "christriant1995@gmail.com",
    license = "GPLv3",
    platforms = 'Linux',
    url = "https://github.com/Clepto/Vault",
    keywords = ["folders", "encrypted", "vault"],
    classifiers = [
        "Programming Language :: Python",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: POSIX :: Linux",
        "Environment :: X11 Applications :: Qt",
        "Natural Language :: English",
        "Natural Language :: Greek",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Utilities"],
    long_description = """
Vault is a GUI application for creating and managing encrypted folders. 
Vault is written in Python and QT. It uses EncFS (man encfs, to see more)
for the encryption.
"""
)
