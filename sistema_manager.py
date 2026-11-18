import sqlite3
from datetime import datetime


class SistemaManager:
    def __init__(self):
        self.conexion = sqlite3.connect("solicitudes.db", check_same_thread=False)
        self.conexion.row_factory = sqlite3.Row
        self._crear_tablas()
        self._cargar_datos_iniciales()

    def _crear_tablas(self):
        cursor = self.conexion.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS estudiantes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                carrera TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS responsables (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                area TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS solicitudes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                descripcion TEXT NOT NULL,
                tipo TEXT NOT NULL,
                estado TEXT NOT NULL,
                prioridad TEXT NOT NULL,
                fecha_creacion TEXT NOT NULL,
                estudiante_id INTEGER NOT NULL,
                responsable_id INTEGER,
                FOREIGN KEY(estudiante_id) REFERENCES estudiantes(id),
                FOREIGN KEY(responsable_id) REFERENCES responsables(id)
            )
        """)
        self.conexion.commit()

    def _cargar_datos_iniciales(self):
        cursor = self.conexion.cursor()
        cursor.execute("SELECT COUNT(*) AS cantidad FROM estudiantes")
        if cursor.fetchone()["cantidad"] == 0:
            cursor.execute("INSERT INTO estudiantes(nombre,email,carrera) VALUES(?,?,?)",
                           ("Lucía Gómez", "lucia@ejemplo.com", "Programación"))
            cursor.execute("INSERT INTO estudiantes(nombre,email,carrera) VALUES(?,?,?)",
                           ("Tomás Pérez", "tomas@ejemplo.com", "Sistemas"))
        cursor.execute("SELECT COUNT(*) AS cantidad FROM responsables")
        if cursor.fetchone()["cantidad"] == 0:
            cursor.execute("INSERT INTO responsables(nombre,area) VALUES(?,?)",
                           ("María López", "Alumnado"))
            cursor.execute("INSERT INTO responsables(nombre,area) VALUES(?,?)",
                           ("Carlos Díaz", "Secretaría Académica"))
        self.conexion.commit()

    def crear_solicitud(self, titulo, descripcion, tipo, estudiante_id,
                        dias_espera, estado_inicial):
        # Se revisa que el título tenga contenido.
        if titulo is None or titulo.strip() == "":
            raise ValueError("El título es obligatorio")
        # Se revisa que la descripción tenga contenido.
        if descripcion is None or descripcion.strip() == "":
            raise ValueError("La descripción es obligatoria")
        if tipo not in ["CERTIFICADO", "INSCRIPCION", "EQUIVALENCIA", "OTRO"]:
            raise ValueError("Tipo de solicitud inválido")
        if dias_espera < 0:
            raise ValueError("Los días de espera no pueden ser negativos")

        cursor = self.conexion.cursor()
        cursor.execute("SELECT id FROM estudiantes WHERE id = ?", (estudiante_id,))
        estudiante = cursor.fetchone()
        if estudiante is None:
            raise ValueError("El estudiante no existe")

        prioridad = "BAJA"
        if tipo == "EQUIVALENCIA":
            prioridad = "ALTA"
        elif tipo == "INSCRIPCION":
            prioridad = "MEDIA"
        elif tipo == "CERTIFICADO":
            prioridad = "BAJA"
        else:
            prioridad = "MEDIA"

        if dias_espera > 5:
            prioridad = "ALTA"
        if dias_espera > 10:
            prioridad = "URGENTE"

        fecha = datetime.now().isoformat(timespec="seconds")
        cursor.execute("""
            INSERT INTO solicitudes
            (titulo, descripcion, tipo, estado, prioridad, fecha_creacion, estudiante_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (titulo, descripcion, tipo, estado_inicial, prioridad, fecha, estudiante_id))
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
        data = dict(cursor.fetchone())
        data["mensaje"] = "Solicitud registrada correctamente"
        return data

    def cambiar_estado(self, solicitud_id, nuevo_estado):
        if nuevo_estado not in ["PENDIENTE", "EN_REVISION", "APROBADA", "RECHAZADA", "CERRADA"]:
            raise ValueError("Estado inválido")
        cursor = self.conexion.cursor()
        cursor.execute("SELECT id FROM solicitudes WHERE id = ?", (solicitud_id,))
        if cursor.fetchone() is None:
            raise ValueError("La solicitud no existe")
        cursor.execute("UPDATE solicitudes SET estado = ? WHERE id = ?",
                       (nuevo_estado, solicitud_id))
        self.conexion.commit()
        cursor.execute("SELECT * FROM solicitudes WHERE id = ?", (solicitud_id,))
        return dict(cursor.fetchone())

    def asignar_responsable(self, solicitud_id, responsable_id):
        cursor = self.conexion.cursor()
        cursor.execute("SELECT id FROM solicitudes WHERE id = ?", (solicitud_id,))
        solicitud = cursor.fetchone()
        if solicitud is None:
            raise ValueError("La solicitud no existe")
        cursor.execute("SELECT id FROM responsables WHERE id = ?", (responsable_id,))
        responsable = cursor.fetchone()
        if responsable is None:
            raise ValueError("El responsable no existe")
        cursor.execute("UPDATE solicitudes SET responsable_id = ? WHERE id = ?",
                       (responsable_id, solicitud_id))
        self.conexion.commit()
        cursor.execute("""
            SELECT s.*, r.nombre AS responsable_nombre
            FROM solicitudes s LEFT JOIN responsables r ON r.id = s.responsable_id
            WHERE s.id = ?
        """, (solicitud_id,))
        return dict(cursor.fetchone())

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
        data = [dict(row) for row in cursor.fetchall()]

        total = len(data)
        pendientes = 0
        aprobadas = 0
        rechazadas = 0
        for aux in data:
            if aux["estado"] == "PENDIENTE":
                pendientes += 1
            elif aux["estado"] == "APROBADA":
                aprobadas += 1
            elif aux["estado"] == "RECHAZADA":
                rechazadas += 1

        reporte = {
            "total": total,
            "pendientes": pendientes,
            "aprobadas": aprobadas,
            "rechazadas": rechazadas,
            "solicitudes": data
        }
        return reporte

    def listar_estudiantes(self):
        cursor = self.conexion.cursor()
        cursor.execute("SELECT * FROM estudiantes ORDER BY nombre")
        return [dict(row) for row in cursor.fetchall()]

    def listar_responsables(self):
        cursor = self.conexion.cursor()
        cursor.execute("SELECT * FROM responsables ORDER BY nombre")
        return [dict(row) for row in cursor.fetchall()]

    def procesar1(self, solicitud_id):
        cursor = self.conexion.cursor()
        cursor.execute("SELECT * FROM solicitudes WHERE id = ?", (solicitud_id,))
        data = cursor.fetchone()
        if data is None:
            return {"flag": False, "mensaje": "No encontrada"}
        return {"flag": True, "data": dict(data)}
