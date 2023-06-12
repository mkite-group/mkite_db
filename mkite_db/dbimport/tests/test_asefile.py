import unittest as ut
from pkg_resources import resource_filename

from ase import Atoms
from ase.io import read
from mkite_core.models import CrystalInfo, ConformerInfo, NodeResults
from mkite_db.dbimport.asefile import AseFileImporter


CIF_FILE = resource_filename("mkite_db.tests.files.dbimport", "silicon.cif")
XYZ_FILE = resource_filename("mkite_db.tests.files.dbimport", "caffeine.xyz")


class TestAseFileImporter(ut.TestCase):
    def setUp(self):
        self.dbimp = AseFileImporter(
            project="test_prj",
            experiment="test_exp",
        )

    def get_crystal(self):
        return read(CIF_FILE)

    def get_conformer(self):
        return read(XYZ_FILE)

    def test_read_cif(self):
        data = self.dbimp.read(CIF_FILE)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertIsInstance(data[0], Atoms)

    def test_read_xyz(self):
        data = self.dbimp.read(XYZ_FILE)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertIsInstance(data[0], Atoms)

    def test_query(self):
        data = self.dbimp.query(CIF_FILE)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertIsInstance(data[0], Atoms)

    def test_convert_crystal(self):
        item = self.get_crystal()

        results = self.dbimp.convert_item(item)

        self.assertIsInstance(results, NodeResults)
        self.assertIsInstance(results.chemnode, dict)

        info = CrystalInfo.from_dict(results.chemnode)

    def test_convert_conformer(self):
        item = self.get_conformer()

        results = self.dbimp.convert_item(item)

        self.assertIsInstance(results, NodeResults)
        self.assertIsInstance(results.chemnode, dict)

        info = ConformerInfo.from_dict(results.chemnode)

    def test_convert(self):
        data = [
            self.get_crystal(),
            self.get_conformer(),
        ]
        results = self.dbimp.convert(data)

        self.assertIsInstance(results, list)
        self.assertIsInstance(results[0], NodeResults)
        self.assertEqual(len(results), 2)
