from __future__ import print_function

import os

from jinja2.loaders import FileSystemLoader
from jinja2 import Environment
import json


def wrap_in_raw(docs):
    for doc in docs:
        if doc:
            if 'description' in doc:
                doc['description'] = "{% raw %}" + doc['description'] + "{% endraw %}"


class Documentation(object):
    def __init__(self, documentation, version):
        super(Documentation, self).__init__()
        loader = FileSystemLoader(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'))
        self.env = Environment(loader=loader)

        self.parented = {}
        self.documentation = documentation
        self.version = version
        self.classes = {}
        self.classes_members = {}

        for doc_element in self.documentation:
            if doc_element['kind'] == 'class':
                class_name = doc_element['longname']
                self.classes[class_name] = doc_element
                self.classes_members[class_name] = []

        for doc_element in documentation:
            if 'memberof' in doc_element:
                memberof = doc_element['memberof']
                if memberof in self.classes_members.keys():
                    self.classes_members[memberof].append(doc_element)

                if memberof in self.parented:
                    self.parented[memberof].append(doc_element)
                else:
                    self.parented[memberof] = [doc_element]

    def generate_method_signature(self, member):
        named_params = []
        params = member.get('params', [])
        for param in params:
            named_parameter = param['name']
            if param.get('optional'):
                named_parameter += '?'
            if 'type' in param:
                type_name = param['type']['names'][0]
                type_ref = None
                if type_name in self.classes:
                    type_ref = '<a href="#{type_name_anchor}">{type_name}</a>'.format(type_name=type_name,
                                                                                      type_name_anchor=type_name.replace(
                                                                                          '.', '-'))

                named_parameter += ':' + (type_name if not type_ref else type_ref)
            named_params.append(named_parameter)
        return member['name'] + '(' + ', '.join(named_params) + ')'

    def generate_method_return_value(self, method):
        ret_types = []
        for retval in method['returns']:
            for type_name in retval['type']['names']:
                type_ref = None
                if type_name in self.classes:
                    type_ref = '<a href="#{type_name_anchor}">{type_name}</a>'.format(type_name=type_name,
                                                                                      type_name_anchor=type_name.replace(
                                                                                          '.', '-'))
                ret_types.append(type_name if not type_ref else type_ref)

        return '|'.join(ret_types)

    def get_class_documentation(self, class_key):
        class_ = self.classes[class_key]
        members = self.classes_members[class_key]
        constructors = filter(lambda d: d['kind'] == 'constructor', members)
        constructor = None

        if constructors:
            constructor = constructors[0]
            constructor['signature'] = self.generate_method_signature(constructor)

        methods = filter(lambda d: d['kind'] == 'function', members)
        properties = filter(lambda d: d['kind'] == 'member', members)

        wrap_in_raw([constructor])
        wrap_in_raw([class_])
        wrap_in_raw(methods)
        wrap_in_raw(properties)

        for method in methods:
            method['signature'] = self.generate_method_signature(method)
            if 'returns' in method:
                method['returnValue'] = self.generate_method_return_value(method)

        return {
            'class': class_,
            'constructor': constructor,
            'methods': methods,
            'properties': properties
        }

    def generate(self):
        classes_doc = [self.get_class_documentation(class_name) for class_name in self.classes.keys()]
        main_template = self.env.get_template('main.jinja2')
        return main_template.render({
            'classes': classes_doc,
            'version': self.version
        })


if __name__ == '__main__':
    import sys

    input_file = sys.stdin
    data = input_file.read()
    documentation_data = json.loads(data)
    doc = Documentation(documentation_data, '1.1')
    print(doc.generate())
