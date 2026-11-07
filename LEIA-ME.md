# LEIA-ME (Português)

Este repositório é um **estudo de caso técnico (black-box)** da DIANA — uma assistente de IA pessoal que roda no desktop, controla o sistema operacional de verdade e reescreve o próprio código com segurança.

O código funcional **não está aqui** (é proprietário). O que você encontra são diagramas, especificações de arquitetura e trechos genéricos que ilustram padrões de engenharia sem expor lógica de negócio.

## O que a DIANA é

- Uma assistente que **executa** no PC: abre e fecha aplicativos, edita arquivos, roda scripts, controla dispositivos IoT e mede hardware.
- Uma interface viva: o backend emite um estado emocional e de atividade, e o frontend renderiza um **orbe de energia reativo** (WebGL) que muda de cor, pulso e turbulência conforme o humor e a tarefa em execução.
- Uma agente que **não mente**: só afirma sucesso quando a ferramenta retornou `ok == true`. Se falta uma skill, ela admite e propõe instalar.

## Pilares de engenharia

1. **Function calling com verificação de resultado** — o modelo emite chamadas de ferramenta estruturadas, que são executadas e cujo resultado real volta para o modelo.
2. **Auto-modificação segura** — toda edição de código passa por validação de sintaxe (AST), checagem de nomes indefinidos (pyflakes) e teste real de importação; se falhar, é revertida automaticamente.
3. **Grounding / anti-alucinação** — proibido inventar dados mensuráveis.
4. **Autonomia com iniciativa** — barramento de sensores, estado límbico e planejador de tarefas em etapas verificadas.
5. **Segurança local em 5 camadas** — monitor de processos, varredura de arquivos, auditoria de inicialização, filtro de falso positivo e motor de risco com analista LLM opcional.

## Documentação

- [`docs/diagrams/architecture.md`](docs/diagrams/architecture.md) — diagramas de fluxo
- [`docs/autonomy.md`](docs/autonomy.md) — sensores, estado e planejador
- [`docs/protection.md`](docs/protection.md) — camadas de segurança
- [`docs/voice.md`](docs/voice.md) — pipeline de voz (STT, correção, TTS)
- [`docs/roadmap.md`](docs/roadmap.md) — feito, próximo e não-objetivos

## Autor

Winston Pereira — arquiteto de produto e IA.
