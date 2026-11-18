from datetime import datetime
from src.repository.repository import SolicitudRepository
from src.models.model import SolicitudEntrada
from src.models.enums import TipoSolicitud, Prioridad

class SolicitudService:
    def __init__(self):
        self.repository = SolicitudRepository()

    def obtener_estudiantes(self):
        return self.repository.obtener_estudiantes()

    def obtener_responsables(self):
        return self.repository.obtener_responsables()

    def _calcular_prioridad(self, tipo: TipoSolicitud, dias_espera: int) -> Prioridad:
        prioridad_base = {
            TipoSolicitud.EQUIVALENCIA: Prioridad.ALTA,
            TipoSolicitud.INSCRIPCION: Prioridad.MEDIA,
            TipoSolicitud.CERTIFICADO: Prioridad.BAJA,
            TipoSolicitud.OTRO: Prioridad.MEDIA,
        }
        
        prioridad = prioridad_base.get(tipo, Prioridad.MEDIA)

        if dias_espera > 10:
            return Prioridad.URGENTE
        if dias_espera > 5:
            return Prioridad.ALTA

        return prioridad

    def crear_solicitud(self, datos: SolicitudEntrada):
        if not datos.titulo.strip():
            raise ValueError("El título es obligatorio")
        if not datos.descripcion.strip():
            raise ValueError("La descripción es obligatoria")
        if datos.dias_espera < 0:
            raise ValueError("Los días de espera no pueden ser negativos")

        prioridad = self._calcular_prioridad(datos.tipo, datos.dias_espera)
        fecha = datetime.now().isoformat(timespec="seconds")
        estado_inicial = "PENDIENTE"

        return self.repository.guardar_solicitud(
            titulo=datos.titulo,
            descripcion=datos.descripcion,
            tipo=datos.tipo.value,
            estado=estado_inicial,
            prioridad=prioridad.value,
            fecha=fecha,
            estudiante_id=datos.estudiante_id
        )

    def listar_y_reportar(self, estado=None, tipo=None):
        return self.repository.listar_y_reportar(estado=estado, tipo=tipo)

    def cambiar_estado(self, solicitud_id: int, nuevo_estado: str):
        resultado = self.repository.cambiar_estado(solicitud_id, nuevo_estado)
        if not resultado:
            raise ValueError(f"No se encontró la solicitud con ID {solicitud_id}")
        return resultado

    def asignar_responsable(self, solicitud_id: int, responsable_id: int):
        resultado = self.repository.asignar_responsable(solicitud_id, responsable_id)
        if not resultado:
            raise ValueError(f"No se encontró la solicitud con ID {solicitud_id}")
        return resultado