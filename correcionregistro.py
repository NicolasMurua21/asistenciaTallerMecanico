import sqlite3
from datetime import datetime

class CorreccionRegistro:
    def __init__(self, id_correccion, fecha_hora, motivo, valor_anterior, valor_nuevo, empleado_id=None, asistencia_id=None):
        self.id_correccion = id_correccion
        self.fecha_hora = fecha_hora
        self.motivo = motivo
        self.valor_anterior = valor_anterior
        self.valor_nuevo = valor_nuevo
        self.empleado_id = empleado_id
        self.asistencia_id = asistencia_id

    @classmethod
    def aplicar(cls, DB, empleado_id, fecha, hora_ingreso, salida_intermedia, reingreso, hora_egreso, motivo):
        cursor = DB.cursor()
        
        cursor.execute(
            "SELECT asistencia_id, hora_ingreso, salida_intermedia, reingreso, hora_egreso FROM asistencia WHERE empleado_id = ? AND fecha = ?",
            (empleado_id, fecha)
        )
        resultado = cursor.fetchone()
        
        valor_nuevo_str = f"{hora_ingreso}|{salida_intermedia}|{reingreso}|{hora_egreso}"
        
        if resultado:
            asistencia_id = resultado[0]
            valor_anterior_str = f"{resultado[1]}|{resultado[2]}|{resultado[3]}|{resultado[4]}"
            
            cursor.execute("""
                UPDATE asistencia 
                SET hora_ingreso = ?, salida_intermedia = ?, reingreso = ?, hora_egreso = ?, estado = 'Modificado'
                WHERE asistencia_id = ?
            """, (hora_ingreso, salida_intermedia, reingreso, hora_egreso, asistencia_id))
        else:
            valor_anterior_str = "Sin registro previo"
            cursor.execute("""
                INSERT INTO asistencia (empleado_id, fecha, hora_ingreso, salida_intermedia, reingreso, hora_egreso, estado)
                VALUES (?, ?, ?, ?, ?, ?, 'Modificado')
            """, (empleado_id, fecha, hora_ingreso, salida_intermedia, reingreso, hora_egreso))
            asistencia_id = cursor.lastrowid

        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO correccion_registro (fecha_hora, motivo, valor_anterior, valor_nuevo, empleado_id, asistencia_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (fecha_actual, motivo, valor_anterior_str, valor_nuevo_str, empleado_id, asistencia_id))
        
        id_correccion = cursor.lastrowid
        DB.commit()

        return cls(id_correccion, fecha_actual, motivo, valor_anterior_str, valor_nuevo_str, empleado_id, asistencia_id)

    @classmethod
    def deshacer(cls, DB, id_correccion):
        cursor = DB.cursor()
        
        # 1. Obtener los valores guardados en la auditoría
        cursor.execute(
            "SELECT asistencia_id, valor_anterior FROM correccion_registro WHERE id_correccion = ?",
            (id_correccion,)
        )
        resultado = cursor.fetchone()
        
        if resultado and resultado[0]:
            asistencia_id = resultado[0]
            valor_anterior = resultado[1]
            
            if valor_anterior == "Sin registro previo":
                cursor.execute("DELETE FROM asistencia WHERE asistencia_id = ?", (asistencia_id,))
            else:
                # Restaurar valores anteriores
                h_ing, s_int, reing, h_egr = valor_anterior.split("|")
                cursor.execute("""
                    UPDATE asistencia 
                    SET hora_ingreso = ?, salida_intermedia = ?, reingreso = ?, hora_egreso = ?, estado = 'Normal'
                    WHERE asistencia_id = ?
                """, (h_ing, s_int, reing, h_egr, asistencia_id))
            
        # 2. Borrar el registro de corrección
        cursor.execute("DELETE FROM correccion_registro WHERE id_correccion = ?", (id_correccion,))
        DB.commit()
        return True