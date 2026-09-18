from correcionregistro import CorreccionRegistro
import Falta
from reporteasistencia import ReporteAsistencia
from empleado import Empleado
import baseDatos


class Administrador:
   
    def corregirRegistro(DB, DNI, fechaEmpleado ,camposModificar,  hora_salida = None, fecha = None, hora_entrada = None, estado_asistencia = None, hora_fuera = None ):
        cursor = DB.cursor()
        cursor.execute(
            "SELECT empleado_id FROM empleado WHERE documento = ?", 
            (DNI,)
        )
        empleado = cursor.fetchone()
        if not empleado:
            return "EMPLEADO NO EXISTE"
        
        cursor.execute(
            "SELECT asistencia_id FROM asistencia WHERE empleado_id = ? AND fecha = ?", 
            (empleado[0], fechaEmpleado)
        )
        asistencia = cursor.fetchone()

        if asistencia:
            return CorreccionRegistro.aplicar(DB, asistencia[0], camposModificar, hora_salida = hora_salida, fecha = fecha, hora_entrada = hora_entrada, estado_asistencia = estado_asistencia, hora_fuera = hora_fuera )
        else:
            return None



        
    def gestionarFalta(DB, DNI, id_falta, justificar = None, Anular = None, registrar = None, motivo = None, horaEgreso = None, HoraIngreso = None):
        cursor = DB.cursor()
        cursor.execute(
            "SELECT empleado_id FROM empleado WHERE documento = ?", 
            (DNI,)
        )
        id_empleado = cursor.fetchone()
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
        
    def consultarPresentismo(DB, DNI = None, fecha_desde = None, fecha_hasta = None):
        if DNI:
            cursor = DB.cursor()
            cursor.execute(
                "SELECT empleado_id FROM empleado WHERE documento = ?", 
                (DNI,)
            )
            id_empleado = cursor.fetchone()
            return ReporteAsistencia.consultar(DB, id_empleado, fecha_desde = fecha_desde, fecha_hasta = fecha_hasta)
        else:
            return ReporteAsistencia.consultar(DB, id_empleado = None, fecha_desde = fecha_desde, fecha_hasta = fecha_hasta)

    #corregir generar
    def generarReportes(DB, fecha_desde, fecha_hasta):
        return ReporteAsistencia.generar(DB, fecha_desde, fecha_hasta)
    
    def exportar(DB, fecha_desde, fecha_hasta, nombre_archivo = None):
        return ReporteAsistencia.exportarExcel(DB, fecha_desde, fecha_hasta, nombre_archivo = nombre_archivo)

    @staticmethod    
    def agregarEmpleado(DB, dni, nombre, apellido, pin):
        return Empleado.registrarNuevo(DB, dni, nombre, apellido, pin)







