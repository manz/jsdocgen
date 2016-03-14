from __future__ import print_function
import argparse
import json
import re
import os

from .documentation import Documentation

parser = argparse.ArgumentParser(description='Generates a jekyll file from jsdoc-parse output read from stdin.')
parser.add_argument('--package-version', dest='package_version', action='store',
                    help='the package version')
parser.add_argument('--package-json', dest='package_json', action='store')
parser.add_argument('--output', action='store', help='Output file, defaults to stdout')
parser.add_argument('--output-directory', action='store', help='Output directory, use version.md as filename')

parser.add_argument('--google-maps', help='Adds references for google maps objects', action='store_true')

BRANCH_REGEX = re.compile('r(\d\.\d)\.x')
VERSION_REGEX = re.compile(r'(?P<version>\d+\.\d+)\.\d+(?:-(?P<prerelease>\d+))?')

if __name__ == '__main__':
    import sys

    result = parser.parse_args()
    if 'help' in result:
        parser.print_help()
    else:
        experimental = False
        if 'package_version' in result and result.package_version:
            match = BRANCH_REGEX.match(result.package_version)
            version = match.group(1) if match else result.package_version
        else:
            version = None

        if result.package_json:
            with open(result.package_json, 'rb') as package_json_file:
                package_json = json.loads(package_json_file.read())
                version = package_json['version']
                match = VERSION_REGEX.match(version)
                version = match.group('version')
                experimental = True if match.group('prerelease') else False

        data = sys.stdin.read()
        documentation_data = json.loads(data)
        doc = Documentation(documentation_data, version, google_maps_links=result.google_maps,
                            experimental=experimental)

        generated_doc = doc.generate().encode('utf-8')

        if result and result.output:
            with open(result.output, 'wt') as output_file:
                output_file.write(generated_doc)
        elif 'output_directory' in result and result.output_directory:
            with open(os.path.join(result.output_directory, (version + '.exp' if experimental else version) + '.md'),
                      'wt') as output_file:
                output_file.write(generated_doc)
        else:
            print(generated_doc)
