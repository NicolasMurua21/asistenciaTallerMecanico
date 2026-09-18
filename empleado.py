import sqlite3
#import RegistroAsistencia


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
            return RegistroAsistencia.calcularHorasTrabajadas(resultado[0])
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
      

    def obtenerID(DB, dni = None, pin = None):
        cursor = DB.cursor()

        if pin is not None:
            cursor.execute(
                "SELECT empleado_id FROM empleado WHERE pin = ?", (pin,)
            )
        elif dni is not None:
            cursor.execute(
                "SELECT empleado_id FROM empleado WHERE documento = ?", (dni,)
            )
        else:
            return None 

        resultado = cursor.fetchone()
        if resultado:
            return resultado[0]
        else:
            return None

