#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name="exportador-bpa-i",
    version="1.0.0",
    description="Aplicativo para exportação de dados no formato BPA-I",
    author="Seu Nome",
    author_email="seu.email@exemplo.com",
    packages=find_packages(),
    install_requires=[
        "psycopg2-binary>=2.9.5",
        "PySimpleGUI>=4.60.0",
    ],
    entry_points={
        "console_scripts": [
            "exportador-bpa-i=exportador:main",
        ],
    },
    python_requires=">=3.6",
    include_package_data=True,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Healthcare Industry",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)