##ACA SE VA A INICIAR LA BASE DE DATOS, Y SU CREACION
import sqlite3

def inicializar_base_datos():
    conexion = sqlite3.connect("taller_mecanico.db")
    cursor = conexion.cursor()

    cursor.execute("PRAGMA foreign_keys = ON;")

    # Tabla TURNO
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS turno (
            turno_id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_turno TEXT NOT NULL,
            hora_inicio TEXT NOT NULL,
            hora_fin TEXT NOT NULL
        );
    """)

    # Tabla EMPLEADO
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS empleado (
            empleado_id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            apellido TEXT NOT NULL,
            documento TEXT NOT NULL UNIQUE,
            pin INTEGER NOT NULL,
            fecha_ingreso TEXT NOT NULL
        );
    """)

    # Tabla ASIGNACION_TURNO
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS asignacion_turno (
            asignacion_id INTEGER PRIMARY KEY AUTOINCREMENT,
            empleado_id INTEGER NOT NULL,
            turno_id INTEGER NOT NULL,
            fecha_desde TEXT NOT NULL,
            fecha_hasta TEXT NOT NULL,
            FOREIGN KEY (empleado_id) REFERENCES empleado(empleado_id),
            FOREIGN KEY (turno_id) REFERENCES turno(turno_id)
        );
    """)

    # Tabla Estado Asistencia (Se agrega un campo de descripción para que el catálogo tenga sentido práctico)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS estado_asistencia (
            estado_id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_estado TEXT NOT NULL
        );
    """)

    # Tabla ASISTENCIA
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS asistencia (
            asistencia_id INTEGER PRIMARY KEY AUTOINCREMENT,
            empleado_id INTEGER NOT NULL,
            fecha TEXT NOT NULL,
            hora_entrada TEXT NOT NULL,
            hora_salida TEXT,
            estado_asistencia INTEGER NOT NULL,
            FOREIGN KEY (empleado_id) REFERENCES empleado(empleado_id),
            FOREIGN KEY (estado_asistencia) REFERENCES estado_asistencia(estado_id)
        );
    """)

    # Tabla JUSTIFICACION
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS justificacion (
            justificacion_id INTEGER PRIMARY KEY AUTOINCREMENT,
            asistencia_id INTEGER NOT NULL,
            motivo TEXT,
            fecha_solicitud TEXT NOT NULL,
            justificado INTEGER NOT NULL, -- 0 para Falso (No), 1 para Verdadero (Sí)
            FOREIGN KEY (asistencia_id) REFERENCES asistencia(asistencia_id)
        );
    """)

    conexion.commit()
    print("Base de datos y tablas creadas exitosamente.")
    return conexion


import sqlite3
from pathlib import Path


def probar_base_datos():
    nombre_db = "taller_mecanico.db"
    
    # 1. Asegurar que partimos de cero para la prueba (opcional)
    if Path(nombre_db).exists():
        Path(nombre_db).unlink()

    # Ejecutamos tu función de inicialización
    inicializar_base_datos()
    
    # --- PRUEBAS DE INSERCIÓN Y CONSULTA ---
    conexion = sqlite3.connect(nombre_db)
    cursor = conexion.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    try:
        # A. Insertar un turno
        cursor.execute("""
            INSERT INTO turno (nombre_turno, hora_inicio, hora_fin)
            VALUES ('Mañana', '08:00:00', '16:00:00');
        """)
        
        # B. Insertar un empleado
        cursor.execute("""
            INSERT INTO empleado (nombre, apellido, documento, fecha_ingreso)
            VALUES ('Carlos', 'Gómez', '35123456', '2025-01-15');
        """)

        # C. Insertar estados de asistencia (catálogo)
        cursor.execute("INSERT INTO estado_asistencia (nombre_estado) VALUES ('Presente');")
        cursor.execute("INSERT INTO estado_asistencia (nombre_estado) VALUES ('Ausente');")

        # D. Registrar una asistencia de prueba
        cursor.execute("""
            INSERT INTO asistencia (empleado_id, fecha, hora_entrada, hora_salida, estado_asistencia)
            VALUES (1, '2026-09-14', '08:05:00', NULL, 1);
        """)

        conexion.commit()
        print("¡Datos de prueba insertados exitosamente!")

        # E. Consultar los datos unidos (Test de relaciones)
        cursor.execute("""
            SELECT e.nombre, e.apellido, a.fecha, a.hora_entrada, ea.nombre_estado
            FROM asistencia a
            JOIN empleado e ON a.empleado_id = e.empleado_id
            JOIN estado_asistencia ea ON a.estado_asistencia = ea.estado_id;
        """)
        
        resultado = cursor.fetchone()
        print(f"\nVerificación de consulta:")
        print(f"Empleado: {resultado[0]} {resultado[1]} | Fecha: {resultado[2]} | Entrada: {resultado[3]} | Estado: {resultado[4]}")

    except sqlite3.Error as e:
        print(f"Error en la base de datos: {e}")
        conexion.rollback()
    finally:
        conexion.close()


if __name__ == "__main__":
    inicializar_base_datos()
    