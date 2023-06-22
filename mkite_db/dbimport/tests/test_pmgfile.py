import unittest as ut
from pkg_resources import resource_filename

from pymatgen.core import Structure
from mkite_core.models import CrystalInfo, NodeResults
from mkite_db.dbimport.pmgfile import PymatgenFileImporter


CIF_FILE = resource_filename("mkite_db.tests.files.dbimport", "silicon.cif")


class TestAseFileImporter(ut.TestCase):
    def setUp(self):
        self.dbimp = PymatgenFileImporter(
            project="test_prj",
            experiment="test_exp",
        )

    def get_crystal(self):
        return Structure.from_file(CIF_FILE)

    def test_read_cif(self):
        data = self.dbimp.read(CIF_FILE)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertIsInstance(data[0], Structure)

    def test_query(self):
        data = self.dbimp.query(CIF_FILE)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertIsInstance(data[0], Structure)

    def test_convert_crystal(self):
        item = self.get_crystal()

        results = self.dbimp.convert_item(item)

        self.assertIsInstance(results, NodeResults)
        self.assertIsInstance(results.chemnode, dict)

        info = CrystalInfo.from_dict(results.chemnode)

    def test_convert(self):
        data = [
            self.get_crystal(),
            self.get_crystal(),
        ]
        results = self.dbimp.convert(data)

        self.assertIsInstance(results, list)
        self.assertIsInstance(results[0], NodeResults)
        self.assertEqual(len(results), len(data))
