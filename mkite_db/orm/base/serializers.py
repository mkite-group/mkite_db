from rest_framework import serializers

from mkite_db.orm.serializers import BaseSerializer
from mkite_db.orm.jobs.serializers import JobSerializer
from .models import Formula, ChemNode, CalcNode


class FormulaSerializer(BaseSerializer):
    class Meta:
        model = Formula
        fields = (
            "id",
            "name",
            "charge",
        )

    def to_internal_value(self, data):
        if data is None:
            modified = None

        elif type(data) == int:
            modified = {"id": data}

        elif type(data) == dict:
            modified = data

        else:
            modified = None

        return super().to_internal_value(modified)


class ChemNodeSerializer(BaseSerializer):
    parentjob = JobSerializer(nested_field=True)

    class Meta:
        model = ChemNode
        fields = (
            "id",
            "uuid",
            "parentjob",
        )
        read_only_fields = (
            "ctime",
            "mtime",
        )


class CalcNodeSerializer(BaseSerializer):
    parentjob = JobSerializer(nested_field=True)
    chemnode = ChemNodeSerializer(nested_field=True)

    class Meta:
        model = CalcNode
        fields = (
            "id",
            "uuid",
            "parentjob",
            "chemnode",
        )
        read_only_fields = ("ctime", "mtime")
