const API_URL = 'http://127.0.0.1:8000';

document.querySelector('.form-empleado').addEventListener('submit', async (e) => {
    e.preventDefault();

    const datos = {
        dni: document.getElementById('dni').value,
        nombre: document.getElementById('nombre').value,
        apellido: document.getElementById('apellido').value
    };

    try {
        const response = await fetch(`${API_URL}/api/admin/empleados/agregarEmpleado`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(datos)
        });

        // Leemos la respuesta del servidor primero para poder usarla tanto en éxito como en error
        const resultado = await response.json();

        if (!response.ok) {
            // Si FastAPI devuelve un error (ej. HTTPException), mostramos ese detalle
            throw new Error(resultado.detail || 'Error al registrar el empleado');
        }

        // Mostramos el texto exacto que devuelve el return de Python en la alerta
        alert(resultado);
        
        document.querySelector('.form-empleado').reset();

    } catch (error) {
        console.error('Error:', error);
        alert(`No se pudo completar la operación: ${error.message}`);
    }
});