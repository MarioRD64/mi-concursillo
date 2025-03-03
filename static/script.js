

let nombreJugador = '';
let codigoSala = '';

// Función para registrar un jugador
function registrarJugador() {
    nombreJugador = document.getElementById("nombreJugador").value.trim();

    if (!nombreJugador) {
        alert("❌ Ingresa tu nombre antes de unirte.");
        return;
    }

    fetch("/registrar", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ nombre: nombreJugador })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
        } else {
            document.getElementById("registro").style.display = "none";
            document.getElementById("unirseSala").style.display = "block";
        }
    })
    .catch(error => console.error("❌ Error en el registro:", error));
}

// Función para crear una sala
function crearSala() {
    const codigo = generarCodigoSala();
    codigoSala = codigo;

    // Crear la sala en el backend
    fetch("/crear_sala", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ nombre: nombreJugador, sala: codigo })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
        } else {
            // Mostrar sala de espera
            document.getElementById("unirseSala").style.display = "none";
            document.getElementById("salaEspera").style.display = "block";
            actualizarJugadoresSala(data.jugadores);
        }
    })
    .catch(error => console.error("❌ Error al crear la sala:", error));
}

// Función para unirse a una sala
function unirseSala() {
    const sala = document.getElementById("nombreSala").value.trim();

    if (!sala || !nombreJugador) {
        alert("❌ Ingresa el nombre de la sala.");
        return;
    }

    fetch("/unirse_sala", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ nombre: nombreJugador, sala: sala })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
        } else {
            // Unirse a la sala y actualizar la pantalla
            document.getElementById("unirseSala").style.display = "none";
            document.getElementById("salaEspera").style.display = "block";
            actualizarJugadoresSala(data.jugadores);
        }
    })
    .catch(error => console.error("❌ Error al unirse a la sala:", error));
}

// Actualiza la lista de jugadores en la sala
function actualizarJugadoresSala(jugadores) {
    let listaJugadores = document.getElementById("jugadoresSala");
    listaJugadores.innerHTML = '';

    jugadores.forEach(jugador => {
        let jugadorDiv = document.createElement("div");
        jugadorDiv.innerText = jugador;
        listaJugadores.appendChild(jugadorDiv);
    });

    // Si soy el creador de la sala, puedo iniciar el juego
    if (jugadores[0] === nombreJugador) {
        document.getElementById("iniciarJuego").style.display = "block";
    }
}

// Generar un código aleatorio para la sala
function generarCodigoSala() {
    const caracteres = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let codigo = '';
    for (let i = 0; i < 6; i++) {
        codigo += caracteres.charAt(Math.floor(Math.random() * caracteres.length));
    }
    return codigo;
}

// Función para iniciar el juego cuando haya suficientes jugadores
function iniciarJuego() {
 
}



// Función para cargar una pregunta
function cargarPregunta() {
    fetch("/preguntas")
        .then(response => response.json())
        .then(data => {
            let preguntaAleatoria = data[Math.floor(Math.random() * data.length)];
            mostrarPregunta(preguntaAleatoria);
        });
}

function mostrarPregunta(pregunta) {
    document.getElementById("textoPregunta").innerText = pregunta.pregunta;

    let opcionesDiv = document.getElementById("opciones");
    opcionesDiv.innerHTML = ""; // Limpiar opciones previas

    Object.keys(pregunta.opciones).forEach(opcion => {
        let boton = document.createElement("button");
        boton.innerText = `${opcion}: ${pregunta.opciones[opcion]}`;
        boton.onclick = () => verificarRespuesta(boton, opcion, pregunta.respuesta_correcta);
        opcionesDiv.appendChild(boton);
    });
}

function verificarRespuesta(boton, seleccion, correcta) {
    let mensaje = document.getElementById("mensaje");

    if (seleccion === correcta) {
        mensaje.innerText = "✅ ¡Correcto!";
        mensaje.style.color = "green";
    } else {
        mensaje.innerText = `❌ Incorrecto, la respuesta era: ${correcta}`;
        mensaje.style.color = "red";
    }

    let botones = document.querySelectorAll(".boton-opcion");
    botones.forEach(b => b.disabled = true);
}
