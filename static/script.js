const socket = io();  // Conectar a Socket.IO

// Función para registrar un jugador
function registrarJugador() {
    let nombre = document.getElementById("nombreJugador").value.trim();

    // Verificamos si el nombre está vacío
    if (!nombre) {
        alert("❌ Ingresa tu nombre antes de unirte.");
        return;
    }

    // Enviar el nombre al backend para registrar al jugador
    fetch("/registrar", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ nombre: nombre })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert(data.error); // Si hubo un error, lo mostramos
        } else {
            document.getElementById("registro").style.display = "none"; // Ocultamos la sección de registro
            document.getElementById("pregunta-container").style.display = "block"; // Mostramos la sección de preguntas
            cargarPregunta(); // Llamamos a la función para cargar la pregunta
        }
    })
    .catch(error => console.error("❌ Error en el registro:", error)); // En caso de error, lo mostramos
}

// Función para unirse a una sala
function unirseSala() {
    let nombre = document.getElementById("nombreJugador").value.trim();
    let sala = document.getElementById("nombreSala").value.trim();

    if (!nombre || !sala) {
        alert("❌ Ingresa tu nombre y el nombre de la sala.");
        return;
    }

    // Enviar el nombre y la sala al backend para unirse
    fetch("/unirse_sala", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ nombre: nombre, sala: sala })
    })
    .then(response => response.json())
    .then(data => {
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
            if (data.length > 0) {
                // Seleccionamos una pregunta aleatoria
                let preguntaAleatoria = data[Math.floor(Math.random() * data.length)];
                mostrarPregunta(preguntaAleatoria); // Mostramos la pregunta
            } else {
                console.error("⚠️ No hay preguntas disponibles.");
            }
        })
        .catch(error => console.error("❌ Error al obtener la pregunta:", error)); // Error al obtener preguntas
}

// Función para mostrar la pregunta
function mostrarPregunta(pregunta) {
    document.getElementById("textoPregunta").innerText = pregunta.pregunta;

    let opcionesDiv = document.getElementById("opciones");
    opcionesDiv.innerHTML = ""; // Limpiamos cualquier opción anterior

    // Crear los botones de las opciones
    Object.keys(pregunta.opciones).forEach(opcion => {
        let boton = document.createElement("button");
        boton.innerText = `${opcion}: ${pregunta.opciones[opcion]}`;
        boton.classList.add("boton-opcion"); // Agregamos clase CSS para estilo
        boton.onclick = () => verificarRespuesta(boton, pregunta.opciones[opcion], pregunta.respuesta_correcta);
        opcionesDiv.appendChild(boton);
    });
}

// Función para verificar la respuesta
function verificarRespuesta(boton, seleccion, correcta) {
    let mensaje = document.getElementById("mensaje");

    if (seleccion === correcta) {
        mensaje.innerText = "✅ ¡Correcto!";
        mensaje.style.color = "green";
        boton.classList.add("correcto");
    } else {
        mensaje.innerText = `❌ Incorrecto, la respuesta era: ${correcta}`;
        mensaje.style.color = "red";
        boton.classList.add("incorrecto");
    }

    // Emitir la puntuación al servidor
    socket.emit("actualizar_puntuacion", { nombre: nombreJugador, puntos: seleccion === correcta ? 10 : 0 });

    // Desactivar todos los botones después de responder
    let botones = document.querySelectorAll(".boton-opcion");
    botones.forEach(b => b.disabled = true);
}
