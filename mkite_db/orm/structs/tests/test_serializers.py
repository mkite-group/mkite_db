from model_bakery import baker
from django.test import TestCase

from mkite_db.orm.base.models import Formula
from mkite_db.orm.jobs.models import Job
from mkite_db.orm.structs.serializers import CrystalSerializer

from .test_models import CrystalCreator


class TestCrystalSerializer(TestCase):
    def setUp(self):
        self.creator = CrystalCreator()

    def test_serialize(self):
        crystal = self.creator.create_crystal()
        serial = CrystalSerializer(crystal)
        data = serial.data

        expected = {
            "spacegroup": 227,
            "species": ["Si", "Si"],
            "coords": [[0.0, 0.0, 0.0], [1.365, 1.365, 1.365]],
            "lattice": [[0.0, 2.73, 2.73], [2.73, 0.0, 2.73], [2.73, 2.73, 0.0]],
            "attributes": {},
            "siteprops": {},
        }

        for k, v in expected.items():
            self.assertEqual(data[k], v)

    def test_deserialize(self):
        job = baker.make(Job)
        data = {
            "parentjob": {"id": job.id},
            "spacegroup": 227,
            "species": ["Si", "Si"],
            "coords": [[0.0, 0.0, 0.0], [1.365, 1.365, 1.365]],
            "lattice": [[0.0, 2.73, 2.73], [2.73, 0.0, 2.73], [2.73, 2.73, 0.0]],
            "attributes": {},
            "siteprops": {},
        }
        serial = CrystalSerializer(data=data)
        self.assertTrue(serial.is_valid())

        new = serial.save()
        self.assertEqual(new.spacegroup, 227)
        self.assertEqual(new.formula.name, "Si2 +0")
        self.assertEqual(new.parentjob.uuid, job.uuid)

    def test_deserialize_without_spgrp(self):
        job = baker.make(Job)
        data = {
            "parentjob": {"id": job.id},
            "species": ["Si", "Si"],
            "coords": [[0.0, 0.0, 0.0], [1.365, 1.365, 1.365]],
            "lattice": [[0.0, 2.73, 2.73], [2.73, 0.0, 2.73], [2.73, 2.73, 0.0]],
            "attributes": {},
            "siteprops": {},
        }
        serial = CrystalSerializer(data=data)
        self.assertTrue(serial.is_valid())

        new = serial.save()
        self.assertEqual(new.spacegroup, 227)
