import os
import shutil
import unittest as ut
from model_bakery import baker
from unittest.mock import patch
from django.test import TestCase

from mkite_db.orm.base.models import ChemNode
from mkite_db.orm.structs.models import Crystal
from mkite_db.orm.jobs.models import Job, JobStatus, JobRecipe, Experiment

from mkite_db.workflow.create import InputQuery
from mkite_db.workflow.create.simple import SimpleJobCreator


class TestJobCreator(TestCase):
    @classmethod
    def setUpClass(cls):
        super(TestJobCreator, cls).setUpClass()
        cls.inp_recipe = baker.make(JobRecipe)
        cls.out_recipe = baker.make(JobRecipe)
        cls.inp_experiment = baker.make(Experiment)
        cls.out_experiment = baker.make(Experiment)

        cls.chemnodes = baker.make(
            Crystal,
            _quantity=7,
            parentjob__recipe=cls.inp_recipe,
            parentjob__experiment=cls.inp_experiment,
            parentjob__status=JobStatus.DONE,
        )

        jobs = []
        for node in cls.chemnodes[:3]:
            job = baker.make(Job, recipe=cls.out_recipe, experiment=cls.out_experiment)
            job.inputs.add(node)
            jobs.append(job)

        cls.jobs = jobs

    @classmethod
    def tearDownClass(cls):
        pjobs = [node.parentjob for node in cls.chemnodes]

        for node in cls.chemnodes:
            node.delete()

        for j in cls.jobs + pjobs:
            j.delete()

        prj = cls.inp_experiment.project
        cls.inp_experiment.delete()
        prj.delete()

        prj = cls.out_experiment.project
        cls.out_experiment.delete()
        prj.delete()

        pkg = cls.out_recipe.package
        cls.out_recipe.delete()
        pkg.delete()

        pkg = cls.inp_recipe.package
        cls.inp_recipe.delete()
        pkg.delete()
        super(TestJobCreator, cls).tearDownClass()

    def setUp(self):
        inputs = [
            InputQuery(
                filter={
                    "parentjob__experiment__name": self.inp_experiment.name,
                    "parentjob__recipe__name": self.inp_recipe.name,
                },
            )
        ]

        self.creator = SimpleJobCreator(
            inputs,
            self.out_experiment.name,
            self.out_recipe.name,
            tags=["test_tag"],
        )

    def test_get_inputs(self):
        nodes = self.creator.get_inputs()
        self.assertEqual(nodes.count(), 4)
        self.assertFalse(self.chemnodes[-1] in nodes)

    def test_job_template(self):
        template = self.creator.job_template
        self.assertIsInstance(template, Job)

    def test_get_object(self):
        obj = self.creator.get_object(JobRecipe, id=self.inp_recipe.id)
        self.assertEqual(obj, self.inp_recipe)

    def test_create(self):
        nodes = self.creator.get_inputs()
        jobs, inputs = self.creator.create()

        self.assertEqual(len(jobs), 4)

        job = jobs[0]
        self.assertNotEqual(job.inputs.count(), 0)
        self.assertEqual(job.tags.count(), 1)
        tag = job.tags.first()
        self.assertEqual(str(tag), "test_tag")

        for j in jobs:
            j.delete()
