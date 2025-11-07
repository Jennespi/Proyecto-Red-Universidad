// chat_mini.js - Control del mini chat en el dashboard

let isMiniChatOpen = false;

function toggleChatMini() {
    const chatWindow = document.getElementById('chat-mini-window');
    const chatBtn = document.getElementById('chat-floating-btn');
    
    if (isMiniChatOpen) {
        // Cerrar el mini chat
        chatWindow.style.display = 'none';
        chatBtn.innerHTML = `
            <svg viewBox="0 0 24 24" class="chat-icon">
                <path fill="white" d="M12 3C6.5 3 2 6.8 2 11c0 1.8.8 3.6 2.3 5L3 21l5.2-2.2c1 .3 2 .4 3 .4 5.5 0 10-3.8 10-8s-4.5-8-10-8z"/>
            </svg>
        `;
        isMiniChatOpen = false;
    } else {
        // Abrir el mini chat
        chatWindow.style.display = 'flex';
        chatBtn.innerHTML = `
            <svg viewBox="0 0 24 24" class="chat-icon">
                <path fill="white" d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
            </svg>
        `;
        isMiniChatOpen = true;
        
        // Enfocar el input cuando se abre
        setTimeout(() => {
            document.getElementById('mini-text').focus();
        }, 100);
    }
}

function sendMiniMessage() {
    const input = document.getElementById('mini-text');
    const messagesContainer = document.getElementById('mini-messages');
    const message = input.value.trim();
    
    if (message === '') return;
    
    // Remover placeholder si existe
    const placeholder = messagesContainer.querySelector('.placeholder');
    if (placeholder) {
        placeholder.remove();
    }
    
    // Crear elemento de mensaje (simulación)
    addMessageToMiniChat(message, 'me');
    
    // Limpiar input
    input.value = '';
    
    // Enfocar de nuevo el input
    input.focus();
}

function addMessageToMiniChat(message, sender) {
    const messagesContainer = document.getElementById('mini-messages');
    
    const messageElement = document.createElement('div');
    messageElement.className = `mini-message ${sender}`;
    messageElement.textContent = message;
    
    messagesContainer.appendChild(messageElement);
    
    // Scroll al final
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function handleMiniKeyPress(event) {
    if (event.key === 'Enter') {
        event.preventDefault();
        sendMiniMessage();
    }
}

// Cerrar el chat si se hace click fuera de él
document.addEventListener('click', function(event) {
    const chatWindow = document.getElementById('chat-mini-window');
    const chatBtn = document.getElementById('chat-floating-btn');
    
    if (isMiniChatOpen && 
        !chatWindow.contains(event.target) && 
        !chatBtn.contains(event.target)) {
        toggleChatMini();
    }
});

// Inicialización
document.addEventListener('DOMContentLoaded', function() {
    console.log('Mini chat inicializado');
    
    // Agregar algún mensaje de bienvenida si está vacío
    const messagesContainer = document.getElementById('mini-messages');
    if (messagesContainer.children.length === 1 && 
        messagesContainer.querySelector('.placeholder')) {
        // Puedes agregar un mensaje de bienvenida aquí si quieres
    }
});