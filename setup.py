
from setuptools import setup, find_packages

setup(
    name="SchadFlow",
    version="1.0",
    packages=find_packages(),
    install_requires=[
        'PySide6',
        'matplotlib',
    ],
)