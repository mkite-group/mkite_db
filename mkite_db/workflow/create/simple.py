from typing import List, Tuple

from django.db.models import QuerySet
from mkite_db.orm.base.models import ChemNode
from mkite_db.orm.jobs.models import Job

from .base import BaseJobCreator, JobCreationError


class SimpleJobCreator(BaseJobCreator):
    def get_inputs(self) -> "QuerySet[ChemNode]":
        if len(self.inputs) != 1:
            raise JobCreationError(
                f"Trying to use {self.__class__.__name__} with\
            more than one input specified. Please specify only one type\
            of input when using this class."
            )

        inp_kwargs = self.inputs[0]
        nodes = ChemNode.objects.filter(**inp_kwargs.filter)
        nodes = nodes.exclude(
            childjobs__experiment=self.out_experiment,
            childjobs__recipe=self.out_recipe,
            **inp_kwargs.exclude,
        )
        return nodes

    def create(self, dry_run: bool = False) -> Tuple[List[Job], QuerySet]:
        inputs = self.get_inputs()
        num_jobs = inputs.count()
        jobs = [self.job_template for n in range(num_jobs)]

        if dry_run:
            return jobs, inputs

        Job.objects.bulk_create(jobs, batch_size=self.batch_size)

        if self.tags:
            self.add_tags(jobs)

        JobParent = Job.inputs.through
        parents = [
            JobParent(chemnode_id=inp.id, job_id=job.id)
            for inp, job in zip(inputs, jobs)
        ]

        JobParent.objects.bulk_create(parents, batch_size=self.batch_size)

        return jobs, inputs
