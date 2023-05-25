from datetime import timedelta
from rest_framework import serializers

from taggit.serializers import TagListSerializerField, TaggitSerializer
from mkite_db.orm.serializers import BaseSerializer

from .models import Project, Experiment, Job, JobRecipe, JobPackage, RunStats


class ProjectSerializer(BaseSerializer):
    description = serializers.CharField(required=False)

    class Meta:
        model = Project
        fields = (
            "id",
            "uuid",
            "name",
            "description",
        )
        read_only_fields = (
            "ctime",
            "mtime",
        )


class ExperimentSerializer(BaseSerializer):
    project = ProjectSerializer(nested_field=True)
    description = serializers.CharField(required=False)

    class Meta:
        model = Experiment
        fields = (
            "id",
            "uuid",
            "name",
            "description",
            "project",
        )
        read_only_fields = (
            "ctime",
            "mtime",
        )


class JobPackageSerializer(BaseSerializer):
    class Meta:
        model = JobPackage
        fields = (
            "id",
            "uuid",
            "name",
        )
        read_only_fields = (
            "ctime",
            "mtime",
        )


class JobRecipeSerializer(BaseSerializer):
    package = JobPackageSerializer(nested_field=True)

    class Meta:
        model = JobRecipe
        fields = (
            "id",
            "uuid",
            "name",
            "method",
            "defaults",
            "package",
        )
        read_only_fields = (
            "ctime",
            "mtime",
        )


class RunStatsSerializer(BaseSerializer):
    class Meta:
        model = RunStats
        fields = (
            "id",
            "uuid",
            "host",
            "cluster",
            "duration",
            "ncores",
            "ngpus",
            "pkgversion",
        )
        read_only_fields = (
            "ctime",
            "mtime",
        )

    def convert_duration(self, duration) -> timedelta:
        if isinstance(duration, timedelta):
            return duration

        if type(duration) in [int, float]:
            duration = round(duration, 6)
            return timedelta(seconds=duration)

        return duration

    def create(self, validated_data: dict):
        validated_data["duration"] = self.convert_duration(validated_data["duration"])
        return super().create(validated_data)

    def update(self, instance, validated_data: dict):
        validated_data["duration"] = self.convert_duration(validated_data["duration"])
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["duration"] = instance.duration.total_seconds()
        return data


class JobSerializer(TaggitSerializer, BaseSerializer):
    experiment = ExperimentSerializer(nested_field=True)
    recipe = JobRecipeSerializer(nested_field=True)
    runstats = RunStatsSerializer(nested_field=True, required=False)
    tags = TagListSerializerField(required=False)

    class Meta:
        model = Job
        fields = (
            "id",
            "uuid",
            "experiment",
            "recipe",
            "runstats",
            "status",
            "isroot",
            "options",
            "tags",
        )
        read_only_fields = (
            "ctime",
            "mtime",
        )
