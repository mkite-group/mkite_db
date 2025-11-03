from django.db import models
from django.contrib.postgres.fields import ArrayField

from mkite_db.orm.repr import _named_repr
from mkite_db.orm.base.models import CalcNode, DbEntry


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
