from django.db import models
from django.contrib.postgres.fields import ArrayField

from mkite_db.orm.base.models import CalcNode


class EnergyForces(CalcNode):
    energy = models.FloatField(null=True)
    forces = ArrayField(ArrayField(models.FloatField(), size=3), null=True)


class Feature(CalcNode):
    value = ArrayField(models.FloatField())
