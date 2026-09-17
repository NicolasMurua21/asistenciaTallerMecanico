from correcionregistro import CorreccionRegistro
import Falta
from reporteasistencia import ReporteAsistencia
from empleado import Empleado
import baseDatos


class Administrador:
    #revisar aplicar
    def corregirRegistro(DB, id_registro, valorNuevo, campoModificar):
        cursor = DB.cursor()
        cursor.execute(
            f"SELECT {campoModificar} FROM asistencia WHERE asistencia_id = ?", 
            (id_registro,),
        )
        resultado = cursor.fetchone()
        if resultado:
            CorreccionRegistro.aplicar(id_registro, campoModificar, valorNuevo, resultado[0])
        else:
            return None



        
    def gestionarFalta(DB, id_empleado, id_falta, justificar = None, Anular = None, registrar = None, motivo = None, horaEgreso = None, HoraIngreso = None):
        if justificar is True:
            Falta.justificar(DB, id_empleado, id_falta, motivo)
            return
        if Anular is True:
            Falta.anular(DB, id_empleado, id_falta, motivo)
            return
        if registrar is True:
            Falta.registrar(DB, id_empleado, id_falta, horaEgreso, HoraIngreso)
            return
        return "NO SE ENVIO CORRECTAMENTE QUE SE QUIERE MODIFICAR"
        
    def consultarPresentismo(DB, empleado_id = None, fecha_desde = None, fecha_hasta = None):
        return ReporteAsistencia.consultar(DB, empleado_id = empleado_id, fecha_desde = fecha_desde, fecha_hasta = fecha_hasta)

    #corregir generar
    def generarReportes(DB, fecha_desde, fecha_hasta):
        return ReporteAsistencia.generar(DB, fecha_desde, fecha_hasta)
    
    def exportar(DB, fecha_desde, fecha_hasta, nombre_archivo = None):
        return ReporteAsistencia.exportarExcel(DB, fecha_desde, fecha_hasta, nombre_archivo = nombre_archivo)

    @staticmethod    
    def agregarEmpleado(DB, dni, nombre, apellido, pin):
        return Empleado.registrarNuevo(DB, dni, nombre, apellido, pin)




DB = baseDatos.inicializar_base_datos()
Administrador.agregarEmpleado(DB, 1234, "juan", "juan", 1234)
print(Administrador.consultarPresentismo(DB))




