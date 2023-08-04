import os
import json
from typing import List

from mkite_core.models import NodeResults
from .base import DbImporter, DbImporterError


class InfoFileImporter(DbImporter):
    RECIPE_DICT = {
        "name": "dbimport.InfoFileImporter",
        "method": "EXT",
    }
    PACKAGE_DICT = {"name": "mkite_db.dbimport"}

    def query(self, data: dict, **kwargs):
        return data

    def convert(self, parsed: List[dict]) -> List[NodeResults]:
        return [self.convert_item(item) for item in parsed]

    def convert_item(self, item: dict) -> NodeResults:
        return NodeResults(chemnode=item)
