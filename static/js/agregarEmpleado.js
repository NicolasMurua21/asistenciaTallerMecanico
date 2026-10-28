
const API_URL = 'http://127.0.0.1:8000';

document.querySelector('.form-empleado').addEventListener('submit', async (e) => {
    e.preventDefault();

    const datos = {
        dni: document.getElementById('dni').value,
        nombre: document.getElementById('nombre').value,
        apellido: document.getElementById('apellido').value
    };

    try {
        // Usás la variable para armar la URL completa
        const response = await fetch(`${API_URL}/api/admin/empleados/agregarEmpleado`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(datos)
        });

        if (!response.ok) {
            throw new Error('Error al registrar el empleado');
        }

        const resultado = await response.json();
        
        alert('¡Empleado añadido con éxito!');
        document.querySelector('.form-empleado').reset();

    } catch (error) {
        console.error('Error:', error);
        alert('No se pudo completar la operación.');
    }
});