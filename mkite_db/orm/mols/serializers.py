from django.db import transaction
from mkite_db.orm.base.serializers import ChemNodeSerializer
from mkite_db.orm.serializers import BaseSerializer
from rest_framework import serializers
from taggit.serializers import TaggitSerializer, TagListSerializerField

from .models import Conformer, Molecule


class MoleculeSerializer(TaggitSerializer, ChemNodeSerializer):
    tags = TagListSerializerField(required=False)

    class Meta:
        model = Molecule
        fields = "__all__"
        read_only_fields = ("inchikey", )

    @transaction.atomic
    def create(self, validated_data):
        from mkite_core.external.rdkit import RdkitInterface

        iface = RdkitInterface.from_smiles(validated_data["smiles"])

        attrs = validated_data.get("attributes", {})
        attrs = {
            **attrs,
            "formula": iface.formula,
            "charge": iface.charge,
        }
        validated_data["attributes"] = attrs

        validated_data.update(
            {
                "inchikey": iface.inchikey,
                "smiles": iface.smiles,
            }
        )

        return super().create(validated_data)


class ConformerSerializer(ChemNodeSerializer):
    mol = MoleculeSerializer(nested_field=True, required=False)

    class Meta:
        model = Conformer
        fields = "__all__"
