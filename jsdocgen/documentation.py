import logging
import os
import re
import cgi
from logging import StreamHandler

from jinja2.loaders import FileSystemLoader
from jinja2 import Environment

logger = logging.getLogger('documentation')
logger.addHandler(StreamHandler())


class Documentation(object):
    ARRAY_OF_REGEX = re.compile('[aA]rray\.<([A-Za-z][A-Za-z0-9.]+)>')
    GOOGLE_REF_PREFIX_URL = 'https://developers.google.com/maps/documentation/javascript/reference'

    def __init__(self, documentation, version, google_maps_links=False):
        super(Documentation, self).__init__()
        loader = FileSystemLoader(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'))
        self.google_maps_links = google_maps_links
        self.env = Environment(loader=loader)

        self.parented = {}
        self.documentation = documentation
        self.version = version
        self.classes = {}
        self.classes_members = {}
        self.references = set()
        self.typedefs = {}

        for doc_element in self.documentation:
            if doc_element['kind'] == 'class':
                class_name = doc_element['longname']
                self.classes[class_name] = doc_element
                self.classes_members[class_name] = []
                self.references.add(class_name)
            elif doc_element['kind'] == 'typedef':
                type_name = doc_element['longname']
                self.references.add(doc_element['longname'])
                self.typedefs[type_name] = doc_element

        for doc_element in documentation:
            if 'memberof' in doc_element:
                memberof = doc_element['memberof']
                if memberof in self.classes_members.keys():
                    self.classes_members[memberof].append(doc_element)

                if memberof in self.parented:
                    self.parented[memberof].append(doc_element)
                else:
                    self.parented[memberof] = [doc_element]

    def generate_named_params(self, member):
        named_params = []

        params = member.get('params', [])
        for param in params:
            named_parameter = param['name']
            if param.get('optional'):
                named_parameter += '?'
            if 'type' in param:
                types = []
                for type_name in param['type']['names']:
                    types.append(self.generate_type_reference(type_name))

                named_parameter += ':' + ('|'.join(types))
            named_params.append(named_parameter)

        return named_params

    def generate_method_signature(self, member):
        named_params = self.generate_named_params(member)

        return member['name'] + '(' + ', '.join(named_params) + ')'

    def generate_method_return_value(self, method):
        ret_types = []
        for retval in method['returns']:
            for type_name in retval['type']['names']:
                type_ref = self.generate_type_reference(type_name)
                ret_types.append(type_ref)

        return '|'.join(ret_types)

    def generate_types_reference(self, type_names):
        type_refs = []
        for type_name in type_names:
            type_refs.append(self.generate_type_reference(type_name))
        return '|'.join(type_refs)

    def generate_type_reference(self, type_name):
        type_key = type_name
        match = self.ARRAY_OF_REGEX.match(type_name)
        if match:
            type_key = match.group(1)

        type_ref = self._generate_type_reference(type_key)

        if match:
            type_ref = 'Array.&lt;{type_ref}&gt;'.format(type_ref=type_ref)

        return type_ref

    def _generate_type_reference(self, type_name):
        type_key = type_name

        if type_key in self.references:
            type_ref = '<a href="#{type_key}">{type_key}</a>'.format(
                type_key=type_key)
        elif self.google_maps_links and type_key.startswith('google.maps.'):
            type_key = type_key.replace('google.maps.', '')
            type_ref = '<a target="_blank" href="{prefix}#{type_key}">{type_name}</a>'.format(
                type_key=type_key,
                type_name=type_name,
                prefix=self.GOOGLE_REF_PREFIX_URL)
        else:
            if '.' not in type_key:
                type_key = type_key.capitalize()
            type_ref = cgi.escape(type_key)

        return type_ref

    def get_constructor(self, members):
        constructor = None
        constructors = filter(lambda d: d['kind'] == 'constructor', members)

        if constructors:
            constructor = constructors[0]
            constructor['signature'] = self.generate_method_signature(constructor)
            # Shortens the constructor description to the first lLine
            if 'description' in constructor:
                if constructor['description']:
                    splitted_description = constructor['description'].split('\n')
                    if splitted_description:
                        constructor['shortDescription'] = splitted_description[0]
        return constructor

    def get_class_documentation(self, class_key):
        class_ = self.classes[class_key]
        members = self.classes_members[class_key]
        constructor = self.get_constructor(members)

        methods = filter(lambda d: d['kind'] == 'function', members)
        properties = filter(lambda d: d['kind'] == 'member', members)

        # lot of stuff to just compute Parent Class (does it even work properly ?)
        inherited_methods = filter(lambda d: d.get('inherited'), methods)
        inherited_methods_names = map(lambda d: d['inherits'], inherited_methods)
        parent_classes = set(map(lambda d: d.split('#')[0], inherited_methods_names))
        parent_classes = map(lambda c: self.generate_type_reference(c), parent_classes)

        for method in methods:
            method['signature'] = self.generate_method_signature(method)
            if 'returns' in method:
                method['returnValue'] = self.generate_method_return_value(method)

        properties = properties if 'properties' not in class_ else properties + class_['properties']
        for prop in properties:
            if 'type' in prop:
                prop['typeRef'] = self.generate_types_reference(prop['type']['names'])

        class_doc = {
            'name': class_['name'],
            'longname': class_['longname'],
            'constructor': constructor,
            'methods': methods,
            'parents': parent_classes,
            # class_['properties'] are defined when we define a class without real code.
            'properties': properties
        }

        if 'virtual' in class_:
            class_doc['virtual'] = class_['virtual']

        if constructor:
            class_doc['examples'] = constructor.get('examples') or class_doc.get('examples')

        return class_doc

    def get_typedef_documentation(self, typedef_key):
        typedef = self.typedefs[typedef_key]

        properties = typedef.get('properties', [])
        for prop in properties:
            if 'type' in prop:
                prop['typeRef'] = self.generate_types_reference(prop['type']['names'])

        # we have a typedef for a callback
        if 'params' in typedef:
            named_params = self.generate_named_params(typedef)
            typedef['signature'] = 'function(' + ','.join(named_params) + ')'
            if 'returns' in typedef:
                return_value = self.generate_method_return_value(typedef)
                typedef['returnValue'] = return_value

        return typedef

    def generate(self):
        classes_doc = [self.get_class_documentation(class_name) for class_name in self.classes.keys()]
        classes_doc.sort(key=lambda c: c['name'])

        typedefs_doc = [self.get_typedef_documentation(typedef_name) for typedef_name in self.typedefs.keys()]
        typedefs_doc.sort(key=lambda c: c['name'])

        main_template = self.env.get_template('main.jinja2')

        return main_template.render({
            'classes': classes_doc,
            'typedefs': typedefs_doc,
            'version': self.version,
            'references': self.references
        })
