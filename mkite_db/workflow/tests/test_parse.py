import unittest as ut
from model_bakery import baker
from django.test import TestCase
from pkg_resources import resource_filename

from collections import namedtuple
from mkite_core.models import JobResults
from mkite_db.orm.jobs.models import Job, JobStatus, RunStats
from mkite_db.orm.structs.models import Crystal
from mkite_db.orm.calcs.models import EnergyForces

from mkite_db.workflow.parse import JobParser


RESULTS_FILE = resource_filename("mkite_db.tests.files.workflow", "jobresults.json")


class TestParser(TestCase):
    def setUp(self):
        self.results = JobResults.from_json(RESULTS_FILE)
        self.parser = JobParser(self.results)

    def test_create_stats(self):
        job = baker.make(Job, status="D")
        new = self.parser.create_stats(job)
        self.assertIsInstance(new, RunStats)

    def test_create_job(self):
        new = self.parser.create_job()
        self.assertIsInstance(new, Job)

    def test_create_chemnode(self):
        job = baker.make(Job, status="R")
        chemdict = self.results.nodes[0].chemnode

        new = self.parser.create_chemnode(chemdict, job)
        self.assertIsInstance(new, Crystal)

    def test_create_calcnode(self):
        chemnode = baker.make(Crystal)
        calcdict = self.results.nodes[0].calcnodes[0]

        new = self.parser.create_calcnode(calcdict, chemnode, chemnode.parentjob)
        self.assertIsInstance(new, EnergyForces)

    def test_create_nodes(self):
        job = baker.make(Job, status="R")
        nodes = self.parser.create_nodes(job)

        self.assertIsInstance(nodes, list)

        results = nodes[0]
        self.assertIsInstance(results.chemnode, Crystal)
        self.assertIsInstance(results.calcnodes, list)
        self.assertIsInstance(results.calcnodes[0], EnergyForces)

    def test_parse(self):
        out = self.parser.parse()

        self.assertIsInstance(out.job, Job)
        self.assertIsInstance(out.runstats, RunStats)
        self.assertIsInstance(out.nodes[0].chemnode, Crystal)
        self.assertIsInstance(out.nodes[0].calcnodes[0], EnergyForces)
