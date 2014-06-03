from django.test import TestCase

from dirtyfields.dirtyfields import _to_dict, _changes

from example_app.testing_app.models import TestModel


class DirtyFieldsMixinTestCase(TestCase):

    def test_dirty_fields(self):
        tm = TestModel()

        # initial state shouldn't be dirty
        self.assertEqual(_changes(tm, _to_dict(tm)), {})

        # changing values should flag them as dirty
        tm.boolean = False
        tm.characters = 'testing'

        self.assertEqual(_changes(tm, _to_dict(tm)), {
            'boolean': True,
            'characters': ''
        })

        # resetting them to original values should unflag
        tm.boolean = True
        self.assertEqual(_changes(tm, _to_dict(tm)), {
            'characters': ''
        })

    def test_sweeping(self):
        tm = TestModel()
        tm.boolean = False
        tm.characters = 'testing'
        self.assertEqual(_changes(tm, _to_dict(tm)), {
            'boolean': True,
            'characters': ''
        })
        tm.save()
        self.assertEqual(_changes(tm, _to_dict(tm)), {})
