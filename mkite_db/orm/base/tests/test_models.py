from model_bakery import baker
from datetime import timedelta
from django.test import TestCase
from mkite_db.orm.base.models import (
    ChemNode,
    CalcNode,
    Formula,
    Elements,
)


class TestBase(TestCase):
    def test_chem(self):
        node = baker.make(ChemNode)
        self.assertTrue(hasattr(node, "parentjob"))

    def test_calc(self):
        node = baker.make(CalcNode)
        self.assertTrue(hasattr(node, "parentjob"))
        self.assertTrue(hasattr(node, "chemnode"))
        self.assertTrue(isinstance(node.chemnode, ChemNode))

    def test_formula(self):
        formula = baker.make(Formula)
        self.assertTrue(hasattr(formula, "name"))
