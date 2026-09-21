// Esperar a que el HTML cargue por completo
document.addEventListener("DOMContentLoaded", function () {

    // --- 1. CARGAR LISTA DE EMPLEADOS (DATOS DE PRUEBA) ---
    var selectEmpleado = document.getElementById("select-empleado");

    if (selectEmpleado) {
        var empleados = [
            { id: 1, nombre: "Carlos Murúa", legajo: "M-101", dni: "38.123.456", turno: "Mañana", horario: "08:00 a 16:00" },
            { id: 2, nombre: "Nicolás Gómez", legajo: "M-102", dni: "40.987.654", turno: "Tarde", horario: "12:00 a 20:00" },
            { id: 3, nombre: "Arian González", legajo: "M-103", dni: "35.456.789", turno: "Mañana", horario: "08:00 a 16:00" }
        ];

        // Llenar el combo desplegable
        for (var i = 0; i < empleados.length; i++) {
            var opcion = document.createElement("option");
            opcion.value = empleados[i].id;
            opcion.textContent = empleados[i].nombre + " (Legajo: " + empleados[i].legajo + ")";
            selectEmpleado.appendChild(opcion);
        }

        // Cambio de tarjeta al seleccionar empleado
        selectEmpleado.addEventListener("change", function () {
            var idSeleccionado = parseInt(selectEmpleado.value);
            var cardEmpleado = document.querySelector(".card-empleado");

            var empleadoEncontrado = null;
            for (var j = 0; j < empleados.length; j++) {
                if (empleados[j].id === idSeleccionado) {
                    empleadoEncontrado = empleados[j];
                    break;
                }
            }

            if (empleadoEncontrado) {
                cardEmpleado.innerHTML = 
                    '<div>' +
                        '<h3>' + empleadoEncontrado.nombre + '</h3>' +
                        '<p>DNI: ' + empleadoEncontrado.dni + '</p>' +
                        '<p>Legajo: ' + empleadoEncontrado.legajo + '</p>' +
                    '</div>' +
                    '<div><p><strong>Turno asignado:</strong> ' + empleadoEncontrado.turno + '</p></div>' +
                    '<div><p><strong>Horario turno:</strong> ' + empleadoEncontrado.horario + '</p></div>';
            } else {
                cardEmpleado.innerHTML = 
                    '<div>' +
                        '<h3>Seleccione un empleado</h3>' +
                        '<p>DNI: ---</p>' +
                        '<p>Legajo: ---</p>' +
                    '</div>' +
                    '<div><p><strong>Turno asignado:</strong> ---</p></div>' +
                    '<div><p><strong>Horario turno:</strong> --- a ---</p></div>';
            }
        });
    }

    // --- 2. BOTÓN BUSCAR REGISTRO ---
    var btnBuscar = document.getElementById("btn-buscar-registro");
    if (btnBuscar) {
        btnBuscar.addEventListener("click", function () {
            var empId = selectEmpleado.value;
            var fecha = document.getElementById("input-fecha").value;

            if (empId === "" || fecha === "") {
                alert("Por favor, seleccione un empleado y una fecha.");
                return;
            }

            // Simulación de búsqueda exitosa
            alert("Búsqueda realizada con éxito para la fecha seleccionada.");
        });
    }

    // --- 3. BOTÓN GUARDAR CAMBIOS ---
    var btnGuardar = document.getElementById("btn-guardar-cambios");
    if (btnGuardar) {
        btnGuardar.addEventListener("click", function (e) {
            e.preventDefault(); // Evitar que recargue la página

            var empId = selectEmpleado.value;
            var motivo = document.getElementById("input-motivo").value;

            if (empId === "") {
                alert("Debe seleccionar un empleado.");
                return;
            }

            if (motivo.trim() === "") {
                alert("El motivo de la modificación es obligatorio.");
                return;
            }

            alert("Modificación guardada con éxito.");
        });
    }

    // --- 4. BOTÓN CANCELAR ---
    var btnCancelar = document.getElementById("btn-cancelar");
    if (btnCancelar) {
        btnCancelar.addEventListener("click", function () {
            document.getElementById("input-nuevo-ingreso").value = "";
            document.getElementById("input-nueva-salida-int").value = "";
            document.getElementById("input-nuevo-reingreso").value = "";
            document.getElementById("input-nuevo-egreso").value = "";
            document.getElementById("input-motivo").value = "";
        });
    }

    // --- 5. NAVEGACIÓN ENTRE PANTALLAS ---
    var btnNavAsistencia = document.getElementById("btn-nav-asistencia");
    if (btnNavAsistencia) {
        btnNavAsistencia.addEventListener("click", function () {
            window.location.href = "modificarasistencia.html";
        });
    }

    var btnNavInicio = document.getElementById("btn-nav-inicio");
    if (btnNavInicio) {
        btnNavInicio.addEventListener("click", function () {
            window.location.href = "paneladmin.html";
        });
    }
});