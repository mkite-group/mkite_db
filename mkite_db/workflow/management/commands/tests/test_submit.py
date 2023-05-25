import os
import json
import shutil
import unittest as ut
from io import StringIO
from model_bakery import baker
from django.test import TestCase
from django.db import models
from django.core.management import call_command
from pkg_resources import resource_filename

from mkite_db.orm.jobs.models import Job, JobStatus, JobRecipe, Experiment, Project
from mkite_core.tests.tempdirs import run_in_tempdir
from mkite_db.workflow.management.commands.submit import Command, CommandError

from mkite_core.tests.tempdirs import run_in_tempdir
from mkite_engines import LocalProducer


ENGINE = resource_filename("mkite_db.tests.files", "engine.yaml")


class TestCommand(TestCase):
    def setUp(self):
        self.cmd = Command(stdout=StringIO(), stderr=StringIO())
        self.cmd.recipe = "test_recipe"
        self.cmd.project = "test_project"
        self.cmd.experiment = "test_experiment"

    def call_command(self, *args, **kwargs):
        call_command(
            "submit",
            *args,
            stdout=StringIO(),
            stderr=StringIO(),
            **kwargs,
        )

    def test_get_recipe_args(self):
        recipe = baker.make(JobRecipe, name="test_recipe")
        args = self.cmd.get_recipe_args()

        self.assertEqual(args, {"recipe": recipe.id})
        recipe.delete()

        self.cmd.recipe = None
        args = self.cmd.get_recipe_args()
        self.assertEqual(args, {})

    def test_get_experiment_args(self):
        prj = baker.make(Project, name="test_project")
        exp = baker.make(Experiment, name="test_experiment", project=prj)

        args = self.cmd.get_experiment_args()
        self.assertEqual(args, {"experiment": exp.id})

        self.cmd.experiment = None
        args = self.cmd.get_experiment_args()
        self.assertEqual(args, {"experiment__project": prj.id})

        self.cmd.project = None
        self.cmd.experiment = "test_experiment"
        args = self.cmd.get_experiment_args()
        self.assertEqual(args, {"experiment": exp.id})

        self.cmd.project = None
        self.cmd.experiment = None
        args = self.cmd.get_experiment_args()
        self.assertEqual(args, {})

        self.cmd.project = "nonexisting"
        with self.assertRaises(CommandError):
            self.cmd.get_experiment_args()

        exp.delete()
        prj.delete()

    def test_get_jobs(self):
        prj = baker.make(Project, name="test_project")
        exp = baker.make(Experiment, name="test_experiment", project=prj)
        recipe = baker.make(JobRecipe, name="test_recipe")

        njobs = 5
        jobs = baker.make(
            Job, njobs, recipe=recipe, experiment=exp, status=JobStatus.READY
        )

        self.cmd.recipe = recipe.name
        self.cmd.experiment = exp.name
        self.cmd.project = prj.name

        query = self.cmd.get_jobs()

        self.assertEqual(query.count(), njobs)

    @run_in_tempdir
    def test_command(self):
        prj = baker.make(Project)
        exp = baker.make(Experiment, project=prj)
        recipe = baker.make(JobRecipe)

        njobs = 5
        jobs = baker.make(
            Job, njobs, recipe=recipe, experiment=exp, status=JobStatus.READY
        )

        self.call_command(
            ENGINE,
            "--project",
            prj.name,
            "--experiment",
            exp.name,
            "--recipe",
            recipe.name,
        )
