import sqlite3

class empleado:
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


    def validarPin():

        pass

    def consultarHoras():
        pass
