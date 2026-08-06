import React from "react";

function TaskDetailModal({ isOpen, task, onClose, getTaskVisualStatus }) {
  if (!isOpen || !task) return null;

  const statusInfo = getTaskVisualStatus(task);

  return (
    <div style={modalBackdropStyle}>
      <div style={modalContentStyle}>
        <h2>Detalle de la Tarea</h2>
        <hr style={{ margin: "10px 0", borderColor: "#eee" }} />

        <p><strong>ID:</strong> {task.id}</p>
        <p><strong>Título:</strong> {task.title}</p>
        <p><strong>Descripción:</strong> {task.content || "Sin descripción"}</p>

        <div style={{ margin: "15px 0" }}>
          <p style={{ margin: "0 0 5px 0" }}>
            <strong>Estado:</strong> {statusInfo.label} ({statusInfo.percentage}%)
          </p>
          <div style={{ width: "100%", backgroundColor: "#e9ecef", height: "10px", borderRadius: "5px", overflow: "hidden" }}>
            <div style={{ width: `${statusInfo.percentage}%`, backgroundColor: statusInfo.color, height: "100%" }} />
          </div>
        </div>

        {task.created_at && <p><strong>Creada el:</strong> {new Date(task.created_at).toLocaleString()}</p>}

        <div style={{ display: "flex", justifyContent: "flex-end", gap: "10px", marginTop: "20px" }}>
          <button onClick={onClose} style={{ padding: "8px 16px", cursor: "pointer" }}>Cerrar</button>
        </div>
      </div>
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

export default TaskDetailModal;
