import sqlite3
from datetime import datetime

class ReporteAsistencia:
    def __init__(self, id_reporte, fecha_generacion, tipo, resultados=None):
        self.id_reporte = id_reporte
        self.fecha_generacion = fecha_generacion
        self.tipo = tipo
        self.resultados = resultados or []

    @classmethod
    def generar(cls, DB, fecha_desde, fecha_hasta, tipo="General"):
        cursor = DB.cursor()
        cursor.execute("""
            SELECT a.asistencia_id, a.empleado_id, e.nombre, e.apellido, a.fecha, a.hora_ingreso, a.salida_intermedia, a.reingreso, a.hora_egreso, a.estado
            FROM asistencia a
            JOIN empleado e ON a.empleado_id = e.empleado_id
            WHERE a.fecha BETWEEN ? AND ?
            ORDER BY a.fecha ASC
        """, (fecha_desde, fecha_hasta))
        
        resultados = cursor.fetchall()
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute("""
            INSERT INTO reporte_asistencia (fecha_generacion, tipo)
            VALUES (?, ?)
        """, (fecha_actual, tipo))
        
        id_reporte = cursor.lastrowid
        DB.commit()

        return cls(id_reporte, fecha_actual, tipo, resultados)