# coding=utf-8
from setuptools import setup, find_packages
from pip.req import parse_requirements

requirements = parse_requirements('requirements.txt', session=False)

setup(
    name="jsdocgen",
    version="0.0.1",
    license="Private",
    url="https://github.com/WebGeoServices/jsdocgen",
    packages=find_packages('.'),
    include_package_data=True,
    classifiers=[
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 2.7"
    ],
    scripts=[
        'js-doc-gen'
    ],
    install_requires=[str(requirement.req) for requirement in requirements]
)
