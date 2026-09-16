// Elementos del HTML
const fechaInicio = document.querySelectorAll(".input")[0];
const fechaFin = document.querySelectorAll(".input")[1];

const grupoEmpleados = document.querySelectorAll("select")[1];

const botonGenerar = document.querySelector(".generate-btn");
const botonHistorial = document.querySelector(".history-btn");

const opciones = document.querySelectorAll(
    ".checkbox-label input"
);



botonGenerar.addEventListener("click", function () {

    if (fechaInicio.value === "" || fechaFin.value === "") {
        alert("Por favor, seleccioná una fecha de inicio y una fecha de fin.");
        return;
    }

    let grupo = grupoEmpleados.value;

    let seleccionadas = [];

    opciones.forEach(function (opcion) {
        if (opcion.checked) {
            seleccionadas.push(opcion.parentElement.textContent.trim());
        }
    });

    alert(
        "Reporte generado correctamente.\n\n" +
        "Desde: " + fechaInicio.value + "\n" +
        "Hasta: " + fechaFin.value + "\n" +
        "Grupo: " + grupo + "\n\n" +
        "Datos incluidos:\n" +
        seleccionadas.join("\n")
    );
});



botonHistorial.addEventListener("click", function () {

    alert("Mostrando historial de exportaciones...");
});