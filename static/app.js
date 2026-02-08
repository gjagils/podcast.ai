const $ = (sel) => document.querySelector(sel);

let currentJobId = null;

// --- Elementen ---
const dropZone = $("#drop-zone");
const fileInput = $("#file-input");
const chooseFileBtn = $("#choose-file-btn");
const fileInfo = $("#file-info");
const fileName = $("#file-name");
const removeFile = $("#remove-file");
const stepUpload = $("#step-upload");
const stepSettings = $("#step-settings");
const stepProgress = $("#step-progress");
const stepResult = $("#step-result");
const stepError = $("#step-error");
const docSummary = $("#doc-summary");
const durationInput = $("#duration");
const durationLabel = $("#duration-label");
const generateBtn = $("#generate-btn");
const audioPlayer = $("#audio-player");
const downloadAudio = $("#download-audio");
const downloadScript = $("#download-script");
const newPodcast = $("#new-podcast");
const retryBtn = $("#retry-btn");
const errorMessage = $("#error-message");
const progScript = $("#prog-script");
const progAudio = $("#prog-audio");

// --- Helpers ---
function showStep(step) {
    [stepUpload, stepSettings, stepProgress, stepResult, stepError].forEach(
        (s) => s.classList.add("hidden")
    );
    step.classList.remove("hidden");
}

function showError(msg) {
    errorMessage.textContent = msg;
    showStep(stepError);
}

// --- Bestandsselectie ---
chooseFileBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    fileInput.click();
});

dropZone.addEventListener("click", (e) => {
    if (e.target === chooseFileBtn || e.target === fileInput) return;
    fileInput.click();
});

// --- Drag & Drop ---
dropZone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropZone.classList.add("dragover");
});

dropZone.addEventListener("dragleave", () => {
    dropZone.classList.remove("dragover");
});

dropZone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropZone.classList.remove("dragover");
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
});

fileInput.addEventListener("change", () => {
    if (fileInput.files[0]) handleFile(fileInput.files[0]);
});

removeFile.addEventListener("click", () => {
    fileInput.value = "";
    fileInfo.classList.add("hidden");
    dropZone.classList.remove("hidden");
    currentJobId = null;
});

// --- Upload ---
async function handleFile(file) {
    if (!file.name.toLowerCase().endsWith(".docx")) {
        showError("Alleen .docx bestanden zijn toegestaan.");
        return;
    }

    fileName.textContent = file.name;
    fileInfo.classList.remove("hidden");
    dropZone.classList.add("hidden");

    const formData = new FormData();
    formData.append("file", file);

    try {
        const res = await fetch("/api/upload", { method: "POST", body: formData });
        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || "Upload mislukt");
        }
        const data = await res.json();
        currentJobId = data.job_id;

        docSummary.innerHTML =
            `<strong>${data.title}</strong><br>` +
            `${data.sections} secties &middot; ${data.words} woorden`;

        showStep(stepSettings);
    } catch (e) {
        showError(e.message);
    }
}

// --- Sliders ---
durationInput.addEventListener("input", () => {
    durationLabel.textContent = `${durationInput.value} minuten`;
});

const speedInput = $("#speed");
const speedLabel = $("#speed-label");
speedInput.addEventListener("input", () => {
    speedLabel.textContent = `${parseFloat(speedInput.value).toFixed(2)}x`;
});

// --- Genereren ---
generateBtn.addEventListener("click", async () => {
    if (!currentJobId) return;

    showStep(stepProgress);
    progScript.className = "progress-step active";
    progAudio.className = "progress-step";

    const formData = new FormData();
    formData.append("duration", durationInput.value);
    formData.append("model", $("#model").value);
    formData.append("mode", $("#mode").value);
    formData.append("tts_engine", $("#tts-engine").value);
    formData.append("speed", speedInput.value);

    try {
        const res = await fetch(`/api/generate/${currentJobId}`, {
            method: "POST",
            body: formData,
        });

        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || "Generatie mislukt");
        }

        const data = await res.json();

        // Klaar
        progScript.className = "progress-step done";
        progAudio.className = "progress-step done";

        audioPlayer.src = data.audio_url;
        downloadAudio.href = `/api/download/${currentJobId}`;
        downloadScript.href = data.script_url;

        showStep(stepResult);
    } catch (e) {
        showError(e.message);
    }
});

// --- Opnieuw / Nieuw ---
newPodcast.addEventListener("click", () => {
    currentJobId = null;
    fileInput.value = "";
    fileInfo.classList.add("hidden");
    dropZone.classList.remove("hidden");
    showStep(stepUpload);
});

retryBtn.addEventListener("click", () => {
    if (currentJobId) {
        showStep(stepSettings);
    } else {
        currentJobId = null;
        fileInput.value = "";
        fileInfo.classList.add("hidden");
        dropZone.classList.remove("hidden");
        showStep(stepUpload);
    }
});
