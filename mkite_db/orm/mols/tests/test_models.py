from model_bakery import baker
from django.test import TestCase

from mkite_db.orm.base.models import Formula
from mkite_db.orm.jobs.models import Job
from mkite_db.orm.mols.models import Molecule, Conformer


class MolCreator:
    def create_formula(self):
        formula, _ = Formula.objects.get_or_create(name="C9 H8 O4 +0", charge=0)
        return formula

    def create_molecule(self):
        ikey = "BSYNRYMUTXBXSQ-UHFFFAOYSA-N"
        mols = Molecule.objects.filter(inchikey=ikey)
        if mols.exists():
            return mols.first()

        mol = baker.make(
            Molecule,
            formula=self.create_formula(),
            inchikey=ikey,
            smiles="CC(=O)OC1=CC=CC=C1C(=O)O",
        )
        return mol

    def create_conformer(self):
        conf = baker.make(
            Conformer,
            formula=self.create_formula(),
            mol=self.create_molecule(),
            species=[
                "C",
                "C",
                "O",
                "O",
                "C",
                "C",
                "C",
                "C",
                "C",
                "C",
                "C",
                "O",
                "O",
                "H",
                "H",
                "H",
                "H",
                "H",
                "H",
                "H",
                "H",
            ],
        )
        return conf


class TestMols(TestCase):
    def setUp(self):
        self.creator = MolCreator()

    def test_molecule(self):
        mol = self.creator.create_molecule()

        self.assertTrue(hasattr(mol, "parentjob"))
        self.assertTrue(hasattr(mol, "chemnode_ptr"))
        self.assertEqual(mol.inchikey, "BSYNRYMUTXBXSQ-UHFFFAOYSA-N")
        self.assertEqual(mol.smiles, "CC(=O)OC1=CC=CC=C1C(=O)O")
        self.assertEqual(repr(mol), f"<Molecule: {mol.inchikey} ({mol.id})>")

    def test_formula(self):
        formula = self.creator.create_formula()
        self.assertEqual(formula.name, "C9 H8 O4 +0")

    def test_molecule_dict(self):
        mol = self.creator.create_molecule()
        data = mol.as_dict()

        expected = {
            "@module": "mkite_db.orm.mols.models",
            "@class": "Molecule",
            "id": mol.id,
            "uuid": str(mol.uuid),
            "ctime": mol.ctime,
            "mtime": mol.mtime,
            "parentjob": mol.parentjob.id,
            "chemnode_ptr": mol.chemnode_ptr.id,
            "attributes": mol.attributes,
            "siteprops": mol.siteprops,
            "formula": mol.formula.id,
            "inchikey": mol.inchikey,
            "smiles": mol.smiles,
            "tags": [],
        }

        self.assertEqual(data, expected)

        node = mol.chemnode_ptr
        self.assertEqual(node.get_data(), expected)

    def test_conformer(self):
        conf = self.creator.create_conformer()

        self.assertTrue(hasattr(conf, "parentjob"))
        self.assertTrue(hasattr(conf, "chemnode_ptr"))
        self.assertTrue(hasattr(conf, "mol"))
        self.assertEqual(len(conf.species), 21)
        self.assertEqual(
            repr(conf),
            f"<Conformer: {conf.formula.name}, Mol {conf.mol.inchikey} ({conf.id})>",
        )
