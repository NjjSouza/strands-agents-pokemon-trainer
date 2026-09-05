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
    obter_textos_eevee,
)

PREFERENCES_FILE = Path("sessions/user_preferences.json")
PREFERENCES_FILE.parent.mkdir(parents=True, exist_ok=True)


def carregar_preferencias() -> dict:
    """Carrega as preferências salvas dos usuários."""
    if PREFERENCES_FILE.exists():
        try:
            return json.loads(PREFERENCES_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def salvar_config(
    user_id: str,
    partner: str | None = None,
    lang: str | None = None,
    awaiting_lang: bool | None = None,
    awaiting_partner: bool | None = None,
):
    """Persiste a escolha de parceiro, idioma e estado de navegação do usuário."""
    prefs = carregar_preferencias()
    cfg = prefs.get(user_id)
    if not isinstance(cfg, dict):
        cfg = {"partner": None, "lang": None, "awaiting_lang": True, "awaiting_partner": False}
    if partner is not None:
        cfg["partner"] = partner if partner else None
    if lang is not None:
        cfg["lang"] = lang
    if awaiting_lang is not None:
        cfg["awaiting_lang"] = awaiting_lang
    if awaiting_partner is not None:
        cfg["awaiting_partner"] = awaiting_partner
    prefs[user_id] = cfg
    PREFERENCES_FILE.write_text(json.dumps(prefs, ensure_ascii=False, indent=2), encoding="utf-8")


def obter_config_usuario(user_id: str) -> dict:
    """Retorna {'partner': ..., 'lang': ..., 'awaiting_lang': ..., 'awaiting_partner': ...}."""
    prefs = carregar_preferencias()
    cfg = prefs.get(user_id)
    if isinstance(cfg, dict):
        lang = cfg.get("lang")
        partner = cfg.get("partner")
        awaiting_lang = cfg.get("awaiting_lang", lang is None)
        awaiting_partner = cfg.get("awaiting_partner", (lang is not None and partner is None))
        return {
            "partner": partner,
            "lang": lang,
            "awaiting_lang": awaiting_lang,
            "awaiting_partner": awaiting_partner,
        }
    elif isinstance(cfg, str):
        return {"partner": cfg, "lang": "pt", "awaiting_lang": False, "awaiting_partner": False}
    return {"partner": None, "lang": None, "awaiting_lang": True, "awaiting_partner": False}


def resetar_config(user_id: str):
    """Remove a preferência do usuário para reiniciar o fluxo."""
    prefs = carregar_preferencias()
    if user_id in prefs:
        del prefs[user_id]
        PREFERENCES_FILE.write_text(json.dumps(prefs, ensure_ascii=False, indent=2), encoding="utf-8")


def prompt_selecao_idioma() -> str:
    """Mensagem oficial para seleção de idioma."""
    return (
        "🌐 *LANGUAGE / IDIOMA*\n\n"
        "Select your language / Escolha seu idioma:\n"
        "*1* ou *PT* - Português\n"
        "*2* ou *EN* - English\n\n"
        "_Digite 1 (ou PT) para Português / Type 2 (or EN) for English._"
    )


def prompt_erro_idioma() -> str:
    """Mensagem de erro amigável quando um número ou texto inválido for enviado durante a seleção de idioma."""
    return (
        "⚠️ *Opção de idioma inválida / Invalid language option!*\n\n"
        "Por favor, selecione seu idioma primeiro antes de escolher o Pokémon:\n"
        "Please select your language first before choosing a Pokemon partner:\n\n"
        "*1* ou *PT* - Português\n"
        "*2* ou *EN* - English\n\n"
        "_Digite 1 para Português ou 2 para English._"
    )


def formatar_confirmacao_parceiro(info: dict, lang: str = "pt") -> str:
    """Retorna o anúncio do parceiro com arte em Braille e orientações."""
    titulo, especialidade, _ = obter_textos_eevee(info, lang)
    if lang == "en":
        return (
            f"{info['emoji']} *{info['nome'].upper()}* ({info['tipo'].title()})\n"
            f"_{titulo}_\n\n"
            f"*Specialty:* {especialidade}\n\n"
            f"{info['art']}\n\n"
            f"🎉 Partner selected! Ask any question about Pokemon battle strategies, moves, or stats.\n"
            f"_Tip: Type *switch* to change partner, *lang* to change language, or *help* for commands._"
        )
    return (
        f"{info['emoji']} *{info['nome'].upper()}* ({info['tipo'].title()})\n"
        f"_{titulo}_\n\n"
        f"*Especialidade:* {especialidade}\n\n"
        f"{info['art']}\n\n"
        f"🎉 Parceiro selecionado! Faça qualquer pergunta sobre estratégias de batalha, golpes ou atributos Pokémon.\n"
        f"_Dica: Digite *switch* para trocar de parceiro, *lang* para alterar idioma ou *help* para comandos._"
    )


def mensagem_boas_vindas(lang: str = "pt") -> str:
    """Mensagem de boas-vindas com comandos e lista de Eeveelutions no idioma selecionado."""
    if lang == "en":
        linhas = [
            "🐾 *EEVEELUTION TACTICAL CENTER*",
            "",
            "Commands:",
            "• *menu* - List all Eeveelutions",
            "• *art* - View partner Braille art",
            "• *switch* - Change active partner",
            "• *lang* - Change language (PT/EN)",
            "• *help* - Show command instructions",
            "• *exit* - Reset partner and language",
            "",
            "Select your partner (number 1-8 or name):",
        ]
    else:
        linhas = [
            "🐾 *CENTRO TÁTICO EEVEELUTIONS*",
            "",
            "Comandos:",
            "• *menu* - Listar todas as Eeveelutions",
            "• *art* - Ver a arte em Braille do parceiro",
            "• *switch* - Trocar de parceiro ativo",
            "• *lang* - Alterar idioma (PT/EN)",
            "• *help* - Exibir instruções de comandos",
            "• *exit* - Reiniciar parceiro e idioma",
            "",
            "Escolha seu parceiro (número 1-8 ou nome):",
        ]

    for key, info in EEVEELUTIONS.items():
        linhas.append(f"*{key}* - {info['emoji']} *{info['nome']}* ({info['tipo'].title()})")
    return "\n".join(linhas)


def formatar_menu_eeveelutions(lang: str = "pt") -> str:
    """Gera o menu com as opções de Eeveelutions para escolha."""
    if lang == "en":
        linhas = [
            "🐾 *EEVEELUTION SELECTION*",
            "",
            "Select your partner (number 1-8 or name):",
        ]
        cmd_hint = "\nCommands: *menu* | *art* | *switch* | *lang* | *help* | *exit*"
    else:
        linhas = [
            "🐾 *SELEÇÃO DE EEVEELUTIONS*",
            "",
            "Escolha seu parceiro (número 1-8 ou nome):",
        ]
        cmd_hint = "\nComandos: *menu* | *art* | *switch* | *lang* | *help* | *exit*"

    for key, info in EEVEELUTIONS.items():
        linhas.append(f"*{key}* - {info['emoji']} *{info['nome']}* ({info['tipo'].title()})")
    linhas.append(cmd_hint)
    return "\n".join(linhas)


def processar_mensagem_usuario(user_id: str, texto: str, tem_midia: bool = False) -> str:
    """Processa a mensagem recebida e retorna o texto a ser enviado no WhatsApp/Simulador."""
    cfg = obter_config_usuario(user_id)
    lang = cfg.get("lang")
    partner_key = cfg.get("partner")
    awaiting_lang = cfg.get("awaiting_lang", lang is None)
    awaiting_partner = cfg.get("awaiting_partner", (lang is not None and partner_key is None))
    dados_eevee = EEVEELUTIONS.get(partner_key) if partner_key else None

    # 1. Tratamento de mídia
    if tem_midia:
        if lang == "en":
            return (
                "Media files are not supported. "
                "Please send your question as text regarding Pokemon battle strategies, stats, moves, or weaknesses."
            )
        return (
            "Arquivos de mídia não são suportados. "
            "Por favor, envie sua dúvida em formato de texto sobre estratégias, estatísticas, golpes ou fraquezas de Pokémon."
        )

    texto_limpo = texto.strip().lower()

    # 2. Reset / Reiniciar sessão (exit / reset / restart / quit / sair / reiniciar)
    if texto_limpo in ("exit", "quit", "sair", "reset", "restart", "reiniciar"):
        resetar_config(user_id)
        salvar_config(user_id, partner="", lang=None, awaiting_lang=True, awaiting_partner=False)
        despedida_txt = ""
        if dados_eevee:
            _, _, despedida = obter_textos_eevee(dados_eevee, lang or "pt")
            despedida_txt = f"{dados_eevee['emoji']} {despedida}\n\n"
        return despedida_txt + prompt_selecao_idioma()

    # 3. ETAPA 1: Seleção de idioma (novo usuário ou após comando 'lang')
    # Regra estrita: Enquanto awaiting_lang for True, nenhuma Eeveelution pode ser escolhida!
    if awaiting_lang or not lang:
        if texto_limpo in ("1", "pt", "portugues", "português", "1 - português", "1 - portugues"):
            salvar_config(user_id, lang="pt", awaiting_lang=False, awaiting_partner=True, partner="")
            return (
                "✅ *Idioma configurado para Português!*\n\n"
                + formatar_menu_eeveelutions("pt")
            )
        elif texto_limpo in ("2", "en", "english", "ingles", "inglês", "2 - english"):
            salvar_config(user_id, lang="en", awaiting_lang=False, awaiting_partner=True, partner="")
            return (
                "✅ *Language set to English!*\n\n"
                + formatar_menu_eeveelutions("en")
            )
        else:
            salvar_config(user_id, awaiting_lang=True, awaiting_partner=False)
            return prompt_erro_idioma()

    # 4. Comandos para trocar de idioma a qualquer momento
    if texto_limpo in ("lang", "language", "idioma"):
        salvar_config(user_id, awaiting_lang=True)
        return prompt_selecao_idioma()

    if texto_limpo in ("lang 1", "lang pt", "idioma pt", "idioma 1"):
        salvar_config(user_id, lang="pt", awaiting_lang=False)
        msg_aviso = "✅ *Idioma alterado para Português!*"
        if not partner_key:
            salvar_config(user_id, awaiting_partner=True)
            return f"{msg_aviso}\n\n" + formatar_menu_eeveelutions("pt")
        return f"{msg_aviso}\n\n" + (f"Continuando com {dados_eevee['emoji']} *{dados_eevee['nome']}*." if dados_eevee else "")

    if texto_limpo in ("lang 2", "lang en", "language en", "language 2"):
        salvar_config(user_id, lang="en", awaiting_lang=False)
        msg_aviso = "✅ *Language changed to English!*"
        if not partner_key:
            salvar_config(user_id, awaiting_partner=True)
            return f"{msg_aviso}\n\n" + formatar_menu_eeveelutions("en")
        return f"{msg_aviso}\n\n" + (f"Continuing with {dados_eevee['emoji']} *{dados_eevee['nome']}*." if dados_eevee else "")

    # 5. Comandos globais (menu, help, art)
    if texto_limpo in ("help", "ajuda", "commands", "comandos"):
        return mensagem_boas_vindas(lang)

    if texto_limpo in ("art", "arte", "desenho"):
        if not dados_eevee:
            hint = "Please select a partner first!\n\n" if lang == "en" else "Por favor, selecione um parceiro primeiro!\n\n"
            return hint + formatar_menu_eeveelutions(lang)
        titulo, _, _ = obter_textos_eevee(dados_eevee, lang)
        return (
            f"{dados_eevee['emoji']} *{dados_eevee['nome'].upper()}*\n"
            f"_{titulo}_\n\n"
            f"{dados_eevee['art']}"
        )

    # 6. Comandos de troca de parceiro (switch / trocar / menu)
    if texto_limpo in ("menu", "switch", "trocar", "parceiro"):
        salvar_config(user_id, awaiting_partner=True)
        return formatar_menu_eeveelutions(lang)

    # Suporte a troca direta com argumento, ex: 'switch 2', 'switch vaporeon', 'trocar jolteon'
    match_switch = re.match(r"^(?:switch|trocar|mudar)\s+(.+)$", texto_limpo)
    if match_switch:
        alvo = match_switch.group(1).strip()
        for key, info in EEVEELUTIONS.items():
            if alvo == key or alvo == info["nome"].lower():
                salvar_config(user_id, partner=key, awaiting_partner=False, awaiting_lang=False)
                return formatar_confirmacao_parceiro(info, lang)

    # 7. ETAPA 2: Seleção de parceiro (quando awaiting_partner=True ou quando ainda não escolheu parceiro)
    if awaiting_partner or not partner_key:
        for key, info in EEVEELUTIONS.items():
            if texto_limpo == key or texto_limpo == info["nome"].lower():
                salvar_config(user_id, partner=key, awaiting_partner=False, awaiting_lang=False)
                return formatar_confirmacao_parceiro(info, lang)

        # Entrada inválida durante a escolha do parceiro
        if lang == "en":
            return (
                "⚠️ *Invalid partner selection!*\n\n"
                "Please select your partner by typing a number (1-8) or name:\n\n"
                + formatar_menu_eeveelutions("en")
            )
        return (
            "⚠️ *Seleção de parceiro inválida!*\n\n"
            "Por favor, escolha seu parceiro digitando um número de 1 a 8 ou o nome:\n\n"
            + formatar_menu_eeveelutions("pt")
        )

    # 8. ETAPA 3: Conversa com o Agente de IA com Memória Persistente e PokeAPI
    id_sessao_limpo = re.sub(r"[^a-zA-Z0-9_-]", "_", user_id)
    
    session_manager = FileSessionManager(
        session_id=f"wa_{id_sessao_limpo}",
        storage_dir="./sessions",
    )

    system_prompt = criar_prompt_de_sistema(dados_eevee, lang=lang)

    agente = Agent(
        model=modelo,
        system_prompt=system_prompt,
        tools=TOOLS_DISPONIVEIS,
        session_manager=session_manager,
    )

    print(f"\n[Message from {user_id}]: {texto}")
    resultado = agente(texto)
    resposta_ia = str(resultado).strip()
    print(f"[Reply for {user_id}]:\n{resposta_ia}\n")

    return f"{dados_eevee['emoji']} *{dados_eevee['nome'].upper()}*:\n\n{dados_eevee['art']}\n\n{resposta_ia}"


def gerar_resposta_twiml(mensagem: str) -> Response:
    """Gera resposta no padrão TwiML XML para a API da Twilio."""
    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message><![CDATA[{mensagem}]]></Message>
</Response>"""
    return Response(content=twiml, media_type="application/xml; charset=utf-8")


# ---------------------------------------------------------------------------
# ROTAS DO WEBHOOK & API
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
        user_id = dados.get("from", "sim_local")
        texto = dados.get("message", "")
        tem_midia = bool(dados.get("has_media", False))
        
        resposta = processar_mensagem_usuario(user_id=user_id, texto=texto, tem_midia=tem_midia)
        return JSONResponse({"from": user_id, "reply": resposta})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)


async def api_reset_simulador(request: Request) -> Response:
    """Endpoint para reiniciar uma sessão no simulador."""
    try:
        try:
            dados = await request.json()
        except Exception:
            dados = {}
        user_id = dados.get("from", "") if isinstance(dados, dict) else ""
        if user_id:
            resetar_config(user_id)
            salvar_config(user_id, partner="", lang=None, awaiting_lang=True, awaiting_partner=False)
        return JSONResponse({"status": "ok", "reply": prompt_selecao_idioma()})
    except Exception:
        return JSONResponse({"status": "ok", "reply": prompt_selecao_idioma()})


async def pagina_inicial(request: Request) -> Response:
    """Interface web interativa para testes e orientações do WhatsApp Bot."""
    html = r"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Eeveelution Tactical Assistant</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background: #0b141a; color: #e9edef; display: flex; flex-direction: column; align-items: center; min-height: 100vh; padding: 20px; }
        .container { width: 100%; max-width: 620px; background: #111b21; border-radius: 12px; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.5); display: flex; flex-direction: column; height: 90vh; }
        .header { background: #202c33; padding: 14px 16px; display: flex; align-items: center; gap: 12px; border-bottom: 1px solid #222d34; }
        .header-icons { font-size: 1.15rem; letter-spacing: 2px; }
        .header h1 { font-size: 1.05rem; color: #00a884; font-weight: 600; }
        .btn-reset { margin-left: auto; background: #2a3942; color: #e9edef; border: 1px solid #3b4a54; padding: 6px 12px; border-radius: 6px; font-size: 0.82rem; cursor: pointer; transition: all 0.2s; }
        .btn-reset:hover { background: #ba1a1a; color: #fff; border-color: #ff5252; }
        .chat-box { flex: 1; padding: 20px; overflow-y: auto; display: flex; flex-direction: column; gap: 12px; background: #0b141a; background-image: radial-gradient(#202c33 1px, transparent 1px); background-size: 16px 16px; }
        .bubble { max-width: 85%; padding: 10px 14px; border-radius: 8px; font-size: 0.95rem; line-height: 1.4; word-break: break-word; white-space: pre-wrap; }
        .bubble.braille-art { font-family: "Consolas", "Courier New", monospace; line-height: 1.15; font-size: 0.82rem; }
        .bubble.bot { background: #202c33; color: #e9edef; align-self: flex-start; border-top-left-radius: 0; }
        .bubble.user { background: #005c4b; color: #e9edef; align-self: flex-end; border-top-right-radius: 0; }
        b, strong { font-weight: 700; color: #ffffff; }
        i, em { font-style: italic; color: #b5c3cb; }
        s, del { text-decoration: line-through; opacity: 0.8; }
        code.wa-inline-code { background: #202c33; border: 1px solid #2a3942; padding: 2px 6px; border-radius: 4px; font-family: "Consolas", monospace; font-size: 0.9em; color: #00a884; }
        pre.wa-code { background: #182229; border: 1px solid #222d34; padding: 8px 12px; border-radius: 6px; font-family: "Consolas", monospace; font-size: 0.85em; overflow-x: auto; margin: 6px 0; }
        .input-area { background: #202c33; padding: 12px; display: flex; gap: 8px; align-items: center; }
        input[type="text"] { flex: 1; background: #2a3942; border: none; color: #fff; padding: 12px 16px; border-radius: 8px; outline: none; font-size: 0.95rem; }
        .btn-media { background: #2a3942; color: #e9edef; border: none; padding: 10px 14px; border-radius: 8px; font-size: 1.15rem; cursor: pointer; transition: background 0.2s; display: flex; align-items: center; justify-content: center; }
        .btn-media:hover { background: #3b4a54; }
        .btn-send { background: #00a884; color: #111b21; border: none; padding: 10px 18px; border-radius: 8px; font-weight: bold; font-size: 0.95rem; cursor: pointer; transition: background 0.2s; display: flex; align-items: center; gap: 6px; }
        .btn-send:hover { background: #06cf9c; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="header-icons">🌙 💧 ⚡ 🔥 🔮 🍃 ❄️ 🎀</div>
            <div>
                <h1>Eeveelution Tactical Assistant</h1>
                <p style="font-size: 0.78rem; color: #8696a0;">Endpoint: <code>/whatsapp/twilio</code></p>
            </div>
            <button type="button" class="btn-reset" onclick="reiniciarConversa()" title="Reiniciar sessão e escolher idioma/parceiro novamente">🔄 Reiniciar</button>
        </div>
        <div class="chat-box" id="chat">
            <div class="bubble bot">🌐 *LANGUAGE / IDIOMA*

Select your language / Escolha seu idioma:
*1* ou *PT* - Português
*2* ou *EN* - English

_Digite 1 (ou PT) para Português / Type 2 (or EN) for English._</div>
        </div>
        <form class="input-area" id="form" onsubmit="enviarMensagem(event)">
            <input type="text" id="msgInput" placeholder="Digite 1 (PT) ou 2 (EN), comando ou estratégia..." autocomplete="off">
            <button type="button" class="btn-media" onclick="simularMidia()" title="Simular envio de foto/áudio">⛶</button>
            <button type="submit" class="btn-send" title="Enviar mensagem"><span>⌯⌲</span> Enviar</button>
        </form>
    </div>

    <script>
        const chat = document.getElementById('chat');
        const msgInput = document.getElementById('msgInput');

        // Garante isolamento de sessão para cada aba/visita no simulador web
        let userId = sessionStorage.getItem('trainer_sim_uid');
        if (!userId) {
            userId = 'sim_' + Date.now().toString(36) + '_' + Math.random().toString(36).substring(2, 7);
            sessionStorage.setItem('trainer_sim_uid', userId);
        }

        function escapeHTML(str) {
            return str
                .replace(/&/g, '&amp;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;')
                .replace(/"/g, '&quot;')
                .replace(/'/g, '&#039;');
        }

        function formatarWhatsApp(texto) {
            let html = escapeHTML(texto);

            // 1. Bloco de código: ```código```
            html = html.replace(/```([\s\S]*?)```/g, '<pre class="wa-code"><code>$1</code></pre>');

            // 2. Código inline: `código`
            html = html.replace(/`([^`\n]+)`/g, '<code class="wa-inline-code">$1</code>');

            // 3. Negrito: *texto*
            html = html.replace(/(^|[\s(>])\*([^*\n]+?)\*(?=[\s)<.,;:!?]|$)/g, '$1<b>$2</b>');

            // 4. Itálico: _texto_
            html = html.replace(/(^|[\s(>])_([^_\n]+?)_(?=[\s)<.,;:!?]|$)/g, '$1<i>$2</i>');

            // 5. Tachado: ~texto~
            html = html.replace(/(^|[\s(>])~([^~\n]+?)~(?=[\s)<.,;:!?]|$)/g, '$1<s>$2</s>');

            return html;
        }

        async function enviarMensagem(e) {
            e.preventDefault();
            const text = msgInput.value.trim();
            if (!text) return;

            adicionarBolha(text, 'user');
            msgInput.value = '';

            try {
                const res = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ from: userId, message: text })
                });
                const data = await res.json();
                adicionarBolha(data.reply, 'bot');
            } catch (err) {
                adicionarBolha('⚠️ Erro ao comunicar com o servidor.', 'bot');
            }
        }

        async function simularMidia() {
            adicionarBolha('⛶ [Foto/Mídia simulada]', 'user');
            try {
                const res = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ from: userId, message: '', has_media: true })
                });
                const data = await res.json();
                adicionarBolha(data.reply, 'bot');
            } catch (err) {
                adicionarBolha('⚠️ Erro ao comunicar com o servidor.', 'bot');
            }
        }

        async function reiniciarConversa() {
            try {
                await fetch('/api/reset', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ from: userId })
                });
            } catch (err) {
                console.warn('Erro no reset remoto:', err);
            }
            userId = 'sim_' + Date.now().toString(36) + '_' + Math.random().toString(36).substring(2, 7);
            sessionStorage.setItem('trainer_sim_uid', userId);
            chat.innerHTML = '';
            adicionarBolha(
                '🌐 *LANGUAGE / IDIOMA*\n\n' +
                'Select your language / Escolha seu idioma:\n' +
                '*1* ou *PT* - Português\n' +
                '*2* ou *EN* - English\n\n' +
                '_Digite 1 (ou PT) para Português / Type 2 (or EN) for English._',
                'bot'
            );
        }

        function adicionarBolha(texto, tipo) {
            const div = document.createElement('div');
            div.className = `bubble ${tipo}`;
            if (/[\u2800-\u28FF]/.test(texto)) {
                div.classList.add('braille-art');
            }
            div.innerHTML = formatarWhatsApp(texto);
            chat.appendChild(div);
            chat.scrollTop = chat.scrollHeight;
        }

        // Formata a mensagem inicial estática
        document.querySelectorAll('.bubble.bot').forEach(b => {
            b.innerHTML = formatarWhatsApp(b.innerText);
        });
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
    Route("/api/reset", endpoint=api_reset_simulador, methods=["POST"]),
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
