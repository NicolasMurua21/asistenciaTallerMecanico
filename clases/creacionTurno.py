
def crearTurno(DB, nombre, horaInicio, horaFinal):
    try:
        cursor = DB.cursor()
        cursor.execute(
            "INSERT INTO turno (nombre_turno, hora_inicio, hora_fin) VALUES (?, ?,"
            " ?)",
            (nombre, horaInicio, horaFinal),
        )
        DB.commit()
        return "TURNO CREADO PERFECTAMENTE"
    except:
        return "TURNO NO CREADO"

def creacionEstadoAsistencia(DB, nombre):
 
        cursor = DB.cursor()
        cursor.execute(
            "INSERT INTO estado_asistencia (nombre_estado) VALUES (?)",
            (nombre,),
        )
        DB.commit()
        return "ESTADO CREADO"
    
