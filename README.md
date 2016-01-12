# js-doc-gen

Generates page to be integrated in a jekyll website

## Installation

```ShellSession
$ npm install jsdoc-parse
$ pip install git://github.com/manz/wgsdocgen
```

## Usage

```ShellSession
$ js-doc-gen --help
usage: generate.py [-h] [--package-version PACKAGE_VERSION] [--output OUTPUT]
                   [--google-maps]

Generates HTML+MD documentation from jsdoc-parse output

optional arguments:
  -h, --help            show this help message and exit
  --package-version PACKAGE_VERSION
                        the package version
  --output OUTPUT       Output file, defaults to stdout
  --google-maps         Adds references for google maps objects
```

```ShellSession
$ jsdoc-parse --src 'src/**/*.js' | js-doc-gen --google-maps --package-version 1.1 --output output.md
```
