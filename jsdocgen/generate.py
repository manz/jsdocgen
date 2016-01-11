from __future__ import print_function
import argparse
import json
import re

from .documentation import Documentation

parser = argparse.ArgumentParser(description='Generates HTML+MD documentation from jsdoc-parse output')
parser.add_argument('--package-version', dest='package_version', action='store',
                    help='the package version')
parser.add_argument('--output', action='store', help='Output file, defaults to stdout')
parser.add_argument('--google-maps', help='Adds references for google maps objects', action='store_true')

VERSION_REGEX = re.compile('(\d\.\d)\.x')
if __name__ == '__main__':
    import sys

    result = parser.parse_args()
    if 'help' in result:
        parser.print_help()
    else:
        if 'package_version' in result:
            match = VERSION_REGEX.match(result.package_version)
            version = match.group(1) if match else result.package_version
        else:
            version = None

        data = sys.stdin.read()
        documentation_data = json.loads(data)
        doc = Documentation(documentation_data, version, google_maps_links=result.google_maps)

        generated_doc = doc.generate().encode('utf-8')

        if 'output' in result:
            with open(result.output, 'wt') as output_file:
                output_file.write(generated_doc)
        else:
            print(generated_doc)
