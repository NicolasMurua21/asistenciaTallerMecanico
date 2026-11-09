console.log("¡El archivo presentismo.js se ha cargado correctamente!");

document.addEventListener("DOMContentLoaded", () => {
    const BASE_URL = 'http://127.0.0.1:8000';
    
    const tbody = document.getElementById("tabla-dashboard-body");
    const inputBuscar = document.getElementById("input-buscar");
    const selectEstado = document.getElementById("select-estado");
    const selectTurno = document.getElementById("select-turno");
    const textoMostrando = document.getElementById("texto-mostrando");

    const elPresentes = document.getElementById("contador-presentes");
    const elAusentes = document.getElementById("contador-ausentes");
    const elSalidas = document.getElementById("contador-salidas");
    const elTotal = document.getElementById("contador-total");

    let todosLosRegistros = [];

    async function cargarDashboard() {
        console.log("Iniciando petición fetch al backend (/api/admin/faltas/historial)...");
        try {
            const response = await fetch(`${BASE_URL}/api/admin/faltas/historial`);
            const resultado = await response.json();

            todosLosRegistros = Array.isArray(resultado) ? resultado : (resultado.ausencias || []);
            console.log("Registros obtenidos:", todosLosRegistros);
            
            aplicarFiltrosYRenderizar();

        } catch (error) {
            console.error("Error crítico al conectar con la API:", error);
            if (tbody) {
                tbody.innerHTML = `<tr><td colspan="6" style="text-align: center; color: #ff6b6b; padding: 20px;">Error al conectar con el servidor backend.</td></tr>`;
            }
        }
    }

    function renderizarTabla(registros) {
        if (!tbody) {
            console.error("No se encontró el elemento tbody en el DOM");
            return;
        }
        
        tbody.innerHTML = "";

        if (registros.length === 0) {
            tbody.innerHTML = `<tr><td colspan="6" style="text-align: center; padding: 20px; color: white;">No se encontraron registros.</td></tr>`;
            if (textoMostrando) textoMostrando.textContent = "Mostrando 0 empleados";
            return;
        }

        registros.forEach((item, index) => {
            const tr = document.createElement("tr");

            tr.innerHTML = `
                <td style="padding: 12px 15px; color: white; border-bottom: 1px solid rgba(255,255,255,0.1);">${index + 1}</td>
                <td style="padding: 12px 15px; color: white; border-bottom: 1px solid rgba(255,255,255,0.1);">${item.emplebado_nombre || "Desconocido"}</td>
                <td style="padding: 12px 15px; color: white; border-bottom: 1px solid rgba(255,255,255,0.1);">${item.dni || "-"}</td>
                <td style="padding: 12px 15px; color: white; border-bottom: 1px solid rgba(255,255,255,0.1);">${item.turno || "-"}</td>
                <td style="padding: 12px 15px; color: white; border-bottom: 1px solid rgba(255,255,255,0.1);">${item.fecha || "-"}</td>
                <td style="padding: 12px 15px; color: white; border-bottom: 1px solid rgba(255,255,255,0.1);">${item.estado || "Ausente"}</td>
            `;
            tbody.appendChild(tr);
        });

        if (textoMostrando) {
            textoMostrando.textContent = `Mostrando ${registros.length} empleados`;
        }
    }

    function actualizarTarjetas(registros) {
        let presentes = 0;
        let ausentes = 0;
        let salidas = 0;

        registros.forEach(item => {
            const est = (item.estado || "").toLowerCase();
            if (est.includes("presente")) presentes++;
            else if (est.includes("salida")) salidas++;
            else ausentes++;
        });

        if (elPresentes) elPresentes.textContent = presentes;
        if (elAusentes) elAusentes.textContent = ausentes;
        if (elSalidas) elSalidas.textContent = salidas;
        if (elTotal) elTotal.textContent = registros.length;
    }

    function aplicarFiltrosYRenderizar() {
        const textoBusqueda = inputBuscar ? inputBuscar.value.toLowerCase() : "";
        const estadoFiltro = selectEstado ? selectEstado.value : "";
        const turnoFiltro = selectTurno ? selectTurno.value : "";

        const filtrados = todosLosRegistros.filter(item => {
            const nombre = (item.emplebado_nombre || "").toLowerCase();
            const dni = (item.dni || "").toString().toLowerCase();
            const estado = item.estado || "";
            const turno = item.turno || "";

            const coincideTexto = nombre.includes(textoBusqueda) || dni.includes(textoBusqueda);
            
            // Si el selector de estado dice "Todos los estados" o está vacío, pasa
            const coincideEstado = !estadoFiltro || estadoFiltro === "Todos los estados" || estado.toLowerCase().includes(estadoFiltro.toLowerCase());
            
            const coincideTurno = !turnoFiltro || turnoFiltro === "Turno actual" || turno.toLowerCase().includes(turnoFiltro.toLowerCase());

            return coincideTexto && coincideEstado && coincideTurno;
        });

        renderizarTabla(filtrados);
        actualizarTarjetas(todosLosRegistros);
    }

    if (inputBuscar) inputBuscar.addEventListener("input", aplicarFiltrosYRenderizar);
    if (selectEstado) selectEstado.addEventListener("change", aplicarFiltrosYRenderizar);
    if (selectTurno) selectTurno.addEventListener("change", aplicarFiltrosYRenderizar);

    cargarDashboard();
});