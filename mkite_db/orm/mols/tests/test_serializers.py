import json
from model_bakery import baker
from django.test import TestCase
from pkg_resources import resource_filename

from mkite_db.orm.base.models import Formula
from mkite_db.orm.jobs.models import Job
from mkite_db.orm.mols.models import Molecule, Conformer
from mkite_db.orm.mols.serializers import (
    MoleculeSerializer,
    ConformerSerializer,
)

from .test_models import MolCreator


TEST_CONFORMER = resource_filename("mkite_core.tests.files.models", "conformer.json")


class TestMolSerializer(TestCase):
    def setUp(self):
        self.creator = MolCreator()

    def test_serialize(self):
        mol = self.creator.create_molecule()
        serial = MoleculeSerializer(mol)
        data = serial.data

        expected = {
            "inchikey": "BSYNRYMUTXBXSQ-UHFFFAOYSA-N",
            "smiles": "CC(=O)OC1=CC=CC=C1C(=O)O",
            "attributes": {},
            "siteprops": {},
        }

        for k, v in expected.items():
            self.assertEqual(data[k], v)

    def test_deserialize(self):
        job = baker.make(Job)
        data = {
            "parentjob": {"id": job.id},
            "smiles": "CN1C=NC2=C1C(=O)N(C(=O)N2C)C",
            "attributes": {},
            "siteprops": {},
        }
        serial = MoleculeSerializer(data=data)
        self.assertTrue(serial.is_valid())

        newmol = serial.save()
        self.assertEqual(newmol.smiles, "Cn1c(=O)c2c(ncn2C)n(C)c1=O")
        self.assertEqual(newmol.formula.name, "H10 C8 N4 O2 +0")
        self.assertEqual(newmol.parentjob.uuid, job.uuid)
        self.assertEqual(newmol.inchikey, "RYYVLZVUVIJVGH-UHFFFAOYSA-N")


class TestConformerSerializer(TestCase):
    def setUp(self):
        self.creator = MolCreator()

    def get_conf_dict(self):
        with open(TEST_CONFORMER, "r") as f:
            return json.load(f)

    def test_serialize(self):
        conf = self.creator.create_conformer()
        serial = ConformerSerializer(conf)
        data = serial.data

        expected = {
            "species": conf.species,
            "coords": conf.coords,
            "attributes": {},
            "siteprops": {},
        }

        for k, v in expected.items():
            self.assertEqual(data[k], v)

    def test_deserialize(self):
        job = baker.make(Job)
        cdict = self.get_conf_dict()
        data = {
            "parentjob": {"id": job.id},
            "formula": cdict["formula"],
            "species": cdict["species"],
            "coords": cdict["coords"],
            "attributes": {},
            "siteprops": {},
        }
        serial = ConformerSerializer(data=data)
        self.assertTrue(serial.is_valid())

        new = serial.save()
        self.assertEqual(new.coords, data["coords"])
        self.assertEqual(new.formula.name, data["formula"]["name"])
        self.assertEqual(new.parentjob.uuid, job.uuid)
