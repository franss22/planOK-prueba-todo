from rest_framework import serializers
from .models import Task

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'

        
class TaskReportRequestSerializer(serializers.Serializer):
    format = serializers.CharField(
        default="written",
        required=False,
    )
    include_completed = serializers.BooleanField(
        default=False,
        required=False,
    )
    language = serializers.CharField(
        default="es",
        required=False,
    )
    task_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        default=list,
    )
    prompt = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
    )