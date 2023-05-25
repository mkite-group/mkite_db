from django.db import transaction
from rest_framework import serializers

from mkite_db.orm.base.serializers import CalcNodeSerializer

from .models import EnergyForces, Feature


class EnergyForcesSerializer(CalcNodeSerializer):
    class Meta:
        model = EnergyForces
        fields = (
            "id",
            "uuid",
            "energy",
            "forces",
            "parentjob",
            "chemnode",
        )


class FeatureSerializer(CalcNodeSerializer):
    class Meta:
        model = Feature
        fields = (
            "id",
            "uuid",
            "value",
            "parentjob",
            "chemnode",
        )
