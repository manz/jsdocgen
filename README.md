# js-doc-gen

Generates page to be integrated in a jekyll website

## Installation

```ShellSession
$ npm install jsdoc-parse
$ pip install git+https://github.com/manz/jsdocgen.git
```

## Usage

```ShellSession
$ js-doc-gen --help
usage: generate.py [-h] [--package-version PACKAGE_VERSION]
                   [--package-json PACKAGE_JSON] [--output OUTPUT]
                   [--output-directory OUTPUT_DIRECTORY] [--google-maps]

Generates a jekyll file from jsdoc-parse output read from stdin.

optional arguments:
  -h, --help            show this help message and exit
  --package-version PACKAGE_VERSION
                        the package version
  --package-json PACKAGE_JSON
  --output OUTPUT       Output file, defaults to stdout
  --output-directory OUTPUT_DIRECTORY
                        Output directory, use version.md as filename
  --google-maps         Adds references for google maps objects
```

## Examples

```ShellSession
$ jsdoc-parse --src 'src/**/*.js' | js-doc-gen --google-maps --package-version 1.1 --output output.md
```

Pulls version information from package.json, used to name the resulting markdown file.
```ShellSession
$ jsdoc-parse --src 'src/**/*.js' | js-doc-gen --google-maps --package-json package.json --output-directory output_directory
```
