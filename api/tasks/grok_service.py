"""Service for sending task data to the Grok chat API."""

import logging
import os
from typing import Any

import requests

logger = logging.getLogger(__name__)


class GrokChatService:
    """Wrap the Grok chat completions API for report generation."""

    _PRIORITY_KEYWORDS = (
        "urgent",
        "urgente",
        "critical",
        "critico",
        "crítico",
        "blocker",
        "bloqueo",
        "important",
        "importante",
        "priority",
        "prioridad",
        "fix",
        "asap",
    )

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        base_url: str | None = None,
        timeout: int | None = None,
    ) -> None:
        self.api_key = api_key or os.getenv("GROK_API_KEY", "")
        self.model = model or os.getenv("GROK_MODEL", "grok-2-latest")
        self.base_url = base_url or os.getenv("GROK_API_URL", "https://api.x.ai/v1/chat/completions")
        self.timeout = timeout or int(os.getenv("GROK_API_TIMEOUT", "30"))

    def _is_spanish_language(self, language: str) -> bool:
        """Return True when the requested language is Spanish."""
        return language.strip().lower().startswith("es")

    def _task_priority_score(self, task: dict[str, Any]) -> int:
        """Score a task by urgency signals in its title and content."""
        haystack = f"{task.get('title', '')} {task.get('content', '')}".lower()
        return sum(1 for keyword in self._PRIORITY_KEYWORDS if keyword in haystack)

    def _pick_priority_task(self, tasks_payload: list[dict[str, Any]]) -> dict[str, Any] | None:
        """Pick the single most important task from the payload."""
        if not tasks_payload:
            return None

        pending_tasks = [task for task in tasks_payload if not task.get("done", False)]
        candidate_tasks = pending_tasks or tasks_payload

        return sorted(
            candidate_tasks,
            key=lambda task: (
                -self._task_priority_score(task),
                task.get("done", False),
                task.get("created_at", ""),
                task.get("title", ""),
            ),
        )[0]

    def generate_report(
        self,
        *,
        prompt: str | None,
        tasks_payload: list[dict[str, Any]],
        total: int,
        completed: int,
        pending: int,
        language: str,
        report_format: str,
    ) -> str:
        """Generate a report by calling the Grok API with prompt and task data."""
        priority_task = self._pick_priority_task(tasks_payload)
        prompt_text = prompt or self._build_default_prompt(
            language=language,
            report_format=report_format,
            total=total,
            completed=completed,
            pending=pending,
            priority_task=priority_task,
        )

        if not self.api_key:
            return self._build_fallback_report(
                tasks_payload=tasks_payload,
                report_format=report_format,
                language=language,
                total=total,
                completed=completed,
                pending=pending,
                priority_task=priority_task,
            )

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": self._build_system_prompt(language),
                },
                {
                    "role": "user",
                    "content": self._build_user_prompt(
                        prompt_text=prompt_text,
                        language=language,
                        report_format=report_format,
                        total=total,
                        completed=completed,
                        pending=pending,
                        priority_task=priority_task,
                        tasks_payload=tasks_payload,
                    ),
                },
            ],
            "temperature": 0.2,
        }

        try:
            response = requests.post(
                self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=self.timeout,
            )
            response.raise_for_status()
            data = response.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            if content:
                return content.strip()
        except requests.RequestException as exc:
            logger.exception("Grok report generation failed: %s", exc)

        return self._build_fallback_report(
            tasks_payload=tasks_payload,
            report_format=report_format,
            language=language,
            total=total,
            completed=completed,
            pending=pending,
            priority_task=priority_task,
        )

    def _build_system_prompt(self, language: str) -> str:
        """Build the system prompt for the selected language."""
        if self._is_spanish_language(language):
            return (
                "Eres un asistente de proyectos que escribe análisis breves y claros. "
                "Responde solo con el reporte final y en español."
            )

        return (
            "You are a project assistant that writes short, clear task analyses. "
            "Respond only with the final report and use the requested language."
        )

    def _build_user_prompt(
        self,
        *,
        prompt_text: str,
        language: str,
        report_format: str,
        total: int,
        completed: int,
        pending: int,
        priority_task: dict[str, Any] | None,
        tasks_payload: list[dict[str, Any]],
    ) -> str:
        """Build the user prompt for Grok."""
        priority_title = priority_task.get("title", "task") if priority_task else "no tasks"

        if self._is_spanish_language(language):
            return (
                f"Escribe un informe {report_format} en español.\n"
                f"Instrucción del usuario: {prompt_text}\n"
                f"Totales: total={total}, completadas={completed}, pendientes={pending}\n"
                f"Tarea prioritaria: {priority_title}\n"
                f"Tareas: {tasks_payload}\n"
                "Devuelve un análisis breve y natural, centrado en una sola tarea prioritaria, "
                "con resumen, motivo de prioridad y siguiente paso."
            )

        return (
            f"Write a {report_format} report in {language}.\n"
            f"User instruction: {prompt_text}\n"
            f"Totals: total={total}, completed={completed}, pending={pending}\n"
            f"Priority task: {priority_title}\n"
            f"Tasks: {tasks_payload}\n"
            "Return a short, natural analysis focused on one priority task, with a summary, "
            "why it should come first, and the next step."
        )

    def _build_default_prompt(
        self,
        *,
        language: str,
        report_format: str,
        total: int,
        completed: int,
        pending: int,
        priority_task: dict[str, Any] | None,
    ) -> str:
        """Build the default prompt used when no custom prompt is supplied."""
        priority_text = (
            "No task data is available yet."
            if priority_task is None
            else f"The single top priority task is: {priority_task.get('title', 'task')}"
        )

        if self._is_spanish_language(language):
            return (
                f"Escribe un informe {report_format} en español sobre el estado actual del proyecto. "
                f"Enfócate en una sola tarea y recomienda qué debe hacerse después. "
                f"{priority_text} "
                f"Totales: total={total}, completadas={completed}, pendientes={pending}."
            )

        return (
            f"Create a {report_format} report in {language} about the current project status. "
            f"Focus on exactly one task and recommend what should be done next. "
            f"{priority_text} "
            f"Totals: total={total}, completed={completed}, pending={pending}."
        )

    def _build_fallback_report(
        self,
        *,
        tasks_payload: list[dict[str, Any]],
        report_format: str,
        language: str,
        total: int,
        completed: int,
        pending: int,
        priority_task: dict[str, Any] | None,
    ) -> str:
        """Build the local fallback report when the API key is unavailable or the call fails."""
        fallback_mode = os.getenv("GROK_FALLBACK_MODE", "analysis").strip().lower()
        priority_title = priority_task.get("title", "task") if priority_task else "no tasks"

        if self._is_spanish_language(language):
            if fallback_mode == "summary":
                return (
                    f"Resumen de respaldo en español. Totales: total={total}, completadas={completed}, "
                    f"pendientes={pending}. Tarea prioritaria: {priority_title}."
                )

            return (
                f"Análisis escrito en español: hay {completed} tarea(s) completada(s) y {pending} pendiente(s) "
                f"de un total de {total}. La tarea que deberías priorizar es '{priority_title}'. "
                f"Siguiente paso: trabaja primero en esa tarea."
            )

        if fallback_mode == "summary":
            return (
                f"Fallback summary in {language}. Totals: total={total}, completed={completed}, "
                f"pending={pending}. Priority task: {priority_title}."
            )

        return (
            f"Fallback analysis in {language}: {completed} of {total} tasks are completed, leaving {pending} pending. "
            f"Prioritize '{priority_title}' next."
        )
