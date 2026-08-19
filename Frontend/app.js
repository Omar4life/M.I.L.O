const API_URL = "http://127.0.0.1:8000";

const folderPath = document.getElementById("folderPath");
const scanButton = document.getElementById("scanButton");
const commandInput = document.getElementById("commandInput");
const runButton = document.getElementById("runButton");
const status = document.getElementById("status");
const fileList = document.getElementById("fileList");

async function scanFolder() {
    const path = folderPath.value.trim();

    if (!path) {
        status.textContent = "Please enter a folder path.";
        return;
    }

    status.textContent = "Scanning folder...";
    fileList.innerHTML = "";

    try {
        const response = await fetch(`${API_URL}/scan`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                path: path
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail || "MILO could not scan the folder."
            );
        }

        status.textContent =
            `Found ${data.files.length} files and folders.`;

        displayFiles(data.files);

    } catch (error) {
        status.textContent = `Error: ${error.message}`;
    }
}

async function runCommand() {
    const command = commandInput.value.trim();
    const folder = folderPath.value.trim();

    if (!command) {
        status.textContent = "Tell MILO what you want it to do.";
        return;
    }

    if (!folder) {
        status.textContent = "Choose a folder first.";
        return;
    }

    status.textContent = "MILO is thinking...";
    fileList.innerHTML = "";

    try {
        const response = await fetch(`${API_URL}/command`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                command: command,
                folder: folder
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail || "MILO encountered an error."
            );
        }

        if (data.action === "SEARCH") {
            status.textContent =
                `MILO searched for "${data.query}" and found ${data.results.length} results.`;

            displayFiles(data.results);

            return;
        }

        if (data.action === "QUESTION") {
            status.textContent = "MILO found an answer:";

            displayAnswer(
                data.answer,
                data.file
            );

            return;
        }

        status.textContent =
            data.message || "MILO does not support that action yet.";

    } catch (error) {
        status.textContent = `Error: ${error.message}`;
    }
}

function displayAnswer(answer, file) {
    const answerElement = document.createElement("div");

    answerElement.className = "answer";

    answerElement.innerHTML = `
        <div class="answer-text">
            ${escapeHTML(answer)}
        </div>
        ${
            file
                ? `
                    <div class="answer-file">
                        <div class="file-name">
                            📄 ${escapeHTML(file.name)}
                        </div>
                        <div class="file-path">
                            ${escapeHTML(file.path)}
                        </div>
                    </div>
                `
                : ""
        }
    `;

    fileList.appendChild(answerElement);
}

function displayFiles(files) {
    if (files.length === 0) {
        fileList.innerHTML =
            "<p>No matching files or folders found.</p>";
        return;
    }

    files.forEach(item => {
        const element = document.createElement("div");

        element.className = "file-item";

        const icon =
            item.type === "folder"
                ? "📁"
                : "📄";

        element.innerHTML = `
            <div>
                <div class="file-name">
                    ${icon} ${escapeHTML(item.name)}
                </div>
                <div class="file-path">
                    ${escapeHTML(item.path)}
                </div>
            </div>
        `;

        fileList.appendChild(element);
    });
}

function escapeHTML(value) {
    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

scanButton.addEventListener(
    "click",
    scanFolder
);

folderPath.addEventListener(
    "keydown",
    event => {
        if (event.key === "Enter") {
            scanFolder();
        }
    }
);

runButton.addEventListener(
    "click",
    runCommand
);

commandInput.addEventListener(
    "keydown",
    event => {
        if (event.key === "Enter") {
            runCommand();
        }
    }
);