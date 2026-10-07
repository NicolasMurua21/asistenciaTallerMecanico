import sqlite3
from datetime import datetime


def registrarIngreso(DB, empleado_id):

    cursor = DB.cursor()

    fecha_actual = datetime.now().strftime("%Y-%m-%d")
    hora_actual = datetime.now().strftime("%H:%M:%S")

    cursor.execute(
        """
        SELECT asistencia_id
        FROM asistencia
        WHERE empleado_id = ? AND fecha = ?
        """,
        (empleado_id, fecha_actual)
    )

    asistencia = cursor.fetchone()

    if asistencia is not None:
        return "YA REGISTRO EL INGRESO HOY"

    cursor.execute(
        """
        INSERT INTO asistencia
        (empleado_id, fecha, hora_entrada, hora_salida, estado_asistencia)
        VALUES (?, ?, ?, ?, ?)
        """,
        (empleado_id, fecha_actual, hora_actual, None, 1)
    )

    DB.commit()

    return "INGRESO REGISTRADO"


def registrarSalida(DB, empleado_id):

    cursor = DB.cursor()

    fecha_actual = datetime.now().strftime("%Y-%m-%d")
    hora_actual = datetime.now().strftime("%H:%M:%S")

    cursor.execute(
        """
        SELECT asistencia_id, hora_entrada, hora_salida
        FROM asistencia
        WHERE empleado_id = ? AND fecha = ?
        """,
        (empleado_id, fecha_actual)
    )

    asistencia = cursor.fetchone()

    if asistencia is None:
        return "NO HAY INGRESO REGISTRADO HOY"

    asistencia_id = asistencia[0]
    hora_entrada = asistencia[1]
    hora_salida = asistencia[2]

    if hora_salida is not None:
        return "YA REGISTRO LA SALIDA"

    cursor.execute(
        """
        UPDATE asistencia
        SET hora_salida = ?
        WHERE asistencia_id = ?
        """,
        (hora_actual, asistencia_id)
    )

    DB.commit()

    return "SALIDA REGISTRADA"


def calcularHorasTrabajadas(DB, empleado_id):

    cursor = DB.cursor()

    cursor.execute(
        """
        SELECT hora_entrada, hora_salida
        FROM asistencia
        WHERE empleado_id = ?
        AND hora_entrada IS NOT NULL
        AND hora_salida IS NOT NULL
        """,
        (empleado_id,)
    )

    asistencias = cursor.fetchall()

    total_segundos = 0

    for asistencia in asistencias:
        hora_entrada = asistencia[0]
        hora_salida = asistencia[1]

        try:
            entrada = datetime.strptime(hora_entrada, "%H:%M:%S")
            salida = datetime.strptime(hora_salida, "%H:%M:%S")

            diferencia = salida - entrada
            total_segundos += diferencia.total_seconds()

        except ValueError:
            pass

    return round(total_segundos / 3600, 2)