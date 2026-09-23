// Esperar a que el HTML cargue por completo
document.addEventListener("DOMContentLoaded", function () {

    // --- 1. BUSCAR REGISTRO DE ASISTENCIA (GET) ---
    var btnBuscar = document.getElementById("btn-buscar-registro");
    if (btnBuscar) {
        btnBuscar.addEventListener("click", function () {
            var dni = document.getElementById("input-dni") ? document.getElementById("input-dni").value : "";
            var fecha = document.getElementById("input-fecha") ? document.getElementById("input-fecha").value : "";

            if (!dni || !fecha) {
                alert("Por favor, ingrese el DNI del empleado y la fecha.");
                return;
            }

            // Petición a FastAPI para consultar el presentismo
            fetch(`/api/admin/empleados/consultarPresentismo?dni=${dni}&fecha_desde=${fecha}&fecha_hasta=${fecha}`)
                .then(function (response) {
                    if (!response.ok) {
                        throw new Error("No se encontraron registros o el empleado no existe.");
                    }
                    return response.json();
                })
                .then(function (data) {
                    alert("Datos obtenidos con éxito del servidor.");
                    console.log("Respuesta servidor:", data);
                })
                .catch(function (error) {
                    alert("Error: " + error.message);
                });
        });
    }

    // --- 2. GUARDAR MODIFICACIÓN DE ASISTENCIA (PATCH) ---
    var btnGuardar = document.getElementById("btn-guardar-cambios");
    if (btnGuardar) {
        btnGuardar.addEventListener("click", function (e) {
            e.preventDefault(); // Evitar que el formulario recargue la página

            var dni = document.getElementById("input-dni") ? document.getElementById("input-dni").value : "";
            var fecha = document.getElementById("input-fecha") ? document.getElementById("input-fecha").value : "";
            var motivo = document.getElementById("input-motivo") ? document.getElementById("input-motivo").value : "";

            var nuevoIngreso = document.getElementById("input-nuevo-ingreso") ? document.getElementById("input-nuevo-ingreso").value : "";
            var nuevaSalidaInt = document.getElementById("input-nueva-salida-int") ? document.getElementById("input-nueva-salida-int").value : "";
            var nuevoReingreso = document.getElementById("input-nuevo-reingreso") ? document.getElementById("input-nuevo-reingreso").value : "";
            var nuevoEgreso = document.getElementById("input-nuevo-egreso") ? document.getElementById("input-nuevo-egreso").value : "";

            if (!dni || !fecha) {
                alert("Debe ingresar el DNI y la fecha.");
                return;
            }

            if (!motivo.trim()) {
                alert("El motivo de la modificación es obligatorio.");
                return;
            }

            // Armar el objeto JSON con los campos requeridos por app.py
            var camposModificar = [];
            if (nuevoIngreso) camposModificar.push("hora_entrada");
            if (nuevaSalidaInt) camposModificar.push("salida_intermedia");
            if (nuevoReingreso) camposModificar.push("reingreso");
            if (nuevoEgreso) camposModificar.push("hora_salida");

            var datosBody = {
                motivo: motivo,
                hora_entrada: nuevoIngreso,
                salida_intermedia: nuevaSalidaInt,
                reingreso: nuevoReingreso,
                hora_salida: nuevoEgreso,
                camposModificar: camposModificar
            };

            // Petición PATCH al endpoint de FastAPI creado por Nicolás
            fetch(`/api/admin/empleados/${dni}/asistencias/${fecha}`, {
                method: "PATCH",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(datosBody)
            })
            .then(function (response) {
                return response.json().then(function (data) {
                    if (!response.ok) {
                        throw new Error(data.detail || "Error al actualizar los datos.");
                    }
                    return data;
                });
            })
            .then(function (data) {
                alert("¡Modificación guardada con éxito en la base de datos!");
                console.log("Respuesta servidor:", data);
            })
            .catch(function (error) {
                alert("Error: " + error.message);
            });
        });
    }

    // --- 3. EXPORTAR A EXCEL / CSV (GET) ---
    var btnExportar = document.getElementById("btn-exportar");
    if (btnExportar) {
        btnExportar.addEventListener("click", function () {
            var fechaDesde = document.getElementById("input-fecha-desde") ? document.getElementById("input-fecha-desde").value : "";
            var fechaHasta = document.getElementById("input-fecha-hasta") ? document.getElementById("input-fecha-hasta").value : "";

            if (!fechaDesde || !fechaHasta) {
                alert("Debe seleccionar un rango de fechas para exportar.");
                return;
            }

            // Redireccionar directamente para descargar el archivo CSV generado por FastAPI
            window.location.href = `/api/admin/empleados/exportar/${fechaDesde}/${fechaHasta}`;
        });
    }

    // --- 4. BOTÓN CANCELAR Y LIMPIAR ---
    var btnCancelar = document.getElementById("btn-cancelar");
    if (btnCancelar) {
        btnCancelar.addEventListener("click", function () {
            if (document.getElementById("input-nuevo-ingreso")) document.getElementById("input-nuevo-ingreso").value = "";
            if (document.getElementById("input-nueva-salida-int")) document.getElementById("input-nueva-salida-int").value = "";
            if (document.getElementById("input-nuevo-reingreso")) document.getElementById("input-nuevo-reingreso").value = "";
            if (document.getElementById("input-nuevo-egreso")) document.getElementById("input-nuevo-egreso").value = "";
            if (document.getElementById("input-motivo")) document.getElementById("input-motivo").value = "";
        });
    }

    // --- 5. NAVEGACIÓN ---
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