import os
from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError

from mkite_core.models import Status
from mkite_engines import EngineRoles, instantiate_from_path
from mkite_db.orm.jobs.models import Job, JobStatus, JobRecipe, Experiment, Project


class Command(BaseCommand):
    help = "Submits jobs using a given engine"

    def log(self, style, msg):
        style_fn = getattr(self.style, style.upper())
        return self.stdout.write(style_fn(msg))

    def add_arguments(self, argparser):
        argparser.add_argument(
            "engine_config",
            type=str,
            help="path to the configuration file for the engine that will be used to submit the jobs",
        )
        argparser.add_argument(
            "-r",
            "--recipe",
            type=str,
            default=None,
            help="Name of the recipe of the jobs to be submittted",
        )
        argparser.add_argument(
            "-p",
            "--project",
            type=str,
            default=None,
            help="Name of the project of the jobs to be submittted",
        )
        argparser.add_argument(
            "-e",
            "--experiment",
            type=str,
            default=None,
            help="Name of the experiment of the jobs to be submittted",
        )
        argparser.add_argument(
            "--dry_run",
            action="store_true",
            help="If set, does not submit anything",
        )
        return argparser

    def handle(self, engine_config, *args, dry_run=False, **kwargs):
        self.project = kwargs["project"]
        self.experiment = kwargs["experiment"]
        self.recipe = kwargs["recipe"]

        self.pub = instantiate_from_path(engine_config, role=EngineRoles.producer)

        jobs = self.get_jobs(**kwargs)

        num_jobs = jobs.count()
        if num_jobs == 0:
            self.log("error", "No jobs to submit. Exiting...")
            return

        if dry_run:
            self.log("success", f"(DRY_RUN) would have submitted {num_jobs} jobs.")
            return

        for job in jobs:
            self.submit_job(job)

        self.log("success", f"Submitted {num_jobs} jobs.")

    def get_jobs(self, **kwargs) -> models.QuerySet:
        self.log("notice", "Submitting jobs with the following constraints:")
        self.log("notice", f"Project: {self.project}")
        self.log("notice", f"Experiment: {self.experiment}")
        self.log("notice", f"Recipe: {self.recipe}")

        exp_args = self.get_experiment_args()
        rec_args = self.get_recipe_args()
        query = Job.objects.filter(
            status=JobStatus.READY,
            **exp_args,
            **rec_args,
        ).order_by("ctime")
        return query

    def get_experiment_args(self) -> dict:
        """Queries the experiments and returns the args of the query for
        the job. If the experiment is not specified, uses only the project
        name. If the project name is not specified, uses the experiment name.
        If neither are specified, simply submit all jobs."""
        try:
            if self.experiment is None and self.project is None:
                return {}

            elif self.experiment is None:
                prj = Project.objects.get(name=self.project)
                return {"experiment__project": prj.id}

            elif self.project is None:
                exp = Experiment.objects.get(name=self.experiment)
                return {"experiment": exp.id}

            else:
                exp = Experiment.objects.get(
                    name=self.experiment,
                    project__name=self.project,
                )
                return {"experiment": exp.id}

        except ObjectDoesNotExist:
            raise CommandError(
                f"Experiment {self.experiment} with project {self.project}\
                does not exist."
            )

    def get_recipe_args(self) -> dict:
        """Queries the recipes and returns the args of the query for
        the job. If the recipe is not specified, uses all recipes."""
        try:
            if self.recipe is None:
                return {}

            recipe = JobRecipe.objects.get(name=self.recipe)
            return {"recipe": recipe.id}

        except ObjectDoesNotExist:
            raise CommandError(f"Recipe {self.recipe} does not exist.")

    def submit_job(self, job: Job):
        info = job.as_info()
        recipe = job.recipe.name
        self.pub.push_info(recipe, info)
        job.status = JobStatus.RUNNING
        job.save()
        self.log("success", f"Submitted Job ID {job.id}.")
