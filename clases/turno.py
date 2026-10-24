from empleado import Empleado


class Turno:
    def __init__(self, idTurno, nombre, horaInicio, horaFin, tipo="Regular", estado="Disponible"):
        self.idTurno = idTurno
        self.nombre = nombre
        self.horaInicio = horaInicio
        self.horaFin = horaFin
        self.tipo = tipo
        self.estado = estado

    def asignar(self, DB, fechaDesde, fechaHasta, dni=None, pin=None):
        idEmpleado = Empleado.obtenerID(DB, dni, pin)

        if idEmpleado is None:
            print("No se encontro el empleado con los datos ingresados.")
            return False

        cursor = DB.cursor()
        sql = """
            INSERT INTO asignacion_turno (empleado_id, turno_id, fecha_desde, fecha_hasta)
            VALUES (?, ?, ?, ?)
        """
        valores = (idEmpleado, self.idTurno, fechaDesde, fechaHasta)

        cursor.execute(sql, valores)
        DB.commit()
        self.estado = "Asignado"
        print("Turno asignado con exito.")
        return True