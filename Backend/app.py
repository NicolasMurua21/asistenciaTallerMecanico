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


class AsignarTurnoRequest(BaseModel):
    turno_id: int
    dni: str
    fecha_desde: str
    fecha_hasta: str


def manejar_respuesta_negocio(resultado):
    if resultado == "FALTAN DATOS":
        raise HTTPException(status_code=400, detail="Faltan datos obligatorios")
    if resultado == "EMPLEADO NO EXISTE":
        raise HTTPException(status_code=404, detail="El empleado no existe")
    if resultado == "ERROR INTERNO":
        raise HTTPException(status_code=500, detail="Ocurrió un error inesperado en el servidor")
    return resultado


from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel

@app.patch("/api/admin/empleados/{dni}/asistencias/{fechaEmpleado}")
async def corregir_asistencia(dni: str, fechaEmpleado: str, request: Request):
    try:
        datos = await request.json()
        if not datos:
            raise HTTPException(status_code=400, detail="No se enviaron datos")

        # Extraemos los campos especiales que viajan en el JSON
        camposModificar = datos.pop("camposModificar", [])
        motivo = datos.pop("motivo", None)

        # Llamamos directamente a la clase puente Administrador
        # **datos desempaqueta los campos de hora_entrada, hora_salida, estado_asistencia, etc.
        resultado = Administrador.corregirRegistro(DB, dni, fechaEmpleado, camposModificar, **datos)

        # Evaluamos el resultado que devuelve la lógica de negocio
        if resultado == "FALTAN DATOS":
            raise HTTPException(status_code=400, detail="Faltan datos obligatorios para la corrección.")
        if resultado == "EMPLEADO NO EXISTE":
            raise HTTPException(status_code=404, detail="El empleado no existe.")
        if resultado is None:
            raise HTTPException(status_code=404, detail="No se encontró un registro de asistencia para esa fecha.")
        if resultado == "ERROR INTERNO":
            raise HTTPException(status_code=500, detail="Error interno al procesar la corrección.")

        return {"mensaje": "Modificación aplicada con éxito", "resultado": resultado}
        
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Error en endpoint corregir_asistencia: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al corregir asistencia: {str(e)}")


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
        resultados, _ = ReporteAsistencia.consultar(DB, empleado_id=empleado_id)
        
        historial = []
        for reg in resultados: 
            try:
                asistencia_id = reg[0]
                nombre = reg[1]
                apellido = reg[2]
                fecha = reg[3]
                nombre_estado = reg[6] if len(reg) > 6 else "Ausente"
                
                cursor = DB.cursor()
                documento = "-"
                turno = "-"
                
                # Buscamos el documento y el nombre del turno actual asignado al empleado
                try:
                    cursor.execute("""
                        SELECT e.documento, t.nombre_turno 
                        FROM empleado e
                        LEFT JOIN asignacion_turno a ON e.empleado_id = a.empleado_id 
                        LEFT JOIN turno t ON a.turno_id = t.turno_id
                        WHERE e.nombre = ? AND e.apellido = ?
                        LIMIT 1
                    """, (nombre, apellido))
                    emp_info = cursor.fetchone()
                    if emp_info:
                        documento = emp_info[0] or "-"
                        turno = emp_info[1] or "-"
                except Exception as e:
                    pass

                cursor.execute("SELECT motivo FROM justificacion WHERE asistencia_id = ?", (asistencia_id,))
                justificacion = cursor.fetchone()
                
                historial.append({
                    "id": asistencia_id,
                    "emplebado_nombre": f"{apellido}, {nombre}",
                    "dni": documento,
                    "turno": turno,
                    "fecha": fecha,
                    "estado": nombre_estado or "Ausente",
                    "justificada": bool(justificacion),
                    "motivo": justificacion[0] if justificacion else ""
                })
            except Exception as inner_e:
                print(f"Error en registro individual: {inner_e}")
                continue
            
        return {"success": True, "ausencias": historial}
        
    except Exception as e:
        print(f"Error general en historial: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al obtener el historial: {str(e)}")

@app.post("/api/admin/turnos/asignar")
def api_asignar_turno(data: AsignarTurnoRequest):
    try:
        cursor = DB.cursor()
        
        # Buscamos el empleado directamente por su documento
        cursor.execute("SELECT empleado_id FROM empleado WHERE documento = ?", (data.dni,))
        emp = cursor.fetchone()
        
        if not emp:
            raise HTTPException(status_code=404, detail="No se encontró ningún empleado con ese DNI.")
        
        empleado_id = emp[0]
        
        # Insertamos la asignación de turno
        cursor.execute("""
            INSERT INTO asignacion_turno (empleado_id, turno_id, fecha_desde, fecha_hasta)
            VALUES (?, ?, ?, ?)
        """, (empleado_id, data.turno_id, data.fecha_desde, data.fecha_hasta))
        
        DB.commit()
        return {"success": True, "message": "Turno asignado con éxito."}
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al asignar el turno: {str(e)}")

@app.get("/api/admin/turnos")
def api_listar_turnos():
    try:
        cursor = DB.cursor()
        cursor.execute("SELECT turno_id, nombre_turno, hora_inicio, hora_fin FROM turno")
        turnos_db = cursor.fetchall()
        
        lista_turnos = []
        for t in turnos_db:
            lista_turnos.append({
                "turno_id": t[0],
                "nombre_turno": t[1],
                "hora_inicio": t[2],
                "hora_fin": t[3]
            })
            
        return {"success": True, "turnos": lista_turnos}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/admin/estados")
def obtener_estados():
    try:
        cursor = DB.cursor()
        # Apuntamos a la tabla 'estado_asistencia' y sus columnas reales
        cursor.execute("SELECT estado_id, nombre_estado FROM estado_asistencia") 
        filas = cursor.fetchall()
        
        estados = [{"id": row[0], "nombre": row[1]} for row in filas]
        return {"success": True, "estados": estados}
    except Exception as e:
        print(f"Error al obtener estados: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al obtener los estados: {str(e)}")

@app.patch("/api/admin/empleados/{empleado_id}/estado")
async def actualizar_estado_empleado(empleado_id: int, request: Request):
    try:
        datos = await request.json()
        activo = datos.get("activo", False) # True o False según mandes desde el JS

        # Pasamos el empleado_id en lugar del DNI
        resultado = Empleado.cambiarEstadoActivo(DB, empleado_id, activo)

        if resultado == "FALTAN DATOS":
            raise HTTPException(status_code=400, detail="Faltan datos obligatorios.")
        if resultado == "EMPLEADO NO EXISTE":
            raise HTTPException(status_code=404, detail="El empleado no existe.")
        if resultado == "ERROR INTERNO":
            raise HTTPException(status_code=500, detail="Error interno del servidor.")

        return {"mensaje": "Estado actualizado con éxito", "activo": activo}
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")