import CorreccionRegistro
import Falta
import ReporteAsistencia
from empleado import Empleado


class Administrador:
    def corregirRegistro(DB, id_registro, motivo : str, valorNuevo : str, campoModificar):
        cursor = DB.cursor()
        cursor.execute(
            f"SELECT {campoModificar} FROM asistencia WHERE asistencia_id = ?", 
            (id_registro,),
        )
        resultado = cursor.fetchone()
        if resultado:
            CorreccionRegistro.aplicar(id_registro, motivo, campoModificar, valorNuevo, resultado[0])
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
        
    def consultarPresentismo(DB, nombre = None, id_turno = None):
        return ReporteAsistencia(DB, nombre = nombre, id_turno = id_turno)
    
    def generarReportes(DB):
        return ReporteAsistencia.generar(DB)
    
    def exportar(DB):
        return ReporteAsistencia.exportarExceñ(DB)

    @staticmethod    
    def agregarEmpleado(DB, dni, nombre, apellido, pin):
        return Empleado.registrarNuevo(DB, dni, nombre, apellido, pin)

