document.addEventListener('DOMContentLoaded', () => {
    const pinInput = document.getElementById('pinInput');
    const API_URL = 'http://127.0.0.1:8000';

    async function enviarFichaje(rutaEndpoint) {
        const pin = pinInput.value.trim();

        if (!pin) {
            alert('Por favor, ingresá tu DNI o PIN.');
            pinInput.focus();
            return;
        }

        // Armamos la URL completa: http://127.0.0.1:8000/api/asistencia/empleados/.../?pin=VALOR
        const urlCompleta = `${API_URL}${rutaEndpoint}?pin=${encodeURIComponent(pin)}`;

        try {
            const response = await fetch(urlCompleta, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            // 'data' aquí recibe exactamente el texto que devuelve el return de Python (ej: "INGRESO REGISTRADO")
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Error al procesar la asistencia.');
            }

            // CAMBIO: Mostramos el texto exacto que envió Python en lugar de un texto fijo
            alert(data); 
            
            pinInput.value = ''; // Limpiamos el input
            pinInput.focus();
        } catch (error) {
            console.error('Error en la petición:', error);
            alert(`No se pudo registrar: ${error.message}`);
        }
    }

    // 1. Botón Ingreso
    document.getElementById('btnRegistrarIngreso')?.addEventListener('click', () => {
        enviarFichaje('/api/asistencia/empleados/ingreso');
    });

    // 2. Botón Egreso / Salida
    document.getElementById('btnRegistrarEgreso')?.addEventListener('click', () => {
        enviarFichaje('/api/asistencia/empleados/salida');
    });

    // 3. Botón Salida Intermedia
    document.getElementById('btnSalidaIntermedia')?.addEventListener('click', () => {
        enviarFichaje('/api/asistencia/empleados/salidaIntermedia');
    });

    // 4. Botón Reingreso
    document.getElementById('btnReingreso')?.addEventListener('click', () => {
        enviarFichaje('/api/asistencia/empleados/reingreso');
    });
});