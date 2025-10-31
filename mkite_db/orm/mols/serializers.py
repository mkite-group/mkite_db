from django.db import transaction
from mkite_db.orm.base.models import Formula
from mkite_db.orm.base.serializers import ChemNodeSerializer, FormulaSerializer
from mkite_db.orm.serializers import BaseSerializer
from rest_framework import serializers
from taggit.serializers import TaggitSerializer, TagListSerializerField

from .models import Conformer, Molecule


class MoleculeSerializer(TaggitSerializer, ChemNodeSerializer):
    # If formula is a nested field, then one needs to pass the full
    # dictionary for the formula. However, this is not a good idea,
    # as the formula is generated automatically from the SMILES.
    # Therefore, we comment it out for now.
    formula = FormulaSerializer(nested_field=True, required=False, allow_null=True)
    tags = TagListSerializerField(required=False)

    class Meta:
        model = Molecule
        fields = "__all__"
        read_only_fields = ("inchikey", "formula")

    @transaction.atomic
    def create(self, validated_data):
        from mkite_core.external.rdkit import RdkitInterface

        iface = RdkitInterface.from_smiles(validated_data["smiles"])

        attrs = validated_data.get("attributes", {})
        attrs.update({
            "formula": iface.formula,
            "charge": iface.charge,
        })

        validated_data.update(
            {
                "inchikey": iface.inchikey,
                "smiles": iface.smiles,
            }
        )

        return super().create(validated_data)


class ConformerSerializer(ChemNodeSerializer):
    formula = FormulaSerializer(nested_field=True, required=False, allow_null=True)
    mol = MoleculeSerializer(nested_field=True, required=False)

    class Meta:
        model = Conformer
        fields = "__all__"
        read_only_fields = ("formula",)
