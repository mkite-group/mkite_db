from model_bakery import baker
from django.test import TestCase

from mkite_db.orm.base.models import ChemNode, CalcNode, CalcType
from mkite_db.orm.jobs.models import Job
from mkite_db.orm.jobs.serializers import JobSerializer
from mkite_db.orm.base.serializers import (
    ChemNodeSerializer,
    CalcNodeSerializer,
    CalcTypeSerializer,
)


class TestCalcTypeSerializer(TestCase):
    def test_deserialize(self):
        data = {
            "@module": "mkite_db.orm.base.models",
            "@class": "CalcType",
            "name": "test_ctype",
        }
        serial = CalcTypeSerializer(data=data)
        self.assertTrue(serial.is_valid())

        new = serial.save()
        self.assertEqual(new.name, data["name"])

    def test_serialize(self):
        node = baker.make(CalcType)
        expected = {
            "id": node.id,
            "uuid": str(node.uuid),
            "name": node.name,
            "@module": "mkite_db.orm.base.models",
            "@class": "CalcType",
        }
        serial = CalcTypeSerializer(node)

        self.assertEqual(serial.data, expected)


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
        ctype = baker.make(CalcType)
        chem = baker.make(ChemNode)
        data = {
            "@module": "mkite_db.orm.base.models",
            "@class": "CalcNode",
            "parentjob": {"id": chem.parentjob.id},
            "chemnode": {"id": chem.id},
            "calctype": {"id": ctype.id, "name": ctype.name},
            "data": {"key": "value"},
        }
        serial = CalcNodeSerializer(data=data)
        self.assertTrue(serial.is_valid())

        new = serial.save()
        self.assertEqual(new.data, data["data"])
        self.assertEqual(new.calctype.name, ctype.name)
        self.assertEqual(new.chemnode.uuid, chem.uuid)
        self.assertEqual(new.parentjob.uuid, chem.parentjob.uuid)

    def test_serialize(self):
        ctype = baker.make(CalcType)
        node = baker.make(CalcNode)
        node.data["test"] = "value"
        node.calctype = ctype

        jobdata = JobSerializer(node.parentjob).data
        chemdata = ChemNodeSerializer(node.chemnode).data
        expected = {
            "@module": "mkite_db.orm.base.models",
            "@class": "CalcNode",
            "id": node.id,
            "uuid": str(node.uuid),
            "data": node.data,
            "parentjob": jobdata,
            "chemnode": chemdata,
        }
        serial = CalcNodeSerializer(node)
        data = serial.data

        for k, v in expected.items():
            self.assertEqual(v, data[k])

        self.assertEqual(data["calctype"]["uuid"], str(ctype.uuid))
