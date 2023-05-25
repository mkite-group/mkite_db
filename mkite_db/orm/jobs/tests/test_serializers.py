import unittest as ut
from datetime import timedelta
from model_bakery import baker
from django.test import TestCase
from rest_framework import serializers
from collections.abc import Mapping

from mkite_db.orm.jobs.models import (
    Project,
    Experiment,
    JobPackage,
    JobRecipe,
    RunStats,
    Job,
    JobStatus,
)
from mkite_db.orm.jobs.serializers import (
    ProjectSerializer,
    ExperimentSerializer,
    JobPackageSerializer,
    JobRecipeSerializer,
    RunStatsSerializer,
    JobSerializer,
)

from .test_models import JobTestCreator


class SerializerTester(TestCase):
    def setUp(self):
        self.creator = JobTestCreator()


class TestProjectSerializer(SerializerTester):
    def test_serialize(self):
        obj = self.creator.create_project()
        serial = ProjectSerializer(obj)
        data = serial.data

        expected = {
            "id": obj.id,
            "uuid": str(obj.uuid),
            "name": "test_prj",
            "description": "project for testing purposes",
        }

        for k, v in expected.items():
            self.assertEqual(data[k], v)

    def test_deserialize(self):
        data = {
            "name": "test_prj_2",
            "description": "testing",
        }
        serial = ProjectSerializer(data=data)
        self.assertTrue(serial.is_valid())

        new = serial.save()
        self.assertEqual(new.name, "test_prj_2")
        self.assertEqual(new.description, "testing")


class TestExperimentSerializer(SerializerTester):
    def test_serialize(self):
        obj = self.creator.create_experiment()
        serial = ExperimentSerializer(obj)
        data = serial.data

        expected = {
            "id": obj.id,
            "uuid": str(obj.uuid),
            "name": "test_exp",
            "description": "first experiment",
        }

        self.assertTrue("project" in data)
        for k, v in expected.items():
            self.assertEqual(data[k], v)

    def test_deserialize(self):
        prj = baker.make(Project)
        data = {
            "project": {"id": prj.id},
            "name": "test_exp_2",
            "description": "testing",
        }
        serial = ExperimentSerializer(data=data)
        serial.is_valid()
        self.assertTrue(serial.is_valid())

        new = serial.save()
        self.assertEqual(new.project.name, prj.name)
        self.assertEqual(new.name, "test_exp_2")
        self.assertEqual(new.description, "testing")


class TestJobPackageSerializer(SerializerTester):
    def test_serialize(self):
        obj = self.creator.create_package()
        serial = JobPackageSerializer(obj)
        data = serial.data

        expected = {
            "id": obj.id,
            "uuid": str(obj.uuid),
            "name": obj.name,
        }

        for k, v in expected.items():
            self.assertEqual(data[k], v)

    def test_deserialize(self):
        data = {
            "name": "test_pkg_2",
        }
        serial = JobPackageSerializer(data=data)
        self.assertTrue(serial.is_valid())

        new = serial.save()
        for k, v in data.items():
            self.assertEqual(getattr(new, k), v)


class TestJobRecipeSerializer(SerializerTester):
    def test_serialize(self):
        obj = self.creator.create_recipe()
        serial = JobRecipeSerializer(obj)
        data = serial.data

        expected = {
            "id": obj.id,
            "uuid": str(obj.uuid),
            "name": obj.name,
            "method": obj.method,
        }

        self.assertTrue("package" in data)
        for k, v in expected.items():
            self.assertEqual(data[k], v)

    def test_deserialize(self):
        pkg = baker.make(JobPackage)
        data = {
            "package": {"uuid": pkg.uuid},
            "name": "test_recipe_2",
            "method": "FF",
        }
        serial = JobRecipeSerializer(data=data)
        self.assertTrue(serial.is_valid())

        new = serial.save()
        for k, v in data.items():
            if not isinstance(v, Mapping):
                self.assertEqual(getattr(new, k), v)


class TestRunStatsSerializer(SerializerTester):
    def test_serialize(self):
        obj = self.creator.create_runstats()
        serial = RunStatsSerializer(obj)
        data = serial.data

        expected = {
            "id": obj.id,
            "uuid": str(obj.uuid),
            "host": obj.host,
            "cluster": obj.cluster,
            "duration": obj.duration.total_seconds(),
            "ncores": obj.ncores,
            "ngpus": obj.ngpus,
            "pkgversion": obj.pkgversion,
        }

        for k, v in expected.items():
            self.assertEqual(data[k], v)

    def test_deserialize(self):
        data = {
            "host": "test_host_2",
            "cluster": "test_cluster_2",
            "duration": timedelta(seconds=1000),
            "ncores": 6,
            "ngpus": 1,
            "pkgversion": "1.0",
        }
        serial = RunStatsSerializer(data=data)
        self.assertTrue(serial.is_valid())

        new = serial.save()
        for k, v in data.items():
            self.assertEqual(getattr(new, k), v)

    def test_deserialize_duration_float(self):
        data = {
            "host": "test_host_2",
            "cluster": "test_cluster_2",
            "duration": 0.03,
            "ncores": 6,
            "ngpus": 1,
            "pkgversion": "1.0",
        }
        serial = RunStatsSerializer(data=data)
        self.assertTrue(serial.is_valid())

        new = serial.save()
        for k, v in data.items():
            if k == "duration":
                continue

            self.assertEqual(getattr(new, k), v)

    def test_deserialize_duration_decimal(self):
        data = {
            "host": "test_host_2",
            "cluster": "test_cluster_2",
            "duration": 0.5329999990000000000003,
            "ncores": 6,
            "ngpus": 1,
            "pkgversion": "1.0",
        }
        serial = RunStatsSerializer(data=data)
        self.assertTrue(serial.is_valid())

        new = serial.save()
        for k, v in data.items():
            if k == "duration":
                continue

            self.assertEqual(getattr(new, k), v)


class TestJobSerializer(SerializerTester):
    def test_serialize(self):
        obj = self.creator.create_job()
        serial = JobSerializer(obj)
        data = serial.data

        expected = {
            "id": obj.id,
            "uuid": str(obj.uuid),
            "status": obj.status,
            "isroot": obj.isroot,
        }

        for k in ["experiment", "recipe", "runstats", "tags"]:
            self.assertTrue(k in data)

        for k, v in expected.items():
            self.assertEqual(data[k], v)

    def test_deserialize(self):
        recipe = baker.make(JobRecipe)
        experiment = baker.make(Experiment)
        runstats_data = {
            "host": "test_host_2",
            "cluster": "test_cluster_2",
            "duration": timedelta(seconds=1000),
            "ncores": 6,
            "ngpus": 1,
        }
        job_data = {
            "experiment": {"id": experiment.id},
            "recipe": {"name": recipe.name},
            "runstats": runstats_data,
            "status": JobStatus.DONE,
            "tags": ["tag_1", "tag_2"],
        }

        serial = JobSerializer(data=job_data)
        self.assertTrue(serial.is_valid())

        new = serial.save()
        for k, v in job_data.items():
            if not isinstance(v, Mapping) and k != "tags":
                self.assertEqual(getattr(new, k), v)

    def test_invalid_runstats(self):
        recipe = baker.make(JobRecipe)
        experiment = baker.make(Experiment)
        invalid_runstats_data = {
            "ncores": 6,
            "ngpus": 1,
        }
        job_data = {
            "experiment": {"id": experiment.id},
            "recipe": {"id": recipe.id},
            "runstats": invalid_runstats_data,
            "status": JobStatus.DONE,
        }
        serial = JobSerializer(data=job_data)
        self.assertTrue(serial.is_valid())
        with self.assertRaises(serializers.ValidationError):
            serial.save()

    def test_deserialize_new_job(self):
        recipe = baker.make(JobRecipe)
        experiment = baker.make(Experiment)
        job_data = {
            "experiment": {"id": experiment.id},
            "recipe": {"name": recipe.name},
            "status": JobStatus.READY,
        }

        serial = JobSerializer(data=job_data)
        self.assertTrue(serial.is_valid())

        new = serial.save()
        for k, v in job_data.items():
            if not isinstance(v, Mapping):
                self.assertEqual(getattr(new, k), v)
