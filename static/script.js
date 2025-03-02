function registrarJugador() {
    let nombre = document.getElementById("nombreJugador").value.trim();

    if (!nombre) {
        alert("❌ Ingresa tu nombre antes de unirte.");
        return;
    }

    fetch("/registrar", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ nombre: nombre })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
        } else {
            document.getElementById("registro").style.display = "none"; // Oculta el registro
            document.getElementById("pregunta-container").style.display = "block"; // Muestra la pregunta
            cargarPregunta();
        }
    })
    .catch(error => console.error("❌ Error en el registro:", error));
}

function cargarPregunta() {
    fetch("/preguntas")
        .then(response => response.json())
        .then(data => {
            if (data.length > 0) {
                let preguntaAleatoria = data[Math.floor(Math.random() * data.length)]; // Seleccionar aleatoria
                mostrarPregunta(preguntaAleatoria);
            } else {
                console.error("⚠️ No hay preguntas disponibles.");
            }
        })
        .catch(error => console.error("❌ Error al obtener la pregunta:", error));
}

function mostrarPregunta(pregunta) {
    document.getElementById("textoPregunta").innerText = pregunta.texto;
    
    let opcionesDiv = document.getElementById("opciones");
    opcionesDiv.innerHTML = ""; // Limpiar opciones anteriores

    pregunta.opciones.forEach((opcion, index) => {
        let boton = document.createElement("button");
        boton.innerText = opcion;
        boton.classList.add("boton-opcion"); // Agregamos clase CSS
        boton.onclick = () => verificarRespuesta(boton, opcion, pregunta.respuesta);
        opcionesDiv.appendChild(boton);
    });
}

function verificarRespuesta(boton, seleccion, correcta) {
    let mensaje = document.getElementById("mensaje");
    
    if (seleccion === correcta) {
        mensaje.innerText = "✅ ¡Correcto!";
        mensaje.style.color = "green";
        boton.classList.add("correcto");
    } else {
        mensaje.innerText = "❌ Incorrecto, la respuesta era: " + correcta;
        mensaje.style.color = "red";
        boton.classList.add("incorrecto");
    }

    // Desactivar botones después de responder
    document.querySelectorAll(".boton-opcion").forEach(btn => btn.disabled = true);
}
