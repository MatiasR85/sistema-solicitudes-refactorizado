# Gestión de Solicitudes Académicas

Prototipo de API REST desarrollado con Python, FastAPI y SQLite.

## Requisitos

- Python 3.10 o superior
- pip

## Instalación

```bash
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

Linux / macOS:

```bash
source venv/bin/activate
```

Instalar dependencias:

```bash
pip install -r requirements.txt
```

## Ejecutar

Desde la carpeta del proyecto:

```bash
uvicorn main:app --reload
```

La API queda disponible en:

- Inicio: http://127.0.0.1:8000/
- Documentación interactiva: http://127.0.0.1:8000/docs
- Pruebas manuales: archivo `pruebas.http`

La base `solicitudes.db` se crea automáticamente al iniciar la aplicación. También se insertan dos estudiantes y dos responsables de ejemplo si las tablas están vacías.

## Entidades

- **Estudiante:** persona que inicia una solicitud académica.
- **Responsable:** persona/área que gestiona una solicitud.
- **Solicitud:** trámite iniciado por un estudiante.

## Operaciones principales

| Operación | Método y endpoint |
|---|---|
| Crear solicitud | `POST /solicitudes` |
| Cambiar estado | `PATCH /solicitudes/{id}/estado` |
| Asignar responsable | `PATCH /solicitudes/{id}/responsable` |
| Listar / filtrar / reportar | `GET /solicitudes` |

Tipos admitidos: `CERTIFICADO`, `INSCRIPCION`, `EQUIVALENCIA`, `OTRO`.

Estados admitidos: `PENDIENTE`, `EN_REVISION`, `APROBADA`, `RECHAZADA`, `CERRADA`.

El listado acepta filtros opcionales `estado` y `tipo` y devuelve un resumen con cantidades por estado.
