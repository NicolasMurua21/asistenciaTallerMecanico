import sqlite3
import ReporteAsistencia


class Empleado:
    dni : str
    nombre : str
    apellido : str
    pin : int

    def __init__(self, dni, nombre, apellido, pin):
        self.dni = dni
        self.nombre = nombre
        self.apellido = apellido
        self.pin = pin

    @classmethod
    def identificarPorDni(cls, DB, dniBuscar):
        cursor = DB.cursor()
        cursor.execute(
            "SELECT documento, nombre, apellido, pin FROM empleado WHERE documento = ?",
          (dniBuscar,),
        )
        resultado = cursor.fetchone()
        if resultado:
            return cls(resultado[0], resultado[1], resultado[2], resultado[3])
        else:
            return None

    @classmethod
    def validarPin(cls, DB, pin):
        cursor = DB.cursor()
        cursor.execute(
            "SELECT documento, nombre, apellido, pin FROM empleado WHERE pin = ?",
            (pin,),
        )
        resultado = cursor.fetchone()
        if resultado:
            return cls(resultado[0], resultado[1], resultado[2], resultado[3])
        else:
            return None


    def consultarHoras(DB, pin):
        cursor = DB.cursor()
        cursor.execute(
            "SELECT empleado_id FROM empleado WHERE pin = ?",
            (pin,),
        )
        resultado = cursor.fetchone()

        if resultado:
            return ReporteAsistencia.consultar(resultado[0])
        else:
            return None
        
    @classmethod
    def registrarNuevo(cls, DB, dni, nombre, apellido, pin):
      try:
        cursor = DB.cursor()
        cursor.execute(
            "INSERT INTO empleado (documento, nombre, apellido, pin, fecha_ingreso) VALUES (?, ?,"
            " ?, ?, DATE('now'))",
            (dni, nombre, apellido, pin),
        )
        DB.commit()

        return cls(dni, nombre, apellido, pin)
      except:
          print("YA EXISTE")
          return None


