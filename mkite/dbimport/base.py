from typing import Iterable, List
from abc import ABC, abstractmethod

from mkite_core.models import NodeResults, JobResults


class DbImporterError(Exception):
    pass


class DbImporter(ABC):
    """Class that provides translation between mkite and other databases."""

    RECIPE_DICT = None
    PACKAGE_DICT = None

    def __init__(
        self,
        project: str,
        experiment: str,
    ):
        self.project = project
        self.experiment = experiment

    @classmethod
    def from_env(cls, project: str, experiment: str) -> "DbImporter":
        """Creates a new instance of DbImporter based on environmental
        variables. This is useful when parsing API keys and similar
        information that does not have to be handled by the command.
        By default, no environmental variables are assumed and the
        DbImporter is instantiated as normal"""
        return cls(project, experiment)

    @abstractmethod
    def query(self, *args, **kwargs) -> Iterable[dict]:
        """Queries the database and returns a list of results"""

    @abstractmethod
    def convert(self, parsed: List[dict]) -> List[NodeResults]:
        """Converts the parsed results from the database into the
        mkite standard, using the NodeResults notation"""

    def query_and_convert(self, *args, **kwargs) -> List[NodeResults]:
        raw_data = self.query(*args, **kwargs)
        nodes = self.convert(raw_data)
        return nodes

    def import_data(self, **kwargs) -> JobResults:
        # TODO: add RunStats for querying if possible
        job_data = self.create_job(
            self.project,
            self.experiment,
            isroot=True,
            options=kwargs,
        )
        nodes = self.query_and_convert(**kwargs)

        return JobResults(job=job_data, nodes=nodes)

    def create_job(
        self,
        project: str,
        experiment: str,
        isroot=True,
        options={},
    ):
        """Creates a job that will be used to deserialize all the jobs
        added to the database through the given options"""

        recipe_dict = {
            "package": self.PACKAGE_DICT,
            **self.RECIPE_DICT,
        }

        jobdict = {
            "experiment": {
                "name": experiment,
                "project": {"name": project},
            },
            "recipe": recipe_dict,
            "isroot": isroot,
            "status": "D",
            "options": options,
        }

        return jobdict
