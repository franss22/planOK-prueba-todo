"""Serializers for the Task application."""

from rest_framework import serializers

from .models import Task


class TaskSerializer(serializers.ModelSerializer):
    """Serializer for the Task model.

    This serializer converts Task model instances into JSON format and vice versa.
    It includes all fields of the Task model and marks 'id' and 'created_at'
    as read-only fields.
    """

    class Meta:
        """Meta options for the TaskSerializer."""

        model = Task
        fields = ("id", "title", "content", "done", "created_at")
        read_only_fields = ("id", "created_at")


class TaskReportRequestSerializer(serializers.Serializer):
    """Serializer for task report requests."""

    format = serializers.ChoiceField(choices=("summary", "detailed"), default="summary")
    include_completed = serializers.BooleanField(default=True)
    language = serializers.CharField(default="es", max_length=10)
    prompt = serializers.CharField(required=False, allow_blank=True, max_length=500)
    task_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        required=False,
        allow_empty=True,
    )
