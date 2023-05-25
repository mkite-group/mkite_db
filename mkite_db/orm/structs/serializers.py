from django.db import transaction
from rest_framework import serializers

from taggit.serializers import TagListSerializerField, TaggitSerializer
from mkite_db.orm.serializers import BaseSerializer
from mkite_db.orm.base.models import Formula
from mkite_db.orm.base.serializers import FormulaSerializer, ChemNodeSerializer
from mkite_core.models import FormulaInfo, CrystalInfo, SpaceGroupInfo

from .models import Crystal, SpaceGroups


class CrystalSerializer(TaggitSerializer, ChemNodeSerializer):
    spacegroup = serializers.ChoiceField(SpaceGroups.choices, required=False)
    formula = FormulaSerializer(nested_field=True, required=False)
    tags = TagListSerializerField(required=False)

    class Meta:
        model = Crystal
        fields = "__all__"

    @transaction.atomic
    def create(self, validated_data):
        if "formula" not in validated_data:
            info = FormulaInfo.from_list(validated_data["species"])
            validated_data["formula"] = info.as_dict()

        if "spacegroup" not in validated_data:
            info = CrystalInfo.from_dict(validated_data)
            spgrp = SpaceGroupInfo.from_info(info)
            validated_data["spacegroup"] = spgrp.number

        return super().create(validated_data)
