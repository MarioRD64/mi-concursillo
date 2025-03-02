const socket = io();  // Conectar a Socket.IO

let nombreJugador = "";  // Variable global para almacenar el nombre del jugador

// Función para registrar un jugador
function registrarJugador() {
    nombreJugador = document.getElementById("nombreJugador").value.trim();

    // Verificamos si el nombre está vacío
    if (!nombreJugador) {
        alert("❌ Ingresa tu nombre antes de unirte.");
        return;
    }

    // Enviar el nombre al backend para registrar al jugador
    fetch("/registrar", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ nombre: nombreJugador })
    })
    .then(response => response.json())
    .then(data => {
        console.log(data); // Verificar la respuesta del servidor
        if (data.error) {
            alert(data.error); // Si hubo un error, lo mostramos
        } else {
            document.getElementById("registro").style.display = "none"; // Ocultamos la sección de registro
            document.getElementById("unirseSala").style.display = "block"; // Mostramos la sección de unirse a sala
        }
    })
    .catch(error => console.error("❌ Error en el registro:", error)); // En caso de error, lo mostramos
}

// Función para unirse a una sala
function unirseSala() {
    nombreJugador = document.getElementById("nombreJugador").value.trim();
    let sala = document.getElementById("nombreSala").value.trim();

    if (!nombreJugador || !sala) {
        alert("❌ Ingresa tu nombre y el nombre de la sala.");
        return;
    }

    // Enviar el nombre y la sala al backend para unirse
    fetch("/unirse_sala", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ nombre: nombreJugador, sala: sala })
    })
    .then(response => response.json())
    .then(data => {
        console.log(data); // Verificar la respuesta del servidor
        if (data.error) {
            alert(data.error); // Si hubo un error, lo mostramos
        } else {
            alert(data.mensaje);
            document.getElementById("unirseSala").style.display = "none"; // Ocultamos la sección de unir a sala
            document.getElementById("pregunta-container").style.display = "block"; // Mostramos la sección de preguntas
            cargarPregunta(); // Llamamos a la función para cargar la pregunta
        }
    })
    .catch(error => console.error("❌ Error al unirse a la sala:", error)); // En caso de error, lo mostramos
}

// Función para cargar las preguntas
function cargarPregunta() {
    // Llamamos al backend para obtener las preguntas
    fetch("/preguntas")
        .then(response => response.json())
        .then(data => {
            console.log(data); // Verificar que las preguntas están cargando correctamente
            if (data.length > 0) {
                // Seleccionamos una pregunta aleatoria
                let preguntaAleatoria = data[Math.floor(Math.random() * data.length)];
                mostrarPregunta(preguntaAleatoria); // Mostramos la pregunta
            } else {
                console.error("⚠️ No hay preguntas disponibles.");
            }
        })
        .catch
