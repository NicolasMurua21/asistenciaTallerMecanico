import sqlite3
from datetime import datetime


def registrar_salida_intermedia(documento):
    conexion = sqlite3.connect("taller_mecanico.db")
    cursor = conexion.cursor()

    try:
        
        cursor.execute("""
            SELECT empleado_id, nombre, apellido
            FROM empleado
            WHERE documento = ?
        """, (documento,))

        empleado = cursor.fetchone()

        if empleado is None:
            print("No se encontró un empleado con ese DNI.")
            return False

        empleado_id = empleado[0]

        
        fecha_actual = datetime.now().strftime("%Y-%m-%d")

        cursor.execute("""
            SELECT asistencia_id, hora_salida
            FROM asistencia
            WHERE empleado_id = ?
            AND fecha = ?
        """, (empleado_id, fecha_actual))

        asistencia = cursor.fetchone()

        if asistencia is None:
            print("El empleado no tiene una asistencia registrada hoy.")
            return False

        asistencia_id = asistencia[0]
        hora_salida = asistencia[1]

        
        if hora_salida is not None:
            print("El empleado ya registró su salida.")
            return False

        
        hora_actual = datetime.now().strftime("%H:%M:%S")

        cursor.execute("""
            UPDATE asistencia
            SET hora_fuera = ?
            WHERE asistencia_id = ?
        """, (hora_actual, asistencia_id))

        conexion.commit()

        print(
            f"Salida intermedia registrada para "
            f"{empleado[1]} {empleado[2]} a las {hora_actual}."
        )

        return True

    except sqlite3.Error as error:
        print(f"Error en la base de datos: {error}")
        conexion.rollback()
        return False

    finally:
        conexion.close()


if __name__ == "__main__":
    documento = input("Ingrese el DNI del empleado: ")

    registrar_salida_intermedia(documento)

