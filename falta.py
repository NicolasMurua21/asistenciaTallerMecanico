

class Falta:
    idEmpleado: int
    idFalta: int
    fecha: str
    tipo: str
    motivo: str
    justificada: bool

    def __init__(self, idFalta=None, idEmpleado=None, fecha=None, tipo="Inasistencia", motivo="", justificada=False):
        self.idFalta = idFalta
        self.idEmpleado = idEmpleado
        self.fecha = fecha
        self.tipo = tipo
        self.motivo = motivo
        self.justificada = justificada

    def registrar(self, DB, estadoAusenteId=2):
        cursor = DB.cursor()
        
        try:
            # 1. Insertamos la asistencia como ausente
            sql_asistencia = """
                INSERT INTO asistencia (empleado_id, fecha, hora_entrada, hora_salida, estado_asistencia)
                VALUES (?, ?, '00:00:00', '00:00:00', ?)
            """
            cursor.execute(sql_asistencia, (self.idEmpleado, self.fecha, estadoAusenteId))
            self.idFalta = cursor.lastrowid

            # 2. Si viene marcada como justificada desde el formulario, la guardamos de una
            if self.justificada:
                if self.motivo:
                    motivo_a_usar = self.motivo
                else:
                    motivo_a_usar = "Sin motivo especificado"
                # Llamamos a la función existente asegurando que use la misma conexión
                exito_justificacion = self.justificar(DB, motivo_a_usar)
                if not exito_justificacion:
                    raise Exception("Fallo al intentar justificar la falta durante el registro.")

            DB.commit()
            print("Falta registrada con éxito.")
            return True
            
        except Exception as e:
            DB.rollback()
            print(f"Error al registrar la falta: {e}")
            return False

    def justificar(self, DB, motivo):
        """Función independiente para justificar la falta en cualquier momento posterior."""
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
            print("Falta justificada con éxito.")
            return True
        except Exception as e:
            print(f"Error al justificar la falta: {e}")
            return False

    def anular(self, DB, estadoPresenteId=1):
        cursor = DB.cursor()
        sql = "UPDATE asistencia SET estado_asistencia = ? WHERE asistencia_id = ?"

        try:
            cursor.execute(sql, (estadoPresenteId, self.idFalta))
            DB.commit()
            print("Falta anulada (estado revertido) con éxito.")
            return True
        except Exception as e:
            print(f"Error al anular la falta: {e}")
            return False