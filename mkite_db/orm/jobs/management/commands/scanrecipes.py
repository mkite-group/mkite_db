from importlib import metadata
from django.core.management.base import BaseCommand, CommandError

from mkite_core.plugins import get_recipes
from mkite_db.orm.jobs.models import JobRecipe
from mkite_db.orm.jobs.serializers import JobRecipeSerializer


class Command(BaseCommand):
    help = "Creates jobs according to the given input/output recipes"

    def log(self, style, msg):
        style_fn = getattr(self.style, style.upper())
        return self.stdout.write(style_fn(msg))

    def add_arguments(self, argparser):
        argparser.add_argument(
            "--dry_run",
            action="store_true",
            help="If set, does not store objects into the database",
        )
        return argparser

    def handle(self, *args, dry_run=False, **kwargs):
        self.log("notice", f"Scanning entry point mkite_db.recipes...")
        recipes = get_recipes()

        new_recipes = []
        for name, entry in recipes.items():
            new = self.add_entry_point(name, entry, dry_run=dry_run)
            if new is not None:
                new_recipes.append(new)

        if dry_run:
            self.log("success", f"Found {len(new_recipes)} recipes in entry points")
        else:
            self.log("success", f"Added {len(new_recipes)} recipes to the database")

    def add_entry_point(
        self, name: str, entry: metadata.EntryPoint, dry_run: bool = False
    ):
        cls = entry.load()
        data = {
            "name": name,
            "method": cls._METHOD,
            "package": {"name": cls._PACKAGE_NAME},
        }

        if dry_run:
            self.log("success", f"Found recipe {name} in entry points")
            return data

        try:
            new = self.create_recipe(data)
            self.log("success", f"Added recipe {name} to the database")
            return new

        except Exception as e:
            self.log("error", f"Error adding recipe {name} to the database: {str(e)}")
            return None

    def create_recipe(self, data: dict) -> JobRecipe:
        serial = JobRecipeSerializer(data=data)
        if not serial.is_valid():
            raise CommandError(f"Error deserializing data: {serial.errors}")

        return serial.save()
