import os
from typing import Iterable
from django.core.management.base import BaseCommand, CommandError

from mkite_core.models import JobResults, Status
from mkite_db.workflow.parse import JobParser
from mkite_engines import EngineRoles, instantiate_from_path

from mkite_db.orm.jobs.models import Job


class Command(BaseCommand):
    help = "Parses the job results from a folder into the database"

    def log(self, style, msg):
        style_fn = getattr(self.style, style.upper())
        return self.stdout.write(style_fn(msg))

    def add_arguments(self, argparser):
        argparser.add_argument(
            "filename",
            type=str,
            help="path to a file to be parsed. If given, ignores the choice of engine and parses only that file",
        )
        return argparser

    def handle(self, filename, **kwargs):
        self.log("notice", f"Parsing file: {filename}")
        results = JobResults.from_json(filename)
        self.parse_result(results)

    def parse_result(self, info: JobResults) -> bool:
        jobstr = self.get_info_string(info)
        try:
            if not self.is_valid_parse(info):
                raise CommandError(
                    f"Invalid parsing of {jobstr}. Job is likely done already."
                )

            parser = JobParser(info)
            out = parser.parse()
            self.log("success", f"Parsed {jobstr}")

            return out

        except Exception as e:
            self.log("error", f"Error processing {jobstr}: {str(e)}")

            return None

    def is_valid_parse(self, info: JobResults):
        """Verifies if it is valid to parse the JobResults given by info. This prevents
        duplicate jobs from being parsed into the system.
        """
        if "id" not in info.job and "uuid" not in info.job:
            return False

        if "uuid" in info.job:
            job = Job.objects.filter(uuid=info.job["uuid"])

        elif "id" in info.job:
            job = Job.objects.filter(id=info.job["id"])

        if not job.exists():
            return True

        return job.status != "D"

    def get_dict_string(self, data: dict, prefix="job"):
        if not prefix.endswith(" "):
            prefix += " "

        if "uuid" in data:
            return prefix + data["uuid"]

        elif "id" in data:
            return prefix + str(data["id"])

        elif "name" in data:
            return prefix + data["name"]

        return ""

    def get_info_string(self, info: JobResults):
        string = self.get_dict_string(info.job, prefix="job")

        if string:
            return string

        elif "experiment" in info.job:
            string = self.get_dict_string(info.job["experiment"], prefix="experiment")
            if string:
                return string

        elif "recipe" in info.job:
            string = self.get_dict_string(info.job["recipe"], prefix="recipe")
            if string:
                return string

        return ""
