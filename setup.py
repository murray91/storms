import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="Storms",
    version="1.1.0",
    author="Ryan Murray",
    author_email="ryanwaltermurray@gmail.com",
    description=("Creates design storms."),
    license="MIT",
    keywords="hydrology design storms Chicago",
    packages=['storms'],
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Scientific/Engineering :: Hydrology",
        "License :: OSI Approved :: MIT License",
    ],
    install_requires=[
   'numpy',
   'scipy',
   'pandas',
   'mikeio'
    ]
)
