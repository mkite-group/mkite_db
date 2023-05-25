from typing import Dict, Iterable
from itertools import chain
from django.db import models, transaction
from rest_framework import serializers
from rest_framework.fields import empty


class BaseSerializer(serializers.ModelSerializer):
    """Class that augments the functionalities of DRF to automate
    the creation/update of instances if unique fields are
    specified in the input data. Instead of attempting the creation
    of a new instance every time a serializer is used (POST behavior),
    this class simplifies the representation of the input data, which
    enables `id`, `uuid`, and `name` fields to be used as identifiers
    to check the existence of a new instance.
    """

    id = serializers.IntegerField(required=False)
    uuid = serializers.UUIDField(required=False)

    def __init__(self, instance=None, data=empty, nested_field=False, **kwargs):
        if instance is None and data is not empty:
            instance, data = self.get_instance_from_data(data)

        if instance is not None:
            kwargs["partial"] = kwargs.get("partial", True)

        super().__init__(instance, data, **kwargs)

        self.nested_field = nested_field
        if nested_field:
            self._setup_serializer_as_field()

    def _setup_serializer_as_field(self):
        """Useful to bypass validation when nested serializers are used
        in mkite_db. Ensures then that the rest of the validation is
        performed by the user at the creation/update stage.
        """
        for field_name, field in self.fields.items():
            field.required = False
            field.read_only = False
            if field_name in self.id_fields:
                field.validators = []

    @property
    def id_fields(self):
        default = ["id", "uuid", "name", "inchikey", "smiles"]
        return getattr(self.Meta, "id_fields", default)

    def get_instance_from_data(self, data: dict):
        model = self.Meta.model

        id_data = {k: v for k, v in data.items() if k in self.id_fields}
        if not id_data:
            return None, data

        instances = model.objects.filter(**id_data)
        if not instances.exists():
            return None, data

        if instances.count() > 1:
            raise serializers.ValidationError(
                "There is more than one \
                instance for the data provided."
            )

        instance = instances.first()

        # prevent the serializer from passing unique-like data ahead
        new_data = {k: v for k, v in data.items() if k not in self.id_fields}

        return instance, new_data

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["@module"] = instance._meta.model.__module__
        data["@class"] = instance._meta.model.__name__
        return data

    def get_nested_fields(self) -> Dict[str, serializers.Field]:
        return {
            name: field
            for name, field in self.fields.items()
            if getattr(field, "nested_field", False)
        }

    def get_nested_objects(self, validated_data: dict) -> Dict[str, object]:
        """Using the given validated data, retrieves all information
        that had been passed to the serializer to create/get the model
        corresponding to that field. As this base serializer has plenty
        of nested fields, this model helps creating/updating new objects
        based on these nested fields.
        """
        nested_objs = {}

        nested_fields = self.get_nested_fields()

        for field_name, field in nested_fields.items():
            if field_name not in validated_data:
                continue

            field_data = validated_data.pop(field_name)
            obj = self.deserialize_nested(field, field_data)
            nested_objs[field_name] = obj

        return nested_objs

    def update_m2m(self, instance, field_name: str, field_value: Iterable):
        field = getattr(instance, field_name)
        if not isinstance(field_value, Iterable):
            field_value = [field_value]

        field.add(*field_value)

    @transaction.atomic
    def create(self, validated_data: dict):
        nested_objs = self.get_nested_objects(validated_data)
        create_dict = {**validated_data, **nested_objs}

        model = self.Meta.model
        instance = model.objects.create(**create_dict)

        return instance

    @transaction.atomic
    def update(self, instance, validated_data: dict):
        nested_objs = self.get_nested_objects(validated_data)
        update_dict = {**validated_data, **nested_objs}

        for k, v in update_dict.items():
            setattr(instance, k, v)

        instance.save()

        return instance

    def deserialize_nested(self, field, field_data: dict):
        serializer = field.__class__(data=field_data)
        if not serializer.is_valid():
            raise serializers.ValidationError(
                f"Data for {field.field_name} is not valid"
            )

        return serializer.save()
