from datetime import datetime
import sqlite3


class salidaIntermedia:

    @staticmethod
    def registrar_salida_intermedia(DB, empleado_id):
        cursor = DB.cursor()

        try:
            fecha_actual = datetime.now().strftime("%Y-%m-%d")

            cursor.execute("""
                SELECT asistencia_id, hora_fuera
                FROM asistencia
                WHERE empleado_id = ?
                AND fecha = ?
            """, (empleado_id, fecha_actual))

            asistencia = cursor.fetchone()

            if asistencia is None:
                print("El empleado no tiene una asistencia registrada hoy.")
                return False

            asistencia_id = asistencia[0]
            hora_fuera = asistencia[1]

            # Si hora_fuera ya tiene un valor, significa que ya salió
            if hora_fuera is not None:
                print("El empleado ya tiene una salida intermedia registrada.")
                return False

            hora_actual = datetime.now().strftime("%H:%M:%S")

            # Guardamos la hora en la que salió
            cursor.execute("""
                UPDATE asistencia
                SET hora_fuera = ?
                WHERE asistencia_id = ?
            """, (hora_actual, asistencia_id))

            DB.commit()

            print(f"Salida intermedia registrada a las {hora_actual}.")
            return True

        except sqlite3.Error as error:
            print(f"Error en la base de datos: {error}")
            DB.rollback()
            return False

    @staticmethod
    def registrar_reingreso(DB, empleado_id):
        cursor = DB.cursor()

        try:
            fecha_actual = datetime.now().strftime("%Y-%m-%d")

            cursor.execute("""
                SELECT asistencia_id, hora_fuera
                FROM asistencia
                WHERE empleado_id = ?
                AND fecha = ?
            """, (empleado_id, fecha_actual))

            asistencia = cursor.fetchone()

            if asistencia is None:
                print("El empleado no tiene una asistencia registrada hoy.")
                return False

            asistencia_id = asistencia[0]
            hora_fuera = asistencia[1]

            if hora_fuera is None:
                print("El empleado no tiene una salida intermedia registrada.")
                return False

            hora_actual = datetime.now().strftime("%H:%M:%S")

            hora_salida_fuera = datetime.strptime(hora_fuera, "%H:%M:%S")
            hora_reingreso = datetime.strptime(hora_actual, "%H:%M:%S")

            tiempo_afuerа = hora_reingreso - hora_salida_fuera

            cursor.execute("""
                UPDATE asistencia
                SET hora_fuera = ?
                WHERE asistencia_id = ?
            """, (int(tiempo_afuerа.total_seconds()), asistencia_id))

            DB.commit()

            print(f"Reingreso registrado a las {hora_actual}.")
            print(f"Tiempo afuera: {tiempo_afuerа}")

            return True

        except sqlite3.Error as error:
            print(f"Error en la base de datos: {error}")
            DB.rollback()
            return False