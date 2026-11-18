from enum import Enum

class TipoSolicitud(str, Enum):
    CERTIFICADO = "CERTIFICADO"
    INSCRIPCION = "INSCRIPCION"
    EQUIVALENCIA = "EQUIVALENCIA"
    OTRO = "OTRO"

class Prioridad(str, Enum):
    BAJA = "BAJA"
    MEDIA = "MEDIA"
    ALTA = "ALTA"
    URGENTE = "URGENTE"