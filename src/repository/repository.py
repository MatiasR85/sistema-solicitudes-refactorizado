import sqlite3

class SolicitudRepository:
    def __init__(self, db_path="solicitudes.db"):
        self.conexion = sqlite3.connect(db_path, check_same_thread=False)
        self.conexion.row_factory = sqlite3.Row

    def obtener_estudiantes(self):
        cursor = self.conexion.cursor()
        cursor.execute("SELECT * FROM estudiantes ORDER BY nombre")
        return [dict(row) for row in cursor.fetchall()]

    def obtener_responsables(self):
        cursor = self.conexion.cursor()
        cursor.execute("SELECT * FROM responsables ORDER BY nombre")
        return [dict(row) for row in cursor.fetchall()]

    def guardar_solicitud(self, titulo, descripcion, tipo, estado, prioridad, fecha, estudiante_id):
        cursor = self.conexion.cursor()
        cursor.execute("""
            INSERT INTO solicitudes
            (titulo, descripcion, tipo, estado, prioridad, fecha_creacion, estudiante_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (titulo, descripcion, tipo, estado, prioridad, fecha, estudiante_id))
        self.conexion.commit()
        nuevo_id = cursor.lastrowid

        cursor.execute("""
            SELECT s.*, e.nombre AS estudiante_nombre,
                   r.nombre AS responsable_nombre
            FROM solicitudes s
            JOIN estudiantes e ON e.id = s.estudiante_id
            LEFT JOIN responsables r ON r.id = s.responsable_id
            WHERE s.id = ?
        """, (nuevo_id,))
        return dict(cursor.fetchone())

    def cambiar_estado(self, solicitud_id, nuevo_estado):
        cursor = self.conexion.cursor()
        cursor.execute("UPDATE solicitudes SET estado = ? WHERE id = ?", (nuevo_estado, solicitud_id))
        self.conexion.commit()
        
        cursor.execute("SELECT * FROM solicitudes WHERE id = ?", (solicitud_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def asignar_responsable(self, solicitud_id, responsable_id):
        cursor = self.conexion.cursor()
        cursor.execute("UPDATE solicitudes SET responsable_id = ? WHERE id = ?", (responsable_id, solicitud_id))
        self.conexion.commit()
        
        cursor.execute("""
            SELECT s.*, r.nombre AS responsable_nombre
            FROM solicitudes s LEFT JOIN responsables r ON r.id = s.responsable_id
            WHERE s.id = ?
        """, (solicitud_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def listar_y_reportar(self, estado=None, tipo=None):
        cursor = self.conexion.cursor()
        sql = """
            SELECT s.*, e.nombre AS estudiante_nombre,
                   r.nombre AS responsable_nombre
            FROM solicitudes s
            JOIN estudiantes e ON e.id = s.estudiante_id
            LEFT JOIN responsables r ON r.id = s.responsable_id
            WHERE 1 = 1
        """
        params = []
        if estado:
            sql += " AND s.estado = ?"
            params.append(estado)
        if tipo:
            sql += " AND s.tipo = ?"
            params.append(tipo)
        sql += " ORDER BY s.fecha_creacion DESC"
        
        cursor.execute(sql, params)
        return [dict(row) for row in cursor.fetchall()]


