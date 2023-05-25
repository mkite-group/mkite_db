import os
import mp_api
import numpy as np
import unittest as ut
from unittest.mock import MagicMock
from monty.serialization import loadfn
from pkg_resources import resource_filename

from pymatgen.core import Structure
from mkite_core.models import CrystalInfo, EnergyForcesInfo, NodeResults, JobResults
from mkite_db.dbimport.mp import MPImporter, MP_KEY


RESPONSE_PATH = resource_filename("mkite_db.tests.files.dbimport", "mp.json")


class MockDoc(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__dict__ = self


class MockMPResponse(MagicMock):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.return_value = self.format_response()

    def format_response(self):
        response = loadfn(RESPONSE_PATH)

        return [MockDoc(**data) for data in response]


class MockMPImporter(MPImporter):
    query = MockMPResponse()


class TestMPImporter(ut.TestCase):
    def setUp(self):
        self.dbimp = MockMPImporter(
            project="test_prj",
            experiment="test_exp",
        )

    def get_query_args(self):
        return {
            "elements": ["Si"],
            "num_elements": (1, 1),
            "energy_above_hull": (0, 1e-6),
        }

    def get_response(self):
        qargs = self.get_query_args()
        return self.dbimp.query_structures(**qargs)

    def test_query_structures(self):
        response = self.get_response()
        self.assertTrue(self.dbimp.query.called)

    def test_convert_structure(self):
        response = self.get_response()
        doc = response[0]
        info = self.dbimp.convert_structure(doc)
        self.assertIsInstance(info, dict)

    def test_convert_energy_forces(self):
        response = self.get_response()
        doc = response[0]
        info = self.dbimp.convert_energy_forces(doc)
        self.assertIsInstance(info, dict)
        self.assertAlmostEqual(info["energy"], -5.42531402 * 2)
        self.assertTrue((np.array(info["forces"]) < 1e-10).all())

    def test_convert_doc(self):
        response = self.get_response()
        doc = response[0]
        info = self.dbimp.convert_doc(doc)
        self.assertIsInstance(info, NodeResults)

    def test_convert(self):
        response = self.get_response()
        info = self.dbimp.convert(response)
        self.assertIsInstance(info, list)

    def test_create_job(self):
        job = self.dbimp.create_job(
            project="test_prj",
            experiment="test_exp",
            isroot=True,
            options=self.get_query_args(),
        )
        expected = {
            "experiment": {"name": "test_exp", "project": {"name": "test_prj"}},
            "recipe": {
                "package": {"name": "mp_api.MPRester"},
                "name": "dbimport.MPImporter",
                "method": "EXT",
            },
            "isroot": True,
            "status": "D",
            "options": self.get_query_args(),
        }

        self.assertEqual(job, expected)

    def test_import_data(self):
        results = self.dbimp.import_data(
            project="test_prj",
            experiment="test_exp",
            isroot=True,
            **self.get_query_args(),
        )
        self.assertIsInstance(results, JobResults)

    @ut.skip
    @ut.skipIf(MP_KEY not in os.environ, "MP_KEY not in environment")
    def test_connection(self):
        raise NotImplementedError("Test TO-DO")
