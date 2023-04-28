import uuid
import warnings
from itertools import chain

from django.db import models, transaction
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class DbEntry(models.Model):
    """Abstract base class for every unique, identifiable entry in the database"""

    uuid = models.UUIDField(unique=True, default=uuid.uuid4)
    ctime = models.DateTimeField(db_index=True, auto_now_add=True)
    mtime = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Node(DbEntry):
    class Meta:
        abstract = True

    def as_dict(self):
        opts = self._meta
        data = {"@module": self.__class__.__module__, "@class": self.__class__.__name__}

        for f in chain(opts.concrete_fields, opts.private_fields):
            data[f.name] = f.value_from_object(self)

        for f in opts.many_to_many:
            data[f.name] = [i.id for i in f.value_from_object(self)]

        if hasattr(self, "uuid"):
            data["uuid"] = str(self.uuid)

        if "tagged_items" in data:
            data.pop("tagged_items")

        return data

    def get_data(self):
        """Nodes are generic entities that can be subclassed. When
        getting their data, however, we are interested in serializing
        all the data from the node, including the models related
        by OneToOne fields. This method verifies what are the non-null
        OneToOne fields containing data and returns the data associated
        to this node.
        """
        fields = [f for f in self._meta.related_objects if f.one_to_one]

        for f in fields:
            if hasattr(self, f.name):
                return getattr(self, f.name).as_dict()

        return self.as_dict()


class ChemNode(Node):
    """Base class for every chemical information point in the database.

    Nodes can only be created by Jobs. To ensure the traceability
    of chemical data, every Node has to have a `parentjob`.

    Nodes are abstract classes that have a `data` generic foreign key. This tries to connect "unstructured" data
    to the node itself at the expense of more storage space. As the multi-table inheritance remains
    in place, the generic foreign key contains redundant information. However, it facilitates finding out what is the
    information that is stored in the node.
    """

    parentjob = models.ForeignKey(
        "jobs.Job",
        null=False,
        related_name="chemnodes",
        on_delete=models.CASCADE,
    )

    def as_dict(self):
        data = super().as_dict()
        data["uuid"] = str(data["uuid"])
        return data


class CalcNode(Node):
    """Base class for every calculation in the database. This includes
    energies, forces, analysis, descriptors etc.

    Nodes can only be created by Jobs. To ensure the traceability
    of data nodes, every Node has to have a `parentjob`. Furthermore,
    every CalcNode has to point to a single ChemNode, to which the information
    is associated. Otherwise, it is just floating information in the database.
    """

    parentjob = models.ForeignKey(
        "jobs.Job",
        null=False,
        related_name="calcnodes",
        on_delete=models.CASCADE,
    )

    chemnode = models.ForeignKey(
        ChemNode,
        null=False,
        related_name="calcnodes",
        on_delete=models.CASCADE,
    )

    def as_dict(self):
        data = super().as_dict()
        data["uuid"] = str(data["uuid"])
        return data


class Formula(models.Model):
    name = models.CharField(max_length=128, unique=True)
    charge = models.SmallIntegerField(default=0)

    def as_info(self):
        from mkite_core.models import FormulaInfo

        return FormulaInfo(self.name, self.charge)


class Elements(models.TextChoices):
    H = "H"
    He = "He"
    Li = "Li"
    Be = "Be"
    B = "B"
    C = "C"
    N = "N"
    O = "O"
    F = "F"
    Ne = "Ne"
    Na = "Na"
    Mg = "Mg"
    Al = "Al"
    Si = "Si"
    P = "P"
    S = "S"
    Cl = "Cl"
    Ar = "Ar"
    K = "K"
    Ca = "Ca"
    Sc = "Sc"
    Ti = "Ti"
    V = "V"
    Cr = "Cr"
    Mn = "Mn"
    Fe = "Fe"
    Co = "Co"
    Ni = "Ni"
    Cu = "Cu"
    Zn = "Zn"
    Ga = "Ga"
    Ge = "Ge"
    As = "As"
    Se = "Se"
    Br = "Br"
    Kr = "Kr"
    Rb = "Rb"
    Sr = "Sr"
    Y = "Y"
    Zr = "Zr"
    Nb = "Nb"
    Mo = "Mo"
    Tc = "Tc"
    Ru = "Ru"
    Rh = "Rh"
    Pd = "Pd"
    Ag = "Ag"
    Cd = "Cd"
    In = "In"
    Sn = "Sn"
    Sb = "Sb"
    Te = "Te"
    I = "I"
    Xe = "Xe"
    Cs = "Cs"
    Ba = "Ba"
    La = "La"
    Ce = "Ce"
    Pr = "Pr"
    Nd = "Nd"
    Pm = "Pm"
    Sm = "Sm"
    Eu = "Eu"
    Gd = "Gd"
    Tb = "Tb"
    Dy = "Dy"
    Ho = "Ho"
    Er = "Er"
    Tm = "Tm"
    Yb = "Yb"
    Lu = "Lu"
    Hf = "Hf"
    Ta = "Ta"
    W = "W"
    Re = "Re"
    Os = "Os"
    Ir = "Ir"
    Pt = "Pt"
    Au = "Au"
    Hg = "Hg"
    Tl = "Tl"
    Pb = "Pb"
    Bi = "Bi"
    Po = "Po"
    At = "At"
    Rn = "Rn"
    Fr = "Fr"
    Ra = "Ra"
    Ac = "Ac"
    Th = "Th"
    Pa = "Pa"
    U = "U"
    Np = "Np"
    Pu = "Pu"
    Am = "Am"
    Cm = "Cm"
    Bk = "Bk"
    Cf = "Cf"
    Es = "Es"
    Fm = "Fm"
    Md = "Md"
    No = "No"
    Lr = "Lr"
    Rf = "Rf"
    Db = "Db"
    Sg = "Sg"
    Bh = "Bh"
    Hs = "Hs"
    Mt = "Mt"
    Ds = "Ds"
    Rg = "Rg"
    Cn = "Cn"
    Nh = "Nh"
    Fl = "Fl"
    Mc = "Mc"
    Lv = "Lv"
    Ts = "Ts"
    Og = "Og"
