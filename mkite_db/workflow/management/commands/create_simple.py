import json
from typing import List
from django.db import transaction
from django.core.management.base import BaseCommand, CommandError

from mkite_db.workflow.create import InputQuery, SimpleJobCreator


class Command(BaseCommand):
    help = "Creates jobs according to the given input/output recipes"

    def log(self, style, msg):
        style_fn = getattr(self.style, style.upper())
        return self.stdout.write(style_fn(msg))

    def add_arguments(self, argparser):
        argparser.add_argument(
            "inp_experiment",
            type=str,
            help="Name of the experiment of the inputs",
        )
        argparser.add_argument(
            "inp_recipe",
            type=str,
            help="Name of the recipe of the ChemNodes to be considered as inputs",
        )
        argparser.add_argument(
            "out_experiment",
            type=str,
            help="Name of the experiment of the outputs",
        )
        argparser.add_argument(
            "out_recipe",
            type=str,
            default=None,
            help="Name of the recipe of the job to be executed",
        )
        argparser.add_argument(
            "-o",
            "--options",
            type=str,
            default=None,
            help="JSON string containing the options for the job to created",
        )
        argparser.add_argument(
            "-f",
            "--filter_kwargs",
            type=str,
            default=None,
            help="JSON string containing additional query options for selecting inputs",
        )
        argparser.add_argument(
            "-x",
            "--exclude_kwargs",
            type=str,
            default=None,
            help="JSON string containing additional query options for excluding inputs",
        )
        argparser.add_argument(
            "-t",
            "--tags",
            type=str,
            nargs="+",
            help="tags to be added to the jobs",
        )
        argparser.add_argument(
            "-b",
            "--batch_size",
            type=int,
            default=None,
            help="Size of the batch when bulk creating new database objects",
        )
        argparser.add_argument(
            "--dry_run",
            action="store_true",
            help="If set, does not store anything into the database",
        )
        return argparser

    @transaction.atomic
    def handle(
        self,
        inp_experiment,
        inp_recipe,
        out_experiment,
        out_recipe,
        *args,
        options=None,
        filter_kwargs=None,
        exclude_kwargs=None,
        tags=None,
        batch_size=None,
        dry_run=False,
        **kwargs,
    ):
        if options is not None:
            options = json.loads(options)

        inputs = self.get_input_query(
            inp_experiment=inp_experiment,
            inp_recipe=inp_recipe,
            filter_kwargs=filter_kwargs,
            exclude_kwargs=exclude_kwargs,
        )

        creator = SimpleJobCreator(
            inputs=inputs,
            out_experiment=out_experiment,
            out_recipe=out_recipe,
            options=options,
            tags=tags,
            batch_size=batch_size,
        )

        self.log("notice", "Constraints for job creation:")
        self.log("notice", f"Inputs: Experiment {inp_experiment}, Recipe {inp_recipe}")
        self.log("notice", f"Outputs: Experiment {out_experiment}, Recipe {out_recipe}")

        jobs, inputs = creator.create(dry_run=dry_run)

        msg = f"created {len(jobs)} new jobs."
        if dry_run:
            msg = "(DRY_RUN) would have" + msg

        self.log("success", msg)

    def get_input_query(
        self,
        inp_experiment: str,
        inp_recipe: str,
        filter_kwargs: str = None,
        exclude_kwargs: str = None,
    ) -> List[InputQuery]:
        filter_kwargs = {
            "parentjob__experiment__name": inp_experiment,
            "parentjob__recipe__name": inp_recipe,
            **self.decode_json_string(filter_kwargs),
        }
        exclude_kwargs = self.decode_json_string(exclude_kwargs)

        iq = InputQuery(filter=filter_kwargs, exclude=exclude_kwargs)

        return [iq]

    def decode_json_string(self, json_str: str):
        if json_str is None:
            return {}

        return json.loads(json_str)
