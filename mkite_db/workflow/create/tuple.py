import os
import itertools
from typing import List, Dict, Tuple

from django.db.models import QuerySet
from mkite_db.orm.base.models import ChemNode
from mkite_db.orm.jobs.models import Job

from .base import BaseJobCreator, JobCreationError


class TupleJobCreator(BaseJobCreator):
    def get_inputs(self) -> "List[QuerySet[ChemNode]]":
        inp_qs = self.get_input_queries()
        inp_to_exclude = self.get_inputs_with_jobs()
        inp_tuples = self.make_combinations(inp_qs, exclude=inp_to_exclude)

        return inp_tuples

    def get_existing_jobs(self) -> "QuerySet[Job]":
        return Job.objects.filter(
            experiment=self.out_experiment,
            recipe=self.out_recipe,
        )

    def get_inputs_with_jobs(self) -> List[Tuple[int]]:
        jobs = self.get_existing_jobs()
        job_inputs = jobs.values_list("id", "inputs")

        tuples = []
        for key, grp in itertools.groupby(job_inputs, key=lambda x: x[0]):
            inp_ids = tuple(sorted([x[1] for x in grp]))
            tuples.append(inp_ids)

        return tuples

    def get_input_queries(self) -> List[List[int]]:
        all_nodes = []
        for inpq in self.inputs:
            nodes = ChemNode.objects.filter(**inpq.filter)
            nodes = nodes.exclude(**inpq.exclude)
            nodes = list(nodes.values_list("id", flat=True))
            all_nodes.append(nodes)

        return all_nodes

    def make_combinations(
        self, query_sets: List[List[int]], exclude: List[Tuple[int]] = None
    ) -> List[QuerySet]:
        ninputs = len(query_sets)
        exclude = [] if exclude is None else exclude

        combinations = itertools.product(*query_sets)

        all_inputs = [
            ChemNode.objects.filter(id__in=tup)
            for tup in combinations
            if tuple(sorted(tup)) not in exclude
        ]

        return all_inputs

    def create(self, dry_run: bool = False) -> Tuple[List[Job], List[QuerySet]]:
        inputs = self.get_inputs()
        num_jobs = len(inputs)
        jobs = [self.job_template for n in range(num_jobs)]

        if dry_run:
            return jobs, inputs

        Job.objects.bulk_create(jobs, batch_size=self.batch_size)

        if self.tags:
            self.add_tags(jobs)

        JobParent = Job.inputs.through
        parents = [
            JobParent(chemnode_id=inp.id, job_id=job.id)
            for inp_set, job in zip(inputs, jobs)
            for inp in inp_set
        ]

        JobParent.objects.bulk_create(parents, batch_size=self.batch_size)

        return jobs, inputs
