

const formulario = document.querySelector("form");

formulario.addEventListener("submit", function(event) {
    event.preventDefault();

    const empleado = formulario.querySelector("select").value;
    const fecha = formulario.querySelector(".date-input input").value;
    const tipo = formulario.querySelector('input[name="absence"]:checked');

    if (empleado === "Seleccionar un empleado...") {
        alert("Seleccione un empleado.");
        return;
    }

    if (fecha === "") {
        alert("Ingrese una fecha.");
        return;
    }

    if (tipo === null) {
        alert("Seleccione un tipo de ausencia.");
        return;
    }

    alert("Ausencia registrada correctamente.");
});




const botonHistorial = document.querySelector(".history-btn");

botonHistorial.addEventListener("click", function() {
    alert("Abriendo historial de ausencias...");
});



const archivo = document.querySelector('input[type="file"]');

archivo.addEventListener("change", function() {
    if (archivo.files.length > 0) {
        const nombreArchivo = archivo.files[0].name;
        alert("Archivo seleccionado: " + nombreArchivo);
    }
});