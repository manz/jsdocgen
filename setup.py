# coding=utf-8
from setuptools import setup, find_packages

def parse_requirements(filename):
    """ load requirements from a pip requirements file """
    lineiter = (line.strip() for line in open(filename))
    return [line for line in lineiter if line and not line.startswith("#")]

requirements = parse_requirements('requirements.txt')

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
