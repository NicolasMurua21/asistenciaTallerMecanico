import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
sys.path.append(current_dir)
sys.path.append(root_dir)

import baseDatos
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from clases.administrador import Administrador
from clases.empleado import Empleado
from salidaintermedia import salidaIntermedia
from registroasistencia import registroAsistencia

# Inicialización única
DB = baseDatos.inicializar_base_datos()
app = FastAPI()

# Única configuración de CORS (bien arriba, antes de las rutas)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def manejar_respuesta_negocio(resultado):
    if resultado == "FALTAN DATOS":
        raise HTTPException(status_code=400, detail="Faltan datos obligatorios")
    if resultado == "EMPLEADO NO EXISTE":
        raise HTTPException(status_code=404, detail="El empleado no existe")
    if resultado == "ERROR INTERNO":
        raise HTTPException(status_code=500, detail="Ocurrió un error inesperado en el servidor")
    return resultado


@app.patch("/api/admin/empleados/{dni}/asistencias/{fechaEmpleado}")
async def corregir_asistencia(dni : str, fechaEmpleado, request: Request):
    datos = await request.json()
    if not datos:
        raise HTTPException(status_code=400, detail="No se enviaron datos")

    camposModificar = datos.pop("camposModificar", [])
    resultado = Administrador.corregirRegistro(DB, dni, fechaEmpleado, camposModificar, **datos)
    manejar_respuesta_negocio(resultado)
    return {"mensaje": "Procesado con éxito", "resultado": resultado}


@app.patch("/api/admin/empleados/{dni}/faltas/{fecha}")
async def faltas(dni : str, fecha : str, request: Request):
    datos = await request.json()
    if not datos:
        raise HTTPException(status_code=400, detail="No se enviaron datos")

    resultado = Administrador.gestionarFalta(DB, dni, fecha, **datos)
    manejar_respuesta_negocio(resultado)
    return resultado


@app.get("/api/admin/empleados/consultarPresentismo")
def presentismo(dni : str = None, fecha_desde : str = None, fecha_hasta : str = None):
    resultado = Administrador.consultarPresentismo(DB, dni, fecha_desde, fecha_hasta)
    manejar_respuesta_negocio(resultado)
    return resultado


@app.get("/api/admin/empleados/generar/{fecha_desde}/{fecha_hasta}")
def generarReporte(fecha_desde : str, fecha_hasta : str):
    resultado = Administrador.generarReportes(DB, fecha_desde, fecha_hasta)
    manejar_respuesta_negocio(resultado)
    return resultado


@app.get("/api/admin/empleados/exportar/{fecha_desde}/{fecha_hasta}")
def exportarAexcel(fecha_desde : str, fecha_hasta : str, nombreArchivo : str = None):
    resultado = Administrador.exportar(DB, fecha_desde, fecha_hasta, nombreArchivo)
    manejar_respuesta_negocio(resultado)
    if not resultado or not os.path.exists(resultado):
        raise HTTPException(status_code=404, detail="No se pudo generar el archivo")

    nombreDescargar = nombreArchivo if nombreArchivo else os.path.basename(resultado)

    return FileResponse(
        path=resultado,
        media_type="text/csv",
        filename=nombreDescargar
    )


@app.post("/api/admin/empleados/agregarEmpleado")
async def agregarEndpoint(request : Request):
    datos = await request.json()
    resultado = Administrador.agregarEmpleado(DB, **datos)
    manejar_respuesta_negocio(resultado)
    return resultado


@app.patch("/api/asistencia/empleados/ingreso")
def marcarIngreso(pin : str):
    id_empleado = Empleado.obtenerID(DB, pin)
    
    if not id_empleado:
        raise HTTPException(status_code=404, detail="El DNI/PIN ingresado no existe en el sistema")
        
    resultado = registroAsistencia.registrarIngreso(DB, id_empleado)
    manejar_respuesta_negocio(resultado)
    return resultado


@app.patch("/api/asistencia/empleados/salida")
def marcarSalida(pin : str):
    id_empleado = Empleado.obtenerID(DB, pin)
    return registroAsistencia.registrarSalida(DB, id_empleado)


@app.patch("/api/asistencia/empleados/salidaIntermedia")
def marcarSalidaIntermedia(pin : str):
    id_empleado = Empleado.obtenerID(DB, pin)
    return salidaIntermedia.registrar_salida_intermedia(DB, id_empleado)


@app.patch("/api/asistencia/empleados/reingreso")
def reingreso(pin : str):
    id_empleado = Empleado.obtenerID(DB, pin)
    return salidaIntermedia.registrar_reingreso(DB, id_empleado)