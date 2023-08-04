import os
import json
from typing import List
from mkite_core.external import load_config
from django.core.management.base import BaseCommand, CommandError

from mkite_core.models import JobResults
from mkite_db import dbimport as dbimp
from mkite_db.workflow.parse import JobParser

from mkite_db.orm.jobs.models import Job


DB_IMPORTERS = {cls.__name__: cls for cls in dbimp.DbImporter.__subclasses__()}


class Command(BaseCommand):
    help = "Parses another database into the mkite database"

    def log(self, style, msg):
        style_fn = getattr(self.style, style.upper())
        return self.stdout.write(style_fn(msg))

    def add_arguments(self, argparser):
        argparser.add_argument(
            "importer",
            type=str,
            choices=DB_IMPORTERS.keys(),
            help="Name of the importer to be used",
        )
        argparser.add_argument(
            "-p",
            "--project",
            type=str,
            required=True,
            help="Name of the project where the data is going to be imported to",
        )
        argparser.add_argument(
            "-e",
            "--experiment",
            type=str,
            required=True,
            help="Name of the experiment where the data is going to be imported to",
        )
        argparser.add_argument(
            "-q",
            "--query",
            type=str,
            default=None,
            help="JSON string containing all arguments of the query to be \
                    performed",
        )
        argparser.add_argument(
            "-f",
            "--file",
            type=str,
            default=None,
            help="File containing the query to be processed. If present, \
                the command will ignore the JSON string passed with the -q \
                option. The file can be a yaml or json file",
        )
        argparser.add_argument(
            "-j",
            "--json_as_file",
            action="store_true",
            help="If true, treats the JSON file as a file to be passed to \
                the importer instead of using its commands as queries.",
        )
        return argparser

    def handle(self, importer, *args, **kwargs):
        self.project = kwargs["project"]
        self.experiment = kwargs["experiment"]
        self.json_as_file = kwargs.get("json_as_file", False)

        importer_cls = DB_IMPORTERS[importer]
        self.importer = importer_cls.from_env(
            project=self.project,
            experiment=self.experiment,
        )
        self.queries = self.get_query_args(**kwargs)
        results = self.process_queries()
        self.save(results)

    def get_query_args(self, **kwargs):
        if kwargs.get("file", None) is not None:
            filename = kwargs["file"]

            if not self.json_as_file:
                if filename.endswith(".yaml") or filename.endswith(".json"):
                    return load_config(filename)

            return {"filename": kwargs["file"]}

        if kwargs.get("query", None) is not None:
            return json.loads(kwargs["query"])

        raise CommandError(
            "No query specified. Please specify a query with the -q option, \
            or pass an input file with the -f option"
        )

    def process_queries(self) -> List[JobResults]:
        self.log("notice", f"Project: {self.project}")
        self.log("notice", f"Experiment: {self.experiment}")

        if isinstance(self.queries, dict):
            self.log(
                "notice",
                f"Importing single query using {self.importer.__class__.__name__}",
            )
            jobresults = self.importer.import_data(**self.queries)
            self.log("success", "Successfully queried the external database")
            return [jobresults]

        self.log(
            "notice",
            f"Importing multiple queries using {self.importer.__class__.__name__}",
        )

        results = []
        for qargs in self.queries:
            jobresults = self.importer.import_data(**qargs)
            results.append(jobresults)

        self.log("success", f"Imported data sets across {len(self.queries)}")
        return results

    def save(self, results: List[JobResults]):
        saved = 0
        for index, info in enumerate(results):
            try:
                self.save_jobresults(info)
                saved += 1
                self.log(
                    "success",
                    f"Imported query index {index}",
                )
            except Exception as e:
                self.log("error", f"Skipping import of query index {index}: {str(e)}")
                continue

        self.log(
            "success",
            f"Saved {saved} entries in the database",
        )

    def save_jobresults(self, info: JobResults):
        if not self.is_valid_parse(info):
            raise CommandError("Parsing the results of the query is not valid")

        return JobParser(info).parse()

    def is_valid_parse(self, info: JobResults) -> bool:
        """Verifies if it is valid to parse the JobResults given by info.
        This prevents duplicate jobs from being parsed into the system.
        """
        query = Job.objects.filter(
            experiment__name=self.experiment,
            experiment__project__name=self.project,
            options=info.job["options"],
        )

        return not query.exists()
