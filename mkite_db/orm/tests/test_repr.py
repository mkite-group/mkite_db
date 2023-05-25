import unittest as ut

from mkite_db.orm.repr import _named_repr


class MockObject:
    @property
    def id(self):
        return 1

    @property
    def name(self):
        return "object"


class TestRepr(ut.TestCase):
    def setUp(self):
        self.obj = MockObject()

    def test_repr(self):
        out = _named_repr(self.obj)
        expected = "<MockObject: object (1)>"

        self.assertEqual(out, expected)
