const API_URL = "http://127.0.0.1:8000";

const folderPath =
    document.getElementById("folderPath");

const scanButton =
    document.getElementById("scanButton");

const commandInput =
    document.getElementById("commandInput");

const runButton =
    document.getElementById("runButton");

const status =
    document.getElementById("status");

const messages =
    document.getElementById("chatMessages");

const chatList =
    document.getElementById("chatHistory");

const newChatButton =
    document.getElementById("newChatButton");

const currentChatTitle =
    document.getElementById("currentChatTitle");


let chats = JSON.parse(
    localStorage.getItem("miloChats") || "[]"
);

let currentChatId = null;


function saveChats() {
    localStorage.setItem(
        "miloChats",
        JSON.stringify(chats)
    );
}


function createChat() {
    const chat = {
        id:
            Date.now().toString()
            + "-"
            + Math.random()
                .toString(36)
                .slice(2),

        title: "New chat",

        messages: []
    };

    chats.unshift(chat);

    currentChatId =
        chat.id;

    saveChats();

    renderChatList();
    renderCurrentChat();
}


function getCurrentChat() {
    return chats.find(
        chat =>
            chat.id === currentChatId
    );
}


function renderChatList() {

    chatList.innerHTML = "";

    chats.forEach(chat => {

        const item =
            document.createElement("div");

        item.className =
            "chat-history-item";

        if (
            chat.id === currentChatId
        ) {
            item.classList.add(
                "active"
            );
        }

        item.textContent =
            chat.title;

        item.addEventListener(
            "click",
            () => {

                currentChatId =
                    chat.id;

                renderChatList();
                renderCurrentChat();

                commandInput.focus();
            }
        );

        chatList.appendChild(
            item
        );
    });
}


function renderCurrentChat() {

    const chat =
        getCurrentChat();

    if (!chat) {
        return;
    }

    currentChatTitle.textContent =
        chat.title;

    if (
        chat.messages.length === 0
    ) {

        messages.innerHTML = `
            <div class="welcome-message">

                <div class="welcome-icon">
                    ✦
                </div>

                <h2>
                    What can I help you find?
                </h2>

                <p>
                    Ask MILO to find, read,
                    or organize something
                    on your computer.
                </p>

                <div class="suggestions">

                    <button class="suggestion">
                        Find my robotics files
                    </button>

                    <button class="suggestion">
                        Find my Spider-Man ticket
                    </button>

                    <button class="suggestion">
                        Find my AI tools documents
                    </button>

                </div>

            </div>
        `;

        attachSuggestions();

        return;
    }

    messages.innerHTML = "";

    chat.messages.forEach(
        message => {

            renderMessage(
                message.role,
                message.text,
                message.results || []
            );

        }
    );

    scrollToBottom();
}


function renderMessage(
    role,
    text,
    results = []
) {

    const wrapper =
        document.createElement("div");

    wrapper.className =
        `message ${role}`;

    const bubble =
        document.createElement("div");

    bubble.className =
        "message-content";

    bubble.textContent =
        text;

    wrapper.appendChild(
        bubble
    );

    if (
        results.length > 0
    ) {

        results.forEach(
            item => {

                const result =
                    document.createElement(
                        "div"
                    );

                result.className =
                    "result";

                result.innerHTML = `
                    <div class="result-name">
                        ${
                            item.type === "folder"
                                ? "📁"
                                : "📄"
                        }
                        ${escapeHTML(item.name)}
                    </div>

                    <div class="result-path">
                        ${escapeHTML(item.path)}
                    </div>
                `;

                wrapper.appendChild(
                    result
                );
            }
        );
    }

    messages.appendChild(
        wrapper
    );
}


function addMessage(
    role,
    text,
    results = []
) {

    let chat =
        getCurrentChat();

    if (!chat) {

        createChat();

        chat =
            getCurrentChat();
    }

    chat.messages.push({
        role,
        text,
        results
    });

    if (
        role === "user"
        && chat.title === "New chat"
    ) {

        chat.title =
            makeChatTitle(text);
    }

    saveChats();

    renderChatList();
    renderCurrentChat();
}


function makeChatTitle(text) {

    const cleaned =
        text
            .replace(/[.!?]/g, "")
            .trim();

    if (!cleaned) {
        return "New chat";
    }

    const words =
        cleaned.split(/\s+/);

    if (
        words.length <= 5
    ) {
        return cleaned;
    }

    return (
        words
            .slice(0, 5)
            .join(" ")
        + "..."
    );
}


async function scanFolder() {

    const path =
        folderPath.value.trim();

    if (!path) {

        status.textContent =
            "Please enter a folder path.";

        return;
    }

    status.textContent =
        "Scanning folder...";

    scanButton.disabled =
        true;

    try {

        const response =
            await fetch(
                `${API_URL}/scan`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        path
                    })
                }
            );

        const data =
            await response.json();

        if (!response.ok) {

            throw new Error(
                data.detail ||
                "MILO could not scan the folder."
            );
        }

        status.textContent =
            `Found ${data.files.length} files and folders.`;

    } catch (error) {

        status.textContent =
            `Error: ${error.message}`;

    } finally {

        scanButton.disabled =
            false;
    }
}


async function runCommand() {

    const command =
        commandInput.value.trim();

    const folder =
        folderPath.value.trim();

    if (!command) {
        return;
    }

    if (!folder) {

        status.textContent =
            "Choose a folder first.";

        return;
    }

    if (!currentChatId) {
        createChat();
    }

    addMessage(
        "user",
        command
    );

    commandInput.value = "";

    runButton.disabled =
        true;

    commandInput.disabled =
        true;

    status.textContent =
        "MILO is thinking...";

    const chat =
        getCurrentChat();

    const conversationHistory =
        chat.messages
            .slice(-12)
            .map(message => ({
                role:
                    message.role === "user"
                        ? "user"
                        : "assistant",

                content:
                    message.text
            }));

    try {

        const response =
            await fetch(
                `${API_URL}/command`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        command,
                        folder,
                        chat_id:
                            currentChatId,
                        conversation:
                            conversationHistory
                    })
                }
            );

        const data =
            await response.json();

        if (!response.ok) {

            throw new Error(
                data.detail ||
                "MILO encountered an error."
            );
        }


        if (
            data.action === "SEARCH"
        ) {

            const results =
                data.results || [];

            if (
                results.length === 0
            ) {

                addMessage(
                    "milo",
                    "I couldn't find anything matching that.",
                    []
                );

            } else {

                addMessage(
                    "milo",
                    `I found ${results.length} matching result${results.length === 1 ? "" : "s"}.`,
                    results
                );
            }

        } else if (
            data.action === "QUESTION"
        ) {

            addMessage(
                "milo",
                data.answer ||
                "I couldn't answer that.",
                data.file
                    ? [data.file]
                    : []
            );

        } else if (
            data.action === "CHAT"
        ) {

            addMessage(
                "milo",
                data.answer ||
                "I'm listening.",
                []
            );

        } else {

            addMessage(
                "milo",
                data.message ||
                "I'm not sure what to do yet.",
                []
            );
        }

        status.textContent = "";

    } catch (error) {

        addMessage(
            "milo",
            `Something went wrong: ${error.message}`,
            []
        );

        status.textContent = "";

    } finally {

        runButton.disabled =
            false;

        commandInput.disabled =
            false;

        commandInput.focus();
    }
}


function attachSuggestions() {

    document
        .querySelectorAll(".suggestion")
        .forEach(
            button => {

                button.addEventListener(
                    "click",
                    () => {

                        commandInput.value =
                            button.textContent.trim();

                        commandInput.focus();
                    }
                );

            }
        );
}


function scrollToBottom() {

    messages.scrollTop =
        messages.scrollHeight;
}


function escapeHTML(value) {

    return String(value)
        .replaceAll(
            "&",
            "&amp;"
        )
        .replaceAll(
            "<",
            "&lt;"
        )
        .replaceAll(
            ">",
            "&gt;"
        )
        .replaceAll(
            '"',
            "&quot;"
        )
        .replaceAll(
            "'",
            "&#039;"
        );
}


newChatButton.addEventListener(
    "click",
    () => {

        createChat();

        commandInput.focus();
    }
);


scanButton.addEventListener(
    "click",
    scanFolder
);


folderPath.addEventListener(
    "keydown",
    event => {

        if (
            event.key === "Enter"
        ) {
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

        if (
            event.key === "Enter"
        ) {
            runCommand();
        }
    }
);


if (chats.length === 0) {

    createChat();

} else {

    currentChatId =
        chats[0].id;

    renderChatList();
    renderCurrentChat();
}