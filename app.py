##ACA VA TODA LA LOGICA QUE TIENE QUE VER CON LA API DE FASTAPI
from fastapi import FastAPI, Request, HTTPException
from administrador import Administrador
from fastapi.responses import FileResponse
import baseDatos
import os

DB = baseDatos.inicializar_base_datos()
app = FastAPI()


@app.patch("/api/admin/empleados/{dni}/asistencias/{fechaEmpleado}")
async def corregir_asistencia(dni : str, fechaEmpleado, request: Request):
    datos = await request.json()

    if not datos:
        raise HTTPException(status_code=400, detail="No se enviaron datos")

    camposModificar = datos.pop("camposModificar", [])
    resultado = Administrador.corregirRegistro(DB, dni, fechaEmpleado, camposModificar, **datos)

    if resultado == "EMPLEADO NO EXISTE":
          raise HTTPException(status_code=404, detail="No se encontro al empleado")

    return {"mensaje": "Procesado con éxito", "resultado": resultado}


@app.patch("/api/admin/empleados/{dni}/faltas/{fecha}")
async def faltas(dni : str, fecha : str, request: Request):
    datos = await request.json()

    if not datos:
        raise HTTPException(status_code=400, detail="No se enviaron datos")

    resultado = Administrador.gestionarFalta(DB, dni, fecha, **datos)

    return resultado

@app.get("/api/admin/empleados/consultarPresentismo")
def presentismo(dni : str = None, fecha_desde : str = None, fecha_hasta : str = None):
    return Administrador.consultarPresentismo(DB, dni, fecha_desde, fecha_hasta)

@app.get("/api/admin/empleados/generar/{fecha_desde}/{fecha_hasta}")
def generarReporte(fecha_desde : str, fecha_hasta : str):
    return Administrador.generarReportes(DB, fecha_desde, fecha_hasta)

@app.get("/api/admin/empleados/exportar/{fecha_desde}/{fecha_hasta}")
def exportarAexcel(fecha_desde : str, fecha_hasta : str, nombreArchivo : str = None):
    resultado = Administrador.exportar(DB, fecha_desde, fecha_hasta, nombreArchivo)

    if not resultado or not os.path.exists(resultado):
        raise HTTPException(status_code=404, detail="No se pudo generar el archivo")

    if not nombreArchivo:
        nombreDescargar = os.path.basename(resultado)
    else:
        nombreDescargar = nombreArchivo

    return FileResponse(
        path=resultado,
        media_type="text/csv",
        filename=nombreDescargar
    )
    