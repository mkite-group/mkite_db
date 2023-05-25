from rest_framework import serializers

from mkite_db.orm.serializers import BaseSerializer
from mkite_db.orm.jobs.serializers import JobSerializer
from .models import Formula, ChemNode, CalcNode


class FormulaSerializer(BaseSerializer):
    class Meta:
        model = Formula
        fields = "__all__"


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
