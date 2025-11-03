import unittest as ut
from model_bakery import baker
from django.test import TestCase

from mkite_db.orm.base.models import ChemNode
from mkite_db.orm.base.serializers import ChemNodeSerializer
from mkite_db.orm.jobs.models import Job
from mkite_db.orm.jobs.serializers import JobSerializer
from mkite_db.orm.calcs.models import CalcType, GenericCalc
from mkite_db.orm.calcs.serializers import CalcTypeSerializer, GenericCalcSerializer


class TestCalcTypeSerializer(TestCase):
    def test_deserialize(self):
        data = {
            "@module": "mkite_db.orm.calcs.models",
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
            "@module": "mkite_db.orm.calcs.models",
            "@class": "CalcType",
        }
        serial = CalcTypeSerializer(node)

        self.assertEqual(serial.data, expected)


class TestGenericCalcSerializer(TestCase):
    def test_deserialize(self):
        ctype = baker.make(CalcType)
        chem = baker.make(ChemNode)
        data = {
            "@module": "mkite_db.orm.calcs.models",
            "@class": "GenericCalc",
            "parentjob": {"id": chem.parentjob.id},
            "chemnode": {"id": chem.id},
            "calctype": {"id": ctype.id, "name": ctype.name},
            "data": {"key": "value"}
        }
        serial = GenericCalcSerializer(data=data)
        self.assertTrue(serial.is_valid())

        new = serial.save()
        self.assertEqual(new.data, data["data"])
        self.assertEqual(new.calctype.name, ctype.name)
        self.assertEqual(new.chemnode.uuid, chem.uuid)
        self.assertEqual(new.parentjob.uuid, chem.parentjob.uuid)

    def test_serialize(self):
        node = baker.make(GenericCalc)
        node.data["test"] = "value"

        expected = {
            "id": node.id,
            "uuid": str(node.uuid),
            "data": node.data,
            "@module": "mkite_db.orm.calcs.models",
            "@class": "GenericCalc",
        }
        serial = GenericCalcSerializer(node)
        data = serial.data

        for k, v in expected.items():
            self.assertEqual(v, data[k])

        self.assertEqual(data["calctype"]["uuid"], str(node.calctype.uuid))
