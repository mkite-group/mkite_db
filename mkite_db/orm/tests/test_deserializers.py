import json
from django.test import TestCase
from pkg_resources import resource_filename

from mkite_db.orm.deserializers import get_serializer
from mkite_db.orm.mols.models import Molecule
from mkite_db.orm.structs.models import Crystal


MOL_JSON = resource_filename("mkite_core.tests.files.models", "molecule.json")
CRYSTAL_JSON = resource_filename("mkite_core.tests.files.models", "crystal.json")


def load_json(filename):
    with open(filename, "r") as f:
        return json.load(f)


class TestDeserialization(TestCase):
    def setUp(self):
        self.mol_dict = load_json(MOL_JSON)
        self.crystal_dict = load_json(CRYSTAL_JSON)

    def test_mol(self):
        serial = get_serializer(self.mol_dict)
        serial.is_valid()
        self.assertTrue(serial.is_valid())

        obj = serial.save()

        self.assertIsInstance(obj, Molecule)

    def test_crystal(self):
        serial = get_serializer(self.crystal_dict)
        self.assertTrue(serial.is_valid())

        obj = serial.save()

        self.assertIsInstance(obj, Crystal)
