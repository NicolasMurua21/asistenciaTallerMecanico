from correcionregistro import CorreccionRegistro
import Falta
from reporteasistencia import ReporteAsistencia
from empleado import Empleado
import baseDatos


class Administrador:
   
    def corregirRegistro(DB, DNI, fechaEmpleado ,camposModificar,  hora_salida = None, fecha = None, hora_entrada = None, estado_asistencia = None, hora_fuera = None ):
        try:
            if not DB or not DNI or not fechaEmpleado or not camposModificar:
                return "FALTAN DATOS"
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
        except:
            return "ERROR INTERNO"
 
    def gestionarFalta(DB, DNI, fecha, justificar = None, Anular = None, registrar = None, motivo = None, horaEgreso = None, HoraIngreso = None):
        try:
            if not DB or not DNI or not fecha:
                return "FALTAN DATOS"
            cursor = DB.cursor()
            cursor.execute(
                "SELECT empleado_id FROM empleado WHERE documento = ?", 
                (DNI,)
            )
            id_empleado = cursor.fetchone()
            cursor.execute(
                "SELECT asistencia_id FROM asistencia WHERE fecha = ? AND empleado_id = ?",
                (fecha, id_empleado,)
            )
            id_falta = cursor.fetchone()
            if justificar is True:
                Falta.justificar(DB, id_empleado, id_falta, motivo)
                return "EXITO"
            if Anular is True:
                Falta.anular(DB, id_empleado, id_falta, motivo)
                return "EXITO"
            if registrar is True:
                Falta.registrar(DB, id_empleado, id_falta, horaEgreso, HoraIngreso)
                return "EXITO"
            
            return "FALTAN DATOS"
        except:
            return "ERROR INTERNO"
        
    def consultarPresentismo(DB, DNI = None, fecha_desde = None, fecha_hasta = None):
        try:
            if not DB:
                return "FALTAN DATOS"
            if DNI:
                cursor = DB.cursor()
                cursor.execute(
                    "SELECT empleado_id FROM empleado WHERE documento = ?", 
                    (DNI,)
                )
                id_empleado = cursor.fetchone()
                if not id_empleado:
                    return "EMPLEADO NO EXISTE"
                
                return ReporteAsistencia.consultar(DB, id_empleado[0], fecha_desde = fecha_desde, fecha_hasta = fecha_hasta)
            else:
                return ReporteAsistencia.consultar(DB, id_empleado = None, fecha_desde = fecha_desde, fecha_hasta = fecha_hasta)
        except:
            return "ERROR INTERNO"

    
    def generarReportes(DB, fecha_desde, fecha_hasta):
        try:
            if not DB or not fecha_desde or not fecha_hasta:
                return "FALTAN DATOS"
            return ReporteAsistencia.generar(DB, fecha_desde, fecha_hasta)
        except:
            return "ERROR INTERNO"
    
    def exportar(DB, fecha_desde, fecha_hasta, nombre_archivo = None):
        try:
            if not DB or not fecha_desde or not fecha_hasta:
                return "FALTAN DATOS"
            return ReporteAsistencia.exportarExcel(DB, fecha_desde, fecha_hasta, nombre_archivo = nombre_archivo)
        except:
            return "ERROR INTERNO"

    @staticmethod    
    def agregarEmpleado(DB, dni, nombre, apellido, pin):
        try:
            if not dni or not nombre or not apellido:
                return "FALTAN DATOS"
            return Empleado.registrarNuevo(DB, dni, nombre, apellido, pin)
        except:
            return "ERROR INTERNO"







