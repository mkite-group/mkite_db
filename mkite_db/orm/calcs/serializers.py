from django.db import transaction
from rest_framework import serializers

from mkite_db.orm.serializers import BaseSerializer
from mkite_db.orm.base.serializers import CalcNodeSerializer

from .models import CalcType, GenericCalc


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


class GenericCalcSerializer(CalcNodeSerializer):
    calctype = CalcTypeSerializer(nested_field=True)

    class Meta:
        model = GenericCalc
        fields = (
            "id",
            "uuid",
            "parentjob",
            "chemnode",
            "calctype",
            "data",
        )
