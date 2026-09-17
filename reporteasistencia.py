import sqlite3
import csv
from datetime import datetime

class ReporteAsistencia:
    def __init__(self, id_reporte, fecha_desde, fecha_hasta, tipo, fecha_generacion=None, resultados=None):
        self.id_reporte = id_reporte
        self.fecha_desde = fecha_desde
        self.fecha_hasta = fecha_hasta
        self.tipo = tipo
        self.fecha_generacion = fecha_generacion
        self.resultados = resultados or []

    @classmethod
    def generar(cls, DB, fecha_desde, fecha_hasta, tipo="General"):
        cursor = DB.cursor()
        resultados = cls.consultar(DB, fecha_desde=fecha_desde, fecha_hasta=fecha_hasta)
        
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO reporte_asistencia (fecha_desde, fecha_hasta, fecha_generacion, tipo)
            VALUES (?, ?, ?, ?)
        """, (fecha_desde, fecha_hasta, fecha_actual, tipo))
        
        id_reporte = cursor.lastrowid
        DB.commit()

        return cls(id_reporte, fecha_desde, fecha_hasta, tipo, fecha_actual, resultados)

    @classmethod
    def consultar(cls, DB, empleado_id=None, fecha_desde=None, fecha_hasta=None):
        cursor = DB.cursor()
        query = """
            SELECT a.asistencia_id, e.nombre, e.apellido, a.fecha, 
                   a.hora_entrada, a.hora_salida, a.estado_asistencia, a.hora_fuera
            FROM asistencia a
            JOIN empleado e ON a.empleado_id = e.empleado_id
            WHERE 1=1
        """
        parametros = []
        
        if empleado_id:
            query += " AND a.empleado_id = ?"
            parametros.append(empleado_id)
        if fecha_desde and fecha_hasta:
            query += " AND a.fecha BETWEEN ? AND ?"
            parametros.extend([fecha_desde, fecha_hasta])
            
        query += " ORDER BY a.fecha DESC"
        cursor.execute(query, parametros)
        return cursor.fetchall()

    @classmethod
    def exportarExcel(cls, DB, fecha_desde, fecha_hasta, nombre_archivo="reporte_asistencia.csv"):
        datos = cls.consultar(DB, fecha_desde=fecha_desde, fecha_hasta=fecha_hasta)
        
        with open(nombre_archivo, mode='w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow(['ID Asistencia', 'Nombre', 'Apellido', 'Fecha', 'Ingreso', 'Salida Int.', 'Reingreso', 'Egreso', 'Estado'])
            writer.writerows(datos)
            
        return nombre_archivo