from django.db import models
from django.contrib.postgres.fields import ArrayField

from taggit.managers import TaggableManager
from mkite_db.orm.repr import _named_repr
from mkite_db.orm.base.models import DbEntry, ChemNode, Elements


class Molecule(ChemNode):
    """Class to hold the information of molecular graphs"""

    inchikey = models.CharField(
        max_length=27,
        null=False,
        unique=True,
    )

    smiles = models.CharField(
        max_length=10000,
        null=False,
        unique=True,
    )

    siteprops = models.JSONField(default=dict)

    attributes = models.JSONField(default=dict)

    tags = TaggableManager()

    @property
    def formula(self):
        if "formula" in self.attributes:
            return self.attributes["formula"]
        return None

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.inchikey} ({self.id})>"

    def as_info(self):
        from mkite_core.models import MoleculeInfo

        return MoleculeInfo.from_molecule(self)


class Conformer(ChemNode):
    mol = models.ForeignKey(
        Molecule,
        null=True,
        related_name="conformers",
        on_delete=models.PROTECT,
    )

    species = ArrayField(
        models.CharField(
            max_length=2,
            null=False,
            choices=Elements.choices,
        )
    )
    coords = ArrayField(ArrayField(models.FloatField(), size=3))
    siteprops = models.JSONField(default=dict)
    attributes = models.JSONField(default=dict)

    @property
    def formula(self):
        if "formula" in self.attributes:
            return self.attributes["formula"]
        return None

    def __repr__(self):
        ikey = "None" if self.mol is None else self.mol.inchikey
        formula = str(self.formula)
        return (
            f"<{self.__class__.__name__}: {formula}, Mol {ikey} ({self.id})>"
        )

    def as_info(self):
        from mkite_core.models import ConformerInfo

        return ConformerInfo.from_conformer(self)

    def as_dict(self):
        data = super().as_dict()
        data["mol"] = self.mol.as_dict()
        return data
