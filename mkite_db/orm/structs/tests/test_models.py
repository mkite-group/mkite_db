from model_bakery import baker
from django.test import TestCase

from mkite_db.orm.base.models import Formula
from mkite_db.orm.jobs.models import Job
from mkite_db.orm.structs.models import Crystal, SpaceGroups
from mkite_core.models import CrystalInfo


class CrystalCreator:
    def create_formula(self):
        formula, _ = Formula.objects.get_or_create(
            name="Si2 +0",
            charge=0,
        )
        return formula

    def create_crystal(self):
        crystal = baker.make(
            Crystal,
            formula=self.create_formula(),
            spacegroup=SpaceGroups(227),
            species=["Si", "Si"],
            coords=[[0.0, 0.0, 0.0], [1.365, 1.365, 1.365]],
            lattice=[[0.0, 2.73, 2.73], [2.73, 0.0, 2.73], [2.73, 2.73, 0.0]],
        )
        return crystal


class TestStructs(TestCase):
    def setUp(self):
        self.creator = CrystalCreator()

    def test_crystal(self):
        crystal = self.creator.create_crystal()

        self.assertTrue(hasattr(crystal, "parentjob"))
        self.assertTrue(hasattr(crystal, "chemnode_ptr"))
        self.assertTrue(hasattr(crystal, "tags"))

        self.assertEqual(crystal.spacegroup, 227)
        self.assertEqual(crystal.species, ["Si", "Si"])

        info = crystal.as_info()
        self.assertIsInstance(info, CrystalInfo)

    def test_formula(self):
        formula = self.creator.create_formula()
        self.assertEqual(formula.name, "Si2 +0")
        self.assertEqual(formula.charge, 0)
