import os
from typing import Iterable, List
from mkite_core.external import load_config

from ase import Atoms
from ase.io import read as ase_read
from mkite_core.models import CrystalInfo, ConformerInfo, MoleculeInfo, NodeResults
from .base import DbImporter, DbImporterError


class AseFileImporter(DbImporter):
    RECIPE_DICT = {
        "name": "dbimport.AseFileImporter",
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
        return ase_read(filename, index=":")

    def convert(self, parsed: List[dict]) -> List[NodeResults]:
        """Converts the files into Infos, which is then converted into a
        Node.
        """
        return [self.convert_item(atoms) for atoms in parsed]

    def convert_item(self, atoms: Atoms) -> NodeResults:
        if atoms.pbc.any():
            info = self.get_crystal_info(atoms)
        else:
            info = self.get_conformer_info(atoms)

        return NodeResults(chemnode=info.as_dict())

    def get_crystal_info(self, atoms: Atoms) -> CrystalInfo:
        return CrystalInfo.from_ase(atoms)

    def get_conformer_info(self, atoms: Atoms) -> ConformerInfo:
        if "smiles" in atoms.info:
            mol = MoleculeInfo.from_smiles(atoms.info["smiles"])
        else:
            mol = None

        return ConformerInfo.from_ase(atoms, mol=mol)
