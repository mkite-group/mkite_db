import unittest as ut
from io import StringIO
from django.test import TestCase
from django.core.management import call_command

from mkite_db.orm.jobs.management.commands.scanrecipes import Command


class TestCommand(TestCase):
    def call_command(self, *args, **kwargs):
        call_command(
            "scanrecipes",
            *args,
            stdout=StringIO(),
            stderr=StringIO(),
            **kwargs,
        )

    def test_command(self):
        self.call_command("--dry_run")
