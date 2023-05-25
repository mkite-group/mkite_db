import json
import unittest as ut
from io import StringIO
from model_bakery import baker
from pkg_resources import resource_filename
from django.test import TestCase
from django.core.management import call_command

from mkite_db.orm.structs.models import Crystal
from mkite_db.orm.jobs.models import Job, JobStatus, JobRecipe, Experiment


RULES_FILE = resource_filename("mkite_db.tests.files.workflow", "create_rules.yaml")


class TestCommand(TestCase):
    @classmethod
    def setUpClass(cls):
        super(TestCommand, cls).setUpClass()

        for n in range(1, 6):
            baker.make(JobRecipe, name=f"test_recipe{n}")

        for n in range(1, 3):
            baker.make(Experiment, name=f"test_exp{n}")

    def call_command(self, *args, **kwargs):
        call_command(
            "create_from_file",
            *args,
            stdout=StringIO(),
            stderr=StringIO(),
            **kwargs,
        )

    def test_command(self):
        self.call_command("simple", RULES_FILE)

    def test_dry_run(self):
        self.call_command(
            "simple",
            RULES_FILE,
            "--dry_run",
        )
