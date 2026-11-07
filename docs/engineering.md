# Engineering Notes — How DIANA Is Actually Built

This page documents the engineering decisions behind the claims in the main README. It is deliberately specific: a black-box case study is only credible when the hard parts are named.

## 1. The agent loop and why iteration is capped

A single user turn can require several tool calls (open an app, read the window, type, verify). The loop caps iterations at a small number (8) for two reasons: prevents runaway cost on a misbehaving model, and forces the agent to *report* instead of looping forever.

The loop is also stateless with respect to the tools — every result is appended to the message history with its `tool_call_id`, so the model can reason about what it already tried.

## 2. Failure taxonomy

Every tool returns the same shape, and every failure carries enough metadata for the agent to decide the next move:

| Field | Meaning | Agent behaviour |
|---|---|---|
| `ok` | did it actually work | only claim success when true |
| `error` | exact error string | quote it, never paraphrase into a success |
| `explained.cause` | root cause guess | explain to the user in plain language |
| `explained.can_autofix` | recoverable? | try a repair path if true |
| `explained.severity` | low / medium / high | decide whether to stop and ask |

This is the difference between "the agent failed" and "the agent failed *and told you why*".

## 3. The self-modification guard chain

Order matters. Each gate is cheap before the next, expensive one:

1. **Read before write.** Never edit from memory — the exact source is re-read.
2. **Surgical replace.** `old_string` → `new_string`, smallest possible span. Whole-file overwrite is forbidden by contract.
3. **AST parse.** Catches syntax errors before touching disk.
4. **Undefined-name analysis.** pyflakes catches the classic bug: a `def` removed while call sites remain, which breaks the backend at import time.
5. **Backup.** Copy of the original kept outside the project.
6. **Write.**
7. **Runtime test.** Import the module. If it raises, restore the backup automatically.
8. **Report.** Only after step 7 passes does the agent tell the user it worked.

Failure counter: after three consecutive rejections the agent stops and reports the exact error instead of retrying forever.

## 4. Grounding: how hallucination is prevented structurally

Prompt instructions alone are unreliable. The system uses three structural layers:

1. **Tool catalogue is the only source of capability.** If there is no measurement tool for CPU temperature, the model has no tool to call — so the correct answer is "I can't measure that".
2. **Results are injected as data, not prose.** The model receives `{"ok": false, "error": "..."}` and is instructed that a failed result can never be described as success.
3. **Numeric claims require a tool result in the same turn.** No tool call, no number. This is enforced in review: a reply containing a metric without a corresponding tool result is treated as a defect.

## 5. Context management for long sessions

Naive history concatenation degrades fast. The system keeps two layers:

- **Task layer**: what the user is asking *right now*, kept verbatim and small.
- **History layer**: compressed summaries of earlier turns, plus persistent memory entries.

Rules are injected from disk on every turn, so behaviour survives even when the conversation is summarised away.

## 6. Sensor design constraints

Sensors must be cheap: a window-title read and a few counters cost microseconds; a full process enumeration costs milliseconds and is therefore throttled. The limbic state is derived, not stored as truth — it is a hint for tone, never a gate for work.

## 7. Security layer trade-offs

- **False positives are the primary failure mode.** A security assistant that flags `chrome.exe` as suspicious is worse than useless, so a filter layer runs before the risk engine.
- **Quarantine, never delete.** Every action is reversible.
- **Optional LLM analyst.** Cloud explanation is opt-in; the whole layer works offline.

## 8. What was deliberately not built

- No cloud dependency for core capabilities.
- No autonomous destructive actions without explicit confirmation.
- No claim of screen understanding without a measurement step backing it.
- No "AGI" framing: the self-modification is scoped to project files and validated at every step.

## 9. Metrics that matter in this kind of system

If you are evaluating an agent like this, these are the numbers worth asking for:

- **Tool-call success rate** per tool, measured on real invocations (not unit tests).
- **Silent-failure rate**: cases where the agent claimed success and it was false. Target: zero.
- **Rollback rate** in self-modification: how often an edit is rejected. A healthy system rejects some — it means the guard works.
- **Time-to-recovery** after a failed step.
- **False-positive rate** of the security layer.
