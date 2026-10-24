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
    def aplicar(cls, DB, id_registro, camposModificar, hora_salida = None, fecha = None, hora_entrada = None, estado_asistencia = None, hora_fuera = None ):
        valores_disponibles = {
            "hora_salida": hora_salida,
            "fecha": fecha,
            "hora_entrada": hora_entrada,
            "estado_asistencia": estado_asistencia,
            "hora_fuera": hora_fuera
        }
        
        
        valoresNuevos = [valores_disponibles[campo] for campo in camposModificar]
        
        cursor = DB.cursor()
        
        
        set_clause = ", ".join([f"{campo} = ?" for campo in camposModificar])
        
        parametros = tuple(valoresNuevos) + (id_registro,)
        
        cursor.execute(
            f"UPDATE asistencia SET {set_clause} WHERE asistencia_id = ?",
            parametros
        )
        
        DB.commit()

        # Devuelve la cantidad de filas cambiadas (True si fue exitoso, False si no)
        return cursor.rowcount > 0
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