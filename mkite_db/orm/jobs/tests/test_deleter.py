import unittest as ut
from django.test import TestCase
from model_bakery import baker

from mkite_db.orm.models import Crystal, Job, RunStats
from mkite_db.orm.jobs.deleter import delete_tree


class TestDeleter(TestCase):
    def setUp(self):
        """Creates a tree of jobs"""
        self.node1 = baker.make(Crystal)
        self.node2 = baker.make(Crystal)
        self.node2.parentjob.inputs.add(self.node1)
        self.node3 = baker.make(Crystal, parentjob=self.node2.parentjob)

        self.node4 = baker.make(Crystal)
        self.node4.parentjob.inputs.add(self.node2)

        self.node5 = baker.make(Crystal)
        self.node5.parentjob.inputs.add(self.node3)

        self.leaf_job = baker.make(Job)
        self.leaf_stats = baker.make(RunStats)
        self.leaf_job.inputs.add(self.node5)
        self.leaf_job.runstats = self.leaf_stats
        self.leaf_job.save()

    def test_delete_leaf(self):
        delete_tree(self.leaf_job)
        self.assertIsNone(self.leaf_job.pk)
        self.assertIsNone(self.leaf_stats.pk)
        self.assertFalse(self.node5.childjobs.exists())

    def test_delete_node5(self):
        delete_tree(self.node5.parentjob)
        node5q = Crystal.objects.filter(id=self.node5.id)
        self.assertFalse(node5q.exists())
        self.assertFalse(self.node3.childjobs.exists())

    def test_delete_node2(self):
        delete_tree(self.node2.parentjob)
        node2q = Crystal.objects.filter(id=self.node2.id)
        self.assertFalse(node2q.exists())

    def test_delete_node1(self):
        delete_tree(self.node1.parentjob)
        qs = Crystal.objects.all()
        self.assertEqual(qs.count(), 0)
        self.assertEqual(Job.objects.count(), 0)
