from django.core.management.base import BaseCommand, CommandError

from mkite_db.orm.jobs.models import Project, Experiment


class Command(BaseCommand):
    help = "Adds a new experiment to the database"

    def log(self, style, msg):
        style_fn = getattr(self.style, style.upper())
        return self.stdout.write(style_fn(msg))

    def add_arguments(self, argparser):
        argparser.add_argument(
            "project",
            type=str,
            default=None,
            help="Name of the project where the experiment will be nested",
        )
        argparser.add_argument(
            "experiment",
            type=str,
            default=None,
            help="Name of the experiment to be created",
        )
        argparser.add_argument(
            "--dry_run",
            action="store_true",
            help="If set, does not store objects into the database",
        )
        return argparser

    def handle(self, project, experiment, *args, dry_run=False, **kwargs):
        prj = Project.objects.get(name=project)
        exp = Experiment.objects.filter(name=experiment, project=prj)

        if exp.exists():
            self.log(
                "error",
                f"An experiment named {experiment} already exists in project {project}.",
            )
            return

        if dry_run:
            self.log(
                "success",
                f"[DRY_RUN] Would have created experiment {experiment} under project {project}",
            )
        else:
            exp = Experiment.objects.create(name=experiment, project=prj)
            self.log("success", f"Added experiment {experiment} (id {exp.id})")
