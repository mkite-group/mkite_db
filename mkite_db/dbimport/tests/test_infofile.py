import json
import unittest as ut
from pkg_resources import resource_filename

from mkite_core.models import CrystalInfo, ConformerInfo, NodeResults
from mkite_db.dbimport.infofile import InfoFileImporter


INFO_FILE = resource_filename("mkite_db.tests.files.dbimport", "infofile.json")


class TestInfoFileImporter(ut.TestCase):
    def setUp(self):
        self.dbimp = InfoFileImporter(
            project="test_prj",
            experiment="test_exp",
        )

    def load(self):
        with open(INFO_FILE, "r") as f:
            data = json.load(f)

        return data

    def test_read(self):
        data = self.dbimp.read(INFO_FILE)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 2)
        self.assertIsInstance(data[0], dict)

    def test_query(self):
        data = self.dbimp.query(INFO_FILE)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 2)
        self.assertIsInstance(data[0], dict)

    def test_convert_item(self):
        data = self.load()
        results = self.dbimp.convert_item(data[0])

        self.assertIsInstance(results, NodeResults)
        self.assertIsInstance(results.chemnode, dict)

        info = CrystalInfo.from_dict(results.chemnode)

    def test_convert(self):
        data = self.load()
        results = self.dbimp.convert(data)

        self.assertIsInstance(results, list)
        self.assertIsInstance(results[0], NodeResults)
        self.assertEqual(len(results), 2)
