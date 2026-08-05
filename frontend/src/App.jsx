import { useState } from "react";

function App() {
  // Estado inicial local con datos de prueba
  const [tasks, setTasks] = useState([
    {
      id: 1,
      title: "Diseñar prototipo de UI",
      description: "Crear wireframes en Figma para la vista principal.",
      completed: false,
      created_at: new Date().toISOString(),
    },
    {
      id: 2,
      title: "Configurar repositorio",
      description: "Inicializar proyecto con Git y React.",
      completed: true,
      created_at: new Date().toISOString(),
    },
  ]);

  // Estado para el filtro de tareas ('all' | 'completed' | 'pending')
  const [filter, setFilter] = useState("all");

  // Estados para Modales de CRUD
  const [isFormModalOpen, setIsFormModalOpen] = useState(false);
  const [isDetailModalOpen, setIsDetailModalOpen] = useState(false);

  // Estados para Modal de IA
  const [isAiModalOpen, setIsAiModalOpen] = useState(false);
  const [aiTopic, setAiTopic] = useState("");

  // Tarea seleccionada (para editar o ver detalle)
  const [selectedTask, setSelectedTask] = useState(null);

  // Campos del formulario
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");

  // Contadores calculados directamente en render (sin necesidad de useEffect)
  const completedCount = tasks.filter((t) => t.completed).length;
  const pendingCount = tasks.filter((t) => !t.completed).length;

  // Filtrado reactivo sin modificar el arreglo original
  const filteredTasks = tasks.filter((task) => {
    if (filter === "completed") return task.completed;
    if (filter === "pending") return !task.completed;
    return true; // 'all'
  });

  // Mapeo de estado visual directo (0% -> 100%)
  const getTaskVisualStatus = (task) => {
    if (task.completed) {
      return {
        percentage: 100,
        label: "Completada",
        color: "#28a745",
        btnText: "Finalizado",
      };
    }
    return {
      percentage: 0,
      label: "Pendiente",
      color: "#6c757d",
      btnText: "Completar Tarea",
    };
  };

  // Control de Modales CRUD
  const handleOpenCreateModal = () => {
    setSelectedTask(null);
    setTitle("");
    setDescription("");
    setIsFormModalOpen(true);
  };

  const handleOpenEditModal = (task) => {
    setSelectedTask(task);
    setTitle(task.title);
    setDescription(task.description || "");
    setIsFormModalOpen(true);
  };

  const handleOpenDetailModal = (task) => {
    setSelectedTask(task);
    setIsDetailModalOpen(true);
  };

  // Guardar tarea (Crear o Editar localmente)
  const handleSubmitForm = (e) => {
    e.preventDefault();
    if (!title.trim()) return;

    if (selectedTask) {
      // Editar existente
      setTasks(
        tasks.map((t) =>
          t.id === selectedTask.id ? { ...t, title, description } : t
        )
      );
    } else {
      // Crear nueva tarea local
      const newTask = {
        id: Date.now(),
        title,
        description,
        completed: false,
        created_at: new Date().toISOString(),
      };
      setTasks([newTask, ...tasks]);
    }

    setIsFormModalOpen(false);
  };

  // Simular la generación de tareas con IA
  const handleGenerateAiTasks = (e) => {
    e.preventDefault();
    if (!aiTopic.trim()) return;

    // Generar 3 tareas simuladas basadas en el tema ingresado
    const generatedTasks = [
      {
        id: Date.now() + 1,
        title: `Investigar sobre ${aiTopic}`,
        description: `Recopilar información inicial y requerimientos para ${aiTopic}.`,
        completed: false,
        created_at: new Date().toISOString(),
      },
      {
        id: Date.now() + 2,
        title: `Planificar plan de acción para ${aiTopic}`,
        description: `Definir hitos principales y entregables.`,
        completed: false,
        created_at: new Date().toISOString(),
      },
      {
        id: Date.now() + 3,
        title: `Ejecutar primera fase de ${aiTopic}`,
        description: `Comenzar con la implementación de las tareas prioritarias.`,
        completed: false,
        created_at: new Date().toISOString(),
      },
    ];

    setTasks([...generatedTasks, ...tasks]);
    setAiTopic("");
    setIsAiModalOpen(false);
  };

  // Avanzar estado directo: Pendiente (0%) -> Completada (100%)
  const handleAdvanceStatus = (task) => {
    if (task.completed) return;

    setTasks(
      tasks.map((t) => (t.id === task.id ? { ...t, completed: true } : t))
    );
  };

  // Eliminar tarea del estado local
  const handleDeleteTask = (id) => {
    setTasks(tasks.filter((t) => t.id !== id));
    if (isDetailModalOpen) setIsDetailModalOpen(false);
  };

  return (
    <div
      style={{
        maxWidth: "800px",
        margin: "40px auto",
        padding: "0 20px",
        fontFamily: "sans-serif",
      }}
    >
      {/* Cabecera y Botones Principales */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "20px",
        }}
      >
        <h1 style={{ margin: 0 }}>Gestor de Tareas</h1>
        <div style={{ display: "flex", gap: "10px" }}>
          {/* <button
            onClick={() => setIsAiModalOpen(true)}
            style={{
              padding: "10px 15px",
              fontSize: "15px",
              backgroundColor: "#6f42c1",
              color: "#fff",
              border: "none",
              borderRadius: "5px",
              cursor: "pointer",
            }}
          >
            ✨ Generar con IA
          </button> */}
          <button
            onClick={handleOpenCreateModal}
            style={{
              padding: "10px 15px",
              fontSize: "15px",
              backgroundColor: "#007bff",
              color: "#fff",
              border: "none",
              borderRadius: "5px",
              cursor: "pointer",
            }}
          >
            + Nueva Tarea
          </button>
        </div>
      </div>

      {/* Barra de Filtros por Estado */}
      <div
        style={{
          display: "flex",
          gap: "10px",
          marginBottom: "20px",
          borderBottom: "1px solid #ddd",
          paddingBottom: "10px",
        }}
      >
        <button
          onClick={() => setFilter("all")}
          style={{
            padding: "6px 12px",
            borderRadius: "20px",
            border: "1px solid #007bff",
            backgroundColor: filter === "all" ? "#007bff" : "#fff",
            color: filter === "all" ? "#fff" : "#007bff",
            cursor: "pointer",
          }}
        >
          Todas ({tasks.length})
        </button>
        <button
          onClick={() => setFilter("pending")}
          style={{
            padding: "6px 12px",
            borderRadius: "20px",
            border: "1px solid #6c757d",
            backgroundColor: filter === "pending" ? "#6c757d" : "#fff",
            color: filter === "pending" ? "#fff" : "#6c757d",
            cursor: "pointer",
          }}
        >
          Pendientes ({pendingCount})
        </button>
        <button
          onClick={() => setFilter("completed")}
          style={{
            padding: "6px 12px",
            borderRadius: "20px",
            border: "1px solid #28a745",
            backgroundColor: filter === "completed" ? "#28a745" : "#fff",
            color: filter === "completed" ? "#fff" : "#28a745",
            cursor: "pointer",
          }}
        >
          Completadas ({completedCount})
        </button>
      </div>

      {/* Listado de Tareas (Filtered) */}
      <div style={{ display: "flex", flexDirection: "column", gap: "15px" }}>
        {filteredTasks.map((task) => {
          const statusInfo = getTaskVisualStatus(task);
          const isCompleted = task.completed;

          return (
            <div
              key={task.id}
              style={{
                padding: "20px",
                border: "1px solid #ddd",
                borderRadius: "8px",
                backgroundColor: isCompleted ? "#f8f9fa" : "#fff",
                display: "flex",
                flexDirection: "column",
                gap: "12px",
              }}
            >
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "flex-start",
                }}
              >
                <div>
                  <h3
                    onClick={() => handleOpenDetailModal(task)}
                    style={{
                      margin: "0 0 5px 0",
                      cursor: "pointer",
                      textDecoration: "none",
                      color: isCompleted ? "#28a745" : "#007bff",
                    }}
                  >
                    {task.title}
                  </h3>
                  {task.description && (
                    <p
                      style={{ margin: 0, color: "#6c757d", fontSize: "14px" }}
                    >
                      {task.description.length > 60
                        ? `${task.description.substring(0, 60)}...`
                        : task.description}
                    </p>
                  )}
                </div>

                <div style={{ display: "flex", gap: "8px" }}>
                  <button onClick={() => handleOpenDetailModal(task)}>
                    Ver
                  </button>

                  {!isCompleted && (
                    <button onClick={() => handleOpenEditModal(task)}>
                      Editar
                    </button>
                  )}

                  <button
                    onClick={() => handleAdvanceStatus(task)}
                    disabled={isCompleted}
                    style={{
                      backgroundColor: isCompleted ? "#e0e0e0" : "#28a745",
                      color: isCompleted ? "#888" : "#fff",
                      border: "none",
                      padding: "6px 12px",
                      borderRadius: "4px",
                      cursor: isCompleted ? "not-allowed" : "pointer",
                    }}
                  >
                    {statusInfo.btnText}
                  </button>

                  <button
                    onClick={() => handleDeleteTask(task.id)}
                    style={{
                      backgroundColor: "#dc3545",
                      color: "#fff",
                      border: "none",
                      padding: "6px 12px",
                      borderRadius: "4px",
                      cursor: "pointer",
                    }}
                  >
                    Eliminar
                  </button>
                </div>
              </div>

              {/* Barra de Progreso Visual */}
              <div>
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    fontSize: "12px",
                    marginBottom: "4px",
                    color: "#555",
                  }}
                >
                  <span>
                    Estado: <strong>{statusInfo.label}</strong>
                  </span>
                  <span>{statusInfo.percentage}%</span>
                </div>
                <div
                  style={{
                    width: "100%",
                    backgroundColor: "#e9ecef",
                    height: "10px",
                    borderRadius: "5px",
                    overflow: "hidden",
                  }}
                >
                  <div
                    style={{
                      width: `${statusInfo.percentage}%`,
                      backgroundColor: statusInfo.color,
                      height: "100%",
                      transition: "width 0.4s ease-in-out",
                    }}
                  />
                </div>
              </div>
            </div>
          );
        })}

        {filteredTasks.length === 0 && (
          <p style={{ textAlign: "center", color: "#666" }}>
            No hay tareas registradas en este estado.
          </p>
        )}
      </div>

      {/* MODAL 1: Crear / Editar Tarea */}
      {isFormModalOpen && (
        <div style={modalBackdropStyle}>
          <div style={modalContentStyle}>
            <h2>{selectedTask ? "Editar Tarea" : "Nueva Tarea"}</h2>
            <form
              onSubmit={handleSubmitForm}
              style={{ display: "flex", flexDirection: "column", gap: "15px" }}
            >
              <div>
                <label style={{ display: "block", marginBottom: "5px" }}>
                  Título:
                </label>
                <input
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  style={{
                    width: "100%",
                    padding: "8px",
                    fontSize: "16px",
                    boxSizing: "border-box",
                  }}
                  required
                />
              </div>

              <div>
                <label style={{ display: "block", marginBottom: "5px" }}>
                  Descripción:
                </label>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  style={{
                    width: "100%",
                    padding: "8px",
                    fontSize: "16px",
                    minHeight: "80px",
                    boxSizing: "border-box",
                  }}
                />
              </div>

              <div
                style={{
                  display: "flex",
                  justifyContent: "flex-end",
                  gap: "10px",
                  marginTop: "10px",
                }}
              >
                <button
                  type="button"
                  onClick={() => setIsFormModalOpen(false)}
                  style={{ padding: "8px 16px", cursor: "pointer" }}
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  style={{
                    padding: "8px 16px",
                    backgroundColor: "#28a745",
                    color: "#fff",
                    border: "none",
                    borderRadius: "4px",
                    cursor: "pointer",
                  }}
                >
                  Guardar
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* MODAL 2: Vista Detallada de Tarea */}
      {isDetailModalOpen && selectedTask && (
        <div style={modalBackdropStyle}>
          <div style={modalContentStyle}>
            <h2>Detalle de la Tarea</h2>
            <hr style={{ margin: "10px 0", borderColor: "#eee" }} />

            <p>
              <strong>ID:</strong> {selectedTask.id}
            </p>
            <p>
              <strong>Título:</strong> {selectedTask.title}
            </p>
            <p>
              <strong>Descripción:</strong>{" "}
              {selectedTask.description || "Sin descripción"}
            </p>

            <div style={{ margin: "15px 0" }}>
              <p style={{ margin: "0 0 5px 0" }}>
                <strong>Estado:</strong>{" "}
                {getTaskVisualStatus(selectedTask).label} (
                {getTaskVisualStatus(selectedTask).percentage}%)
              </p>
              <div
                style={{
                  width: "100%",
                  backgroundColor: "#e9ecef",
                  height: "10px",
                  borderRadius: "5px",
                  overflow: "hidden",
                }}
              >
                <div
                  style={{
                    width: `${getTaskVisualStatus(selectedTask).percentage}%`,
                    backgroundColor: getTaskVisualStatus(selectedTask).color,
                    height: "100%",
                  }}
                />
              </div>
            </div>

            {selectedTask.created_at && (
              <p>
                <strong>Creada el:</strong>{" "}
                {new Date(selectedTask.created_at).toLocaleString()}
              </p>
            )}

            <div
              style={{
                display: "flex",
                justifyContent: "flex-end",
                gap: "10px",
                marginTop: "20px",
              }}
            >
              <button
                onClick={() => setIsDetailModalOpen(false)}
                style={{ padding: "8px 16px", cursor: "pointer" }}
              >
                Cerrar
              </button>
            </div>
          </div>
        </div>
      )}

      {/* MODAL 3: Agente de IA (Simulado) */}
      {isAiModalOpen && (
        <div style={modalBackdropStyle}>
          <div style={modalContentStyle}>
            <h2>Generar Tareas con IA</h2>
            <p style={{ color: "#666", fontSize: "14px" }}>
              Describe un objetivo o proyecto y el agente generará tareas de ejemplo automáticamente.
            </p>

            <form
              onSubmit={handleGenerateAiTasks}
              style={{
                display: "flex",
                flexDirection: "column",
                gap: "15px",
                marginTop: "15px",
              }}
            >
              <div>
                <label style={{ display: "block", marginBottom: "5px" }}>
                  Objetivo o Proyecto:
                </label>
                <input
                  type="text"
                  placeholder="Ej: Lanzar MVP de un e-commerce..."
                  value={aiTopic}
                  onChange={(e) => setAiTopic(e.target.value)}
                  style={{
                    width: "100%",
                    padding: "8px",
                    fontSize: "16px",
                    boxSizing: "border-box",
                  }}
                  required
                />
              </div>

              <div
                style={{
                  display: "flex",
                  justifyContent: "flex-end",
                  gap: "10px",
                  marginTop: "10px",
                }}
              >
                <button
                  type="button"
                  onClick={() => setIsAiModalOpen(false)}
                  style={{ padding: "8px 16px", cursor: "pointer" }}
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  style={{
                    padding: "8px 16px",
                    backgroundColor: "#6f42c1",
                    color: "#fff",
                    border: "none",
                    borderRadius: "4px",
                    cursor: "pointer",
                  }}
                >
                  Generar Tareas
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

const modalBackdropStyle = {
  position: "fixed",
  top: 0,
  left: 0,
  width: "100vw",
  height: "100vh",
  backgroundColor: "rgba(0, 0, 0, 0.5)",
  display: "flex",
  justifyContent: "center",
  alignItems: "center",
  zIndex: 1000,
};

const modalContentStyle = {
  backgroundColor: "#fff",
  padding: "24px",
  borderRadius: "8px",
  width: "100%",
  maxWidth: "500px",
  boxShadow: "0 4px 6px rgba(0, 0, 0, 0.1)",
};

export default App;