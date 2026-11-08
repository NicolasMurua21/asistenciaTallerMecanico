import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
sys.path.append(current_dir)
sys.path.append(root_dir)

import baseDatos
from pydantic import BaseModel
from typing import Optional
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from clases.administrador import Administrador
from clases.empleado import Empleado
from salidaintermedia import salidaIntermedia
from registroasistencia import registroAsistencia
from clases.reporteasistencia import ReporteAsistencia
from falta import Falta

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

class RegistrarAusenciaRequest(BaseModel):
    empleado_id: int
    fecha: str
    justificada: bool  # True si eligió "Justificada", False si eligió "Injustificada"
    motivo: Optional[str] = ""
    tipo: Optional[str] = "Inasistencia"


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
    try:
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
    except Exception as e:
        print("ERROR INTERNO EN EXPORTAR:", str(e))
        import traceback
        traceback.print_exc() # Esto fuerza a que se imprima todo el error detallado en la terminal
        traceback.print_exc()
        raise e

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


@app.post("/api/admin/faltas/registrar")
def api_registrar_ausencia(data: RegistrarAusenciaRequest):
    cursor = DB.cursor()
    
    try:
        # 1. Verificamos si ya existe una ausencia (o registro) para ese empleado en esa fecha
        cursor.execute(
            "SELECT asistencia_id FROM asistencia WHERE empleado_id = ? AND fecha = ?", 
            (data.empleado_id, data.fecha)
        )
        existente = cursor.fetchone()
        
        if existente:
            raise HTTPException(
                status_code=400, 
                detail="El empleado ya tiene un registro de asistencia o ausencia cargado para esta fecha."
            )

        # 2. Si no existe, procedemos a crear la instancia y registrar
        nueva_falta = Falta(
            idEmpleado=data.empleado_id,
            fecha=data.fecha,
            tipo=data.tipo,
            motivo=data.motivo,
            justificada=data.justificada
        )
        
        exito = nueva_falta.registrar(DB)
        
        if exito:
            return {"success": True, "mensaje": "Ausencia registrada correctamente", "idFalta": nueva_falta.idFalta}
        else:
            raise HTTPException(status_code=400, detail="No se pudo registrar la ausencia en la base de datos.")
            
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@app.get("/api/admin/empleados")
def listar_empleados():
    try:
        cursor = DB.cursor()
        cursor.execute("SELECT empleado_id, nombre, apellido FROM empleado ORDER BY apellido, nombre")
        resultados = cursor.fetchall()
        
        empleados = []
        for row in resultados:
            empleados.append({
                "empleado_id": row[0],
                "nombre": row[1],
                "apellido": row[2]
            })
            
        return {"success": True, "empleados": empleados}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/admin/faltas/historial")
def api_historial_ausencias(empleado_id: Optional[int] = None):
    try:
        # Llamamos directamente al método que ya tienes implementado
        # (Asumiendo que la clase se llama Asistencia o Falta, ajusta el nombre según corresponda)
        resultados, _ = ReporteAsistencia.consultar(DB, empleado_id=empleado_id)
        
        historial = []
        for reg in resultados: 
            # reg según tu query devuelve: 
            # [0] asistencia_id, [1] nombre, [2] apellido, [3] fecha, 
            # [4] hora_entrada, [5] hora_salida, [6] nombre_estado, [7] hora_fuera
            
            # Determinamos si está justificada consultando la tabla justificacion
            cursor = DB.cursor()
            cursor.execute("SELECT motivo FROM justificacion WHERE asistencia_id = ?", (reg[0],))
            justificacion = cursor.fetchone()
            
            historial.append({
                "id": reg[0],
                "emplebado_nombre": f"{reg[2]}, {reg[1]}", # Apellido, Nombre
                "fecha": reg[3],
                "estado": reg[6] or "Ausente",
                "justificada": bool(justificacion),
                "motivo": justificacion[0] if justificacion else ""
            })
            
        return {"success": True, "ausencias": historial}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener el historial: {str(e)}")