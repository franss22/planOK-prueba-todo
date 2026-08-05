"""Views for the Task application."""

import os
from typing import TYPE_CHECKING

from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Task
from .serializers import TaskReportRequestSerializer, TaskSerializer

if TYPE_CHECKING:
    from django.db.models import QuerySet
    from rest_framework.request import Request


class TaskViewSet(viewsets.ModelViewSet):
    """ViewSet for managing Task instances."""

    serializer_class = TaskSerializer
    queryset = Task.objects.all()

    def get_queryset(self) -> QuerySet[Task]:
        """Retrieve the queryset of Task instances, optionally filtered by query parameters."""
        queryset = super().get_queryset()

        done = self.request.query_params.get("done")
        if done is not None:
            normalized = done.strip().lower()
            if normalized in {"true", "1", "yes", "on"}:
                queryset = queryset.filter(done=True)
            elif normalized in {"false", "0", "no", "off"}:
                queryset = queryset.filter(done=False)

        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(title__icontains=search) | queryset.filter(content__icontains=search)

        return queryset


class TaskReportAPIView(APIView):
    """Endpoint for generating AI task reports."""

    def post(self, request: Request) -> Response:
        """Validate request parameters and return a task report payload."""
        serializer = TaskReportRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        report_format = serializer.validated_data["format"]
        include_completed = serializer.validated_data["include_completed"]
        language = serializer.validated_data["language"]
        task_ids = serializer.validated_data.get("task_ids", [])

        all_tasks = Task.objects.all()
        if task_ids:
            report_tasks = all_tasks.filter(id__in=task_ids)
        else:
            report_tasks = all_tasks if include_completed else all_tasks.filter(done=False)

        total = all_tasks.count()
        completed = all_tasks.filter(done=True).count()
        pending = all_tasks.filter(done=False).count()

        tasks_payload = [
            {
                "id": task.id,
                "title": task.title,
                "content": task.content,
                "done": task.done,
                "created_at": task.created_at.isoformat(),
            }
            for task in report_tasks
        ]

        report_text = self._build_report(
            tasks_payload=tasks_payload,
            total=total,
            completed=completed,
            pending=pending,
            report_format=report_format,
            language=language,
        )

        return Response(
            {
                "generated_at": Task.objects.first().created_at.isoformat() if total else None,
                "model": os.getenv("GROK_MODEL", "grok"),
                "report": report_text,
                "stats": {
                    "total": total,
                    "completed": completed,
                    "pending": pending,
                },
            },
            status=status.HTTP_200_OK,
        )

    def _build_report(
        self,
        *,
        tasks_payload: list[dict[str, object]],
        total: int,
        completed: int,
        pending: int,
        report_format: str,
        language: str,
    ) -> str:
        """Build a report with Grok, or return a deterministic fallback if no API key exists."""
        grok_api_key = os.getenv("GROK_API_KEY")
        grok_model = os.getenv("GROK_MODEL", "grok-beta")

        if not grok_api_key:
            return f"Report ({report_format}, {language}): total={total}, completed={completed}, pending={pending}."

        prompt = ChatPromptTemplate.from_template(
            """
            You are a project assistant that creates concise task reports.

            Language: {language}
            Format: {report_format}
            Totals: total={total}, completed={completed}, pending={pending}
            Tasks: {tasks_payload}

            Return a clear report with:
            1) Status summary
            2) Key pending tasks
            3) Recommended next actions
            """
        )

        chain = prompt | ChatGroq(model=grok_model, api_key=grok_api_key)
        response = chain.invoke(
            {
                "language": language,
                "report_format": report_format,
                "total": total,
                "completed": completed,
                "pending": pending,
                "tasks_payload": tasks_payload,
            }
        )
        return response.content
