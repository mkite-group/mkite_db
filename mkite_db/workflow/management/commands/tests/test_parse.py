import os
import shutil
from io import StringIO
from django.test import TestCase
from django.core.management import call_command
from pkg_resources import resource_filename

from mkite_db.orm.jobs.models import Job
from mkite_core.models import JobResults, Status
from mkite_core.external import load_config
from mkite_core.tests.tempdirs import run_in_tempdir
from mkite_db.workflow.management.commands.parse import Command
from mkite_engines.local import LOCAL_QUEUE_PREFIX


ENGINE = resource_filename("mkite_db.tests.files", "engine.yaml")
ENGINE_CFG = load_config(ENGINE)
JOB_RESULTS_FILE = resource_filename("mkite_db.tests.files.workflow", "jobresults.json")


def _prepare_folder():
    parsing = f"{LOCAL_QUEUE_PREFIX}{Status.PARSING.value}"
    path = os.path.join(ENGINE_CFG["root_path"], parsing)
    os.mkdir(path)
    shutil.copy(JOB_RESULTS_FILE, path)
    return path


class TestParserCommand(TestCase):
    def call_command(self, *args, **kwargs):
        call_command(
            "parse",
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
        
        self.assertTrue(cmd.is_valid_parse(info))

    def test_parse_result(self):
        cmd = self.get_command()
        info = self.get_info()
        out = cmd.parse_result(info)

        self.assertTrue(out is not None)
        self.assertIsInstance(out.job, Job)
        self.assertTrue(hasattr(out.job, "id"))

    @run_in_tempdir
    def test_parse_all(self):
        cmd = self.get_command()
        folder = _prepare_folder()
        cmd.engine = cmd.get_engine(ENGINE)

        nparsed, nerrors = cmd.parse_all(num_parse=10)

        self.assertEqual(nparsed, 1)
        self.assertEqual(nerrors, 0)

    @run_in_tempdir
    def test_call(self):
        _prepare_folder()
        self.call_command(ENGINE)

        info = self.get_info()
        query = Job.objects.filter(
            experiment__name=info.job["experiment"]["name"],
            recipe__name=info.job["recipe"]["name"],
            runstats__cluster=info.runstats.cluster,
        )
        self.assertTrue(query.exists())
