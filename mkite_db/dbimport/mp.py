import os
import numpy as np
from typing import Iterable, List

from mkite_core.models import CrystalInfo, EnergyForcesInfo, NodeResults
from .base import DbImporter, DbImporterError


MP_KEY = "MP_API_KEY"


class MPImporter(DbImporter):
    RECIPE_DICT = {
        "name": "dbimport.MPImporter",
        "method": "EXT",
    }
    PACKAGE_DICT = {"name": "mp_api.MPRester"}

    def __init__(self, project: str, experiment: str, api_key: str = None):
        super().__init__(project, experiment)
        self.key = api_key

    def get_rester(self):
        from mp_api.client import MPRester

        return MPRester(self.key)

    @classmethod
    def from_env(cls, project: str, experiment: str) -> "MPImporter":
        if MP_KEY not in os.environ:
            raise DbImporterError(f"{MP_KEY} is not defined in the environment")

        return cls(
            project=project,
            experiment=experiment,
            api_key=os.environ[MP_KEY],
        )

    def convert(self, docs: List[dict]) -> List[NodeResults]:
        return [self.convert_doc(doc) for doc in docs]

    def convert_doc(self, doc: dict) -> NodeResults:
        if not hasattr(doc, "structure"):
            raise DbImporterError(
                'Structure not found in MPImporter query.\
                Did you pass "structure" on the `fields` value of your \
                query?'
            )

        chemnode = self.convert_structure(doc)

        calcnodes = []
        if hasattr(doc, "energy_per_atom"):
            energy_forces = self.convert_energy_forces(doc)
            calcnodes.append(energy_forces)

        return NodeResults(chemnode=chemnode, calcnodes=calcnodes)

    def convert_structure(self, doc: dict) -> dict:
        structure = getattr(doc, "structure")
        info = CrystalInfo.from_pymatgen(structure)

        keys_to_save = ["material_id"]
        for k in keys_to_save:
            if hasattr(doc, k):
                info.attributes[k] = getattr(doc, k)

        return info.as_dict()

    def convert_energy_forces(self, doc: dict) -> dict:
        num_atoms = len(getattr(doc, "structure"))
        energy = getattr(doc, "energy_per_atom") * num_atoms
        forces = np.zeros((num_atoms, 3)).tolist()
        return EnergyForcesInfo(energy=energy, forces=forces).as_dict()

    def query(self, rester: str, query_function: str, **kwargs) -> Iterable[dict]:
        with self.get_rester() as mpr:
            engine = getattr(mpr, rester)
            fn = getattr(engine, query_function)
            docs = fn(**kwargs)

        return docs

    def query_structures(self, **kwargs) -> Iterable[dict]:
        fields = kwargs.get("fields", []) + [
            "material_id",
            "structure",
            "energy_per_atom",
        ]
        kwargs["fields"] = list(set(fields))

        return self.query("summary", "search", **kwargs)
