"""Views for the Task application."""

import os
from typing import TYPE_CHECKING

from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .grok_service import DEFAULT_GROK_MODEL, GrokChatService
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

    _FALLBACK_STRINGS = {
        "en": {
            "title": "Fallback report",
            "summary": "There are {total} tasks in total: {completed} completed and {pending} pending.",
            "focus": "Focus next on: {task_title}.",
            "reason": "Reason: it is still pending and should be handled before less urgent work.",
            "empty": "No tasks are available to analyze.",
        },
        "es": {
            "title": "Reporte de respaldo",
            "summary": "Hay {total} tareas en total: {completed} completadas y {pending} pendientes.",
            "focus": "Enfócate después en: {task_title}.",
            "reason": "Motivo: sigue pendiente y conviene resolverla antes que el trabajo menos urgente.",
            "empty": "No hay tareas disponibles para analizar.",
        },
    }

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
            prompt=serializer.validated_data.get("prompt", ""),
        )

        return Response(
            {
                "generated_at": Task.objects.first().created_at.isoformat() if total else None,
                "model": os.getenv("GROK_MODEL", DEFAULT_GROK_MODEL),
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
        prompt: str | None = None,
    ) -> str:
        """Generate the report through the shared GrokChatService pipeline."""
        if not (os.getenv("GROK_API_KEY") or os.getenv("XAI_API_KEY")):
            return self._build_fallback_report(
                tasks_payload=tasks_payload,
                total=total,
                completed=completed,
                pending=pending,
                language=language,
            )

        service = GrokChatService(
            api_key=os.getenv("GROK_API_KEY"),
            model=os.getenv("GROK_MODEL", DEFAULT_GROK_MODEL),
        )
        return service.generate_report(
            prompt=prompt,
            tasks_payload=tasks_payload,
            total=total,
            completed=completed,
            pending=pending,
            language=language,
            report_format=report_format,
        )

    def _build_fallback_report(
        self,
        *,
        tasks_payload: list[dict[str, object]],
        total: int,
        completed: int,
        pending: int,
        language: str,
    ) -> str:
        """Return a deterministic local report when no AI credentials are configured."""
        strings = self._FALLBACK_STRINGS["es" if language.strip().lower().startswith("es") else "en"]
        summary = strings["summary"].format(total=total, completed=completed, pending=pending)

        pending_task = next((task for task in tasks_payload if not task.get("done")), None)
        if pending_task:
            focus = strings["focus"].format(task_title=pending_task["title"])
            reason = strings["reason"]
        else:
            focus = strings["empty"]
            reason = ""

        report_parts = [strings["title"], summary, focus]
        if reason:
            report_parts.append(reason)
        return " ".join(report_parts)

