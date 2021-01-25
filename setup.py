# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='transport',
    version='0.0.2',
    license='MIT',
    description='一个简单批处理工具，输入整理好的 excel 基于模板输出 DDL',
    author="yinheli",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=True,
    install_requires=[
        "click",
        "openpyxl",
        "Jinja2",
        "sqlparse",
    ],
    entry_points={
        'console_scripts': [
            'transport=transport.cli:main'
        ]
    }
)
