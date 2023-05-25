from typing import List, Dict, Union, Iterable, Tuple
from abc import ABC, abstractmethod
from pydantic import BaseModel, Field

from mkite_db.orm.base.models import ChemNode
from mkite_db.orm.jobs.models import Job, JobRecipe, Experiment


class JobCreationError(Exception):
    pass


class InputQuery(BaseModel):
    """Dictionary containing all the information to filter/exclude
    when querying what are going to be the inputs of the job.
    The input dictionary should be of the following format:

    ```
    "filter": {
        "parentjob__experiment__name": "test_exp",
        "parentjob__recipe__name": "test_recipe",
        "parentjob__tags__name": "tag",
        "crystal__isnull": True,
    }
    "exclude": {
        "parentjob__tags__name": "tag2",
    }
    ```
    """

    filter: dict = Field(
        default_factory=dict,
        description="kwargs used to filter nodes. Anything accepted by django",
    )
    exclude: dict = Field(
        default_factory=dict,
        description="kwargs used to exclude nodes. Anything accepted by django",
    )


class BaseJobCreator(ABC):
    def __init__(
        self,
        inputs: List[InputQuery],
        out_experiment: str,
        out_recipe: str,
        options: dict = None,
        tags: List[str] = None,
        batch_size: int = None,
    ):
        """Initializes the JobCreator with the information required to
        create all jobs.

        Args:
            inputs: dictionary containing all the information to filter/exclude
                when querying what are going to be the inputs of the job. As
                the job may take more than one input, it requires a list of
                dictionaries. Used according to the format of `InputQuery`.
            out_experiment: name of the experiment of the job to be created. Should
                already exist in the database.
            out_recipe: name of the recipe of the job to be created. Should already
                exist in the database.
            options: dicionary containing the special options to override the defaults
                in the job.
            tags: list of tags to add to the new job
            batch_size: size of the batch when bulk creating new jobs.
        """

        self.inputs = self.format_inputs(inputs)
        self.out_experiment = self.get_object(model=Experiment, name=out_experiment)
        self.out_recipe = self.get_object(model=JobRecipe, name=out_recipe)

        self.options = options if options is not None else {}
        self.tags = self.format_tags(tags)
        self.batch_size = batch_size

    def format_inputs(self, inputs: List[Union[dict, InputQuery]]) -> List[InputQuery]:
        formatted = []
        for inp in inputs:
            if isinstance(inp, InputQuery):
                formatted.append(inp)

            elif isinstance(inp, dict):
                iq = InputQuery(**inp)
                formatted.append(iq)

            else:
                raise JobCreationError(f"Invalid input type {type(inp)}")

        return formatted

    def get_object(self, model, **kwargs):
        return model.objects.get(**kwargs)

    @abstractmethod
    def get_inputs(self) -> Iterable[ChemNode]:
        """Gets the inputs of the jobs"""

    @property
    def job_template(self) -> Job:
        return Job(
            experiment=self.out_experiment,
            recipe=self.out_recipe,
            options=self.options,
            isroot=False,
        )

    def format_tags(self, tags) -> List[str]:
        if tags is None:
            return []

        if type(tags) == str:
            return [tags]

        return tags

    def add_tags(self, jobs: List[Job]):
        for j in jobs:
            j.tags.add(*self.tags)

    @abstractmethod
    def create(self, dry_run: bool = False) -> Tuple[List[Job], Iterable]:
        """Creates the jobs based on the inputs"""
