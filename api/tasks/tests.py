"""Tests for the tasks app."""

from unittest.mock import Mock, patch

from django.test import SimpleTestCase, TestCase
from django.urls import reverse
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from rest_framework import status
from rest_framework.test import APITestCase

from .grok_service import GrokChatService
from .models import Task
from .serializers import TaskReportRequestSerializer, TaskSerializer


class GrokChatServiceTests(SimpleTestCase):
    """Tests for the Grok chat service."""

    @patch("tasks.grok_service.GrokChatService._build_chain")
    def test_generate_report_uses_langchain_pipeline(self, mock_build_chain: Mock) -> None:
        """The service should invoke a LangChain pipeline and return its content."""
        mock_chain = Mock()
        mock_chain.invoke.return_value = Mock(content="Reporte generado")
        mock_build_chain.return_value = mock_chain

        service = GrokChatService(api_key="secret", model="grok-4")
        content = service.generate_report(
            prompt="Resume las tareas",
            tasks_payload=[{"id": 1, "title": "Tarea 1", "completed": False}],
            total=1,
            completed=0,
            pending=1,
            language="es",
            report_format="summary",
        )

        self.assertEqual(content, "Reporte generado")
        mock_build_chain.assert_called_once()

    def test_prompt_template_accepts_literal_task_dicts(self) -> None:
        """Prompt construction should not treat task payload dict keys as template variables."""
        service = GrokChatService(api_key="secret", model="grok-4")

        prompt_template = ChatPromptTemplate.from_messages(
            [
                SystemMessage(content=service._build_system_prompt("es")),
                HumanMessage(
                    content=service._build_user_prompt(
                        prompt_text="Resume las tareas",
                        language="es",
                        report_format="summary",
                        total=1,
                        completed=0,
                        pending=1,
                        tasks_payload=[{"id": 1, "title": "Tarea 1", "completed": False}],
                    )
                ),
            ]
        )

        messages = prompt_template.invoke({}).messages

        self.assertIn("'id': 1", messages[1].content)


class TaskSerializerTests(TestCase):
    """Tests for task-related serializers."""

    def test_task_serializer_valid_data_sets_default_done(self) -> None:
        """TaskSerializer should accept valid payload and use model default completed when omitted."""
        serializer = TaskSerializer(data={"title": "Buy milk", "content": "2 liters"})

        self.assertTrue(serializer.is_valid(), serializer.errors)
        task = serializer.save()

        self.assertFalse(task.completed)
        self.assertEqual(task.title, "Buy milk")

    def test_task_serializer_requires_title_and_content(self) -> None:
        """TaskSerializer should require title and content fields."""
        serializer = TaskSerializer(data={})

        self.assertFalse(serializer.is_valid())
        self.assertIn("title", serializer.errors)
        self.assertIn("content", serializer.errors)

    def test_task_report_request_serializer_defaults(self) -> None:
        """TaskReportRequestSerializer should apply defaults for optional fields."""
        serializer = TaskReportRequestSerializer(data={})

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["format"], "summary")
        self.assertTrue(serializer.validated_data["include_completed"])
        self.assertEqual(serializer.validated_data["language"], "es")

    def test_task_report_request_serializer_rejects_invalid_format(self) -> None:
        """TaskReportRequestSerializer should validate format choices."""
        serializer = TaskReportRequestSerializer(data={"format": "invalid"})

        self.assertFalse(serializer.is_valid())
        self.assertIn("format", serializer.errors)


class TaskCrudApiTests(APITestCase):
    """CRUD API tests for task endpoints."""

    def setUp(self) -> None:
        """Create base URL and seed task for detail endpoint tests."""
        self.list_url = reverse("task-list")
        self.task = Task.objects.create(title="Initial task", content="Initial content", completed=False)

    def test_list_tasks_returns_paginated_payload(self) -> None:
        """List endpoint should return paginated task results."""
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["id"], self.task.id)

    def test_create_task(self) -> None:
        """Create endpoint should persist and return the new task."""
        payload = {
            "title": "Write tests",
            "content": "Add CRUD tests",
            "completed": True,
        }

        response = self.client.post(self.list_url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 2)
        created = Task.objects.get(id=response.data["id"])
        self.assertEqual(created.title, payload["title"])
        self.assertEqual(created.content, payload["content"])
        self.assertTrue(created.completed)

    def test_retrieve_task(self) -> None:
        """Detail endpoint should return a single task by id."""
        url = reverse("task-detail", args=[self.task.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.task.id)
        self.assertEqual(response.data["title"], self.task.title)

    def test_partial_update_task(self) -> None:
        """Patch endpoint should update only provided fields."""
        url = reverse("task-detail", args=[self.task.id])
        response = self.client.patch(url, {"completed": True}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertTrue(self.task.completed)
        self.assertEqual(self.task.title, "Initial task")

    def test_delete_task(self) -> None:
        """Delete endpoint should remove task and return 204."""
        url = reverse("task-detail", args=[self.task.id])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Task.objects.filter(id=self.task.id).exists())

    def test_list_tasks_filters_by_done(self) -> None:
        """List endpoint should filter tasks by completed query parameter."""
        done_task = Task.objects.create(title="completed task", content="Completed", completed=True)

        pending_response = self.client.get(self.list_url, {"completed": "false"})
        done_response = self.client.get(self.list_url, {"completed": "true"})

        self.assertEqual(pending_response.status_code, status.HTTP_200_OK)
        self.assertEqual(done_response.status_code, status.HTTP_200_OK)

        pending_ids = {item["id"] for item in pending_response.data["results"]}
        done_ids = {item["id"] for item in done_response.data["results"]}

        self.assertIn(self.task.id, pending_ids)
        self.assertNotIn(done_task.id, pending_ids)
        self.assertIn(done_task.id, done_ids)
        self.assertNotIn(self.task.id, done_ids)

    def test_list_tasks_filters_by_search(self) -> None:
        """List endpoint should filter tasks by title/content search query parameter."""
        Task.objects.create(title="Do laundry", content="Use cold cycle", completed=False)
        Task.objects.create(title="Read book", content="Search chapter", completed=False)

        response = self.client.get(self.list_url, {"search": "laundry"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["title"], "Do laundry")


class TaskReportApiTests(APITestCase):
    """API tests for the task report endpoint."""

    def setUp(self) -> None:
        """Create sample tasks and report endpoint URL."""
        self.report_url = reverse("tasks-report")
        Task.objects.create(title="Pending task", content="To do", completed=False)
        Task.objects.create(title="completed task", content="Already completed", completed=True)

    @patch.dict("os.environ", {"GROK_API_KEY": ""}, clear=False)
    def test_report_endpoint_without_api_key_returns_fallback(self) -> None:
        """Report endpoint should return deterministic fallback text when GROK_API_KEY is empty."""
        payload = {"format": "summary", "include_completed": True, "language": "es"}
        response = self.client.post(self.report_url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("report", response.data)
        self.assertIn("Reporte de respaldo", response.data["report"])
        self.assertIn("tareas", response.data["report"])
        self.assertEqual(response.data["stats"]["total"], 2)
        self.assertEqual(response.data["stats"]["completed"], 1)
        self.assertEqual(response.data["stats"]["pending"], 1)

    @patch.dict("os.environ", {"GROK_API_KEY": ""}, clear=False)
    def test_report_endpoint_without_api_key_uses_simple_fallback_template(self) -> None:
        """Fallback report should stay lightweight and template-based."""
        Task.objects.create(title="Urgent fix", content="Fix the blocker", completed=False)

        response = self.client.post(
            self.report_url,
            {"format": "summary", "include_completed": True, "language": "es"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Reporte de respaldo", response.data["report"])
        self.assertIn("tareas", response.data["report"])

    @patch("tasks.views.TaskReportAPIView._build_report", return_value="mocked report")
    @patch.dict("os.environ", {"GROK_API_KEY": "test-key", "GROK_MODEL": "grok-test"}, clear=False)
    def test_report_endpoint_uses_prompt_from_request(self, mock_build_report: Mock) -> None:
        """The report endpoint should forward the prompt from the request to the report builder."""
        payload = {
            "format": "detailed",
            "include_completed": False,
            "language": "en",
            "prompt": "Prioritize the blocker",
        }
        response = self.client.post(self.report_url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["report"], "mocked report")
        self.assertEqual(mock_build_report.call_args.kwargs["prompt"], "Prioritize the blocker")

    @patch("tasks.views.TaskReportAPIView._build_report", return_value="mocked report")
    @patch.dict("os.environ", {"GROK_API_KEY": "test-key", "GROK_MODEL": "grok-test"}, clear=False)
    def test_report_endpoint_with_api_key_uses_report_builder(self, mock_build_report: Mock) -> None:
        """Report endpoint should use report builder flow when GROK_API_KEY is set."""
        payload = {"format": "detailed", "include_completed": False, "language": "en"}
        response = self.client.post(self.report_url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["report"], "mocked report")
        self.assertEqual(response.data["model"], "grok-test")
        self.assertEqual(mock_build_report.call_count, 1)
