import unittest as ut
from model_bakery import baker
from unittest.mock import patch
from django.test import TestCase

from mkite_db.orm.base.models import ChemNode
from mkite_db.orm.structs.models import Crystal
from mkite_db.orm.jobs.models import Job, JobStatus, JobRecipe, Experiment

from mkite_db.workflow.create import InputQuery
from mkite_db.workflow.create.tuple import TupleJobCreator


class TestJobCreator(TestCase):
    @classmethod
    def setUpClass(cls):
        super(TestJobCreator, cls).setUpClass()
        cls.recipe_1 = baker.make(JobRecipe)
        cls.recipe_2 = baker.make(JobRecipe)
        cls.out_recipe = baker.make(JobRecipe)
        cls.inp_experiment = baker.make(Experiment)
        cls.out_experiment = baker.make(Experiment)

        cls.crystals = baker.make(
            Crystal,
            _quantity=7,
            parentjob__recipe=cls.recipe_1,
            parentjob__experiment=cls.inp_experiment,
            parentjob__status=JobStatus.DONE,
        )

        cls.conformers = baker.make(
            Crystal,
            _quantity=5,
            parentjob__recipe=cls.recipe_2,
            parentjob__experiment=cls.inp_experiment,
            parentjob__status=JobStatus.DONE,
        )

        NJOBS = 3
        jobs = []
        for crystal, conf in zip(cls.crystals[:NJOBS], cls.conformers[:NJOBS]):
            job = baker.make(Job, recipe=cls.out_recipe, experiment=cls.out_experiment)
            job.inputs.add(crystal)
            job.inputs.add(conf)
            jobs.append(job)

        cls.jobs = jobs

    @classmethod
    def tearDownClass(cls):
        pjobs = [node.parentjob for node in cls.crystals]
        pjobs += [node.parentjob for node in cls.conformers]

        for j in cls.jobs + pjobs:
            j.delete()

        for exp in [cls.inp_experiment, cls.out_experiment]:
            prj = exp.project
            exp.delete()
            prj.delete()

        for recipe in [cls.recipe_1, cls.recipe_2, cls.out_recipe]:
            pkg = recipe.package
            recipe.delete()
            pkg.delete()

        super(TestJobCreator, cls).tearDownClass()

    def setUp(self):
        inputs = [
            InputQuery(
                filter={
                    "parentjob__experiment__name": self.inp_experiment.name,
                    "parentjob__recipe__name": self.recipe_1.name,
                },
            ),
            InputQuery(
                filter={
                    "parentjob__experiment__name": self.inp_experiment.name,
                    "parentjob__recipe__name": self.recipe_2.name,
                },
            ),
        ]

        self.creator = TupleJobCreator(
            inputs,
            self.out_experiment.name,
            self.out_recipe.name,
            tags=["test_tag"],
        )

    def test_get_existing_jobs(self):
        jobs = self.creator.get_existing_jobs()
        self.assertEqual(jobs.count(), 3)

    def test_get_input_queries(self):
        qs = self.creator.get_input_queries()

        self.assertIsInstance(qs, list)
        self.assertEqual(len(qs), 2)
        self.assertIsInstance(qs[0], list)
        self.assertEqual(len(qs[0]), 7)
        self.assertEqual(len(qs[1]), 5)

        node_id = qs[0][0]
        node = ChemNode.objects.get(id=node_id)
        self.assertEqual(node.parentjob.recipe, self.recipe_1)
        self.assertEqual(node.parentjob.experiment, self.inp_experiment)

        node_id = qs[1][0]
        node = ChemNode.objects.get(id=node_id)
        self.assertEqual(node.parentjob.recipe, self.recipe_2)
        self.assertEqual(node.parentjob.experiment, self.inp_experiment)

    def test_make_combinations(self):
        group1 = [1, 2]
        group2 = [3, 4, 5]

        combs = self.creator.make_combinations([group1, group2], exclude=[(1, 4)])

        self.assertEqual(len(combs), 5)

    def test_get_inputs_with_jobs(self):
        tuples = self.creator.get_inputs_with_jobs()
        self.assertEqual(len(tuples), 3)
        self.assertIsInstance(tuples[0], tuple)

    def test_get_inputs(self):
        nodes = self.creator.get_inputs()
        self.assertEqual(len(nodes), 32)

        for qs in nodes:
            self.assertEqual(qs.count(), 2)
            self.assertIsInstance(qs.first(), ChemNode)

    def test_create(self):
        jobs, inputs = self.creator.create()

        self.assertEqual(len(jobs), 32)

        job = jobs[0]
        self.assertEqual(job.inputs.count(), 2)
        self.assertEqual(job.tags.count(), 1)

        for j in jobs:
            j.delete()
