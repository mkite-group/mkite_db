from mkite_db.orm.base.serializers import (
    FormulaSerializer,
    ChemNodeSerializer,
    CalcNodeSerializer,
)
from mkite_db.orm.calcs.serializers import (
    EnergyForcesSerializer,
    FeatureSerializer,
)
from mkite_db.orm.structs.serializers import CrystalSerializer
from mkite_db.orm.mols.serializers import (
    MoleculeSerializer,
    ConformerSerializer,
)
from mkite_db.orm.jobs.serializers import (
    ProjectSerializer,
    ExperimentSerializer,
    JobPackageSerializer,
    JobRecipeSerializer,
    RunStatsSerializer,
    JobSerializer,
)


SERIALIZERS = {
    "Formula": FormulaSerializer,
    "ChemNode": ChemNodeSerializer,
    "CalcNode": CalcNodeSerializer,
    "EnergyForces": EnergyForcesSerializer,
    "Feature": FeatureSerializer,
    "Molecule": MoleculeSerializer,
    "Conformer": ConformerSerializer,
    "Crystal": CrystalSerializer,
    "Project": ProjectSerializer,
    "Experiment": ExperimentSerializer,
    "JobPackage": JobPackageSerializer,
    "JobRecipe": JobRecipeSerializer,
    "RunStats": RunStatsSerializer,
    "Job": JobSerializer,
}


class DeserializeError(Exception):
    pass


def get_serializer(data: dict):
    modname = data.get("@module", None)
    clsname = data.get("@class", None)
    data = {k: v for k, v in data.items() if not k.startswith("@")}

    if clsname not in SERIALIZERS:
        raise DeserializeError(
            f"Could not find serializer for class {clsname}. Specify \
                a valid class module/name using the key `'@class'` in the \
                input data"
        )

    return SERIALIZERS[clsname](data=data)


class ModuleDeserializer:
    def __init__(self, data: dict):
        self.modname = data.get("@module", None)
        self.clsname = data.get("@class", None)
        self.data = {k: v for k, v in data.items() if not k.startswith("@")}

    def get_module(self):
        return __import__(self.modname, globals(), locals(), [self.clsname], 0)

    def save(self):
        if self.clsname is None or self.modname is None:
            raise DeserializeError(
                f"Could not find module {self.modname} for class {self.clsname}.\
                    specify valid module/class names using the keys `'@module'` \
                    /`'@class'` in the input data"
            )

        return self.deserialize()

    def deserialize(self):
        mod = self.get_module()
        if not hasattr(mod, self.clsname):
            raise DeserializeError(
                f"Class {self.clsname} not found in module {self.modname}"
            )

        cls_ = getattr(mod, self.clsname)

        if hasattr(cls_, "from_dict"):
            obj = cls_.from_dict(self.data)
            obj.save()
            return obj

        obj = cls_(**self.data)
        obj.save()
        return obj
