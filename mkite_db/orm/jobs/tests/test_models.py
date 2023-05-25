from datetime import timedelta
from django.test import TestCase
from mkite_db.orm.jobs.models import (
    Project,
    Experiment,
    JobStatus,
    Job,
    JobRecipe,
    JobPackage,
    RunStats,
)
from mkite_core.models import JobInfo, RunStatsInfo


class JobTestCreator:
    def create_project(self):
        prj, _ = Project.objects.get_or_create(
            name="test_prj", description="project for testing purposes"
        )
        return prj

    def create_experiment(self):
        prj = self.create_project()
        exp, _ = Experiment.objects.get_or_create(
            name="test_exp",
            description="first experiment",
            project=prj,
        )
        return exp

    def create_package(self):
        pkg, _ = JobPackage.objects.get_or_create(
            name="test_pkg",
        )
        return pkg

    def create_recipe(self):
        pkg = self.create_package()
        recipe, _ = JobRecipe.objects.get_or_create(
            name="test_recipe",
            package=pkg,
            method="DFT",
        )
        return recipe

    def create_runstats(self):
        stats, _ = RunStats.objects.get_or_create(
            host="test_host",
            cluster="test_cluster",
            duration=timedelta(seconds=3600),
            ncores=8,
            ngpus=0,
            pkgversion="1.0",
        )
        return stats

    def create_job(self):
        job, _ = Job.objects.get_or_create(
            experiment=self.create_experiment(),
            recipe=self.create_recipe(),
            runstats=self.create_runstats(),
            status=JobStatus.READY,
            isroot=True,
        )
        job.tags.add("tag1", "tag2")
        return job


class TestJobModels(TestCase):
    def setUp(self):
        self.creator = JobTestCreator()

    def test_project(self):
        prj = self.creator.create_project()
        newprj = Project.objects.get(name=prj.name)
        self.assertEqual(newprj, prj)

    def test_experiment(self):
        exp = self.creator.create_experiment()
        newexp = Experiment.objects.get(name=exp.name)
        self.assertEqual(exp, newexp)

    def test_package(self):
        pkg = self.creator.create_package()
        newpkg = JobPackage.objects.get(name=pkg.name)
        self.assertEqual(pkg, newpkg)

    def test_recipe(self):
        recipe = self.creator.create_recipe()
        newrecipe = JobRecipe.objects.get(name=recipe.name)
        self.assertEqual(recipe, newrecipe)

    def test_recipe_dict(self):
        recipe = self.creator.create_recipe()

        rdict = recipe.as_dict()
        self.assertTrue("uuid" in rdict)
        self.assertEqual(rdict["name"], recipe.name)
        self.assertEqual(rdict["package"], "test_pkg")
        self.assertEqual(rdict["method"], "DFT")

    def test_job(self):
        job = self.creator.create_job()
        newjob = Job.objects.get(
            status=JobStatus.READY, isroot=True, recipe__name="test_recipe"
        )
        self.assertEqual(newjob, job)

    def test_job_info(self):
        job = self.creator.create_job()
        info = job.as_info()
        self.assertIsInstance(info, JobInfo)

    def test_job_dict(self):
        job = self.creator.create_job()
        data = job.as_dict()
        expected = {
            "id": job.id,
            "uuid": str(job.uuid),
            "ctime": job.ctime,
            "project": job.experiment.project.name,
            "experiment": job.experiment.name,
        }
        self.assertEqual(data, expected)


class TestRunStats(TestCase):
    def setUp(self):
        self.creator = JobTestCreator()
        self.stats = self.creator.create_runstats()

    def test_create(self):
        self.assertFalse(self.stats.id is None)
        self.assertEqual(self.stats.host, "test_host")
        self.assertEqual(self.stats.cluster, "test_cluster")

    def test_dict(self):
        expected = {
            "host": "test_host",
            "cluster": "test_cluster",
            "duration": timedelta(seconds=3600),
            "ncores": 8,
            "ngpus": 0,
            "pkgversion": "1.0",
        }

        self.assertEqual(self.stats.as_dict(), expected)

    def test_info(self):
        info = self.stats.as_info()
        self.assertIsInstance(info, RunStatsInfo)

        new = RunStats.from_info(info)

    def test_duration(self):
        t = 1800
        duration = RunStats.duration_from_seconds(t)

        self.assertIsInstance(duration, timedelta)
        self.assertEqual(duration, timedelta(seconds=t))
