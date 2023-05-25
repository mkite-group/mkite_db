from datetime import timedelta
from django.db import models
from django.core.serializers.json import DjangoJSONEncoder

from mkite_db.orm.repr import _named_repr
from mkite_db.orm.base.models import DbEntry
from taggit.managers import TaggableManager


class Project(DbEntry):
    name = models.CharField(max_length=32, unique=True)
    description = models.CharField(max_length=256, null=True)

    def __repr__(self):
        return _named_repr(self)


class Experiment(DbEntry):
    name = models.CharField(max_length=32, unique=True)
    description = models.CharField(max_length=256, null=True)
    project = models.ForeignKey(
        Project,
        null=False,
        related_name="experiments",
        on_delete=models.PROTECT,
    )

    def __repr__(self):
        return _named_repr(self)


class JobStatus(models.TextChoices):
    # status for incomplete jobs
    READY = "Y"
    RUNNING = "R"
    STOPPED = "S"

    # status for complete jobs
    ERROR = "E"
    DONE = "D"


class Job(DbEntry):
    """Stores jobs in the database and its values"""

    experiment = models.ForeignKey(
        Experiment,
        null=False,
        db_index=True,
        related_name="jobs",
        on_delete=models.PROTECT,
    )

    inputs = models.ManyToManyField(
        "base.ChemNode",
        related_name="childjobs",
    )

    recipe = models.ForeignKey(
        "JobRecipe",
        null=False,
        db_index=True,
        related_name="jobs",
        on_delete=models.PROTECT,
    )

    runstats = models.OneToOneField(
        "RunStats", null=True, related_name="job", on_delete=models.CASCADE
    )

    status = models.CharField(
        max_length=1,
        null=False,
        choices=JobStatus.choices,
        default=JobStatus.READY,
    )

    options = models.JSONField(encoder=DjangoJSONEncoder, default=dict)

    isroot = models.BooleanField(default=False)

    tags = TaggableManager()

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.experiment.name}, {self.recipe.name}, {JobStatus(self.status).label} ({self.id})>"

    def as_dict(self):
        return {
            "id": self.id,
            "uuid": str(self.uuid),
            "ctime": self.ctime,
            "project": self.experiment.project.name,
            "experiment": self.experiment.name,
        }

    def as_info(self):
        from mkite_core.models import JobInfo

        return JobInfo.from_job(self)

    @property
    def parentjobs(self):
        return self.__class__.objects.filter(
            id__in=self.inputs.values_list("parentjob")
        )

    @property
    def childjobs(self):
        return self.__class__.objects.filter(
            id__in=self.chemnodes.values_list("childjobs")
        )


class RecipeMethods(models.TextChoices):
    """Enum class to provide different types of recipes.

    Attributes:
        DFT: Density Functional Theory
        FF: Force Field
        WF: Wavefunction
        ML: Machine Learning
        FT: Featurization
        EXT: External
        GEN: Generation
    """

    DFT = "DFT"
    FF = "FF"
    WF = "WF"
    ML = "ML"
    FT = "FT"
    EXT = "EXT"
    GEN = "GEN"


class JobRecipe(DbEntry):
    name = models.CharField(max_length=64, db_index=True)
    package = models.ForeignKey(
        "JobPackage", null=False, related_name="recipes", on_delete=models.PROTECT
    )
    method = models.CharField(
        max_length=3,
        null=False,
        choices=RecipeMethods.choices,
        default=RecipeMethods.DFT,
    )
    defaults = models.JSONField(encoder=DjangoJSONEncoder, default=dict)

    def as_dict(self):
        return {
            "id": self.id,
            "uuid": str(self.uuid),
            "name": self.name,
            "package": self.package.name,
            "method": str(self.method),
        }

    def __repr__(self):
        return _named_repr(self)


class JobPackage(DbEntry):
    name = models.CharField(max_length=64, db_index=True)

    def __repr__(self):
        return _named_repr(self)


class RunStats(DbEntry):
    host = models.CharField(max_length=64, db_index=True)
    cluster = models.CharField(max_length=64, db_index=True)
    duration = models.DurationField()
    ncores = models.PositiveIntegerField()
    ngpus = models.PositiveIntegerField(default=0)
    pkgversion = models.CharField(max_length=128, null=True)

    def as_dict(self):
        return {
            "host": self.host,
            "cluster": self.cluster,
            "duration": self.duration,
            "ncores": self.ncores,
            "ngpus": self.ngpus,
            "pkgversion": self.pkgversion,
        }

    def as_info(self):
        from mkite_core.models import RunStatsInfo

        return RunStatsInfo(**self.as_dict())

    @classmethod
    def from_info(cls, info: "RunStatsInfo") -> "RunStats":
        return cls(
            host=info.host,
            cluster=info.cluster,
            duration=info.duration,
            ncores=info.ncores,
            ngpus=info.ngpus,
            pkgversion=info.pkgversion,
        )

    @staticmethod
    def duration_from_seconds(seconds: float) -> timedelta:
        return timedelta(seconds=seconds)

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.host} @ {self.cluster} ({self.id})>"
