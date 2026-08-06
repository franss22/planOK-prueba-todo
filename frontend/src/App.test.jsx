import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import App from "./App";
import api from "./api";

// Interceptamos el cliente axios importado en ./api
vi.mock("./api");

describe("Frontend Integration Tests - App Component", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("1. Carga y renderiza el listado inicial de tareas desde la API", async () => {
    const mockTasks = [
      {
        id: 1,
        title: "Tarea Pendiente 1",
        content: "Desc 1",
        completed: false,
      },
      {
        id: 2,
        title: "Tarea Completada 1",
        content: "Desc 2",
        completed: true,
      },
    ];

    api.get.mockResolvedValueOnce({ data: mockTasks });

    render(<App />);

    await waitFor(() => {
      expect(screen.getByText("Tarea Pendiente 1")).toBeInTheDocument();
      expect(screen.getByText("Tarea Completada 1")).toBeInTheDocument();
    });
  });

  it("1b. Solicita las tareas al endpoint del backend al cargar", async () => {
    api.get.mockResolvedValueOnce({ data: [] });

    render(<App />);

    await waitFor(() => {
      expect(api.get).toHaveBeenCalledWith("tasks/");
    });
  });

  it("2. Filtra correctamente las tareas por estado (Pendientes / Completadas)", async () => {
    const mockTasks = [
      {
        id: 1,
        title: "Tarea Alfa Pendiente",
        content: "Desc 1",
        completed: false,
      },
      {
        id: 2,
        title: "Tarea Beta Completada",
        content: "Desc 2",
        completed: true,
      },
    ];

    api.get.mockResolvedValueOnce({ data: mockTasks });

    render(<App />);

    await waitFor(() => {
      expect(screen.getByText("Tarea Alfa Pendiente")).toBeInTheDocument();
    });

    // Clic en el filtro "Pendientes"
    const pendingFilterBtn = screen.getByRole("button", {
      name: /Pendientes/i,
    });
    fireEvent.click(pendingFilterBtn);

    expect(screen.getByText("Tarea Alfa Pendiente")).toBeInTheDocument();
    expect(screen.queryByText("Tarea Beta Completada")).not.toBeInTheDocument();

    // Clic en el filtro "Completadas"
    const completedFilterBtn = screen.getByRole("button", {
      name: /Completadas/i,
    });
    fireEvent.click(completedFilterBtn);

    expect(screen.getByText("Tarea Beta Completada")).toBeInTheDocument();
    expect(screen.queryByText("Tarea Alfa Pendiente")).not.toBeInTheDocument();
  });

  it("3. Abre el modal de IA y genera nuevas tareas", async () => {
    api.get.mockResolvedValueOnce({ data: [] });

    render(<App />);

    // Abrir modal de IA
    const aiButton = screen.getByRole("button", { name: /✨ Generar con IA/i });
    fireEvent.click(aiButton);

    // Llenar el formulario
    const input = screen.getByPlaceholderText(/Lanzar MVP/i);
    fireEvent.change(input, { target: { value: "Aprender Docker y React" } });

    // Mock de la llamada POST a la API de IA
    const aiGeneratedTasks = [
      {
        id: 10,
        title: "Subtarea IA Generada",
        content: "Creada por agente",
        completed: false,
      },
    ];
    api.post.mockResolvedValueOnce({ data: aiGeneratedTasks });

    // Enviar el formulario del modal
    const submitButton = screen.getByRole("button", {
      name: /Generar Tareas/i,
    });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(api.post).toHaveBeenCalledWith("tasks/generate-ai-tasks/", {
        topic: "Aprender Docker y React",
      });
      expect(screen.getByText("Subtarea IA Generada")).toBeInTheDocument();
    });
  });
});
