import sqlite3
from datetime import datetime

class CorreccionRegistro:
    def __init__(self, id_correccion, fecha_hora, motivo, empleado_id, asistencia_id=None):
        self.id_correccion = id_correccion
        self.fecha_hora = fecha_hora
        self.motivo = motivo
        self.empleado_id = empleado_id
        self.asistencia_id = asistencia_id

    @classmethod
    def aplicar(cls, DB, empleado_id, fecha, hora_ingreso, salida_intermedia, reingreso, hora_egreso, motivo):
        cursor = DB.cursor()
        
        cursor.execute(
            "SELECT asistencia_id FROM asistencia WHERE empleado_id = ? AND fecha = ?",
            (empleado_id, fecha)
        )
        resultado = cursor.fetchone()
        
        if resultado:
            asistencia_id = resultado[0]
            cursor.execute("""
                UPDATE asistencia 
                SET hora_ingreso = ?, salida_intermedia = ?, reingreso = ?, hora_egreso = ?, estado = 'Modificado'
                WHERE asistencia_id = ?
            """, (hora_ingreso, salida_intermedia, reingreso, hora_egreso, asistencia_id))
        else:
            cursor.execute("""
                INSERT INTO asistencia (empleado_id, fecha, hora_ingreso, salida_intermedia, reingreso, hora_egreso, estado)
                VALUES (?, ?, ?, ?, ?, ?, 'Modificado')
            """, (empleado_id, fecha, hora_ingreso, salida_intermedia, reingreso, hora_egreso))
            asistencia_id = cursor.lastrowid

        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO correccion_registro (fecha_hora, motivo, empleado_id, asistencia_id)
            VALUES (?, ?, ?, ?)
        """, (fecha_actual, motivo, empleado_id, asistencia_id))
        
        id_correccion = cursor.lastrowid
        DB.commit()

        return cls(id_correccion, fecha_actual, motivo, empleado_id, asistencia_id)

    @classmethod
    def deshacer(cls, DB, id_correccion):
        cursor = DB.cursor()
        
        cursor.execute(
            "SELECT asistencia_id FROM correccion_registro WHERE id_correccion = ?",
            (id_correccion,)
        )
        resultado = cursor.fetchone()
        
        if resultado and resultado[0]:
            asistencia_id = resultado[0]
            cursor.execute("DELETE FROM asistencia WHERE asistencia_id = ?", (asistencia_id,))
            
        cursor.execute("DELETE FROM correccion_registro WHERE id_correccion = ?", (id_correccion,))
        
        DB.commit()
        return True