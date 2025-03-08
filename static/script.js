const socket = io("http://127.0.0.1:5000");

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
    fetch("/crear_sala", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ nombre: nombreJugador })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
        } else {
            codigoSala = data.codigo_sala;
            mostrarSalaEspera(data.jugadores);
            mostrarCodigoSala(codigoSala);
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
            codigoSala = sala;
            mostrarSalaEspera(data.jugadores);
        }
    })
    .catch(error => console.error("❌ Error al unirse a la sala:", error));
}

// Función para mostrar la sala de espera
function mostrarSalaEspera(jugadores) {
    document.getElementById("unirseSala").style.display = "none";
    document.getElementById("salaEspera").style.display = "block";
    actualizarJugadoresSala(jugadores);
}

// Mostrar código de sala en la UI
function mostrarCodigoSala(codigo) {
    let codigoElemento = document.createElement("p");
    codigoElemento.innerHTML = `Código de sala: <strong>${codigo}</strong>`;
    document.getElementById("salaEspera").prepend(codigoElemento);
}

// Función para actualizar la lista de jugadores en la sala
function actualizarJugadoresSala(jugadores) {
    let listaJugadores = document.getElementById("jugadoresSala");
    listaJugadores.innerHTML = '';

    jugadores.forEach(jugador => {
        let jugadorDiv = document.createElement("div");
        jugadorDiv.innerText = jugador;
        listaJugadores.appendChild(jugadorDiv);
    });

    if (jugadores[0] === nombreJugador) {
        document.getElementById("iniciarJuego").style.display = "block";
    }
}

// Función para iniciar el juego
function iniciarJuego() {
    socket.emit("iniciar_partida", { sala: codigoSala });
}

// Escuchar WebSockets
socket.on("jugador_unido", (data) => actualizarJugadoresSala(data.jugadores));

socket.on("inicio_partida", () => {
    document.getElementById("salaEspera").style.display = "none";
    cargarPregunta();
});

// Función para cargar y mostrar preguntas
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
    opcionesDiv.innerHTML = "";

    Object.keys(pregunta.opciones).forEach(opcion => {
        let boton = document.createElement("button");
        boton.classList.add("boton-opcion");
        boton.innerText = `${opcion}: ${pregunta.opciones[opcion]}`;
        boton.onclick = () => verificarRespuesta(boton, opcion, pregunta.respuesta_correcta);
        opcionesDiv.appendChild(boton);
    });
}

// Función para verificar la respuesta
function verificarRespuesta(boton, seleccion, correcta) {
    let mensaje = document.getElementById("mensaje");

    if (seleccion === correcta) {
        mensaje.innerText = "✅ ¡Correcto!";
        mensaje.style.color = "green";
    } else {
        mensaje.innerText = "❌ Incorrecto";
        mensaje.style.color = "red";
    }

    document.querySelectorAll(".boton-opcion").forEach(b => b.disabled = true);
}
