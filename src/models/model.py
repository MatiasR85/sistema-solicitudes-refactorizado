from pydantic import BaseModel
from src.models.enums import TipoSolicitud

class SolicitudEntrada(BaseModel):
    titulo: str
    descripcion: str
    tipo: TipoSolicitud
    estudiante_id: int
    dias_espera: int = 0


class EstadoEntrada(BaseModel):
    estado: str


class ResponsableEntrada(BaseModel):
    responsable_id: int
