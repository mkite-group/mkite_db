from typing import Union
from collections import namedtuple
from django.db import transaction

from mkite_core.models import JobResults
from mkite_db.orm.deserializers import get_serializer, DeserializeError
from mkite_db.orm.jobs.serializers import JobSerializer, RunStatsSerializer


ParserOutput = namedtuple("ParserOutput", "job runstats nodes")
NodesOutput = namedtuple("NodesOutput", "chemnode calcnodes")


class JobParser:
    """Class that parses the jobs correctly run in different systems.
    Given a certain engine, gets all jobs that have been correctly run
    and not yet parsed.
    """

    def __init__(self, results: JobResults):
        self.results = results

    @transaction.atomic
    def parse(self) -> ParserOutput:
        job = self.create_job()
        runstats = self.create_stats(job)

        if runstats is not None:
            job.runstats = runstats
            job.save()

        nodes = self.create_nodes(job)

        return ParserOutput(job=job, runstats=runstats, nodes=nodes)

    def create_job(self) -> "Job":
        data = self.results.job

        if "status" not in data:
            data["status"] = "D"

        serial = JobSerializer(data=data)
        if not serial.is_valid():
            raise DeserializeError(f"Error deserializing Job. Errors: {serial.errors}")

        return serial.save()

    def create_stats(self, job: "Job") -> "RunStats":
        if not self.results.runstats:
            return None

        data = self.results.runstats.as_dict()

        if type(data.get("duration")) == float:
            data["duration"] = round(data["duration"], 6)

        serial = RunStatsSerializer(data=data)

        if not serial.is_valid():
            raise DeserializeError(
                f"Error deserializing RunStats. Errors: {serial.errors}"
            )

        return serial.save()

    def create_nodes(self, job: "Job") -> NodesOutput:
        nodes = []
        for node_results in self.results.nodes:
            chnode = self.create_chemnode(node_results.chemnode, job=job)
            calcs = [
                self.create_calcnode(calcdict, job=job, chemnode=chnode)
                for calcdict in node_results.calcnodes
            ]
            nodes += [NodesOutput(chemnode=chnode, calcnodes=calcs)]

        return nodes

    def create_chemnode(self, chemdict: dict, job: "Job") -> "ChemBase":
        chemdict["parentjob"] = {"id": job.id}
        return self.deserialize_node(chemdict)

    def create_calcnode(
        self, calcdict: dict, chemnode: "ChemBase", job: "Job"
    ) -> "CalcBase":
        calcdict["parentjob"] = {"id": job.id}
        calcdict["chemnode"] = {"id": chemnode.id}
        return self.deserialize_node(calcdict)

    def deserialize_node(self, nodedict: dict) -> Union["ChemBase", "CalcBase"]:
        serial = get_serializer(nodedict)
        if not serial.is_valid():
            raise DeserializeError(f"Error deserializing Job. Errors: {serial.errors}")
        return serial.save()
