document.addEventListener("DOMContentLoaded", () => {
    const BASE_URL = "http://127.0.0.1:8000"; // Ajustá el puerto si es necesario

    const formAlta = document.querySelector(".form-empleado");
    const selectEmpleadoEstado = document.getElementById("select-empleado-estado");
    const selectNuevoEstado = document.getElementById("select-nuevo-estado-emp");
    const btnGuardarEstado = document.getElementById("btn-guardar-estado");

    // 1. Función para cargar la lista de empleados en el selector
    async function cargarEmpleados() {
        try {
            const response = await fetch(`${BASE_URL}/api/admin/empleados`);
            const resultado = await response.json();
            
            const empleados = resultado.empleados || resultado;
            console.log("Empleados cargados:", empleados); // <-- Revisa esto en la consola del navegador (F12)

            if (selectEmpleadoEstado) {
                selectEmpleadoEstado.innerHTML = `<option value="">Seleccione un empleado...</option>`;
                empleados.forEach(emp => {
                    const option = document.createElement("option");
                    // Asegúrate de usar la clave exacta que devuelve tu backend (ej: emp.empleado_id o emp.id)
                    option.value = emp.empleado_id; 
                    option.textContent = `${emp.apellido}, ${emp.nombre}`;
                    selectEmpleadoEstado.appendChild(option);
                });
            }
        } catch (error) {
            console.error("Error al cargar los empleados:", error);
        }
    }

    // Ejecutar al cargar la página
    cargarEmpleados();

    // 2. Lógica para dar de alta un nuevo empleado (formulario superior)
    if (formAlta) {
        formAlta.addEventListener("submit", async (e) => {
            e.preventDefault();

            const dni = document.getElementById("dni").value.trim();
            const nombre = document.getElementById("nombre").value.trim();
            const apellido = document.getElementById("apellido").value.trim();

            if (!dni || !nombre || !apellido) {
                alert("Por favor, completa todos los campos.");
                return;
            }

            try {
                const response = await fetch(`${BASE_URL}/api/admin/empleados`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({ dni, nombre, apellido })
                });

                const resultado = await response.json();

                if (response.ok) {
                    alert(resultado.mensaje || "Empleado registrado con éxito");
                    formAlta.reset();
                    cargarEmpleados(); // Recargamos el selector de empleados
                } else {
                    alert(resultado.detail || "Error al registrar empleado");
                }
            } catch (error) {
                console.error("Error en la petición de alta:", error);
                alert("No se pudo conectar con el servidor.");
            }
        });
    }

    // 3. Lógica para enviar el PATCH al cambiar el estado (Activo / Inactivo)
    if (btnGuardarEstado) {
        btnGuardarEstado.addEventListener("click", async () => {
            const dniSeleccionado = selectEmpleadoEstado.value;
            const nuevoEstadoValor = selectNuevoEstado.value; // "1" o "0"

            if (!dniSeleccionado) {
                alert("Por favor, seleccioná un empleado de la lista.");
                return;
            }

            // Convertimos a booleano (true para Activo, false para Inactivo)
            const activoBoolean = nuevoEstadoValor === "1";

            try {
                const response = await fetch(`${BASE_URL}/api/admin/empleados/${dniSeleccionado}/estado`, {
                    method: "PATCH",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({ activo: activoBoolean })
                });

                const resultado = await response.json();

                if (response.ok) {
                    alert(resultado.mensaje || "Estado actualizado correctamente.");
                } else {
                    alert(resultado.detail || "Error al actualizar el estado.");
                }
            } catch (error) {
                console.error("Error en la petición de estado:", error);
                alert("No se pudo conectar con el servidor.");
            }
        });
    }
});