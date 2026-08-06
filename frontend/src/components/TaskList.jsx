import React from "react";

function TaskList({ tasks, filter, onOpenDetail, onOpenEdit, onAdvanceStatus, onDelete, onFilterChange, completedCount, pendingCount }) {
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

  const filteredTasks = tasks.filter((task) => {
    if (filter === "completed") return task.completed;
    if (filter === "pending") return !task.completed;
    return true;
  });

  return (
    <div>
      <div style={{ display: "flex", gap: "10px", marginBottom: "20px", borderBottom: "1px solid #ddd", paddingBottom: "10px" }}>
        <button onClick={() => onFilterChange("all")} style={{ padding: "6px 12px", borderRadius: "20px", border: "1px solid #007bff", backgroundColor: filter === "all" ? "#007bff" : "#fff", color: filter === "all" ? "#fff" : "#007bff", cursor: "pointer" }}>
          Todas ({tasks.length})
        </button>
        <button onClick={() => onFilterChange("pending")} style={{ padding: "6px 12px", borderRadius: "20px", border: "1px solid #6c757d", backgroundColor: filter === "pending" ? "#6c757d" : "#fff", color: filter === "pending" ? "#fff" : "#6c757d", cursor: "pointer" }}>
          Pendientes ({pendingCount})
        </button>
        <button onClick={() => onFilterChange("completed")} style={{ padding: "6px 12px", borderRadius: "20px", border: "1px solid #28a745", backgroundColor: filter === "completed" ? "#28a745" : "#fff", color: filter === "completed" ? "#fff" : "#28a745", cursor: "pointer" }}>
          Completadas ({completedCount})
        </button>
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: "15px" }}>
        {filteredTasks.map((task) => {
          const statusInfo = getTaskVisualStatus(task);
          const isCompleted = task.completed;

          return (
            <div key={task.id} style={{ padding: "20px", border: "1px solid #ddd", borderRadius: "8px", backgroundColor: isCompleted ? "#f8f9fa" : "#fff", display: "flex", flexDirection: "column", gap: "12px" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                <div>
                  <h3 onClick={() => onOpenDetail(task)} style={{ margin: "0 0 5px 0", cursor: "pointer", textDecoration: "none", color: isCompleted ? "#28a745" : "#007bff" }}>
                    {task.title}
                  </h3>
                  {task.content && (
                    <p style={{ margin: 0, color: "#6c757d", fontSize: "14px" }}>
                      {task.content.length > 60 ? `${task.content.substring(0, 60)}...` : task.content}
                    </p>
                  )}
                </div>

                <div style={{ display: "flex", gap: "8px" }}>
                  <button onClick={() => onOpenDetail(task)}>Ver</button>
                  {!isCompleted && <button onClick={() => onOpenEdit(task)}>Editar</button>}
                  <button onClick={() => onAdvanceStatus(task)} disabled={isCompleted} style={{ backgroundColor: isCompleted ? "#e0e0e0" : "#28a745", color: isCompleted ? "#888" : "#fff", border: "none", padding: "6px 12px", borderRadius: "4px", cursor: isCompleted ? "not-allowed" : "pointer" }}>
                    {statusInfo.btnText}
                  </button>
                  <button onClick={() => onDelete(task.id)} style={{ backgroundColor: "#dc3545", color: "#fff", border: "none", padding: "6px 12px", borderRadius: "4px", cursor: "pointer" }}>
                    Eliminar
                  </button>
                </div>
              </div>

              <div>
                <div style={{ display: "flex", justifyContent: "space-between", fontSize: "12px", marginBottom: "4px", color: "#555" }}>
                  <span>Estado: <strong>{statusInfo.label}</strong></span>
                  <span>{statusInfo.percentage}%</span>
                </div>
                <div style={{ width: "100%", backgroundColor: "#e9ecef", height: "10px", borderRadius: "5px", overflow: "hidden" }}>
                  <div style={{ width: `${statusInfo.percentage}%`, backgroundColor: statusInfo.color, height: "100%", transition: "width 0.4s ease-in-out" }} />
                </div>
              </div>
            </div>
          );
        })}

        {filteredTasks.length === 0 && <p style={{ textAlign: "center", color: "#666" }}>No hay tareas registradas en este estado.</p>}
      </div>
    </div>
  );
}

export default TaskList;
