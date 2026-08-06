import React from "react";

function TaskFormModal({ isOpen, selectedTask, title, content, onTitleChange, onContentChange, onCancel, onSubmit }) {
  if (!isOpen) return null;

  return (
    <div style={modalBackdropStyle}>
      <div style={modalContentStyle}>
        <h2>{selectedTask ? "Editar Tarea" : "Nueva Tarea"}</h2>
        <form onSubmit={onSubmit} style={{ display: "flex", flexDirection: "column", gap: "15px" }}>
          <div>
            <label style={{ display: "block", marginBottom: "5px" }}>Título:</label>
            <input type="text" value={title} onChange={onTitleChange} style={{ width: "100%", padding: "8px", fontSize: "16px", boxSizing: "border-box" }} required />
          </div>

          <div>
            <label style={{ display: "block", marginBottom: "5px" }}>Descripción:</label>
            <textarea value={content} onChange={onContentChange} style={{ width: "100%", padding: "8px", fontSize: "16px", minHeight: "80px", boxSizing: "border-box" }} />
          </div>

          <div style={{ display: "flex", justifyContent: "flex-end", gap: "10px", marginTop: "10px" }}>
            <button type="button" onClick={onCancel} style={{ padding: "8px 16px", cursor: "pointer" }}>Cancelar</button>
            <button type="submit" style={{ padding: "8px 16px", backgroundColor: "#28a745", color: "#fff", border: "none", borderRadius: "4px", cursor: "pointer" }}>Guardar</button>
          </div>
        </form>
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

export default TaskFormModal;
