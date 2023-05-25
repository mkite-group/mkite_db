import os
from typing import List
from mkite_core.external import load_config
from django.core.management.base import BaseCommand, CommandError

from mkite_db.workflow.create import InputQuery, JOB_CREATORS


class Command(BaseCommand):
    help = "Creates jobs according to the given input/output recipes"

    def log(self, style, msg):
        style_fn = getattr(self.style, style.upper())
        return self.stdout.write(style_fn(msg))

    def add_arguments(self, argparser):
        argparser.add_argument(
            "creator_name",
            type=str,
            choices=JOB_CREATORS.keys(),
            help="Type of JobCreator to use",
        )
        argparser.add_argument(
            "rules_file",
            type=str,
            help="File containing the rules on job creation",
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

    def handle(
        self, creator_name, rules_file, *args, batch_size=None, dry_run=False, **kwargs
    ):
        rules = self.get_rules(rules_file)
        creator_cls = JOB_CREATORS[creator_name]

        self.log("notice", f"File {rules_file}, creator {creator_name}")

        for i, r in enumerate(rules, 1):
            creator = creator_cls(
                inputs=r["inputs"],
                out_experiment=r["out_experiment"],
                out_recipe=r["out_recipe"],
                options=r.get("options", None),
                tags=r.get("tags", None),
                batch_size=batch_size,
            )

            self.log("notice", f"Rule {i}: ({r['out_experiment']}, {r['out_recipe']})")

            jobs, inputs = creator.create(dry_run=dry_run)

            msg = f"created {len(jobs)} new jobs."
            if dry_run:
                msg = "(DRY_RUN) would have " + msg

            self.log("success", msg)

    def get_rules(self, rules_file: os.PathLike) -> List[dict]:
        """Loads the rules from the file. Expected format (in Python dictionary):

        ```
        rules = [
            {
                "inp_experiment": "Experiment1",
                "inp_recipe": "Recipe1",
                "out_experiment": "Experiment2",
                "out_recipe": "Recipe2",
                "options": {...},
                "tags": ["tag3"],
                "filter_kwargs": {
                    "parentjob__tags__in": ["tag1", "tag2"],
                },
                "exclude_kwargs": {},
            },
            ...
        ]
        ```
        """

        rules = load_config(rules_file)
        if isinstance(rules, dict):
            rules = [rules]

        validated_rules = [r for r in rules if self.is_valid_rule(r)]

        return validated_rules

    def is_valid_rule(self, rule: dict) -> bool:
        if not isinstance(rule, dict):
            return False

        required_keys = ["inputs", "out_experiment", "out_recipe"]
        return all([k in rule for k in required_keys])
