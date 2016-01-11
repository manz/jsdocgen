from unittest.case import TestCase

from jsdocgen.documentation import Documentation


class GenerateTest(TestCase):
    def test_generate_method_signature(self):
        doc = Documentation({}, 1.1)
        signature = doc.generate_method_signature({
            'name': 'aMethodName',
            'params': [
                {
                    'name': 'myParam',
                    'type': {'names': ['woosumap.Class']}
                }
            ]
        })

        self.assertEquals(signature, 'aMethodName(myParam:woosumap.Class)')

    def test_generate_method_signature_optional_param(self):
        doc = Documentation({}, 1.1)
        signature = doc.generate_method_signature({
            'name': 'aMethodName',
            'params': [
                {
                    'optional': True,
                    'name': 'myParam',
                    'type': {'names': ['woosumap.Class']}
                }
            ]
        })

        self.assertEquals(signature, 'aMethodName(myParam?:woosumap.Class)')

    def test_generate_method_signature_reference_type(self):
        doc = Documentation({}, 1.1)
        doc.references.add('woosumap.Class')

        signature = doc.generate_method_signature({
            'name': 'aMethodName',
            'params': [
                {
                    'name': 'myParam',
                    'type': {'names': ['woosumap.Class']}
                }
            ]
        })

        self.assertEquals(signature, 'aMethodName(myParam:<a href="#woosumap.Class">woosumap.Class</a>)')

    def test_generate_method_signature_with_multiple_types_for_param(self):
        doc = Documentation({}, 1.1)

        signature = doc.generate_method_signature({
            'name': 'aMethodName',
            'params': [
                {
                    'name': 'myParam',
                    'type': {'names': ['woosumap.Class', 'String']}
                }
            ]
        })

        self.assertEquals(signature, 'aMethodName(myParam:woosumap.Class|String)')

    def test_generate_method_signature_with_all_on(self):
        doc = Documentation({}, 1.1)
        doc.references.add('woosumap.Class')
        doc.references.add('String')

        signature = doc.generate_method_signature({
            'name': 'aMethodName',
            'params': [
                {
                    'optional': True,
                    'name': 'myParam',
                    'type': {'names': ['woosumap.Class', 'String']}
                }
            ]
        })

        class_ref = '<a href="#woosumap.Class">woosumap.Class</a>'
        string_ref = '<a href="#String">String</a>'
        self.assertEquals(signature, 'aMethodName(myParam?:{class_ref}|{string_ref})'.format(
            class_ref=class_ref,
            string_ref=string_ref))

    def test_generate_type_reference_should_work_with_arrays(self):
        doc = Documentation({}, 1.1)
        doc.references.add('Toto')

        type_ref = doc.generate_type_reference('Array.<Toto>')
        self.assertEquals(type_ref, 'Array.&lt;<a href="#Toto">Toto</a>&gt;')

    def test_generate_type_reference_should_resolve_google_maps(self):
        doc = Documentation({}, 1.1, google_maps_links=True)
        type_ref = doc.generate_type_reference('google.maps.Map')
        self.assertEquals(type_ref, '<a target="_blank" href="https://developers.google.com/maps/documentation/javascript/reference#Map">google.maps.Map</a>')
        doc.google_maps_links = False
        type_ref = doc.generate_type_reference('google.maps.Map')
        self.assertEquals(type_ref, 'google.maps.Map')
