from rest_framework import serializers

from mkite_db.orm.serializers import BaseSerializer
from mkite_db.orm.jobs.serializers import JobSerializer
from .models import ChemNode, CalcNode, CalcType


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


class CalcTypeSerializer(BaseSerializer):
    class Meta:
        model = CalcType
        fields = (
            "id",
            "uuid",
            "name",
        )
        read_only_fields = (
            "ctime",
            "mtime",
        )


class CalcNodeSerializer(BaseSerializer):
    parentjob = JobSerializer(nested_field=True)
    chemnode = ChemNodeSerializer(nested_field=True)
    calctype = CalcTypeSerializer(nested_field=True, required=False)

    class Meta:
        model = CalcNode
        fields = (
            "id",
            "uuid",
            "parentjob",
            "chemnode",
            "calctype",
            "data",
        )
        read_only_fields = ("ctime", "mtime")
