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
    def generar(cls, DB, fecha_desde, fecha_hasta):
        #Llamamos a consultar y obtenemos asistencias y ausencias
        resultados, total_ausencias = cls.consultar(DB, empleado_id=None, fecha_desde=fecha_desde, fecha_hasta=fecha_hasta)
        
        total_asistencias = len(resultados)
        
        #Calcular el total de horas trabajadas sumando las diferencias
        total_segundos = 0
        for fila in resultados:
            hora_entrada = fila[4]
            hora_salida = fila[5]
            
            if hora_entrada and hora_salida:
                try:
                    t1 = datetime.strptime(hora_entrada, "%H:%M:%S")
                    t2 = datetime.strptime(hora_salida, "%H:%M:%S")
                    diferencia = t2 - t1
                    total_segundos += diferencia.total_seconds()
                except ValueError:
                    pass
                    
        total_horas_trabajadas = round(total_segundos / 3600, 2)
        
        fecha_generacion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        #Creamos el objeto
        reporte = cls(
            id_reporte=None, 
            fecha_desde=fecha_desde, 
            fecha_hasta=fecha_hasta, 
            tipo="Métricas del Taller", 
            fecha_generacion=fecha_generacion, 
            resultados=resultados
        )
        
        reporte.total_asistencias = total_asistencias
        reporte.total_horas_trabajadas = total_horas_trabajadas
        reporte.total_ausencias = total_ausencias
        
        return reporte

    @classmethod
    def consultar(cls, DB, empleado_id=None, fecha_desde=None, fecha_hasta=None):
        cursor = DB.cursor()
        
        #asistencia
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
        resultados_asistencia = cursor.fetchall()
        
        #faltas
        query_faltas = "SELECT COUNT(*) FROM falta WHERE 1=1"
        parametros_faltas = []
        
        if empleado_id:
            query_faltas += " AND empleado_id = ?"
            parametros_faltas.append(empleado_id)
        if fecha_desde and fecha_hasta:
            query_faltas += " AND fecha BETWEEN ? AND ?"
            parametros_faltas.extend([fecha_desde, fecha_hasta])
            
        cursor.execute(query_faltas, parametros_faltas)
        total_ausencias = cursor.fetchone()[0]
        
        # Retornamos ambas cosas juntas
        return resultados_asistencia, total_ausencias

    
    @classmethod
    def exportarExcel(cls, DB, fecha_desde, fecha_hasta, nombre_archivo="reporte_asistencia.csv"):
        datos, _ = cls.consultar(DB, fecha_desde=fecha_desde, fecha_hasta=fecha_hasta)
        
        with open(nombre_archivo, mode='w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow(['ID Asistencia', 'Nombre', 'Apellido', 'Fecha', 'Ingreso', 'Salida Int.', 'Reingreso', 'Egreso', 'Estado'])
            writer.writerows(datos)
            
        return nombre_archivo