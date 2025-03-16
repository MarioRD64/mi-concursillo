const socket = io("http://127.0.0.1:5000");

let nombreJugador = '';
let codigoSala = '';

// **Función para registrar un jugador**
function registrarJugador() {
    let email = document.getElementById("emailJugador").value.trim();
    let password = document.getElementById("passwordJugador").value.trim();

    if (!email || !password) {
        alert("❌ Ingresa correo y contraseña válidos.");
        return;
    }

    fetch("/registro", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
        } else {
            alert("✅ Registro exitoso. Revisa tu correo para confirmar antes de jugar.");
            // Se oculta el formulario de registro y se muestra el de unirse a sala
            document.getElementById("registro").style.display = "none";
            document.getElementById("unirseSala").style.display = "block";
        }
    })
    .catch(err => console.error("❌ Error:", err));
}

// **Función para iniciar sesión**
function iniciarSesion() {
    let email = document.getElementById("emailJugador").value.trim();
    let password = document.getElementById("passwordJugador").value.trim();

    fetch("/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
        } else {
            alert("✅ Sesión iniciada. Ya puedes crear o unirte a una sala.");
            document.getElementById("registro").style.display = "none";
            document.getElementById("unirseSala").style.display = "block";
        }
    })
    .catch(err => console.error("❌ Error:", err));
}

// **Función para registrar el nombre del jugador**
function registrarNombreJugador() {
    nombreJugador = document.getElementById("nombreJugador").value.trim();

    if (!nombreJugador) {
        alert("❌ Ingresa tu nombre antes de unirte.");
        return;
    }

    // Se oculta el registro y se muestra la opción de unirse a sala
    document.getElementById("registro").style.display = "none";
    document.getElementById("unirseSala").style.display = "block";
}

// **Función para crear una sala**
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
            mostrarCodigoSala(codigoSala);
            mostrarSalaEspera(data.jugadores);

            // Unirse como HOST a la sala WebSocket
            socket.emit("unirse_sala", { nombre: nombreJugador, sala: codigoSala });
        }
    })
    .catch(error => console.error("❌ Error al crear la sala:", error));
}

// **Función para unirse a una sala**
function unirseSala() {
    const sala = document.getElementById("nombreSala").value.trim();

    if (!sala || !nombreJugador) {
        alert("❌ Ingresa el nombre de la sala.");
        return;
    }

    // Unirse vía socket
    codigoSala = sala;
    socket.emit("unirse_sala", { nombre: nombreJugador, sala: codigoSala });

    // Mostrar sala de espera
    document.getElementById("unirseSala").style.display = "none";
    document.getElementById("salaEspera").style.display = "block";
}

// **Mostrar código de sala en la UI**
function mostrarCodigoSala(codigo) {
    let codigoElemento = document.createElement("p");
    codigoElemento.innerHTML = `Código de sala: <strong>${codigo}</strong>`;
    document.getElementById("salaEspera").prepend(codigoElemento);
}

// **Mostrar la sala de espera**
function mostrarSalaEspera(jugadores) {
    actualizarJugadoresSala(jugadores);
}

// **Actualizar la lista de jugadores en la sala**
function actualizarJugadoresSala(jugadores) {
    let listaJugadores = document.getElementById("jugadoresSala");
    listaJugadores.innerHTML = '';

    jugadores.forEach(jugador => {
        let jugadorDiv = document.createElement("div");
        jugadorDiv.innerText = jugador;
        listaJugadores.appendChild(jugadorDiv);
    });

    // Mostrar botón de iniciar solo al host (primer jugador en la lista)
    if (jugadores[0] === nombreJugador) {
        document.getElementById("iniciarJuego").style.display = "block";
    } else {
        document.getElementById("iniciarJuego").style.display = "none";
    }
}

// **Función para iniciar el juego (solo host)**
function iniciarJuego() {
    socket.emit("iniciar_partida", { sala: codigoSala });
}

// **Escuchar WebSockets**

socket.on("jugador_unido", (data) => {
    console.log("👥 Jugadores actualizados:", data.jugadores);
    actualizarJugadoresSala(data.jugadores);
});

socket.on("inicio_partida", () => {
    console.log("🚀 Partida iniciada!");
    document.getElementById("salaEspera").style.display = "none";
    document.getElementById("zonaJuego").style.display = "block";
    cargarPregunta();
});

// **Cargar y mostrar preguntas**
function cargarPregunta() {
    fetch("/preguntas")
        .then(response => response.json())
        .then(data => {
            let preguntaAleatoria = data[Math.floor(Math.random() * data.length)];
            mostrarPregunta(preguntaAleatoria);
        });
}

// **Mostrar la pregunta y opciones**
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

// **Verificar respuesta**
function verificarRespuesta(boton, seleccion, correcta) {
    let mensaje = document.getElementById("mensaje");

    if (seleccion === correcta) {
        mensaje.innerText = "✅ ¡Correcto!";
        mensaje.style.color = "green";
    } else {
        mensaje.innerText = "❌ Incorrecto";
        mensaje.style.color = "red";
    }

    // Deshabilitar todas las opciones
    document.querySelectorAll(".boton-opcion").forEach(b => b.disabled = true);
}
