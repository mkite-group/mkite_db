import unittest as ut
from model_bakery import baker
from django.test import TestCase

from mkite_db.orm.base.models import ChemNode
from mkite_db.orm.base.serializers import ChemNodeSerializer
from mkite_db.orm.jobs.models import Job
from mkite_db.orm.jobs.serializers import JobSerializer
from mkite_db.orm.calcs.models import Feature, EnergyForces
from mkite_db.orm.calcs.serializers import EnergyForcesSerializer, FeatureSerializer


class TestFeatureSerializer(TestCase):
    @property
    def dict(self):
        return {"value": [1.0, 1.0, 0.0]}

    def test_serialize(self):
        f = baker.make(Feature, **self.dict)
        serial = FeatureSerializer(f)
        data = serial.data

        expected = {
            "@module": "mkite_db.orm.calcs.models",
            "@class": "Feature",
            **self.dict,
        }
        for k, v in expected.items():
            self.assertEqual(data[k], v)

        expected_keys = ["parentjob", "chemnode"]
        for key in expected_keys:
            self.assertTrue(key in data)

    def test_deserialize(self):
        chemnode = baker.make(ChemNode)
        data = {
            "@module": "mkite_db.orm.calcs.models",
            "@class": "Feature",
            "parentjob": {"id": chemnode.parentjob.id},
            "chemnode": {"id": chemnode.id},
            **self.dict,
        }
        serial = FeatureSerializer(data=data)

        self.assertTrue(serial.is_valid())

        new = serial.save()

        self.assertEqual(new.value, self.dict["value"])


class TestEnergyForcesSerializer(TestCase):
    def test_deserialize(self):
        chem = baker.make(ChemNode)
        data = {
            "@module": "mkite_db.orm.calcs.models",
            "@class": "EnergyForces",
            "parentjob": {"id": chem.parentjob.id},
            "chemnode": {"id": chem.id},
            "energy": -1,
            "forces": [[0, 0, 0]],
        }
        serial = EnergyForcesSerializer(data=data)
        self.assertTrue(serial.is_valid())

        new = serial.save()
        self.assertEqual(new.chemnode, chem)
        self.assertEqual(new.parentjob, chem.parentjob)
        self.assertEqual(new.energy, data["energy"])
        self.assertEqual(new.forces, data["forces"])

    def test_serialize(self):
        node = baker.make(EnergyForces)
        jobdata = JobSerializer(node.parentjob).data
        chemdata = ChemNodeSerializer(node.chemnode).data
        expected = {
            "id": node.id,
            "uuid": str(node.uuid),
            "parentjob": jobdata,
            "chemnode": chemdata,
            "energy": node.energy,
            "forces": node.forces,
            "@module": "mkite_db.orm.calcs.models",
            "@class": "EnergyForces",
        }
        serial = EnergyForcesSerializer(node)

        self.assertEqual(serial.data, expected)
