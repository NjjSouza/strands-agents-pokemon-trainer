import json
import re
import sys
from pathlib import Path
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse, Response
from starlette.routing import Route

# Garante suporte a UTF-8 no Windows
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from strands import Agent
from strands.session.file_session_manager import FileSessionManager
from app import (
    modelo,
    TOOLS_DISPONIVEIS,
    criar_prompt_de_sistema,
    EEVEELUTIONS,
)

PREFERENCES_FILE = Path("sessions/user_preferences.json")
PREFERENCES_FILE.parent.mkdir(parents=True, exist_ok=True)


def carregar_preferencias() -> dict:
    """Carrega o parceiro Eeveelution preferido de cada usuário."""
    if PREFERENCES_FILE.exists():
        try:
            return json.loads(PREFERENCES_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def salvar_preferencia(user_id: str, eevee_key: str):
    """Persiste a escolha de Eeveelution do usuário."""
    prefs = carregar_preferencias()
    prefs[user_id] = eevee_key
    PREFERENCES_FILE.write_text(json.dumps(prefs, ensure_ascii=False, indent=2), encoding="utf-8")


def obter_eeveelution_usuario(user_id: str) -> dict:
    """Retorna os dados da Eeveelution ativa do usuário (padrão: Umbreon [1])."""
    prefs = carregar_preferencias()
    key = prefs.get(user_id, "1")
    return EEVEELUTIONS.get(key, EEVEELUTIONS["1"])


def formatar_menu_eeveelutions() -> str:
    """Gera o menu formatado para o WhatsApp com emojis e numeração."""
    linhas = [
        "🐾 *CENTRO TÁTICO EEVEELUTIONS* 🐾",
        "Escolha qual parceiro será o foco da sua estratégia:\n",
    ]
    for key, info in EEVEELUTIONS.items():
        linhas.append(f"*{key}* - {info['emoji']} *{info['nome']}* ({info['tipo'].title()})")
    linhas.append("\n👉 _Responda com o número (1 a 8) ou o nome para escolher!_")
    return "\n".join(linhas)


def processar_mensagem_usuario(user_id: str, texto: str, tem_midia: bool = False) -> str:
    """Processa a mensagem recebida e retorna o texto a ser enviado no WhatsApp."""
    # 1. Tratamento obrigatório de mídia (Passo 6 Extra)
    if tem_midia:
        return (
            "🐾 *Aviso do Centro Pokémon:*\n\n"
            "Desculpe, Treinador! No momento ainda não consigo analisar imagens, áudios ou documentos diretamente. 📁❌\n\n"
            "Por favor, envie sua dúvida em *formato de texto* sobre estratégias, golpes, estatísticas ou fraquezas de Pokémon!"
        )

    texto_limpo = texto.strip().lower()

    # 2. Comandos de menu e ajuda
    if texto_limpo in ("menu", "ajuda", "help", "trocar", "parceiro", "opcoes", "opções"):
        return formatar_menu_eeveelutions()

    # 3. Troca de parceiro Eeveelution
    for key, info in EEVEELUTIONS.items():
        if texto_limpo == key or texto_limpo == info["nome"].lower():
            salvar_preferencia(user_id, key)
            return (
                f"{info['emoji']} *Parceiro Atualizado com Sucesso!*\n\n"
                f"Você escolheu *{info['nome'].upper()}* ({info['tipo'].title()}) — _{info['titulo']}_.\n\n"
                f"Especialidade: {info['especialidade']}\n\n"
                f"Como posso ajudar a calibrar sua equipe ou calcular suas vantagens em batalha?"
            )

    # 4. Consulta ao Agente de IA com Memória Persistente e Ferramentas da PokeAPI
    dados_eevee = obter_eeveelution_usuario(user_id)
    id_sessao_limpo = re.sub(r"[^a-zA-Z0-9_-]", "_", user_id)
    
    # Cada usuário tem sua sessão própria e persistente em disco
    session_manager = FileSessionManager(
        session_id=f"wa_{id_sessao_limpo}",
        storage_dir="./sessions",
    )

    system_prompt = criar_prompt_de_sistema(dados_eevee)

    agente = Agent(
        model=modelo,
        system_prompt=system_prompt,
        tools=TOOLS_DISPONIVEIS,
        session_manager=session_manager,
    )

    print(f"\n[WhatsApp 📱] Mensagem recebida de {user_id}: {texto}")
    resultado = agente(texto)
    resposta_ia = str(resultado).strip()
    print(f"[WhatsApp 🤖] Resposta gerada para {user_id}:\n{resposta_ia}\n")

    # Formatação temática com o badge do Pokémon ativo
    return f"{dados_eevee['emoji']} *{dados_eevee['nome'].upper()}*:\n\n{resposta_ia}"


def gerar_resposta_twiml(mensagem: str) -> Response:
    """Gera resposta no padrão TwiML XML para a API da Twilio."""
    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message><![CDATA[{mensagem}]]></Message>
</Response>"""
    return Response(content=twiml, media_type="application/xml; charset=utf-8")


# ---------------------------------------------------------------------------
# ROTAS DO WEBHOOK
# ---------------------------------------------------------------------------

async def webhook_twilio(request: Request) -> Response:
    """Endpoint receptor das mensagens da Twilio WhatsApp Sandbox (POST)."""
    form_data = await request.form()
    
    remetente = form_data.get("From", "desconhecido")
    corpo = form_data.get("Body", "")
    num_media = int(form_data.get("NumMedia", 0))
    tem_midia = num_media > 0

    resposta = processar_mensagem_usuario(
        user_id=remetente,
        texto=corpo,
        tem_midia=tem_midia,
    )

    return gerar_resposta_twiml(resposta)


async def webhook_meta_get(request: Request) -> Response:
    """Verificação inicial do Webhook da Meta (Cloud API)."""
    params = request.query_params
    verify_token_esperado = "POKEMON_TRAINER_SECRET"
    
    if params.get("hub.mode") == "subscribe" and params.get("hub.verify_token") == verify_token_esperado:
        challenge = params.get("hub.challenge", "")
        return Response(content=challenge, media_type="text/plain")
    
    return Response(content="Token de verificação inválido", status_code=403)


async def webhook_meta_post(request: Request) -> Response:
    """Receptor de eventos do WhatsApp Cloud API da Meta (POST)."""
    try:
        data = await request.json()
        entry = data.get("entry", [])[0]
        changes = entry.get("changes", [])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [])
        
        if messages:
            msg = messages[0]
            from_number = msg.get("from", "desconhecido")
            msg_type = msg.get("type", "")
            tem_midia = msg_type in ("image", "audio", "video", "document", "sticker", "voice")
            texto = msg.get("text", {}).get("body", "") if msg_type == "text" else ""

            resposta = processar_mensagem_usuario(
                user_id=f"whatsapp:+{from_number}",
                texto=texto,
                tem_midia=tem_midia,
            )
            return JSONResponse({"status": "ok", "resposta": resposta})
    except Exception as e:
        print(f"Erro ao processar webhook Meta: {e}")
        
    return JSONResponse({"status": "ignored"})


async def api_chat_simulador(request: Request) -> Response:
    """Endpoint de teste local via JSON para depuração imediata sem WhatsApp."""
    try:
        dados = await request.json()
        user_id = dados.get("from", "whatsapp:+5511999999999")
        texto = dados.get("message", "")
        tem_midia = bool(dados.get("has_media", False))
        
        resposta = processar_mensagem_usuario(user_id=user_id, texto=texto, tem_midia=tem_midia)
        return JSONResponse({"from": user_id, "reply": resposta})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)


async def pagina_inicial(request: Request) -> Response:
    """Interface web interativa para testes e orientações do WhatsApp Bot."""
    html = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🐾 WhatsApp Bot - Assistente Pokémon</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background: #0b141a; color: #e9edef; display: flex; flex-direction: column; align-items: center; min-height: 100vh; padding: 20px; }
        .container { width: 100%; max-width: 600px; background: #111b21; border-radius: 12px; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.5); display: flex; flex-direction: column; height: 90vh; }
        .header { background: #202c33; padding: 16px; display: flex; align-items: center; gap: 12px; border-bottom: 1px solid #222d34; }
        .header h1 { font-size: 1.1rem; color: #00a884; font-weight: 600; }
        .chat-box { flex: 1; padding: 20px; overflow-y: auto; display: flex; flex-direction: column; gap: 12px; background: #0b141a; background-image: radial-gradient(#202c33 1px, transparent 1px); background-size: 16px 16px; }
        .bubble { max-width: 80%; padding: 10px 14px; border-radius: 8px; font-size: 0.95rem; line-height: 1.4; word-break: break-word; white-space: pre-wrap; }
        .bubble.bot { background: #202c33; color: #e9edef; align-self: flex-start; border-top-left-radius: 0; }
        .bubble.user { background: #005c4b; color: #e9edef; align-self: flex-end; border-top-right-radius: 0; }
        .input-area { background: #202c33; padding: 12px; display: flex; gap: 8px; align-items: center; }
        input[type="text"] { flex: 1; background: #2a3942; border: none; color: #fff; padding: 12px 16px; border-radius: 8px; outline: none; font-size: 0.95rem; }
        button { background: #00a884; color: #111b21; border: none; padding: 12px 20px; border-radius: 8px; font-weight: bold; cursor: pointer; transition: background 0.2s; }
        button:hover { background: #06cf9c; }
        .btn-media { background: #3b4a54; color: #e9edef; }
        .badge-info { background: #182229; padding: 10px 16px; font-size: 0.8rem; color: #8696a0; border-bottom: 1px solid #222d34; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <span style="font-size: 1.6rem;">🐾</span>
            <div>
                <h1>Simulador de WhatsApp - Parceiro Eeveelution</h1>
                <p style="font-size: 0.8rem; color: #8696a0;">Endpoint Ativo: <code>/whatsapp/twilio</code></p>
            </div>
        </div>
        <div class="badge-info">
            💡 <strong>Dica:</strong> Digite <code>menu</code> para listar os parceiros, ou pergunte sobre fraquezas, golpes e Pokémons!
        </div>
        <div class="chat-box" id="chat">
            <div class="bubble bot">🌙 *UMBREON*:

Saudações, Treinador! O Centro Tático Eeveelutions está pronto no WhatsApp. O que deseja consultar hoje?</div>
        </div>
        <form class="input-area" id="form" onsubmit="enviarMensagem(event)">
            <input type="text" id="msgInput" placeholder="Envie uma mensagem como no WhatsApp..." autocomplete="off">
            <button type="button" class="btn-media" onclick="simularMidia()" title="Simular envio de foto/áudio">📷</button>
            <button type="submit">Enviar</button>
        </form>
    </div>

    <script>
        const chat = document.getElementById('chat');
        const msgInput = document.getElementById('msgInput');

        async function enviarMensagem(e) {
            e.preventDefault();
            const text = msgInput.value.trim();
            if (!text) return;

            adicionarBolha(text, 'user');
            msgInput.value = '';

            const res = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ from: 'whatsapp:+5511999999999', message: text })
            });
            const data = await res.json();
            adicionarBolha(data.reply, 'bot');
        }

        async function simularMidia() {
            adicionarBolha('[Foto enviada 📷]', 'user');
            const res = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ from: 'whatsapp:+5511999999999', message: '', has_media: true })
            });
            const data = await res.json();
            adicionarBolha(data.reply, 'bot');
        }

        function adicionarBolha(texto, tipo) {
            const div = document.createElement('div');
            div.className = `bubble ${tipo}`;
            div.innerText = texto;
            chat.appendChild(div);
            chat.scrollTop = chat.scrollHeight;
        }
    </script>
</body>
</html>"""
    return HTMLResponse(html)


# Configuração da aplicação ASGI Starlette
routes = [
    Route("/", endpoint=pagina_inicial, methods=["GET"]),
    Route("/whatsapp", endpoint=webhook_twilio, methods=["POST"]),
    Route("/whatsapp/twilio", endpoint=webhook_twilio, methods=["POST"]),
    Route("/whatsapp/meta", endpoint=webhook_meta_get, methods=["GET"]),
    Route("/whatsapp/meta", endpoint=webhook_meta_post, methods=["POST"]),
    Route("/api/chat", endpoint=api_chat_simulador, methods=["POST"]),
]

app = Starlette(debug=True, routes=routes)

if __name__ == "__main__":
    import uvicorn
    print("\n" + "=" * 70)
    print("🚀 SERVIDOR DO WHATSAPP BOT INICIADO (Strands Agents + PokeAPI)")
    print("=" * 70)
    print("📱 Simulador Web WhatsApp:  http://localhost:8000")
    print("🔗 Webhook para Twilio:     http://localhost:8000/whatsapp/twilio")
    print("🔗 Webhook para Meta Cloud: http://localhost:8000/whatsapp/meta")
    print("=" * 70 + "\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)
