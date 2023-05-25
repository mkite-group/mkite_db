from django.core.management.base import BaseCommand

from mkite_db.orm.jobs.models import Project


class Command(BaseCommand):
    help = "Adds a new project to the database"

    def log(self, style, msg):
        style_fn = getattr(self.style, style.upper())
        return self.stdout.write(style_fn(msg))

    def add_arguments(self, argparser):
        argparser.add_argument(
            "project",
            type=str,
            default=None,
            help="Name of the project that will be created",
        )
        argparser.add_argument(
            "--dry_run",
            action="store_true",
            help="If set, does not store objects into the database",
        )
        return argparser

    def handle(self, project, *args, dry_run=False, **kwargs):
        prj = Project.objects.filter(name=project)

        if prj.exists():
            self.log(
                "error",
                f"A Project named {project} already exists in the database.",
            )
            return

        if dry_run:
            self.log(
                "success",
                f"[DRY_RUN] Would have created Project {project}",
            )
        else:
            prj = Project.objects.create(name=project)
            self.log("success", f"Added project {project} (id {prj.id})")
