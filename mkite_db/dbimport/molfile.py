import os
from typing import Iterable, List
from mkite_core.external import load_config

from mkite_core.models import MoleculeInfo, ConformerInfo, NodeResults
from .base import DbImporter, DbImporterError


class MolFileImporter(DbImporter):
    RECIPE_DICT = {
        "name": "dbimport.MolFileImporter",
        "method": "EXT",
    }
    PACKAGE_DICT = {"name": "mkite_db.dbimport"}

    def query(self, **kwargs):
        """Opens the file provided and returns its contents.
        For now, does not perform any filtering."""

        if "filename" in kwargs:
            return self.read(kwargs["filename"])

        return [kwargs]

    def read(self, filename: os.PathLike):
        if filename.endswith(".json") or filename.endswith(".yaml"):
            return load_config(filename)

        if filename.endswith(".sdf"):
            raise NotImplementedError("Importing .sdf files is not yet supported")

    def convert(self, parsed: List[dict]) -> List[NodeResults]:
        """Converts the files into MoleculeInfo, which is then converted into a
        Node. The expected format of the dictionary of parsed information is
        the following:

        ```
            parsed[0] = {
                "smiles": "c1ccccc1",
                "attributes": {...},
            }
        ```
        """
        return [self.convert_item(item) for item in parsed]

    def convert_item(self, item: dict) -> NodeResults:
        info = MoleculeInfo.from_smiles(item["smiles"])
        if "attributes" in item:
            info.attributes = item["attributes"]

        return NodeResults(chemnode=info.as_dict())
