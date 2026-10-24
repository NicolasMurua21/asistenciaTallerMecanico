

class Falta:
    idEmpleado: int
    idFalta: int
    fecha: str
    tipo: str
    motivo: str
    justificada: bool

    def __init__(self, idFalta, idEmpleado, fecha, tipo="Inasistencia", motivo="", justificada=False):
        self.idFalta = idFalta
        self.idEmpleado = idEmpleado
        self.fecha = fecha
        self.tipo = tipo
        self.motivo = motivo
        self.justificada = justificada

    def registrar(self, DB, estadoAusenteId=2):
        cursor = DB.cursor()
        sql = """
            INSERT INTO asistencia (empleado_id, fecha, hora_entrada, hora_salida, estado_asistencia)
            VALUES (?, ?, '00:00:00', '00:00:00', ?)
        """
        valores = (self.idEmpleado, self.fecha, estadoAusenteId)

        try:
            cursor.execute(sql, valores)
            DB.commit()
            self.idFalta = cursor.lastrowid
            print("Falta registrada con exito.")
            return True
        except:
            print("Error al registrar la falta.")
            return False

    def justificar(self, DB, motivo):
        cursor = DB.cursor()
        sql = """
            INSERT INTO justificacion (asistencia_id, motivo, fecha_solicitud, justificado)
            VALUES (?, ?, DATE('now'), 1)
        """
        valores = (self.idFalta, motivo)

        try:
            cursor.execute(sql, valores)
            DB.commit()
            self.motivo = motivo
            self.justificada = True
            print("Falta justificada con exito.")
            return True
        except:
            print("Error al justificar la falta.")
            return False

    def anular(self, DB):
        cursor = DB.cursor()
        sql = "DELETE FROM asistencia WHERE asistencia_id = ?"

        try:
            cursor.execute(sql, (self.idFalta,))
            DB.commit()
            print("Falta anulada con exito.")
            return True
        except:
            print("Error al anular la falta.")
            return False