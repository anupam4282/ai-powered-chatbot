const chatBox = document.getElementById("chatBox");
const form = document.getElementById("chatForm");
const input = document.getElementById("messageInput");
const sendBtn = document.getElementById("sendBtn");
const clearBtn = document.getElementById("clearBtn");

function addMessage(sender, text, temporary = false) {
    const wrapper = document.createElement("div");
    wrapper.className = `message ${sender}${temporary ? " typing-message" : ""}`;

    const bubble = document.createElement("div");
    bubble.className = "bubble";
    bubble.textContent = text;

    wrapper.appendChild(bubble);
    chatBox.appendChild(wrapper);
    chatBox.scrollTop = chatBox.scrollHeight;
    return wrapper;
}

function showWelcome() {
    if (!chatBox.children.length) {
        addMessage(
            "bot",
            "Hello! 👋 I'm your AI support assistant.\nAsk me about orders, refunds, passwords, support hours, or my features."
        );
    }
}

async function loadHistory() {
    try {
        const response = await fetch("/api/history");
        const data = await response.json();
        chatBox.innerHTML = "";

        data.messages.forEach(item => {
            addMessage(item.sender === "user" ? "user" : "bot", item.message);
        });
        showWelcome();
    } catch {
        showWelcome();
    }
}

async function sendMessage(message) {
    if (!message.trim()) return;

    addMessage("user", message);
    input.value = "";
    input.disabled = true;
    sendBtn.disabled = true;

    const typing = addMessage("bot", "Thinking...", true);

    try {
        const response = await fetch("/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message })
        });

        const data = await response.json();
        typing.remove();

        if (!response.ok) {
            addMessage("bot", data.error || "Something went wrong.");
        } else {
            addMessage("bot", data.response);
        }
    } catch {
        typing.remove();
        addMessage("bot", "Unable to connect to the server. Please try again.");
    } finally {
        input.disabled = false;
        sendBtn.disabled = false;
        input.focus();
    }
}

form.addEventListener("submit", event => {
    event.preventDefault();
    sendMessage(input.value);
});

document.querySelectorAll(".suggestions button").forEach(button => {
    button.addEventListener("click", () => sendMessage(button.dataset.message));
});

clearBtn.addEventListener("click", async () => {
    await fetch("/api/history", { method: "DELETE" });
    chatBox.innerHTML = "";
    showWelcome();
});

loadHistory();
