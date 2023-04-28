from django.db import transaction
from .models import Job


@transaction.atomic
def delete_tree(job: Job):
    """Cascades the deletion of the whole job tree under this job.
    All child jobs, along with all their nodes, will be deleted.
    """

    for j in job.childjobs:
        delete_tree(j)

    if job.runstats is not None:
        job.runstats.delete()

    job.calcnodes.all().delete()
    job.chemnodes.all().delete()
    job.delete()
