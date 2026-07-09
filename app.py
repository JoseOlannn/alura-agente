import os
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"
from dotenv import load_dotenv
from flask import Flask, render_template_string, request, jsonify

load_dotenv()

from agent import BimBamAgent

app = Flask(__name__)

# Intentar inicializar el agente al arrancar la app
try:
    if "GOOGLE_API_KEY" not in os.environ or not os.environ["GOOGLE_API_KEY"]:
        raise ValueError("Falta configurar GOOGLE_API_KEY. Revisa el archivo .env")
    
    if not os.path.exists("faiss_index"):
        raise ValueError("No se encontró la base de datos vectorial 'faiss_index'. Debes ejecutar 'python document_processor.py' primero.")
        
    agent = BimBamAgent()
    agent_ready = True
except Exception as e:
    agent = None
    agent_ready = False
    error_message = str(e)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Soporte BimBam Buy</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Outfit', sans-serif;
            background-color: #f4f7f6;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        
        .chat-container {
            width: 100%;
            max-width: 500px;
            background: #ffffff;
            border-radius: 24px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.08);
            overflow: hidden;
            display: flex;
            flex-direction: column;
            height: 85vh;
        }
        
        .chat-header {
            padding: 20px 24px;
            background: #ffffff;
            border-bottom: 1px solid #f0f0f0;
            display: flex;
            align-items: center;
            gap: 15px;
        }
        
        .avatar {
            width: 48px;
            height: 48px;
            background: linear-gradient(135deg, #0061ff, #60efff);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 1.4rem;
            box-shadow: 0 4px 10px rgba(0, 97, 255, 0.3);
        }
        
        .header-info h1 {
            color: #1a1a1a;
            font-size: 1.2rem;
            font-weight: 600;
        }
        
        .header-info p {
            color: #22c55e;
            font-size: 0.85rem;
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 4px;
        }
        
        .header-info p::before {
            content: '';
            display: inline-block;
            width: 8px;
            height: 8px;
            background: #22c55e;
            border-radius: 50%;
        }
        
        .chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 24px;
            display: flex;
            flex-direction: column;
            gap: 16px;
            background-color: #fafafa;
        }
        
        .chat-messages::-webkit-scrollbar { width: 6px; }
        .chat-messages::-webkit-scrollbar-track { background: transparent; }
        .chat-messages::-webkit-scrollbar-thumb { background: #e0e0e0; border-radius: 3px; }
        
        .message {
            max-width: 85%;
            padding: 14px 18px;
            font-size: 0.95rem;
            line-height: 1.5;
            animation: fadeIn 0.3s ease;
        }
        
        .message p { margin-bottom: 8px; }
        .message p:last-child { margin-bottom: 0; }
        .message ul, .message ol { margin-left: 20px; margin-bottom: 8px; }
        .message strong { font-weight: 600; }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(8px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .message.user {
            align-self: flex-end;
            background: #0061ff;
            color: #fff;
            border-radius: 20px 20px 4px 20px;
            box-shadow: 0 4px 10px rgba(0, 97, 255, 0.2);
        }
        
        .message.bot {
            align-self: flex-start;
            background: #ffffff;
            color: #333333;
            border-radius: 20px 20px 20px 4px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
            border: 1px solid #f0f0f0;
        }
        
        .examples {
            display: flex;
            flex-direction: column;
            gap: 8px;
            padding: 0 24px 10px;
            background-color: #fafafa;
        }
        
        .example-btn {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            color: #475569;
            padding: 12px 16px;
            border-radius: 12px;
            font-size: 0.9rem;
            text-align: left;
            cursor: pointer;
            transition: all 0.2s ease;
            font-family: 'Outfit', sans-serif;
            box-shadow: 0 2px 5px rgba(0,0,0,0.02);
        }
        
        .example-btn:hover {
            border-color: #0061ff;
            color: #0061ff;
            transform: translateY(-1px);
            box-shadow: 0 4px 10px rgba(0, 97, 255, 0.1);
        }
        
        .chat-input-area {
            padding: 20px 24px;
            background: #ffffff;
            border-top: 1px solid #f0f0f0;
            display: flex;
            gap: 12px;
            align-items: center;
        }
        
        #user-input {
            flex: 1;
            padding: 14px 18px;
            border-radius: 24px;
            border: 1px solid #e2e8f0;
            background: #f8fafc;
            color: #1e293b;
            font-size: 0.95rem;
            font-family: 'Outfit', sans-serif;
            outline: none;
            transition: all 0.2s;
        }
        
        #user-input::placeholder { color: #94a3b8; }
        #user-input:focus { border-color: #0061ff; background: #ffffff; box-shadow: 0 0 0 3px rgba(0, 97, 255, 0.1); }
        
        #send-btn {
            width: 48px;
            height: 48px;
            border-radius: 50%;
            border: none;
            background: #0061ff;
            color: #fff;
            font-size: 1.2rem;
            cursor: pointer;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        #send-btn:hover { transform: scale(1.05); box-shadow: 0 4px 15px rgba(0, 97, 255, 0.3); }
        #send-btn:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }
        
        .typing-indicator {
            display: none;
            align-self: flex-start;
            padding: 16px 20px;
            background: #ffffff;
            border-radius: 20px 20px 20px 4px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
            border: 1px solid #f0f0f0;
        }
        
        .typing-indicator span {
            display: inline-block;
            width: 6px;
            height: 6px;
            background: #0061ff;
            border-radius: 50%;
            margin: 0 2px;
            animation: bounce 1.4s infinite ease-in-out both;
        }
        
        .typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
        .typing-indicator span:nth-child(2) { animation-delay: -0.16s; }
        
        @keyframes bounce {
            0%, 80%, 100% { transform: scale(0.6); opacity: 0.6; }
            40% { transform: scale(1); opacity: 1; }
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">
            <div class="avatar">🛍️</div>
            <div class="header-info">
                <h1>BimBam Soporte</h1>
                <p>En línea para ayudarte</p>
            </div>
        </div>
        
        <div class="chat-messages" id="chat-messages">
            <div class="message bot">
                ¡Hola! 👋 Soy el asistente de atención al cliente de <strong>BimBam Buy</strong>. ¿En qué te puedo ayudar hoy con respecto a nuestras políticas o tus pedidos?
            </div>
            
            <div class="examples" id="examples">
                <button class="example-btn" onclick="sendExample(this)">📦 ¿Cuántos días tengo para devolver un producto?</button>
                <button class="example-btn" onclick="sendExample(this)">✈️ ¿Hacen envíos internacionales?</button>
                <button class="example-btn" onclick="sendExample(this)">🤝 ¿Cómo funciona el programa de afiliados?</button>
            </div>
        </div>
        
        <div class="typing-indicator" id="typing">
            <span></span><span></span><span></span>
        </div>
        
        <div class="chat-input-area">
            <input type="text" id="user-input" placeholder="Escribe tu consulta aquí..." autocomplete="off">
            <button id="send-btn" onclick="sendMessage()">➤</button>
        </div>
    </div>

    <script>
        const input = document.getElementById('user-input');
        const messages = document.getElementById('chat-messages');
        const typing = document.getElementById('typing');
        const sendBtn = document.getElementById('send-btn');
        const examples = document.getElementById('examples');
        
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !sendBtn.disabled) sendMessage();
        });
        
        function sendExample(btn) {
            input.value = btn.textContent.replace(/^[^\s]+\s/, ''); // Remove emoji for sending
            sendMessage();
        }
        
        async function sendMessage() {
            const text = input.value.trim();
            if (!text) return;
            
            if(examples) examples.style.display = 'none';
            
            const userMsg = document.createElement('div');
            userMsg.className = 'message user';
            userMsg.textContent = text;
            messages.appendChild(userMsg);
            
            input.value = '';
            sendBtn.disabled = true;
            
            typing.style.display = 'block';
            messages.appendChild(typing);
            messages.scrollTop = messages.scrollHeight;
            
            try {
                const res = await fetch('/ask', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ question: text })
                });
                const data = await res.json();
                
                typing.style.display = 'none';
                
                const botMsg = document.createElement('div');
                botMsg.className = 'message bot';
                
                // Usar marked para convertir Markdown a HTML
                botMsg.innerHTML = marked.parse(data.answer);
                
                messages.appendChild(botMsg);
            } catch (err) {
                typing.style.display = 'none';
                const errMsg = document.createElement('div');
                errMsg.className = 'message bot';
                errMsg.innerHTML = '⚠️ Lo siento, tuvimos un problema de conexión. Por favor, intenta de nuevo.';
                messages.appendChild(errMsg);
            }
            
            sendBtn.disabled = false;
            messages.scrollTop = messages.scrollHeight;
            input.focus();
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/ask', methods=['POST'])
def ask():
    if not agent_ready:
        return jsonify({"answer": f"⚠️ Error al inicializar el agente: {error_message}"})
    
    data = request.get_json()
    question = data.get('question', '')
    
    try:
        answer = agent.ask(question)
        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"answer": f"Ocurrió un error al procesar tu pregunta: {str(e)}"})

if __name__ == "__main__":
    print("=" * 50)
    print("🤖 Agente Virtual BimBam Buy")
    print("=" * 50)
    print("Abre tu navegador en: http://127.0.0.1:7860")
    print("Presiona Ctrl+C para detener el servidor")
    print("=" * 50)
    app.run(host="0.0.0.0", port=7860, debug=False)
