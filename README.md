## Pokémon Trainer Assistant - HackTown 2026 (Casa AWS) 𓆩♡𓆪

> Projeto desenvolvido durante o **HackTown 2026** na **Casa AWS (AWS Developers House)**, expandindo o desafio oficial do workshop do [Strands Agents SDK](https://strandsagents.com/) com inteligência local via [Ollama](https://ollama.ai/).

---

### Sobre o Projeto

Durante minha participação no **HackTown 2026**, na **Casa AWS**, me propus a resolver o desafio do workshop de criação de um assistente Pokémon inteligente, que pude personalizar ao meu modo utilizando, em especial, as Eeveelutions.

---

### Escolha do parceiro Eeveelution

Em vez de um assistente qualquer, o treinador pode escolher como seu parceiro oficial qualquer uma das **8 evoluções do Eevee**:
- 🌙 **Umbreon** (*Dark*): Sereno, calmo, misterioso e especialista em estratégias de tanque defensivo.
- 💧 **Vaporeon** (*Water*): Adaptável, acolhedor e focado em suporte fluido e cura com água.
- ⚡ **Jolteon** (*Electric*): Enérgico, ágil, acelerado e focado em ofensiva elétrica relâmpago.
- 🔥 **Flareon** (*Fire*): Entusiasmado, caloroso, corajoso e focado em alto poder físico/fogo.
- 🔮 **Espeon** (*Psychic*): Intelectual, perspicaz, elegante e focado em vidência e ataque especial.
- 🍃 **Leafeon** (*Grass*): Harmonioso, amante da natureza e especialista em cura solar e ataques folha.
- ❄️ **Glaceon** (*Ice*): Preciso, calculista, frio e focado em controle de clima e gelo.
- 🎀 **Sylveon** (*Fairy*): Carinhoso, afetuoso, alegre e focado em laços de amizade e magia fada. 

Cada parceiro responde com tom personalizado, saudações próprias, especialidades competitivas e artes em Braille/ASCII.
O projeto utiliza uma integração completa via tools para buscar dados detalhados de Pokémon, cálculo de fraquezas e resistências de tipos, movimentos, habilidades, cadeias evolutivas e naturezas, utilizando a API PokéAPI.

---

### Simulador Web de WhatsApp Interativo (`whatsapp_bot.py`)
Um simulador completo de WhatsApp roda diretamente no navegador (`http://localhost:8000`) e permite conversar com o seu Pokémon parceiro com uma interface que reproduz a experiência de chat mobile, incluindo:

- Suporte a formatação rica (negrito, itálico, código e artes em Braille).
- Suporte a envio/simulação de mídias e comando `/reset` para reiniciar o fluxo ou trocar de parceiro.
- Preparado para produção com suporte a Webhooks oficiais da **Twilio** e da **Meta WhatsApp Cloud API**.
- Permite alternar fluidamente entre **Português (PT)** e **Inglês (EN)** tanto no terminal quanto no simulador WhatsApp.

---

### Pré-requisitos

Para não repetir detalhes já cobertos, os requisitos fundamentais de ambiente e infraestrutura foram minuciosamente explicados pelo criador original no documento **[README-inicial.md](README-inicial.md)**.

### Resumo Rápido do que é necessário:
- **Python 3.10+** instalado.
- **[Ollama](https://ollama.ai/)** instalado e em execução no seu computador.
  - Baixe o modelo Llama 3.1 com o comando:
    ```bash
    ollama pull llama3.1
    ```
- **Ambiente Virtual Python** com as bibliotecas necessárias:
  - `strands-agents[ollama]`
  - `uvicorn` e `starlette` (essenciais para o simulador do WhatsApp).

---

### Como funciona

Você pode colocar o projeto para rodar seguindo qualquer uma das abordagens abaixo:

#### Abordagem 1: Seguir a Jornada do Workshop Original
Se você deseja aprender passo a passo a evolução do agente desde o início, recomendamos conferir o **[README-inicial.md](README-inicial.md)** e seguir sequencialmente os roteiros na pasta **[steps/](steps/)**:
1. [Passo 1: Setup do Ambiente e Ollama](steps/01_setup.md)
2. [Passo 2: Hello World do Strands Agent](steps/02_hello_world.md)
3. [Passo 3: Criação de Ferramentas / Tools](steps/03_tools.md)
4. [Passo 4: Múltiplas Ferramentas e PokeAPI](steps/04_multi_tools.md)
5. [Passo 5: Memória e Sessões Persistentes](steps/05_memory.md)

---

#### Abordagem 2: Executar no Terminal (CLI)
Para conversar com seu assistente diretamente pelo prompt de comando:

```powershell
# No Windows (usando o ambiente virtual do projeto):
.\.venv\Scripts\python.exe app.py

# Ou ativando o venv:
# .venv\Scripts\activate  (Windows)
# source .venv/bin/activate  (Linux/macOS)
python app.py
```

---

#### Abordagem 3: Executar o Simulador Web de WhatsApp (Recomendado! 🌟)

Para uma experiência interativa muito mais imersiva, utilize o servidor com simulador de WhatsApp Web integrado:

#### 1. Verifique as dependências adicionais
Certifique-se de que o `uvicorn` e o `starlette` estão instalados no seu ambiente virtual:
```bash
pip install uvicorn starlette
```

#### 2. Inicie o servidor do bot
Execute o script do WhatsApp Bot apontando para o Python do seu `.venv`:

```powershell
.\.venv\Scripts\python.exe whatsapp_bot.py
```
*(ou `python whatsapp_bot.py` caso seu ambiente virtual já esteja ativado no terminal).*

#### 3. Abra no navegador
Após iniciar o servidor, abra em seu navegador:
**[http://localhost:8000](http://localhost:8000)**

#### 4. Como interagir:
1. **Escolha o idioma**: digite `1` ou `PT` para Português, ou `2` ou `EN` para Inglês.
2. **Escolha sua Eeveelution parceira**: digite o número correspondente (1 a 8) para escolher entre *Umbreon, Vaporeon, Jolteon, Flareon, Espeon, Leafeon, Glaceon ou Sylveon*.
3. **Explore e converse**: faça perguntas estratégicas como:
   - *"Quais são as fraquezas do tipo Fantasma?"*
   - *"Como funciona a habilidade Synchronize?"*
   - *"Qual a cadeia de evolução do Eevee?"*
   - *"Qual o melhor golpe para o meu parceiro em batalha?"*
4. **Trocar de parceiro / Reiniciar**: clique no botão superior **"🔄 Reiniciar Conversa"** ou envie a mensagem `/reset` no chat.

---

### Estrutura do Repositório

- `app.py`: Aplicação principal em linha de comando, contendo o catálogo completo das personalidades das Eeveelutions, artes em Braille, configuração do modelo Ollama e o loop do agente.
- `whatsapp_bot.py`: Servidor ASGI (Starlette + Uvicorn) contendo a interface web do simulador do WhatsApp, controle de sessão por usuário, persistência de preferências e endpoints de webhook.
- `tools_pokeapi.py`: Módulo de ferramentas do agente conectadas diretamente aos endpoints públicos da PokeAPI.
- `sessions/`: Armazenamento persistente das preferências dos treinadores e histórico de conversas.
- `steps/`: Tutoriais dos passos 1 ao 5 (e desafios extras) do workshop original.
- `README-inicial.md`: Documentação e orientações originais deixadas pelo criador do workshop.

---

### Agradecimentos e Créditos

- À equipe da **AWS Brasil** e aos instrutores presentes na **Casa AWS (HackTown 2026)** pelo workshop e apoio à comunidade de desenvolvedores.
- Ao criador original do workshop, **Luis Leão** ([repositório original](https://github.com/luisleao/strands-agents-pokemon-trainer)), cuja base serviu de ponto de partida para as implementações extras desenvolvidas neste repositório.
- Ao time do [Strands Agents](https://strandsagents.com/) pelo SDK ágil para construção de agentes autônomos. (*ᴗ͈ˬᴗ͈)ꕤ.ﾟ
⠀⠀⠀⠀