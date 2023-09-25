import pandas as pd
from django.core.management.base import BaseCommand, CommandError

from mkite_db.orm.jobs.models import Job, Experiment


class Command(BaseCommand):
    help = "Creates jobs according to the given input/output recipes"

    def log(self, style, msg):
        style_fn = getattr(self.style, style.upper())
        return self.stdout.write(style_fn(msg))

    def add_arguments(self, argparser):
        argparser.add_argument(
            "-p",
            "--project",
            type=str,
            default=None,
            help="If given, summarizes only the given Project",
        )
        argparser.add_argument(
            "-e",
            "--experiment",
            type=str,
            default=None,
            help="If given, summarizes only the given Experiment",
        )
        argparser.add_argument(
            "-f",
            "--fraction",
            action="store_true",
            help="If set, displays the results as fractions instead of number",
        )
        return argparser

    def handle(self, *args, project=None, experiment=None, fraction=False, **kwargs):
        self.log("notice", "Summarizing jobs...")

        exp = Experiment.objects.all()
        if project is not None:
            self.log("notice", f"Project: {project}")
            exp = Experiment.objects.filter(project__name=project)

        if experiment is not None:
            self.log("notice", f"Experiment: {experiment}")
            exp = Experiment.objects.filter(name=experiment)

        jobs = Job.objects.filter(experiment__in=exp)

        data = {
            "id": "id",
            "status": "status",
            "project": "experiment__project__name",
            "experiment": "experiment__name",
        }

        results = pd.DataFrame(jobs.values_list(*data.values()), columns=data.keys())

        table = results.groupby(["project", "experiment", "status"]).count()
        table = (
            table.reset_index()
            .pivot(index="experiment", columns="status", values="id")
            .fillna(0)
        )
        total = table.sum(1)

        if fraction:
            table = table / total.values.reshape(-1, 1)
            table = table.apply(lambda x: round(x, 2))
        else:
            table = table.astype(int)

        table["Tot"] = total.astype(int)

        self.log("success", str(table))
