from model_bakery import baker
from django.test import TestCase

from mkite_db.orm.base.models import Formula, ChemNode, CalcNode
from mkite_db.orm.jobs.models import Job
from mkite_db.orm.jobs.serializers import JobSerializer
from mkite_db.orm.base.serializers import (
    FormulaSerializer,
    ChemNodeSerializer,
    CalcNodeSerializer,
)


class TestFormulaSerializer(TestCase):
    @property
    def dict(self):
        return {
            "name": "H20 C8 N1 +1",
            "charge": 1,
        }

    def test_serialize(self):
        f = baker.make(Formula, **self.dict)
        serial = FormulaSerializer(f)
        data = serial.data

        self.assertTrue("id" in data)
        expected = {
            "@module": "mkite_db.orm.base.models",
            "@class": "Formula",
            "name": "H20 C8 N1 +1",
            "charge": 1,
        }
        for k, v in expected.items():
            self.assertEqual(data[k], v)

    def test_deserialize(self):
        serial = FormulaSerializer(data=self.dict)

        self.assertTrue(serial.is_valid())

        new = serial.save()

        self.assertEqual(new.name, self.dict["name"])
        self.assertEqual(new.charge, self.dict["charge"])


class TestChemSerializer(TestCase):
    def test_deserialize(self):
        job = baker.make(Job)
        data = {
            "@module": "mkite_db.orm.base.models",
            "@class": "ChemNode",
            "parentjob": {"id": job.id},
        }
        serial = ChemNodeSerializer(data=data)
        self.assertTrue(serial.is_valid())

        new = serial.save()
        self.assertEqual(new.parentjob, job)

    def test_serialize(self):
        node = baker.make(ChemNode)
        jobdata = JobSerializer(node.parentjob).data
        expected = {
            "@module": "mkite_db.orm.base.models",
            "@class": "ChemNode",
            "parentjob": jobdata,
            "id": node.id,
            "uuid": str(node.uuid),
        }
        serial = ChemNodeSerializer(node)

        self.assertEqual(serial.data, expected)


class TestCalcSerializer(TestCase):
    def test_deserialize(self):
        chem = baker.make(ChemNode)
        data = {
            "@module": "mkite_db.orm.base.models",
            "@class": "CalcNode",
            "parentjob": {"id": chem.parentjob.id},
            "chemnode": {"id": chem.id},
        }
        serial = CalcNodeSerializer(data=data)
        self.assertTrue(serial.is_valid())

        new = serial.save()
        self.assertEqual(new.chemnode, chem)
        self.assertEqual(new.parentjob, chem.parentjob)

    def test_serialize(self):
        node = baker.make(CalcNode)
        jobdata = JobSerializer(node.parentjob).data
        chemdata = ChemNodeSerializer(node.chemnode).data
        expected = {
            "@module": "mkite_db.orm.base.models",
            "@class": "CalcNode",
            "parentjob": jobdata,
            "chemnode": chemdata,
            "id": node.id,
            "uuid": str(node.uuid),
        }
        serial = CalcNodeSerializer(node)

        self.assertEqual(serial.data, expected)
