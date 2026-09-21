##ACA VA TODA LA LOGICA QUE TIENE QUE VER CON LA API DE FASTAPI
from fastapi import FastAPI, Request
from administrador import Administrador
import baseDatos

DB = baseDatos.inicializar_base_datos()
app = FastAPI()


@app.patch("/api/admin/empleados/{dni}/asistencias/{fechaEmpleado}")
async def corregir_asistencia(dni, fechaEmpleado, request: Request):
    datos = await request.json()

    if not datos:
        return "No se enviaron datos"

    camposModificar = datos.pop("camposModificar", [])
    resultado = Administrador.corregirRegistro(DB, dni, fechaEmpleado, camposModificar, **datos)

    return {"mensaje": "Procesado con éxito", "resultado": resultado}
