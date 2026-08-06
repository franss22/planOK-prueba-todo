import { useEffect, useState } from "react";
import { createTask, deleteTask, fetchTasks, generateTaskReport, updateTask } from "./api";

const renderInlineMarkdown = (text) => {
  const segments = text.split(/(\*\*.*?\*\*)/g);

  return segments.filter(Boolean).map((segment, index) => {
    if (segment.startsWith("**") && segment.endsWith("**")) {
      return <strong key={`bold-${index}`}>{segment.slice(2, -2)}</strong>;
    }

    return <span key={`text-${index}`}>{segment}</span>;
  });
};

const renderReportMarkdown = (text) => {
  const blocks = text.split(/\n\s*\n/).filter((block) => block.trim().length > 0);

  return blocks.map((block, blockIndex) => {
    const trimmedBlock = block.trim();
    const headingMatch = trimmedBlock.match(/^\*\*(.+)\*\*$/);

    if (headingMatch) {
      return (
        <h3
          key={`heading-${blockIndex}`}
          style={{ margin: blockIndex === 0 ? 0 : "20px 0 0", color: "#111827", fontSize: "18px" }}
        >
          {headingMatch[1]}
        </h3>
      );
    }

    const lines = block.split("\n");

    return (
      <p key={`paragraph-${blockIndex}`} style={{ margin: blockIndex === 0 ? 0 : "16px 0 0" }}>
        {lines.map((line, lineIndex) => (
          <span key={`line-${blockIndex}-${lineIndex}`}>
            {renderInlineMarkdown(line)}
            {lineIndex < lines.length - 1 ? <br /> : null}
          </span>
        ))}
      </p>
    );
  });
};

function App() {
  const [tasks, setTasks] = useState([]);

  // Estado para el filtro de tareas ('all' | 'completed' | 'pending')
  const [filter, setFilter] = useState("all");

  // Estados para Modales de CRUD
  const [isFormModalOpen, setIsFormModalOpen] = useState(false);
  const [isDetailModalOpen, setIsDetailModalOpen] = useState(false);

  // Estados para Modal de IA
  const [isGeneratingReport, setIsGeneratingReport] = useState(false);

  // Estado para el reporte generado
  const [report, setReport] = useState(null);
  const [isReportOpen, setIsReportOpen] = useState(false);

  // Tarea seleccionada (para editar o ver detalle)
  const [selectedTask, setSelectedTask] = useState(null);

  // Campos del formulario
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");

  useEffect(() => {
    const loadTasks = async () => {
      try {
        const normalizedTasks = await fetchTasks();
        setTasks(normalizedTasks);
      } catch (error) {
        console.error("Error loading tasks", error);
      }
    };

    loadTasks();
  }, []);

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
    setContent("");
    setIsFormModalOpen(true);
  };

  const handleOpenEditModal = (task) => {
    setSelectedTask(task);
    setTitle(task.title);
    setContent(task.content || "");
    setIsFormModalOpen(true);
  };

  const handleOpenDetailModal = (task) => {
    setSelectedTask(task);
    setIsDetailModalOpen(true);
  };

  // Guardar tarea (Crear o Editar contra la API)
  const handleSubmitForm = async (e) => {
    e.preventDefault();
    if (!title.trim()) return;

    try {
      if (selectedTask) {
        const updatedTask = await updateTask(selectedTask.id, {
          title,
          content: content,
          completed: selectedTask.completed,
        });
        setTasks(
          tasks.map((t) =>
            t.id === selectedTask.id
              ? {
                  ...t,
                  title: updatedTask.title,
                  content: updatedTask.content,
                  completed: updatedTask.completed,
                }
              : t
          )
        );
      } else {
        const newTask = await createTask({
          title,
          content: content,
          completed: false,
        });
        setTasks([newTask, ...tasks]);
      }
    } catch (error) {
      console.error("Error saving task", error);
    }

    setIsFormModalOpen(false);
  };

  const handleGenerateReport = async () => {
    setIsGeneratingReport(true);

    try {
      const payload = await generateTaskReport();
      setReport(payload);
      setIsReportOpen(true);
    } catch (error) {
      console.error("Error generating report", error);
    } finally {
      setIsGeneratingReport(false);
    }
  };

  // Avanzar estado directo: Pendiente (0%) -> Completada (100%)
  const handleAdvanceStatus = async (task) => {
    if (task.completed) return;

    try {
      const updatedTask = await updateTask(task.id, {
        completed: true,
      });
      setTasks(
        tasks.map((t) =>
          t.id === task.id
            ? {
                ...t,
                completed: Boolean(updatedTask.completed),
              }
            : t
        )
      );
    } catch (error) {
      console.error("Error updating task", error);
    }
  };

  // Eliminar tarea del estado local
  const handleDeleteTask = async (id) => {
    try {
      await deleteTask(id);
      setTasks(tasks.filter((t) => t.id !== id));
    } catch (error) {
      console.error("Error deleting task", error);
    }
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
          gap: "18px",
          marginBottom: "28px",
          flexWrap: "wrap",
        }}
      >
        <h1 style={{ margin: 0, lineHeight: 1.1 }}>Gestor de Tareas</h1>
        <div style={{ display: "flex", gap: "10px", flexWrap: "wrap" }}>
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
            onClick={handleGenerateReport}
            disabled={isGeneratingReport}
            style={{
              padding: "10px 15px",
              fontSize: "15px",
              backgroundColor: "#6f42c1",
              color: "#fff",
              border: "none",
              borderRadius: "5px",
              cursor: isGeneratingReport ? "wait" : "pointer",
              opacity: isGeneratingReport ? 0.8 : 1,
            }}
          >
            {isGeneratingReport ? "Generando..." : "📄 Generar Reporte"}
          </button>
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
                  {task.content && (
                    <p
                      style={{ margin: 0, color: "#6c757d", fontSize: "14px" }}
                    >
                      {task.content.length > 60
                        ? `${task.content.substring(0, 60)}...`
                        : task.content}
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
                  value={content}
                  onChange={(e) => setContent(e.target.value)}
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
              {selectedTask.content || "Sin descripción"}
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

      {isReportOpen && report && (
        <div style={modalBackdropStyle}>
          <div
            style={{
              ...modalContentStyle,
              maxWidth: "640px",
              textAlign: "left",
            }}
          >
            <h2 style={{ margin: 0, color: "#1f2937", fontSize: "24px" }}>Reporte generado</h2>
            <p style={{ color: "#4b5563", fontSize: "14px", margin: "8px 0 12px" }}>
              {report.model ? `Modelo: ${report.model}` : "Reporte listo"}
            </p>
            <div
              style={{
                maxHeight: "320px",
                overflowY: "auto",
                overflowWrap: "anywhere",
                wordBreak: "break-word",
                backgroundColor: "#f3f4f6",
                color: "#111827",
                border: "1px solid #d1d5db",
                padding: "16px",
                borderRadius: "8px",
                lineHeight: 1.7,
                fontSize: "15px",
                textAlign: "left",
              }}
            >
              {report.report ? renderReportMarkdown(report.report) : "No se pudo generar un reporte."}
            </div>
            <div style={{ display: "flex", justifyContent: "flex-end", gap: "10px", marginTop: "16px" }}>
              <button type="button" onClick={() => setIsReportOpen(false)} style={{ padding: "8px 16px", cursor: "pointer" }}>
                Cerrar
              </button>
            </div>
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