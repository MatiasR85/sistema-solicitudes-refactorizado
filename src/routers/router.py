from fastapi import APIRouter, HTTPException
from typing import Optional
from src.services.service import SolicitudService
from src.models.model import SolicitudEntrada, EstadoEntrada, ResponsableEntrada
from src.models.enums import TipoSolicitud

router = APIRouter(prefix="/solicitudes", tags=["Solicitudes"])
service = SolicitudService()

@router.get("/estudiantes")
def listar_estudiantes():
    return service.obtener_estudiantes()

@router.get("/responsables")
def listar_responsables():
    return service.obtener_responsables()

@router.post("", status_code=201)
def crear_solicitud(datos: SolicitudEntrada):
    try:
        return service.crear_solicitud(datos)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("")
def listar_y_reportar(
    estado: Optional[str] = None,
    tipo: Optional[TipoSolicitud] = None
):
    tipo_str = tipo.value if tipo else None
    return service.listar_y_reportar(estado=estado, tipo=tipo_str)

@router.patch("/{solicitud_id}/estado")
def cambiar_estado(solicitud_id: int, datos: EstadoEntrada):
    try:
        return service.cambiar_estado(solicitud_id, datos.estado)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.patch("/{solicitud_id}/responsable")
def asignar_responsable(solicitud_id: int, datos: ResponsableEntrada):
    try:
        return service.asignar_responsable(solicitud_id, datos.responsable_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))