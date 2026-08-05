from unittest.mock import patch
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from langchain_core.messages import AIMessage
from .models import Task


class TaskAPITests(APITestCase):

    def setUp(self):
        self.task = Task.objects.create(
            title="Tarea de prueba",
            description="Descripción de prueba",
            completed=False
        )
        self.list_url = reverse('task-list')
        self.detail_url = reverse('task-detail', kwargs={'pk': self.task.pk})

    def test_get_tasks_list(self):
        """Verifica que el endpoint GET /api/tasks/ retorne la lista de tareas."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_task(self):
        """Verifica la creación manual de una tarea mediante POST."""
        data = {
            "title": "Nueva Tarea",
            "description": "Detalle de la nueva tarea",
            "completed": False
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 2)

    def test_update_task_status(self):
        """Verifica la actualización del estado de una tarea."""
        data = {"completed": True}
        response = self.client.patch(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertTrue(self.task.completed)

    def test_delete_task(self):
        """Verifica la eliminación de una tarea."""
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Task.objects.count(), 0)

    @patch('langchain_groq.ChatGroq._generate')
    def test_generate_ai_tasks(self, mock_generate):
        """Verifica la generación de tareas simulando la respuesta de LangChain/Groq."""
        # Creamos una estructura de respuesta válida para la arquitectura interna de LangChain
        from langchain_core.outputs import ChatResult, ChatGeneration
        
        json_content = (
            '['
            '{"title": "Subtarea IA 1", "description": "Descripción IA 1"},'
            '{"title": "Subtarea IA 2", "description": "Descripción IA 2"}'
            ']'
        )
        
        mock_generate.return_value = ChatResult(
            generations=[ChatGeneration(message=AIMessage(content=json_content))]
        )

        generate_url = reverse('task-generate-ai-tasks')
        payload = {"topic": "Aprender Django y React"}
        
        response = self.client.post(generate_url, payload, format='json')

        # Aserciones
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Task.objects.filter(title="Subtarea IA 1").exists())
        self.assertTrue(Task.objects.filter(title="Subtarea IA 2").exists())