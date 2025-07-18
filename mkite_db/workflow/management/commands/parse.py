import os
import sys
from typing import Iterable
from django.core.management.base import BaseCommand, CommandError
from django.db import connections, OperationalError

from mkite_core.models import JobResults, Status, JobInfo
from mkite_db.workflow.parse import JobParser
from mkite_engines import EngineRoles, instantiate_from_path

from mkite_db.orm.jobs.models import Job, JobStatus


def check_database_connection(alias="default"):
    """
    Checks whether the database connection is active.
    Raises OperationalError if the connection fails.
    """
    try:
        connection = connections[alias]
        connection.ensure_connection()
    except OperationalError as e:
        raise OperationalError(f"Database connection failed: {e}")


class Command(BaseCommand):
    help = "Parses the job results from a folder into the database"

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
            "-n",
            "--num_parse",
            type=int,
            default=10000,
            help="maximum number of jobs to parse at once",
        )
        argparser.add_argument(
            "-e",
            "--error",
            action="store_true",
            help="If set, parses the error queue",
        )
        return argparser

    def handle(self, engine_config, *args, num_parse=1000, error=False, **kwargs):
        try:
            check_database_connection()
        except OperationalError as e:
            print(e)
            sys.exit()

        self.engine = self.get_engine(engine_config)
        self.log("notice", f"Parsing from engine: {engine_config}")

        if error:
            self.parse_error(num_parse)
        else:
            self.parse_all(num_parse)

    def get_engine(self, engine_config):
        engine = instantiate_from_path(engine_config, role=EngineRoles.consumer)
        engine.add_queue(Status.PARSING)
        return engine

    def parse_all(self, num_parse: int):
        nparsed = 0
        nerrors = 0
        while nparsed + nerrors < num_parse:
            key, info = self.engine.get_info(
                queue=Status.PARSING.value, info_cls=JobResults
            )
            if info is None:
                break

            out = self.parse_result(info)

            if out is not None:
                nparsed += 1
                self.engine.delete(key)
            else:
                nerrors += 1

        self.log("success", f"Number of parsed files: {nparsed}")
        self.log("warning", f"Number of error files: {nerrors}")

        return nparsed, nerrors

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

    def parse_error(self, num_parse: int):
        nerrors = 0
        while nerrors < num_parse:
            key, msg = self.engine.get(queue=Status.ERROR.value)
            if key is None:
                break

            try:
                job = Job.objects.get(uuid=key)
                job.status = JobStatus.ERROR
                job.save()
                self.engine.delete(key)
                nerrors += 1

            except Exception as e:
                self.log("error", f"Error processing {key}: {str(e)}")

        self.log("success", f"Number of error jobs: {nerrors}")

        return nerrors

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

        job = job.first()

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
