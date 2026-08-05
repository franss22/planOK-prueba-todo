"""Service for sending task data to the Grok chat API."""

import logging
import os
from typing import Any

import requests

logger = logging.getLogger(__name__)


class GrokChatService:
    """Wraps the Grok chat completions API for report generation."""

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

    def _pick_priority_task(self, tasks_payload: list[dict[str, Any]]) -> dict[str, Any] | None:
        """Pick the most important task from the payload."""
        if not tasks_payload:
            return None

        pending_tasks = [task for task in tasks_payload if not task.get("done", False)]
        candidate_tasks = pending_tasks or tasks_payload

        return sorted(
            candidate_tasks,
            key=lambda task: (
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
        prompt_text = prompt or self._build_default_prompt(
            language=language,
            report_format=report_format,
            total=total,
            completed=completed,
            pending=pending,
            priority_task=self._pick_priority_task(tasks_payload),
        )

        if not self.api_key:
            return self._build_fallback_report(
                tasks_payload=tasks_payload,
                report_format=report_format,
                language=language,
                total=total,
                completed=completed,
                pending=pending,
            )

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a project assistant that turns task lists into concise business reports. "
                        "Return actionable insights and highlight pending work."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Create a {report_format} report in {language}.\n"
                        f"User instruction: {prompt_text}\n"
                        f"Totals: total={total}, completed={completed}, pending={pending}\n"
                        f"Tasks: {tasks_payload}"
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
        priority_text = (
            "No task data is available yet."
            if priority_task is None
            else (f"The single top priority task is: {priority_task.get('title', 'task')}")
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
    ) -> str:
        fallback_mode = os.getenv("GROK_FALLBACK_MODE", "analysis").strip().lower()
        fallback_style = os.getenv("GROK_FALLBACK_STYLE", "written").strip().lower()
        fallback_note = os.getenv(
            "GROK_FALLBACK_NOTE",
            "Name one task to prioritize and explain why it should be next.",
        ).strip()

        priority_task = self._pick_priority_task(tasks_payload)
        priority_title = priority_task.get("title", "task") if priority_task else "no tasks"

        if fallback_mode == "summary":
            return (
                f"{fallback_style.capitalize()} fallback report in {language}. "
                f"Totals: total={total}, completed={completed}, pending={pending}. "
                f"Priority task: {priority_title}. Note: {fallback_note}"
            )

        return (
            f"{fallback_style.capitalize()} analysis in {language}: the current list has {completed} completed "
            f"task(s) and {pending} pending task(s) out of {total}. Prioritize '{priority_title}' next. "
            f"Suggestion: {fallback_note}"
        )
