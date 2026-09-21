##ACA VA TODA LA LOGICA QUE TIENE QUE VER CON LA API DE FASTAPI
from fastapi import FastAPI, Request, HTTPException
from administrador import Administrador
import baseDatos

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
async def presentismo(dni : str = None, fecha_desde : str = None, fecha_hasta : str = None):
 
    return Administrador.consultarPresentismo(DB, dni, fecha_desde, fecha_hasta)
    