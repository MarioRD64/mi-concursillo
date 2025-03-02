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
            alert(data.error); // Si hubo un error (nombre ya en uso), lo mostramos
        } else {
            document.getElementById("registro").style.display = "none"; // Oculta la sección de registro
            document.getElementById("pregunta-container").style.display = "block"; // Muestra la sección de preguntas
            cargarPregunta(); // Llama a la función para cargar la pregunta
        }
    })
    .catch(error => console.error("❌ Error en el registro:", error)); // En caso de error, lo mostramos
}

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

function mostrarPregunta(pregunta) {
    // Establecer el texto de la pregunta
    document.getElementById("textoPregunta").innerText = pregunta.texto;

    // Obtener el contenedor donde se mostrarán las opciones
    let opcionesDiv = document.getElementById("opciones");
    opcionesDiv.innerHTML = ""; // Limpiamos cualquier opción anterior

    // Crear los botones de las opciones
    pregunta.opciones.forEach((opcion, index) => {
        let boton = document.createElement("button");
        boton.innerText = opcion;
        boton.classList.add("boton-opcion"); // Agregamos clase CSS para estilo
        boton.onclick = () => verificarRespuesta(boton, opcion, pregunta.respuesta); // Comprobamos si la respuesta es correcta
        opcionesDiv.appendChild(boton); // Agregamos el botón al contenedor
    });
}

function verificarRespuesta(boton, seleccion, correcta) {
    let mensaje = document.getElementById("mensaje");

    // Comprobamos si la selección es correcta
    if (seleccion === correcta) {
        mensaje.innerText = "✅ ¡Correcto!"; // Si la respuesta es correcta
        mensaje.style.color = "green";
        boton.classList.add("correcto"); // Cambiamos el color del botón a verde
    } else {
        mensaje.innerText = `❌ Incorrecto, la respuesta era: ${correcta}`; // Si la respuesta es incorrecta
        mensaje.style.color = "red";
        boton.classList.add("incorrecto"); // Cambiamos el color del botón a rojo
    }

    // Desactivar todos los botones después de responder
    document.querySelectorAll(".boton-opcion").forEach(btn => btn.disabled = true);
}

