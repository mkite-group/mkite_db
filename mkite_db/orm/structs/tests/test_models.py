from model_bakery import baker
from django.test import TestCase

from mkite_db.orm.jobs.models import Job
from mkite_db.orm.structs.models import Crystal, SpaceGroups
from mkite_core.models import CrystalInfo


class CrystalCreator:
    def create_crystal(self):
        crystal = baker.make(
            Crystal,
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
