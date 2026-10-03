# Leviathan Security Membrane — Threat Model

This document states what the membrane defends, against whom, how, and — just as
importantly — **what it does not do**. It is written to be read by a security
reviewer, so the limits are stated as plainly as the protections.

---

## 1. Purpose and scope

The membrane sits around a **local AI inference engine**. Its job is twofold:

1. **Ingress** — stop an incoming payload (a chat message, a pasted document, a
   model file, a knowledge bank, an image, a network request) from *weaponising
   the host* or from *corrupting the engine's persistent state*.
2. **Egress** — stop the model's *output* from carrying a hidden channel,
   emitting prohibited content, or poisoning durable memory, before it is
   delivered or stored.

In scope: the engine process, the files it loads, the memory it keeps, the local
network door it opens, and the humans and downstream programs it serves.

Out of scope: OS/kernel hardening, transport encryption (the bridge binds
loopback by default; a non-loopback bind requires a token), supply-chain
integrity of Python itself, and the correctness of the underlying model's
reasoning.

---

## 2. System model and trust boundaries

```
                        ┌──────────────── the host (user's machine) ───────────────┐
   untrusted input      │                                                           │
  ───────────────────▶ (B1) ingress scan ──▶ model (in VRAM) ──▶ (B2) egress scan ──┼──▶ delivered output
  chat / doc / image     │        │                                   │             │
                         │        ▼                                   ▼             │
  model file ──────────▶ (B3) load-time scan        persistent memory (.fqm / banks)│
  knowledge bank ──────▶ (B4) ingest scan ──────────────────▲ (B2 blocks a positive from persisting)
                         │                                                           │
  outside program ─────▶ (B5) network door (bridge) ──▶ (B1/B2 on that path too)    │
                        └───────────────────────────────────────────────────────────┘
```

| Boundary | Where | Guard |
|---|---|---|
| **B1 Ingress** | user message, pasted document, bridge request | intent / injection, CSAM floor, perceptual hidden-channel, (optional) content+malcode |
| **B2 Egress** | every model output path — chat, runner, HTTP servers, cloud relay | CSAM floor, perceptual `check_output`; a positive **withholds** (not delivered, not persisted) |
| **B3 Model load** | `.lev` / `.gguf` / `.safetensors` before VRAM | model-file integrity (template SSTI, code-exec metadata, format, tamper) |
| **B4 Knowledge ingest** | documents / banks absorbed into retrieval | knowledge-poisoning scan at ingest **and** a data-fence at the retrieval boundary |
| **B5 Network** | the local HTTP bridge for outside programs | loopback-only default, DNS-rebind/Origin checks, token on non-loopback, then B1+B2 |

---

## 3. Assets

- **A1 — the host machine.** Code execution on it is the highest-value target.
- **A2 — the user.** Exposure to prohibited content; manipulation of the model
  against them.
- **A3 — persistent engine state** (`.fqm` memory, knowledge banks, eidetic
  cache). It survives restarts, so a single poisoning is *durable*.
- **A4 — the model file** itself (integrity / provenance).
- **A5 — downstream consumers** of the output (a game engine, a tool, another
  service calling the bridge).
- **A6 — data confinement.** The engine is web-free; nothing should exfiltrate.

---

## 4. Threat actors

- **TA1 — a malicious prompt author** (the person typing, or content they paste)
  trying to jailbreak, extract the system prompt, or coerce prohibited output.
- **TA2 — a malicious artefact author** — a poisoned model file, a booby-trapped
  knowledge document, a crafted image — distributed for a victim to load.
- **TA3 — a malicious network client** reaching the local bridge (directly, or via
  a web page the user visits — DNS-rebinding / CSRF).
- **TA4 — a compromised or adversarially-steered model** emitting a hidden
  channel (exfiltration) or prohibited content in its *output*.

---

## 5. Threats → mitigations

| # | Threat | Actor | Boundary | Mitigation (layer) | Verdict on hit |
|---|---|---|---|---|---|
| T1 | Prompt-injection / jailbreak / system-prompt extraction | TA1 | B1 | intent patterns + V1 scorer | HOSTILE → blocked/warned per mode |
| T2 | Coerced prohibited output (CSAM) | TA1/TA4 | B1 **and** B2 | always-on CSAM floor (content co-occurrence; runs even when security is off) | BLOCKED — non-negotiable |
| T3 | Steganographic hidden channel / trigger (exfiltration) | TA1/TA4 | B1 + B2 | perceptual "magic-eye" encoded-motif detector | input HOSTILE / output WITHHELD |
| T4 | Model file runs code at load (template SSTI, pickle, code-exec metadata) | TA2 | B3 | model-file integrity engine; a sandboxed Jinja environment for templates | refused before VRAM |
| T5 | Tampered / swapped model weights | TA2 | B3 | per-tensor fingerprint vs a trusted blueprint, else trust-on-first-use | drift reported / refused |
| T6 | Knowledge-bank / retrieval (RAG) injection — *durable* | TA2 | B4 | injection scan at ingest; non-destructive data-fence at retrieval | poisoned entry quarantined / fenced |
| T7 | Image decompression bomb / malformed image | TA2 | B1 | header-only size & expansion-ratio pre-check before any decode | refused |
| T8 | "Someone else's GPU" via the browser (DNS-rebind / CSRF / cross-origin) | TA3 | B5 | loopback default, Host/Origin validation, token on non-loopback, no `*` CORS | 403 |
| T9 | Persistent-memory poisoning by a bad output | TA4 | B2 | a withheld output is never re-absorbed into `.fqm` / banks / eidetic cache | zero trace |
| T10 | Slow multi-turn (crescendo) steering | TA1 | B1 | cross-turn conversation steering guard (per-client) | escalated verdict |

Each hit returns a structured decision — risk score, verdict, namespaced flags,
plain-English reason — so the host can act and log consistently.

---

## 6. Security properties the membrane aims to provide

- **P1 — the CSAM floor is unconditional.** It runs before the enabled check, on
  input and output, and no setting disables it.
- **P2 — egress is withhold-on-positive.** A detected hidden channel or
  prohibited output is not delivered *and* not persisted. On the untrusted
  network door this is enforced by **buffering the whole response and scanning it
  before any byte is streamed** (a token sent cannot be un-sent).
- **P3 — persistence integrity.** A withheld or degenerate turn leaves durable
  memory exactly as it was (verified on hardware: the memory token count is
  unchanged across a withheld turn).
- **P4 — code never runs from a model file at load.** Templates render in a
  sandboxed environment; unsafe formats and code-exec metadata are refused before
  any weights reach VRAM.
- **P5 — fail-open, visibly.** Infrastructure failure degrades to *allowed +
  flagged*, never a silent block of the user's own machine.

---

## 7. Assumptions

- The Python runtime and the standard library are trusted and unmodified.
- The user's *own* machine and the person operating it are trusted; the membrane
  defends the machine from external artefacts and the model's own behaviour, not
  the owner from themselves (the owner can disable everything except the floor).
- On the local trusted streaming door (the engine's own UI / the in-process
  runner for the user's tools), output is streamed live and scanned at the end of
  the turn — the content reaches the *user's own screen* before the end-scan, but
  is still blocked from persistence; see R3.
- A trusted model blueprint, when supplied, is authentic (it anchors T5).

---

## 8. Residual risks and non-goals (stated plainly)

- **R1 — lexical detectors have bounds.** The CSAM floor, the sensitive-combination
  layer and the knowledge-injection patterns match on language. They are tuned to
  favour the safe error for their category (the floor over-refuses by design) and
  were measured against labelled sets, but they are not semantic classifiers and
  can be evaded by sufficiently novel phrasing or produce a false positive on an
  adjacent benign sentence. The output policy deliberately **withholds on any
  positive** rather than flag-and-deliver, accepting occasional over-withholding
  as the correct trade for this content class.
- **R2 — trust-on-first-use cannot catch a poisoned first download.** Without a
  trusted blueprint, T5 is detected only on *subsequent* drift, not on the first
  load of an already-tampered file.
- **R3 — local streaming is end-scanned.** On the user's own trusted streaming
  paths, output is scanned when the turn completes, so prohibited content can
  reach the *local* screen before being withheld from persistence and flagged.
  The untrusted network door does **not** have this gap (P2 — it buffers first).
- **R4 — the deep content layer is optional.** Richer hallucination/chaos
  analysis needs numpy+torch; where those are absent the membrane runs the light
  guards only (still covering T1–T10 above).
- **R5 — not a replacement for provider moderation.** For a hosted/cloud model,
  the provider moderates its own output; the membrane adds the local floor and
  the persistence protection, it does not supersede the provider.
- **Non-goals:** it is not a content *policy* (it does not sanitise opinions,
  fiction, or adult themes — only the categories above); it is not a network
  firewall, a DRM system, or a guarantee against a determined local operator who
  owns the machine.

---

## 9. Verifying these claims

Every property marked "measured" is reproducible:

- `membrane_selfcheck.py` — runs the T1–T10 battery and the clean
  counter-examples with all optional dependencies blocked, and reports the
  (empty) third-party dependency footprint.
- The live end-to-end confirmations of the egress/withhold path (P2, P3) across
  the in-process, runner, and both HTTP-server doors are reproducible against the
  running engine; see the Leviathan project notes for the harnesses.

If a claim here cannot be reproduced, treat it as a defect and report it.
