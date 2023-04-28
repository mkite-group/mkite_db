from .base import JobCreationError, InputQuery
from .simple import SimpleJobCreator
from .tuple import TupleJobCreator


JOB_CREATORS = {
    "simple": SimpleJobCreator,
    "tuple": TupleJobCreator,
}
