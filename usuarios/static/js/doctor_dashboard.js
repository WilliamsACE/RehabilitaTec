/* ============================================================
 VARIABLES GLOBALES
============================================================ */
let maquinas = [];
let intervaloEstado = null;
let maquinaMonitoreada = null;
let pacientes = [];

let estadoSistema = {
    conectado: true,
    conectando: false,
    pacienteSeleccionado: null
};

/* ============================================================
 INICIO: TODO DENTRO DE UN SOLO DOMContentLoaded
============================================================ */
document.addEventListener("DOMContentLoaded", async () => {

    /* ============================================================
    CAPTURA DE ELEMENTOS DEL DOM
    ============================================================ */
    const machineSelect = document.getElementById('rehabilitador-select');
    const autocompleteListMaquinas = document.getElementById('autocomplete-machine');

    const patientSelect = document.getElementById('patient-select');
    const autocompleteList = document.getElementById('autocomplete-list');

    const startBtn = document.getElementById('start-btn');
    const statusIndicator = document.getElementById('status-indicator');

    const weightInput = document.getElementById('weight');
    const calfLengthInput = document.getElementById('calf-length');
    const sessionsInput = document.getElementById('sessions');
    const heightInput = document.getElementById('height');

    const degreesInput = document.getElementById('degrees');
    const repetitionsInput = document.getElementById('repetitions');
    const stopDegreesInput = document.getElementById('stop-degrees');

    const modeContainer = document.getElementById("mode-selectorID");
    const modeDivs = modeContainer.children;

    /* ============================================================
    CARGAR MÁQUINAS
    ============================================================ */
    async function cargarMaquinas() {
        try {
            const response = await fetch('/lista_maquinas_json/');
            maquinas = await response.json();
            console.log("Máquinas cargadas:", maquinas);
        } catch (error) {
            console.error("Error cargando máquinas:", error);
        }
    }
    await cargarMaquinas();

    /* ============================================================
    CONTROL DEL ESTADO DE MÁQUINA
    ============================================================ */
    function detenerMonitoreoEstado() {
        if (intervaloEstado) clearInterval(intervaloEstado);
        intervaloEstado = null;
        maquinaMonitoreada = null;
        actualizarEstadoVisual("Cargando...", false);
    }

    

    function actualizarEstadoVisual(texto, disponible) {
        const estadoElemento = document.getElementById('estado');
        const estadoDiv = document.getElementById('status-indicator');

        estadoDiv.classList.remove('status-connected', 'status-disconnected');
        estadoDiv.classList.add(disponible ? 'status-connected' : 'status-disconnected');
        estadoElemento.innerText = texto;
    }

    async function obtenerEstado(numeroMaquina) {
        try {
            const res = await fetch(`/estado_arduino/?numero=${numeroMaquina}`);
            const data = await res.json();

            actualizarEstadoVisual(
                data.estado || "Ocupado",
                data.estado === "Disponible"
            );
        } catch (err) {
            console.error("Error consultando estado:", err);
            actualizarEstadoVisual("Error de conexión", false);
        }
    }

    function iniciarMonitoreoEstado(numeroMaquina) {
        detenerMonitoreoEstado();
        maquinaMonitoreada = numeroMaquina;
        obtenerEstado(numeroMaquina);
        intervaloEstado = setInterval(() => obtenerEstado(numeroMaquina), 500);
    }

    /* ============================================================
    AUTOCOMPLETADO DE MÁQUINAS
    ============================================================ */
    machineSelect.addEventListener("input", () => {
        const valor = machineSelect.value.toLowerCase();
        autocompleteListMaquinas.innerHTML = "";

        if (valor.length < 1) {
            autocompleteListMaquinas.style.display = "none";
            detenerMonitoreoEstado();
            return;
        }

        const filtradas = maquinas.filter(m =>
            m.numero && m.numero.toLowerCase().includes(valor)
        );

        if (filtradas.length === 0) {
            autocompleteListMaquinas.style.display = "none";
            return;
        }

        filtradas.forEach(m => {
            const item = document.createElement("div");
            item.className = "autocomplete-item";
            item.textContent = m.numero;

            item.addEventListener("click", () => {
                machineSelect.value = m.numero;
                autocompleteListMaquinas.style.display = "none";
                iniciarMonitoreoEstado(m.numero);
            });

            autocompleteListMaquinas.appendChild(item);
        });

        autocompleteListMaquinas.style.display = "block";
    });

    document.addEventListener("click", e => {
        if (!autocompleteListMaquinas.contains(e.target) && e.target !== machineSelect) {
            autocompleteListMaquinas.style.display = "none";
        }
    });

    detenerMonitoreoEstado();


    /* ============================================================
    CARGAR PACIENTES DESDE DJANGO
    ============================================================ */
    async function cargarPacientes() {
        try {
            const resp = await fetch(URL_LISTA_PACIENTES);
            pacientes = await resp.json();
            console.log("Pacientes cargados:", pacientes);
        } catch (err) {
            console.error("Error cargando pacientes:", err);
        }
    }
    await cargarPacientes();


    /* ============================================================
    AUTOCOMPLETADO DE PACIENTES
    ============================================================ */
    patientSelect.addEventListener("input", () => {
        const valor = patientSelect.value.toLowerCase();
        autocompleteList.innerHTML = "";

        if (valor.length < 2) {
            autocompleteList.style.display = "none";
            return;
        }

        const filtrados = pacientes.filter(p => p.nombre.toLowerCase().includes(valor));

        if (filtrados.length === 0) {
            autocompleteList.style.display = "none";
            return;
        }

        filtrados.forEach(paciente => {
            const item = document.createElement("div");
            item.className = "autocomplete-item";
            item.textContent = paciente.nombre;

            item.addEventListener("click", () => {
                patientSelect.value = paciente.nombre;
                autocompleteList.style.display = "none";
                cargarDatosPaciente(paciente);
            });

            autocompleteList.appendChild(item);
        });

        autocompleteList.style.display = "block";
    });

    document.addEventListener("click", e => {
        if (!autocompleteList.contains(e.target) && e.target !== patientSelect) {
            autocompleteList.style.display = "none";
        }
    });

    function cargarDatosPaciente(p) {
        weightInput.value = p.peso || "";
        calfLengthInput.value = p.tamano_de_la_pantorrilla || "";
        sessionsInput.value = p.sesiones || "";
        heightInput.value = p.altura || "";

        estadoSistema.pacienteSeleccionado = p;
        validarCampos();
    }
    
    /* ============================================================
    SELECCIÓN DE MODO
    ============================================================ */
    document.querySelectorAll(".mode-option").forEach(option => {
        option.addEventListener("click", () => {
            document.querySelectorAll(".mode-option").forEach(o => o.classList.remove("active"));
            option.classList.add("active");
            validarCampos();
        });
    });


    /* ============================================================
    VALIDACIÓN DE CAMPOS
    ============================================================ */
    startBtn.disabled = true;

    const camposRequeridos = [
        patientSelect,
        weightInput,
        calfLengthInput,
        heightInput,
        degreesInput,
        repetitionsInput,
        stopDegreesInput
    ];

const modeDivsArray = Array.from(modeDivs);

function validarCampos() {
    const todosLlenos = camposRequeridos.every(c => c.value.trim() !== "");
    const hayModo = modeDivsArray.some(d => d.classList.contains("active"));
    const hayMaquina = machineSelect.value.trim() !== "";
    const hayPaciente = estadoSistema.pacienteSeleccionado !== null;

    startBtn.disabled = !(todosLlenos && hayModo && hayMaquina && hayPaciente);
}


    camposRequeridos.forEach(c => c.addEventListener("input", validarCampos));

    /* ============================================================
    SCROLL EN MÓVIL
    ============================================================ */
    machineSelect.addEventListener("click", () => {
        setTimeout(() => {
            window.scrollTo({ top: document.body.scrollHeight, behavior: "smooth" });
        }, 20);
    });


    /* ============================================================
    OVERLAY PARA AGREGAR PACIENTE
    ============================================================ */
    const BotonPaciente = document.getElementById("btnpaciente");
    const BotonCerrar = document.getElementById("closeOverlay");
    const OverlayFondo = document.getElementById("overlayfondo");
    const OverlayaddP = document.getElementById("overlayID");

    BotonPaciente.addEventListener("click", () => {
        OverlayaddP.style.top = "50%";
        OverlayaddP.style.opacity = "100%";
        OverlayFondo.classList.add("activo");
    });

    BotonCerrar.addEventListener("click", () => {
        OverlayaddP.style.top = "150%";
        OverlayaddP.style.opacity = "0%";
        OverlayFondo.classList.remove("activo");
    });


    /* ============================================================
    BOTONES DE NÚMERO (+ / -)
    ============================================================ */
    document.querySelectorAll(".number-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            const input = document.getElementById(btn.dataset.input);
            let value = parseInt(input.value) || 0;
            const step = parseInt(input.step) || 1;

            value = btn.dataset.direction === "up" ? value + step : Math.max(0, value - step);

            input.value = value;
            input.dispatchEvent(new Event("input"));
        });
    });


    /* ============================================================
    AGREGAR PACIENTE A LA BD
    ============================================================ */
    document.getElementById("BtnSubmit").addEventListener("click", () => {
        const data = {
            nombre: document.getElementById("patient-name").value,
            altura: document.getElementById("patient-height").value,
            tamano_de_la_pantorrilla: document.getElementById("patient-calf").value,
            peso: document.getElementById("patient-weight").value
        };

        fetch("/agregar_paciente/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken")
            },
            body: JSON.stringify(data)
        })
            .then(r => r.json())
            .then(() => alert("Datos guardados en la base de datos"))
            .catch(() => alert("Error guardando datos"));
    });

    /* ============================================================
 BOTÓN INICIAR - ENVÍA LOS DATOS A DJANGO
============================================================ */
startBtn.addEventListener("click", async () => {

    const numeroMaquina = machineSelect.value.trim();
    const paciente = estadoSistema.pacienteSeleccionado;

    if (!numeroMaquina || !paciente) {
        alert("Faltan datos para enviar.");
        return;
    }

    const payload = {
        maquina: numeroMaquina,     // nombre correcto en tu backend
        paciente: paciente.id,      // ID real del paciente
        grados: degreesInput.value,
        repeticiones: repetitionsInput.value,
        stop_grados: stopDegreesInput.value,
        modo: document.querySelector(".mode-option.active")?.dataset.mode || "normal",
        accion: "iniciar"           // para que el backend sepa que es start
    };

    console.log("Enviando payload:", payload);

    try {
        const response = await fetch("/recibir_datos/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken")
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const error = await response.text();
            console.error("Error del servidor:", error);
            alert("Error 400/500 al enviar datos.");
            return;
        }

        const data = await response.json();
        console.log("Respuesta Django:", data);

        alert("Datos enviados correctamente");

    } catch (err) {
        console.error("Error enviando:", err);
        alert("Error conectando al servidor.");
    }
});


}); // FIN DEL DOMContentLoaded



/* ============================================================
 FUNCIÓN CSRF (NO TOCAR)
============================================================ */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
