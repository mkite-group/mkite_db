import json
import unittest as ut
from io import StringIO
from model_bakery import baker
from django.test import TestCase
from django.core.management import call_command

from mkite_db.orm.structs.models import Crystal
from mkite_db.orm.jobs.models import Job, JobStatus, JobRecipe, Experiment


class TestCommand(TestCase):
    @classmethod
    def setUpClass(cls):
        super(TestCommand, cls).setUpClass()
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

    def call_command(self, *args, **kwargs):
        call_command(
            "create_simple",
            *args,
            stdout=StringIO(),
            stderr=StringIO(),
            **kwargs,
        )

    def test_command(self):
        opts = json.dumps({"test": 1})

        query = Job.objects.filter(
            experiment=self.out_experiment,
            recipe=self.out_recipe,
            status=JobStatus.READY,
        )
        self.assertEqual(query.count(), 3)

        tag = "test_tag1"
        self.call_command(
            self.inp_experiment.name,
            self.inp_recipe.name,
            self.out_experiment.name,
            self.out_recipe.name,
            "--options",
            opts,
            "--tags",
            tag,
        )

        query = Job.objects.filter(
            recipe=self.out_recipe,
            status=JobStatus.READY,
            tags__name=tag,
        )
        self.assertEqual(query.count(), 4)

        query = Job.objects.filter(
            recipe=self.out_recipe,
            status=JobStatus.READY,
        )
        self.assertEqual(query.count(), 7)
