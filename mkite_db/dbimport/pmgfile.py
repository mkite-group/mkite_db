import os
from typing import Iterable, List
from mkite_core.external import load_config

from pymatgen.core import Structure
from mkite_core.models import CrystalInfo, NodeResults
from .base import DbImporter, DbImporterError


class PymatgenFileImporter(DbImporter):
    RECIPE_DICT = {
        "name": "dbimport.PymatgenFileImporter",
        "method": "EXT",
    }
    PACKAGE_DICT = {"name": "mkite_db.dbimport"}

    def query(self, filename: os.PathLike, **kwargs):
        """Opens the file provided and returns its contents.
        For now, does not perform any filtering."""
        raw_data = self.read(filename)

        return raw_data

    def read(self, filename: os.PathLike):
        """Reads whatever ASE can read"""
        return [Structure.from_file(filename)]

    def convert(self, parsed: List[dict]) -> List[NodeResults]:
        """Converts the files into Infos, which is then converted into a
        Node.
        """
        return [self.convert_item(struct) for struct in parsed]

    def convert_item(self, structure: Structure) -> NodeResults:
        info = CrystalInfo.from_pymatgen(structure)

        return NodeResults(chemnode=info.as_dict())
