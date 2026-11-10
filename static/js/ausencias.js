document.addEventListener("DOMContentLoaded", () => {
    const BASE_URL = 'http://127.0.0.1:8000';

    // --- 1. CARGAR EMPLEADOS EN LOS SELECTS ---
    const selectEmpleado = document.getElementById("select-empleado");
    const selectFiltroHistorial = document.getElementById("select-filtro-historial");

    async function cargarEmpleados() {
        try {
            const response = await fetch(`${BASE_URL}/api/admin/empleados`);
            const data = await response.json();
            const lista = Array.isArray(data) ? data : (data.empleados || []);

            let optionsHTML = '<option value="">Seleccionar un empleado...</option>';
            let optionsHistorialHTML = '<option value="">-- Ver historial completo (Todos los empleados) --</option>';

            lista.forEach(emp => {
                const optText = `${emp.apellido}, ${emp.nombre}`;
                optionsHTML += `<option value="${emp.empleado_id}">${optText}</option>`;
                optionsHistorialHTML += `<option value="${emp.empleado_id}">${optText}</option>`;
            });

            // Llenamos el select de registro si existe
            if (selectEmpleado) {
                selectEmpleado.innerHTML = optionsHTML;
            }

            // Llenamos el select del historial si existe en el HTML
            if (selectFiltroHistorial) {
                selectFiltroHistorial.innerHTML = optionsHistorialHTML;
            }

        } catch (error) {
            console.error("Error al cargar empleados:", error);
        }
    }

    cargarEmpleados();

    // --- 2. GESTIÓN VISUAL DE LOS BOTONES DE AUSENCIA ---
    const opcioneTipo = document.querySelectorAll(".type-option");
    let valorJustificadaSeleccionado = null; 

    opcioneTipo.forEach(opcion => {
        opcion.addEventListener("click", () => {
            opcioneTipo.forEach(opt => opt.classList.remove("selected"));
            opcion.classList.add("selected");

            const radio = opcion.querySelector("input[type='radio']");
            if (radio) radio.checked = true;

            valorJustificadaSeleccionado = opcion.getAttribute("data-value") === "true";
        });
    });

    // --- 3. REGISTRAR AUSENCIA ---
    const form = document.querySelector("form");
    
    if (form) {
        form.addEventListener("submit", async (e) => {
            e.preventDefault();

            if (!selectEmpleado) return;

            const empleadoId = selectEmpleado.value;
            const inputFecha = document.getElementById("input-fecha");
            const fechaSeleccionada = inputFecha ? inputFecha.value : "";
            const textareaMotivo = form.querySelector("textarea");
            const motivo = textareaMotivo ? textareaMotivo.value : "";

            if (valorJustificadaSeleccionado === null) {
                alert("Por favor seleccione si la ausencia es Justificada o Injustificada.");
                return;
            }

            if (!empleadoId) {
                alert("Por favor seleccione un empleado.");
                return;
            }

            if (!fechaSeleccionada) {
                alert("Por favor seleccione una fecha.");
                return;
            }

            const datosAusencia = {
                empleado_id: parseInt(empleadoId),
                fecha: fechaSeleccionada,
                justificada: valorJustificadaSeleccionado,
                motivo: motivo || "",
                tipo: "Inasistencia"
            };

            try {
                const response = await fetch(`${BASE_URL}/api/admin/faltas/registrar`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(datosAusencia)
                });

                const resultado = await response.json();

                if (response.ok && resultado.success) {
                    alert("¡Ausencia registrada con éxito!");
                    location.reload();
                } else {
                    alert("Atención: " + (resultado.detail || "No se pudo registrar la ausencia."));
                }

            } catch (error) {
                console.error("Error de red:", error);
                alert("Hubo un error al conectar con el servidor.");
            }
        });
    }

    // --- 4. HISTORIAL DE AUSENCIAS ---
    const tbodyHistorial = document.getElementById("tabla-historial-body") || document.querySelector("tbody");

    async function cargarHistorial(empleadoId = "") {
        if (!tbodyHistorial) {
            console.warn("No se encontró el tbody del historial en el DOM.");
            return;
        }

        try {
            let url = `${BASE_URL}/api/admin/faltas/historial`;
            if (empleadoId) {
                url += `?empleado_id=${empleadoId}`;
            }

            console.log("Haciendo fetch a:", url);

            const response = await fetch(url);
            const resultado = await response.json();

            console.log("Datos recibidos del historial:", resultado);

            const ausencias = Array.isArray(resultado) ? resultado : (resultado.ausencias || resultado.data || []);

            tbodyHistorial.innerHTML = "";

            if (ausencias.length === 0) {
                tbodyHistorial.innerHTML = `<tr><td colspan="5" style="text-align: center; padding: 15px;">No hay registros disponibles.</td></tr>`;
                return;
            }

            ausencias.forEach((item, index) => {
                const tr = document.createElement("tr");
                
                const nombreEmpleado = item.emplebado_nombre || item.nombre_empleado || `${item.apellido || ''}, ${item.nombre || ''}`;
                const tipoRegistro = item.estado || "Ausente";

                // Si es una asistencia o el estado no es falta/ausencia, ponemos un guion "-"
                let estadoBadge = "-";
                
                if (tipoRegistro.toLowerCase().includes("ausente") || tipoRegistro.toLowerCase().includes("falta")) {
                    estadoBadge = item.justificada 
                        ? '<span style="color: #2e7d32; font-weight: bold;">Justificada</span>' 
                        : '<span style="color: #c62828; font-weight: bold;">Injustificada</span>';
                }

                tr.innerHTML = `
                    <td style="padding: 10px;">${index + 1}</td>
                    <td style="padding: 10px;">${nombreEmpleado}</td>
                    <td style="padding: 10px;">${item.fecha}</td>
                    <td style="padding: 10px;">${tipoRegistro}</td>
                    <td style="padding: 10px;">${estadoBadge}</td>
                `;
                tbodyHistorial.appendChild(tr);
            });

        } catch (error) {
            console.error("Error al cargar el historial:", error);
        }
    }

    // 1. Cargar el historial completo al abrir la página automáticamente
    cargarHistorial();

    // 2. Escuchar el cambio en el select del filtro para actualizar al instante
    if (selectFiltroHistorial) {
        selectFiltroHistorial.addEventListener("change", (e) => {
            const idSeleccionado = e.target.value;
            console.log("Cambió el filtro de historial. Empleado ID:", idSeleccionado);
            cargarHistorial(idSeleccionado);
        });
    }
});