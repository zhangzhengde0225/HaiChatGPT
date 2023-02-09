const chatForm = document.getElementById("chat-form");
const chatInput = document.getElementById("chat-input");
const chatMessages = document.getElementById("chat-messages");

chatForm.addEventListener("submit", (event) => {
  event.preventDefault();

  const message = chatInput.value;
  chatInput.value = "";

  const messageElement = document.createElement("div");
  messageElement.innerText = message;
  chatMessages.appendChild(messageElement);
});
