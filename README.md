# DIANA — Autonomous AI Agent (Black-Box Case Study)

> **Nota:** Este repositório é uma **vitrine técnica (black-box)**. Ele documenta a arquitetura, os conceitos de engenharia e os desafios superados na construção da DIANA. **O código funcional principal não está aqui** — ele é proprietário. O que você encontra neste repo são diagramas, especificações de arquitetura e snippets genéricos que ilustram padrões de engenharia, sem expor a lógica de negócio.

---

## O que é a DIANA

A DIANA é uma **assistente de IA pessoal com corpo 3D, controle real de sistema operacional e auto-modificação de código**. Ela não é um chatbot: ela executa ações no PC do usuário (abre/fecha aplicativos, edita arquivos, executa scripts, controla dispositivos IoT, mede hardware), fala com o usuário por voz (STT + TTS), e tem um avatar 3D animado que expressa emoções e gestos.

O diferencial de engenharia está em três pilares:

1. **Orquestração de LLM com function calling real** — o modelo não "responde texto sobre o que faria"; ele emite tool calls estruturadas que são executadas no sistema, com resultado verificado e devolvido ao modelo.
2. **Segurança de código de auto-modificação** — a IA pode reescrever o próprio código, mas passa por um pipeline de validação que reverte automaticamente qualquer edição que quebre sintaxe, introduza nomes indefinidos ou falhe em teste real.
3. **Honestidade do agente (grounding)** — o agente nunca inventa medições ou resultados de ferramentas. Se uma skill não existe, ele admite e propõe instalá-la; se uma tool falha, ele reporta o erro exato.

---

## Arquitetura de Alto Nível

```
┌─────────────────────────────────────────────────────────────┐
│                    USUÁRIO (voz / chat / texto)             │
└───────────────────────────┬─────────────────────────────────┘
                            │
          ┌─────────────────▼─────────────────┐
          │   ELECTRON (Frontend Desktop)     │
          │  ─────────────────────────────    │
          │  • Janela de chat                 │
          │  • Avatar 3D (Three.js / GLB)     │
          │  • TTS playback                   │
          │  • Captura de áudio (STT)         │
          └─────────────────┬─────────────────┘
                            │  HTTP / WebSocket
          ┌─────────────────▼─────────────────┐
          │      FASTAPI (Backend Python)     │
          │  ─────────────────────────────    │
          │  • API REST + WS broadcast        │
          │  • Orquestrador de LLM            │
          │  • Skill Registry                 │
          │  • Tool Dispatcher                │
          │  • Pipeline de auto-modificação   │
          │  • Camada de regras de segurança  │
          └──────┬──────────────┬─────────────┘
                 │              │
     ┌───────────▼───┐   ┌──────▼────────────┐
     │  LLM Provider │   │  Sistema Windows  │
     │  (DeepSeek /  │   │  ───────────────  │
     │   Groq / etc) │   │  • Processos      │
     └───────────────┘   │  • Arquivos       │
                         │  • Hardware       │
                         │  • IoT (Tuya)     │
                         │  • Voz (SAPI/TTS) │
                         └───────────────────┘
```

Diagrama detalhado em [`docs/diagrams/architecture.md`](docs/diagrams/architecture.md).

---

## Pilares de Engenharia

### 1. Tool Calling com Verificação de Resultado

O orquestrador envia ao LLM um catálogo de ferramentas (41+ tools) com schemas JSON. O modelo escolhe quais chamar. Cada chamada retorna um objeto estruturado (`ok`, `result`, `error`, `explained`). O agente **só pode afirmar sucesso se `ok == true`** — regra imposta por prompt de sistema e validada no backend.

Snippet ilustrativo: [`snippets/tool_dispatch.py`](snippets/tool_dispatch.py)

### 2. Pipeline de Auto-Modificação Segura

A IA pode editar o próprio código-fonte. Para isso, toda escrita passa por:

1. **Validação de sintaxe** (AST parse) antes de gravar
2. **Checagem de nomes indefinidos** (pyflakes) — detecta funções removidas com chamadas órfãs
3. **Teste real pós-gravação** — importa o módulo; se falhar, a edição é **revertida automaticamente**
4. **Backup automático** antes de qualquer escrita

Snippet ilustrativo: [`snippets/safe_edit_pipeline.py`](snippets/safe_edit_pipeline.py)

### 3. Grounding / Anti-Alucinação

Regras de sistema impedem que o agente invente dados mensuráveis. Se o usuário pergunta "qual minha temperatura de CPU?" e não há skill de medição instalada, a resposta obrigatória é admitir e propor instalar — nunca estimar um número.

### 4. Avatar 3D com Estado Emocional

O backend emite um campo `emotion` na resposta (happy, excited, surprised, thinking, sad, angry, neutral). O frontend mapeia esse campo para animações de corpo inteiro (dance, greet, spin, peace sign, etc.) em um modelo GLB carregado via Three.js. O TTS é sincronizado com a boca do avatar (lip-sync por fonemas/visemas).

### 5. Voz Bidirecional

- **STT**: captura de áudio → transcrição (com fallback entre provedores)
- **TTS**: texto → fala, com remoção de marcação markdown antes da síntese (asteriscos viravam "asterisco" falado)
- Suporte a múltiplos idiomas (responde em inglês quando o usuário fala inglês)

### 6. Skill Registry Dinâmico

Skills são módulos Python descobríveis em runtime. O agente pode **criar novas skills** ao ser solicitado, registrá-las no registry e executá-las imediatamente. Isso permite evolução do sistema sem deploy.

### 7. Integração IoT Local

Descoberta e controle de dispositivos Tuya/Smart Life **sem cloud** (protocolo local UDP/TCP), com cenas multi-dispositivo (ex: "modo cinema" = apagar luzes + ligar TV).

---

## Desafios de Engenharia Superados

| Desafio | Solução |
|---|---|
| IA reescrevendo o próprio código e quebrando o backend | Pipeline de validação tripla com rollback automático |
| Alucinação de métricas de hardware | Regras de grounding + exigência de skill real para medição |
| Sincronização TTS ↔ animação labial | Mapeamento fonema→visema com fila de animação |
| Gestos corporais completos em tempo real | State machine de animações com blend e prioridade |
| Auto-diagnóstico de falhas de tool | Objetos de erro estruturados com `cause`/`action`/`can_autofix` |
| Contexto longo de conversa | Sistema de sumarização com foco em tarefa atual vs. histórico |
| Segurança de ações destrutivas | Confirmação obrigatória + quarentena de arquivos + whitelist de apps |

---

## Estrutura do Projeto (parcial, sem código proprietário)

```
ai-assistant-3d/
├── backend/
│   ├── app/
│   │   ├── api/              # Rotas REST + WebSocket
│   │   ├── core/             # Orquestrador LLM, dispatcher
│   │   ├── tools/            # Catálogo de 41+ ferramentas
│   │   ├── skills/           # Registry dinâmico de skills
│   │   │   ├── builtin/      # Skills nativas
│   │   │   └── generated/    # Skills criadas em runtime
│   │   ├── rules/            # Motor de regras de segurança
│   │   ├── memory/           # Memória persistente + diário
│   │   └── services/         # TTS, STT, visão, IoT
│   └── data/                 # Persistência (runtime, não versionada)
├── frontend/                 # UI do chat
├── electron/                 # Shell desktop + avatar 3D
└── regras/                   # Regras de comportamento (Markdown)
```

---

## Limites Conhecidos (Honestidade Técnica)

- O agente **não** tem visão de tela nativa — depende de ferramentas de medição para julgar resultados visuais.
- A qualidade do tool calling depende do provedor de LLM configurado.
- O avatar 3D exige GPU com suporte a WebGL.
- O controle IoT é local (mesma rede); não há ponte cloud.
- A auto-modificação tem escopo limitado a arquivos do projeto e passa por validação — não é "AGI se reescrevendo".

---

## Stack

**Backend:** Python, FastAPI, WebSockets, asyncio, pyflakes, AST
**Frontend:** Electron, JavaScript/TypeScript, Three.js, Web Audio API
**IA:** LLM via API (DeepSeek/Groq), function calling, STT/TTS
**Infra:** Windows, git, robocopy (backup), PowerShell (automação)

---

## Contato

Este é um case study de portfólio. Para discussão técnica sobre arquitetura de agentes autônomos, sinta-se à vontade para abrir uma issue.

**Autor:** Winston Pereira
**Projeto:** DIANA — Defense Intelligence Assistant
