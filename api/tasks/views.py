import os
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Task
from .serializers import TaskSerializer

# Importaciones de LangChain con Groq
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all().order_by('-created_at')
    serializer_class = TaskSerializer

    @action(detail=False, methods=['post'], url_path='generate-ai-tasks')
    def generate_ai_tasks(self, request):
        topic = request.data.get('topic', 'Organizar proyecto de desarrollo')
        api_key = os.getenv('GROQ_API_KEY') or os.getenv('OPENAI_API_KEY')

        generated_tasks = []

        # Intento de generación con IA mediante LangChain + ChatGroq
        if api_key:
            try:
                llm = ChatGroq(
                    temperature=0.7,
                    model_name="llama-3.1-8b-instant",
                    groq_api_key=api_key
                )

                prompt = ChatPromptTemplate.from_messages([
                    ("system", "Eres un asistente experto en gestión de proyectos. Genera exactamente 3 tareas breves y concretas para lograr el objetivo indicado. Responde únicamente en formato JSON válido con la estructura: [{{\"title\": \"...\", \"description\": \"...\"}}]"),
                    ("human", "Objetivo: {topic}")
                ])

                chain = prompt | llm | JsonOutputParser()
                response_data = chain.invoke({"topic": topic})

                if isinstance(response_data, dict) and "tasks" in response_data:
                    generated_tasks = response_data["tasks"]
                elif isinstance(response_data, list):
                    generated_tasks = response_data

            except Exception as e:
                print(f"Advertencia: Falló la API de IA ({str(e)}). Usando tareas simuladas (Mock).")

        # Fallback / Mock si no hay API Key o si ocurrió un error en la llamada
        if not generated_tasks:
            generated_tasks = [
                {
                    "title": f"Planificar {topic}",
                    "description": f"Definir los requerimientos iniciales y alcance para: {topic}."
                },
                {
                    "title": f"Diseñar estructura para {topic}",
                    "description": "Crear el boceto general de arquitectura e interfaz."
                },
                {
                    "title": f"Ejecutar y validar {topic}",
                    "description": "Desarrollar la primera iteración y realizar pruebas de funcionamiento."
                }
            ]

        # Guardar las tareas generadas en PostgreSQL
        created_tasks = []
        for item in generated_tasks:
            task = Task.objects.create(
                title=item.get('title', 'Tarea sugerida por IA'),
                description=item.get('description', ''),
                completed=False
            )
            created_tasks.append(task)

        # Responder al frontend
        serializer = TaskSerializer(created_tasks, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    