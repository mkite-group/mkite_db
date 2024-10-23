from django.db import models
from django.contrib.postgres.fields import ArrayField

from mkite_db.orm.repr import _named_repr
from mkite_db.orm.base.models import CalcNode, DbEntry


class EnergyForces(CalcNode):
    energy = models.FloatField(null=True)
    forces = ArrayField(ArrayField(models.FloatField(), size=3), null=True)


class Feature(CalcNode):
    value = ArrayField(models.FloatField())


class CalcType(DbEntry):
    name = models.CharField(max_length=128, unique=True)

    def __repr__(self):
        return _named_repr(self)


class GenericCalc(CalcNode):
    data = models.JSONField(default=dict)
    calctype = models.ForeignKey(
        CalcType,
        null=False,
        db_index=True,
        related_name="calcs",
        on_delete=models.PROTECT,
    )
