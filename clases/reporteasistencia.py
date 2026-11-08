import sqlite3
import csv
from datetime import datetime
from collections import defaultdict

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
        
        # Consulta haciendo el JOIN correcto con estado_asistencia en minúsculas
        query = """
            SELECT a.asistencia_id, e.nombre, e.apellido, a.fecha, 
                   a.hora_entrada, a.hora_salida, es.nombre_estado, a.hora_fuera
            FROM asistencia a
            JOIN empleado e ON a.empleado_id = e.empleado_id
            LEFT JOIN estado_asistencia es ON a.estado_asistencia = es.estado_id
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
        
        total_ausencias = 0
        
        return resultados_asistencia, total_ausencias
    
    @classmethod
    def exportarExcel(cls, DB, fecha_desde, fecha_hasta, nombre_archivo=None):
        if not nombre_archivo:
            nombre_archivo = "reporte_asistencia.csv"
            
        datos_brutos, _ = cls.consultar(DB, fecha_desde=fecha_desde, fecha_hasta=fecha_hasta)
        
        datos_procesados = []
        horas_por_empleado = defaultdict(float)
        
        for fila in datos_brutos:
            asistencia_id, nombre, apellido, fecha, hora_entrada, hora_salida, estado, hora_fuera = fila
            
            # Nombre completo para agrupar
            nombre_empleado = f"{nombre} {apellido}"
            
            horas_trabajadas_str = "En curso / Sin salida"
            segundos_trabajados = 0
            
            if hora_entrada and hora_salida:
                try:
                    t_entrada = datetime.strptime(str(hora_entrada).split('.')[0], '%H:%M:%S')
                    t_salida = datetime.strptime(str(hora_salida).split('.')[0], '%H:%M:%S')
                    
                    diferencia = t_salida - t_entrada
                    segundos_trabajados = diferencia.total_seconds()
                    
                    if segundos_trabajados > 0:
                        horas = int(segundos_trabajados // 3600)
                        minutos = int((segundos_trabajados % 3600) // 60)
                        horas_trabajadas_str = f"{horas}h {minutos}m"
                        
                        # Acumulamos las horas trabajadas por este empleado en el período
                        horas_por_empleado[nombre_empleado] += segundos_trabajados
                    else:
                        horas_trabajadas_str = "0h 0m"
                except Exception:
                    horas_trabajadas_str = "Error cálculo"
                    
            datos_procesados.append([
                asistencia_id, nombre, apellido, fecha, hora_entrada, hora_salida, estado, hora_fuera, horas_trabajadas_str
            ])
            
        with open(nombre_archivo, mode='w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f, delimiter=',')
            
            # 1. Detalle principal de asistencias
            writer.writerow(['ID Asistencia', 'Nombre', 'Apellido', 'Fecha', 'Ingreso', 'Salida', 'Estado', 'Hora Fuera', 'Horas Trabajadas'])
            writer.writerows(datos_procesados)
            
            # 2. Espacio de separación y título de resumen
            writer.writerow([])
            writer.writerow(['--- TOTAL DE HORAS TRABAJADAS POR EMPLEADO (EN EL PERÍODO) ---'])
            
            # 3. Mostrar el total acumulado por cada empleado
            for empleado, segs in sorted(horas_por_empleado.items()):
                h = int(segs // 3600)
                m = int((segs % 3600) // 60)
                writer.writerow([empleado, f"Total en el período: {h} horas y {m} minutos"])
                
        return nombre_archivo