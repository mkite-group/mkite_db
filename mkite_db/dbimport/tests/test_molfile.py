import os
import unittest as ut
from mkite_core.external import load_config
from unittest.mock import MagicMock
from pkg_resources import resource_filename

from mkite_core.models import MoleculeInfo, NodeResults, JobResults
from mkite_db.dbimport.molfile import MolFileImporter


MOLFILE = resource_filename("mkite_db.tests.files.dbimport", "molfile.yaml")


class TestMolFileImporter(ut.TestCase):
    def setUp(self):
        self.dbimp = MolFileImporter(
            project="test_prj",
            experiment="test_exp",
        )

    def get_contents(self):
        return load_config(MOLFILE)

    def test_read(self):
        data = self.dbimp.read(MOLFILE)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 3)
        self.assertIsInstance(data[0], dict)

    def test_query(self):
        data = self.dbimp.query(filename=MOLFILE)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 3)
        self.assertIsInstance(data[0], dict)

    def test_convert_item(self):
        data = self.get_contents()

        results = self.dbimp.convert_item(data[0])

        self.assertIsInstance(results, NodeResults)
        self.assertIsInstance(results.chemnode, dict)
        for key in ["smiles", "inchikey", "attributes"]:
            self.assertTrue(key in results.chemnode)

    def test_convert(self):
        data = self.get_contents()
        results = self.dbimp.convert(data)

        self.assertIsInstance(results, list)
        self.assertIsInstance(results[0], NodeResults)
        self.assertEqual(len(results), 3)
