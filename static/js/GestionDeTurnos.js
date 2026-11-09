document.addEventListener("DOMContentLoaded", () => {
    const BASE_URL = 'http://127.0.0.1:8000';
    const selectEmpleado = document.getElementById("select-empleado");
    const selectTurno = document.getElementById("select-turno-id"); // El <select> de turnos
    const formAsignar = document.getElementById("form-asignar-turno");

    // 1. Cargar empleados al <select>
    async function cargarEmpleados() {
        try {
            const response = await fetch(`${BASE_URL}/api/admin/faltas/historial`);
            const resultado = await response.json();
            const registros = resultado.ausencias || [];

            selectEmpleado.innerHTML = `<option value="">Selecciona un empleado...</option>`;
            
            const empleadosUnicos = new Map();
            registros.forEach(item => {
                if (!empleadosUnicos.has(item.dni) && item.dni !== "-") {
                    empleadosUnicos.set(item.dni, item.emplebado_nombre);
                }
            });

            empleadosUnicos.forEach((nombre, dni) => {
                const option = document.createElement("option");
                option.value = dni;
                option.textContent = `${nombre} (DNI: ${dni})`;
                selectEmpleado.appendChild(option);
            });
        } catch (error) {
            console.error("Error al cargar empleados:", error);
        }
    }

    // 2. Cargar turnos reales desde la base de datos al <select>
    async function cargarTurnos() {
        try {
            const response = await fetch(`${BASE_URL}/api/admin/turnos`);
            const resultado = await response.json();
            const turnos = resultado.turnos || [];

            selectTurno.innerHTML = `<option value="">Selecciona un turno...</option>`;

            turnos.forEach(turno => {
                const option = document.createElement("option");
                option.value = turno.turno_id; // El ID real del turno en la BD
                option.textContent = turno.nombre_turno; // Ej: "Mañana", "Tarde", etc.
                selectTurno.appendChild(option);
            });
        } catch (error) {
            console.error("Error al cargar turnos:", error);
        }
    }

    cargarEmpleados();
    cargarTurnos();

    // 3. Manejar el envío del formulario de asignación
    if (formAsignar) {
        formAsignar.addEventListener("submit", async (e) => {
            e.preventDefault();

            const dniSeleccionado = selectEmpleado.value;
            const turnoId = parseInt(selectTurno.value);
            const fechaDesde = document.getElementById("input-fecha-desde").value;
            const fechaHasta = document.getElementById("input-fecha-hasta").value;

            if (!dniSeleccionado || !turnoId) {
                alert("Por favor selecciona un empleado y un turno.");
                return;
            }

            const datosAsignacion = {
                turno_id: turnoId,
                dni: dniSeleccionado,
                fecha_desde: fechaDesde,
                fecha_hasta: fechaHasta
            };

            try {
                const response = await fetch(`${BASE_URL}/api/admin/turnos/asignar`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(datosAsignacion)
                });

                const resultado = await response.json();

                if (response.ok && resultado.success) {
                    alert("¡Turno asignado con éxito!");
                    formAsignar.reset();
                    cargarEmpleados();
                    cargarTurnos();
                } else {
                    alert("Error: " + (resultado.detail || "No se pudo asignar el turno."));
                }
            } catch (error) {
                console.error("Error de red:", error);
                alert("Error al conectar con el servidor.");
            }
        });
    }
});