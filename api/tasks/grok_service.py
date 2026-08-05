"""Service for generating task reports with a Grok LangChain pipeline."""

import logging
import os
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_xai import ChatXAI

logger = logging.getLogger(__name__)

DEFAULT_GROK_MODEL = "grok-4"


class GrokChatService:
    """Wrap a LangChain Grok pipeline for report generation."""

    _LANGUAGE_STRINGS = {
        "en": {
            "system": "You are a project assistant that writes short, clear task analyses. Respond only with the final report and use the requested language.",
            "default_prompt": (
                "Create a {report_format} report in {language} about the current project status. "
                "Focus on exactly one task and recommend what should be completed next. "
                "Totals: total={total}, completed={completed}, pending={pending}."
            ),
            "user_prompt": (
                "Write a {report_format} report in {language}.\n"
                "User instruction: {prompt_text}\n"
                "Totals: total={total}, completed={completed}, pending={pending}\n"
                "Tasks: {tasks_payload}\n"
                "Pick the most urgent task in the list and explain briefly why it should come first."
            ),
            "missing_api_key": "GROK_API_KEY or XAI_API_KEY is required to generate reports",
            "empty_report": "Grok returned an empty report",
            "auth_error": "The Grok API rejected the request. Please verify that GROK_API_KEY is valid.",
            "upstream_error": "Grok request failed: {details}",
        },
        "es": {
            "system": "Eres un asistente de proyectos que escribe análisis breves y claros. Responde solo con el reporte final y en español.",
            "default_prompt": (
                "Escribe un informe {report_format} en español sobre el estado actual del proyecto. "
                "Enfócate en una sola tarea y recomienda qué debe hacerse después. "
                "Totales: total={total}, completadas={completed}, pendientes={pending}."
            ),
            "user_prompt": (
                "Escribe un informe {report_format} en español.\n"
                "Instrucción del usuario: {prompt_text}\n"
                "Totales: total={total}, completadas={completed}, pendientes={pending}\n"
                "Tareas: {tasks_payload}\n"
                "Elige la tarea más urgente del conjunto y explica brevemente por qué debe ir primero."
            ),
            "missing_api_key": "GROK_API_KEY o XAI_API_KEY es requerida para generar reportes",
            "empty_report": "Grok devolvió un reporte vacío",
            "auth_error": "La API de Grok rechazó la solicitud. Verifica que GROK_API_KEY sea válida.",
            "upstream_error": "La solicitud a Grok falló: {details}",
        },
    }

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        timeout: int | None = None,
    ) -> None:
        self.api_key = api_key or os.getenv("GROK_API_KEY") or os.getenv("XAI_API_KEY", "")
        self.model = model or os.getenv("GROK_MODEL", DEFAULT_GROK_MODEL)
        self.timeout = timeout or int(os.getenv("GROK_API_TIMEOUT", "30"))
        self.language_strings = self._get_language_strings("en")

    def _is_spanish_language(self, language: str) -> bool:
        """Return True when the requested language is Spanish."""
        return language.strip().lower().startswith("es")

    def _get_language_strings(self, language: str) -> dict[str, str]:
        """Return the localized string bundle for the requested language."""
        if self._is_spanish_language(language):
            return self._LANGUAGE_STRINGS["es"]
        return self._LANGUAGE_STRINGS["en"]

    def _build_system_prompt(self, language: str) -> str:
        """Build the system prompt for the selected language."""
        return str(self._get_language_strings(language)["system"])

    def _build_user_prompt(
        self,
        *,
        prompt_text: str,
        language: str,
        report_format: str,
        total: int,
        completed: int,
        pending: int,
        tasks_payload: list[dict[str, Any]],
    ) -> str:
        """Build the user prompt for Grok."""
        strings = self._get_language_strings(language)
        template = strings["user_prompt"]
        return template.format(
            report_format=report_format,
            language=language,
            prompt_text=prompt_text,
            total=total,
            completed=completed,
            pending=pending,
            tasks_payload=tasks_payload,
        )

    def _build_default_prompt(
        self,
        *,
        language: str,
        report_format: str,
        total: int,
        completed: int,
        pending: int,
    ) -> str:
        """Build the default prompt used when no custom prompt is supplied."""
        strings = self._get_language_strings(language)
        template = strings["default_prompt"]
        return template.format(
            report_format=report_format,
            language=language,
            total=total,
            completed=completed,
            pending=pending,
        )

    def _build_chain(
        self,
        *,
        language: str,
        report_format: str,
        total: int,
        completed: int,
        pending: int,
        tasks_payload: list[dict[str, Any]],
        prompt_text: str,
    ) -> Any:
        """Create the LangChain pipeline used to query Grok."""
        system_prompt = self._build_system_prompt(language)
        user_prompt = self._build_user_prompt(
            prompt_text=prompt_text,
            language=language,
            report_format=report_format,
            total=total,
            completed=completed,
            pending=pending,
            tasks_payload=tasks_payload,
        )
        prompt_template = ChatPromptTemplate.from_messages(
            [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt),
            ]
        )
        llm = ChatXAI(
            model=self.model,
            xai_api_key=self.api_key,
            temperature=0.2,
            timeout=self.timeout,
        )
        return prompt_template | llm

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
        """Generate a report by calling the Grok LangChain pipeline with task data."""
        prompt_text = prompt or self._build_default_prompt(
            language=language,
            report_format=report_format,
            total=total,
            completed=completed,
            pending=pending,
        )

        if not self.api_key:
            strings = self._get_language_strings(language)
            raise ValueError(strings["missing_api_key"])

        try:
            chain = self._build_chain(
                language=language,
                report_format=report_format,
                total=total,
                completed=completed,
                pending=pending,
                tasks_payload=tasks_payload,
                prompt_text=prompt_text,
            )
            response = chain.invoke({})
            content = getattr(response, "content", response)
            report = str(content).strip()
            if report:
                return report
        except Exception as exc:
            logger.exception("Grok report generation failed: %s", exc)
            strings = self._get_language_strings(language)
            if "401" in str(exc) or "invalid_api_key" in str(exc).lower():
                raise ValueError(strings["auth_error"]) from exc
            raise RuntimeError(strings["upstream_error"].format(details=str(exc))) from exc

        strings = self._get_language_strings(language)
        raise RuntimeError(strings["empty_report"])
