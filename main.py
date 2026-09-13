import os
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI(title="Sistema de Gestión de Empleados - Taller Murúa")

if os.path.exists("static"):
  app.mount("/static", StaticFiles(directory="static"), name="static")


# --- MODELOS / DATOS SIMULADOS (Según Entidad-Relación) ---
class ModificacionSchema(BaseModel):
  empleado_id: int
  fecha: str
  hora_ingreso: Optional[str] = None
  salida_intermedia: Optional[str] = None
  reingreso: Optional[str] = None
  hora_egreso: Optional[str] = None
  motivo: str


# Empleados cargados (EMPLEADO)
empleados_db = [
    {
        "id": 1,
        "nombre": "Juan",
        "apellido": "Pérez",
        "dni": "12345678",
        "legajo": "LEG-001",
    },
    {
        "id": 2,
        "nombre": "María",
        "apellido": "Gómez",
        "dni": "87654321",
        "legajo": "LEG-002",
    },
]

# Registros de asistencia cargados (ASISTENCIA)
asistencias_db = [
    {
        "asistencia_id": 1,
        "empleado_id": 1,
        "fecha": "2026-01-14",
        "hora_ingreso": "08:00:00",
        "salida_intermedia": "--:--",
        "reingreso": "--:--",
        "hora_egreso": "17:00:00",
        "estado": "Presente",
    }
]

# Historial de CorreccionRegistro
correcciones_db = []


# --- RUTAS DE NAVEGACIÓN ---
@app.get("/", response_class=HTMLResponse)
def cargar_inicio():
  ruta_html = os.path.join("templates", "modificarasistencia.html")
  if os.path.exists(ruta_html):
    with open(ruta_html, "r", encoding="utf-8") as file:
      return file.read()
  return "<h1>Archivo modificarasistencia.html no encontrado</h1>"


@app.get("/api/empleados")
def obtener_empleados():
  return empleados_db


# --- ENDPOINTS SEGÚN CLASE CorreccionRegistro ---


# 1. Consultar Asistencia por Empleado y Fecha
@app.get("/api/asistencia/consultar")
def consultar_asistencia(empleado_id: int, fecha: str):
  registro = next(
      (
          a
          for a in asistencias_db
          if a["empleado_id"] == empleado_id and a["fecha"] == fecha
      ),
      None,
  )
  if not registro:
    # Retornar registro vacío para poder crearlo o editarlo
    return {
        "encontrado": False,
        "hora_ingreso": "",
        "salida_intermedia": "",
        "reingreso": "",
        "hora_egreso": "",
    }
  return {"encontrado": True, **registro}


# 2. Aplicar Corrección (CorreccionRegistro.aplicar())
@app.post("/api/asistencia/corregir")
def aplicar_correccion(datos: ModificacionSchema):
  # Buscar o crear asistencia
  registro = next(
      (
          a
          for a in asistencias_db
          if a["empleado_id"] == datos.empleado_id
          and a["fecha"] == datos.fecha
      ),
      None,
  )

  if not registro:
    registro = {
        "asistencia_id": len(asistencias_db) + 1,
        "empleado_id": datos.empleado_id,
        "fecha": datos.fecha,
        "hora_ingreso": datos.hora_ingreso or "--:--",
        "salida_intermedia": datos.salida_intermedia or "--:--",
        "reingreso": datos.reingreso or "--:--",
        "hora_egreso": datos.hora_egreso or "--:--",
        "estado": "Modificado",
    }
    asistencias_db.append(registro)
  else:
    if datos.hora_ingreso:
      registro["hora_ingreso"] = datos.hora_ingreso
    if datos.salida_intermedia:
      registro["salida_intermedia"] = datos.salida_intermedia
    if datos.reingreso:
      registro["reingreso"] = datos.reingreso
    if datos.hora_egreso:
      registro["hora_egreso"] = datos.hora_egreso
    registro["estado"] = "Modificado"

  # Guardar auditoría en CorreccionRegistro
  nueva_correccion = {
      "idCorreccion": len(correcciones_db) + 1,
      "fechaHora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
      "motivo": datos.motivo,
      "empleado_id": datos.empleado_id,
  }
  correcciones_db.append(nueva_correccion)

  return {
      "exito": True,
      "mensaje": "Registro de asistencia corregido correctamente.",
  }