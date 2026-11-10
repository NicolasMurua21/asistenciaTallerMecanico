document.addEventListener("DOMContentLoaded", () => {
    const BASE_URL = 'http://127.0.0.1:8000';
    const selectEmpleado = document.getElementById("select-empleado");
    const selectEstado = document.getElementById("select-nuevo-estado");
    const btnGuardar = document.getElementById("btn-guardar-cambios");

    // 1. Cargar empleados en el select al iniciar la página
    async function cargarEmpleados() {
        try {
            const response = await fetch(`${BASE_URL}/api/admin/faltas/historial`);
            const resultado = await response.json();
            const registros = resultado.ausencias || [];

            selectEmpleado.innerHTML = `<option value="">Seleccionar un empleado...</option>`;
            
            const empleadosUnicos = new Map();
            registros.forEach(item => {
                if (!empleadosUnicos.has(item.dni) && item.dni && item.dni !== "-") {
                    empleadosUnicos.set(item.dni, item.emplebado_nombre);
                }
            });

            empleadosUnicos.forEach((nombreCompleto, dni) => {
                const option = document.createElement("option");
                option.value = dni;
                option.textContent = `${nombreCompleto} (DNI: ${dni})`;
                selectEmpleado.appendChild(option);
            });

        } catch (error) {
            console.error("Error al cargar la lista de empleados:", error);
        }
    }

    // 2. Cargar los estados disponibles dinámicamente desde la base de datos
    async function cargarEstados() {
        try {
            const response = await fetch(`${BASE_URL}/api/admin/estados`);
            const resultado = await response.json();
            
            // Accedemos correctamente al array dentro de la propiedad 'estados'
            const estados = resultado.estados || []; 

            if (selectEstado) {
                selectEstado.innerHTML = `<option value="">Sin cambios en el estado...</option>`;
                estados.forEach(est => {
                    const option = document.createElement("option");
                    option.value = est.id; // Guardamos el ID numérico del estado
                    option.textContent = est.nombre; // Mostramos el nombre ("Presente", "Ausente", etc.)
                    selectEstado.appendChild(option);
                });
            }
        } catch (error) {
            console.error("Error al cargar los estados de asistencia:", error);
        }
    }

    cargarEmpleados();
    cargarEstados();

    // 3. Manejar el evento click del botón Guardar Cambios
    if (btnGuardar) {
        btnGuardar.addEventListener("click", async (e) => {
            e.preventDefault();

            const dni = selectEmpleado.value;
            const fechaEmpleado = document.getElementById("input-fecha").value;
            const motivo = document.getElementById("input-motivo").value.trim();
            const nuevoEstado = selectEstado ? selectEstado.value : "";

            if (!dni) {
                alert("Por favor selecciona un empleado.");
                return;
            }

            if (!fechaEmpleado) {
                alert("Por favor selecciona una fecha.");
                return;
            }

            if (!motivo) {
                alert("El motivo de la modificación es obligatorio.");
                return;
            }

            // Preparamos el payload y el array de campos que espera tu backend
            const camposModificar = [];
            const payload = {
                motivo: motivo
            };

            // Mapeo de los inputs de horarios de la tabla
            const mapeoCampos = [
                { inputId: "input-nuevo-ingreso", campoBackend: "hora_entrada" },
                { inputId: "input-nueva-salida-int", campoBackend: "salida_intermedia" },
                { inputId: "input-nuevo-reingreso", campoBackend: "reingreso" },
                { inputId: "input-nuevo-egreso", campoBackend: "hora_salida" }
            ];

            mapeoCampos.forEach(item => {
                const valorInput = document.getElementById(item.inputId)?.value;
                if (valorInput) {
                    camposModificar.push(item.campoBackend);
                    payload[item.campoBackend] = valorInput;
                }
            });

            // Si se seleccionó un nuevo estado, lo incluimos en la modificación
            // Busca esto en tu main.js y modifícalo:
            if (nuevoEstado) {
                camposModificar.push("estado_asistencia"); // <-- Debe ser exactamente estado_asistencia
                payload.estado_asistencia = nuevoEstado;    // <-- Y aquí también estado_asistencia
            }

            if (camposModificar.length === 0) {
                alert("Debes modificar al menos un horario o cambiar el estado.");
                return;
            }

            payload.camposModificar = camposModificar;

            // 4. Ejecutar el fetch con método PATCH hacia tu endpoint
            try {
                const response = await fetch(`${BASE_URL}/api/admin/empleados/${dni}/asistencias/${fechaEmpleado}`, {
                    method: "PATCH",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify(payload)
                });

                const resultado = await response.json();

                if (response.ok) {
                    alert("¡Modificación guardada con éxito!");
                    location.reload();
                } else {
                    alert("Error: " + (resultado.detail || "No se pudo procesar la modificación."));
                }

            } catch (error) {
                console.error("Error de red:", error);
                alert("Error al conectar con el servidor.");
            }
        });
    }
});