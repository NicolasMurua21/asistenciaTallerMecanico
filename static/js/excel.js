const API_URL = 'http://127.0.0.1:8000';

document.addEventListener('DOMContentLoaded', () => {
    const btnGenerar = document.getElementById('btn-generar-excel');
    const fechaInicioInput = document.getElementById('fecha-inicio');
    const fechaFinInput = document.getElementById('fecha-fin');

    if (!btnGenerar || !fechaInicioInput || !fechaFinInput) {
        console.error('No se encontraron todos los elementos necesarios en el DOM.');
        return;
    }

    btnGenerar.addEventListener('click', async (e) => {
        e.preventDefault();

        const fechaDesde = fechaInicioInput.value;
        const fechaHasta = fechaFinInput.value;

        if (!fechaDesde || !fechaHasta) {
            alert('Por favor, selecciona ambas fechas.');
            return;
        }

        const textoOriginal = btnGenerar.innerHTML;
        btnGenerar.disabled = true;
        btnGenerar.innerHTML = '▣ Generando reporte...';

        try {
            // Aquí combinamos API_URL con tu endpoint
            const url = `${API_URL}/api/admin/empleados/exportar/${fechaDesde}/${fechaHasta}`;

            const response = await fetch(url, {
                method: 'GET',
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || 'No se pudo generar el archivo');
            }

            const blob = await response.blob();

            const disposition = response.headers.get('Content-Disposition');
            let filename = `reporte_empleados_${fechaDesde}_al_${fechaHasta}.csv`;
            if (disposition && disposition.includes('filename=')) {
                const match = disposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
                if (match && match[1]) {
                    filename = match[1].replace(/['"]/g, '');
                }
            }

            const downloadUrl = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = downloadUrl;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            
            a.remove();
            window.URL.revokeObjectURL(downloadUrl);

        } catch (error) {
            console.error('Error al exportar:', error);
            alert(`Error: ${error.message}`);
        } finally {
            btnGenerar.disabled = false;
            btnGenerar.innerHTML = textoOriginal;
        }
    });
});