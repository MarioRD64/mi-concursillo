function cargarPregunta() {
    fetch("/preguntas")
        .then(response => response.json())
        .then(data => {
            const pregunta = data[0]; // Carga la primera pregunta
            document.getElementById("pregunta").innerHTML = `
                <h2>${pregunta.pregunta}</h2>
                <ul>
                    <li>A: ${pregunta.opciones.A}</li>
                    <li>B: ${pregunta.opciones.B}</li>
                    <li>C: ${pregunta.opciones.C}</li>
                    <li>D: ${pregunta.opciones.D}</li>
                </ul>
            `;
        });
}
