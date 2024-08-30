import os
import json
import shutil
import unittest as ut
from unittest.mock import patch
from io import StringIO
from model_bakery import baker
from django.test import TestCase, SimpleTestCase
from django.core.management import call_command

from pkg_resources import resource_filename

from mkite_db.orm.jobs.models import Job, Experiment, Project
from mkite_core.models import JobResults
from mkite_core.tests.tempdirs import run_in_tempdir
from mkite_db.workflow.management.commands.dbimport import Command, DB_IMPORTERS

from mkite_db.dbimport.tests.test_mp import MockMPImporter


JOB_RESULTS_FILE = resource_filename("mkite_db.tests.files.workflow", "jobresults.json")
MP_QUERY_FILE = resource_filename("mkite_db.tests.files.dbimport", "mp_query.json")

MOCK_DB_IMPORTERS = {
    "MockMPImporter": MockMPImporter,
}


class QueryMixin:
    def get_query(self):
        with open(MP_QUERY_FILE, "r") as f:
            data = json.load(f)

        return data

    def get_query_string(self):
        return json.dumps(self.get_query()[0])


class CommandSimpleTests(SimpleTestCase, QueryMixin):
    def setUp(self):
        self.cmd = Command()

    def get_kwargs(self):
        return {
            "project": "test_dbimport",
            "experiment": "test",
        }

    def test_db_importers(self):
        self.assertTrue("MPImporter" in DB_IMPORTERS)

    def test_query_args(self):
        self.cmd.json_as_file = False
        kwargs = {
            **self.get_kwargs(),
            "query": self.get_query_string(),
        }
        query = self.cmd.get_query_args(**kwargs)
        self.assertEqual(query, self.get_query()[0])

        kwargs = {
            **self.get_kwargs(),
            "file": MP_QUERY_FILE,
        }
        query = self.cmd.get_query_args(**kwargs)
        self.assertEqual(query, self.get_query())


class TestCommand(TestCase, QueryMixin):
    def call_command(self, *args, **kwargs):
        call_command(
            "dbimport",
            *args,
            stdout=StringIO(),
            stderr=StringIO(),
            **kwargs,
        )

    def get_command(self):
        return Command(stdout=StringIO(), stderr=StringIO())

    def get_info(self):
        return JobResults.from_json(JOB_RESULTS_FILE)

    def test_is_valid_parse(self):
        cmd = self.get_command()
        info = self.get_info()
        info.job["options"]["test"] = "test_options"

        cmd.project = info.job["experiment"]["project"]["name"]
        cmd.experiment = info.job["experiment"]["name"]

        self.assertTrue(cmd.is_valid_parse(info))

        job = baker.make(
            Job,
            project__name=cmd.project,
            experiment__name=cmd.experiment,
            options=info.job["options"],
        )

        self.assertFalse(cmd.is_valid_parse(info))
        job.delete()

    def test_save_jobresults(self):
        cmd = self.get_command()
        info = self.get_info()
        cmd.project = info.job["experiment"]["project"]["name"]
        cmd.experiment = info.job["experiment"]["name"]

        out = cmd.save_jobresults(info)

        self.assertTrue(out is not None)
        self.assertIsInstance(out.job, Job)
        self.assertTrue(hasattr(out.job, "id"))

    @ut.skipIf("MP_API_KEY" not in os.environ, "MP_API_KEY is not in environment")
    @patch.dict(
        "mkite_db.workflow.management.commands.dbimport.DB_IMPORTERS", MOCK_DB_IMPORTERS
    )
    def test_call(self):
        self.call_command(
            "MockMPImporter",
            "--project",
            "test_dbimport",
            "--experiment",
            "test_exp",
            "--query",
            self.get_query_string(),
        )
