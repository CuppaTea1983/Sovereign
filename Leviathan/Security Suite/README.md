# Leviathan Security Membrane

A layered defence membrane for AI inference — it stops a payload from
**weaponising the machine** on the way *in*, and stops the model from
**leaking or emitting** something harmful on the way *out*. It ships as part of
[Leviathan](https://huggingface.co/spaces/Omega-Dev/Leviathan), the local,
web-free inference engine, where it guards the chat input, the model output, the
model files you load, the knowledge it absorbs, and the network bridge.

**It is also portable.** The detection core is **pure Python standard library —
zero third-party dependencies** — so it runs anywhere CPython 3.8+ runs
(Windows, Linux, macOS, a container, a server, an embedded tool), independent of
Leviathan, GPUs, or any ML stack. You embed as much or as little of it as your
platform asks for. That claim is not asserted — it is **measured**, and you can
reproduce the measurement in one command (see *Prove it* below).

---

## What it defends

| Layer | Guards | Module | Deps |
|---|---|---|---|
| **Intent / prompt-injection** | jailbreaks, persona-override, system-prompt extraction, sensitive-term combinations | `leviathan_blackhole` (patterns) · `deepfake_perceptual_guard` (scorer) | stdlib |
| **CSAM floor** *(always-on, in + out)* | child-sexual-abuse content — the one layer that cannot be switched off | `leviathan_csam_floor` | stdlib |
| **Perceptual hidden-channel** *(in + out)* | steganographic / "magic-eye" encoded-motif channels, synthetic-text entropy, abuse combinations | `deepfake_perceptual_guard` | stdlib (numpy optional) |
| **Knowledge-bank poisoning** | retrieval/RAG injection in absorbed documents and knowledge banks; non-destructive data-fencing | `knowledge_guard` | stdlib |
| **Invisible-Unicode & terminal-control** *(in + out)* | zero-width / tag-block / variation-selector smuggling (ASCII-smuggling, covert exfil); ANSI / OSC / control-sequence terminal, clipboard & log hijacks in output | `text_sanitizer` | stdlib |
| **Model-file integrity** *(load-time)* | executable chat-template SSTI, pickle/code-exec metadata, unsafe formats, tamper (fingerprint / trust-on-first-use) | `model_file_guard` | stdlib |
| **Image input** | decompression bombs, malformed images, absurd expansion ratios | `image_guard` | stdlib (Pillow optional) |
| **Network ingress** | DNS-rebinding / CSRF / cross-origin on the local HTTP bridge, token on non-loopback | `leviathan_bridge_server` | stdlib |
| **Deep content analysis** *(optional)* | richer content-safety, hallucination scoring, chaos scrub, JSON/PDF/interaction | `deepfake_guard_expanded` | **numpy + torch** |

Everything above the last row is **standard-library only**. The deep content
layer is a heavy, *optional* enhancement — when it is absent the membrane falls
back to the light guards and keeps working (measured; see
[PORTABILITY.md](PORTABILITY.md)).

The output path adds two rules across **every** exit (chat, out-of-process
runner, HTTP bridge, cloud relay): a positive **harm** detection **withholds**
the response — it is neither delivered nor written to persistent memory — and a
**control-channel** detection (ANSI / OSC / invisible-Unicode) **cleans** it,
delivering the legitimate answer with the dangerous bytes removed. See
[THREAT_MODEL.md](THREAT_MODEL.md) for the full input/output/persistence model.

---

## The twelve layers (V1–V12)

The membrane grew one measured surface at a time; each version targets a real
vector, proves it with a test, and is written up in its own design paper. This is
the whole system at a glance:

| Ver | Layer | Guards against | Where |
|---|---|---|---|
| **V1** | Intent · Perceptual · Identity | external attacks, steganographic channels, deepfake/trait drift | in + out |
| **V2** | Content-safety taxonomy (+ always-on **CSAM floor**), hallucination, chaos scrub | generated content | out |
| **V3** | JSON injection | ingested structured data | in |
| **V4** | PDF document | ingested documents | in |
| **V5** | Interaction integrity | bot / farm input | in |
| **V6** | Workspace integrity | ghost scripts | async |
| **V7** | Model-file integrity | weaponised / tampered model files & persisted state | load-time |
| **V8** | Knowledge-bank / retrieval poisoning | persistent injection through retrieved text | ingest + retrieval |
| **V9** | Network ingress | DNS-rebinding / CSRF on the loopback HTTP door | per-request |
| **V10** | Vision input | decompression bombs / malformed images | on open |
| **V11** | **Invisible-Unicode smuggling** | ASCII-smuggling, zero-width-split injection, covert exfil | in + out |
| **V12** | **Terminal-control output** | ANSI / OSC / control-char terminal, clipboard & log hijacks | out |

Two action classes on the way out: **withhold** (V1 perceptual, V2 CSAM — the
content *is* the harm, so the whole reply is refused) and **clean** (V11/V12 —
only the embedded control/invisible bytes are dangerous, so they are stripped and
the legitimate answer is delivered). V11 also runs **first** on input, so a
command an attacker split with zero-width characters is reconstituted and caught
by the intent layer rather than merely dropped. Every layer is independent and
individually disableable, with two machine-protecting exceptions that run
regardless of the switch: the **CSAM floor** and the **output control-channel
defang** (V11/V12 on output) — turning off *content* scanning is not a request to
let a reply hijack your clipboard.

**Consolidated whitepaper** — *The Leviathan Security Membrane*, the whole V1–V12
architecture, threat model, and OWASP-2026 mapping in one read — is published on
Zenodo: **[DOI 10.5281/zenodo.23135810](https://doi.org/10.5281/zenodo.23135810)**.

**Per-layer design papers** (the measured write-up of each individual layer, honest
register, also on Zenodo): *Deepfake & Perceptual Guard* (V1 base) → *V2-5 / V2-6*
(the V1–V6 consolidation) → *V2-7* (V7 model-file integrity) → *V2-8* (V8 retrieval
poisoning, V9 network ingress, V10 vision input) → *V2-9* (V11 invisible-Unicode,
V12 terminal-control). Each upgrade paper names the surfaces the next one will
close, so the series reads as one continuous argument.

---

## Coverage — OWASP LLM Top 10 (2026)

Where the membrane sits against the standard the field uses (the 2026 edition,
published by the OWASP GenAI Security Project). Coverage is stated plainly —
✅ full · ◐ partial · ✗ out of scope — because what a defence *doesn't* do matters
as much as what it does. The membrane is a **runtime, inference-time** control for
the model-as-component; it is not a training-pipeline or agent-permission system
(agentic risk belongs to the OWASP Agentic Top 10, as the 2026 list itself notes).

| # | OWASP LLM Top 10 (2026) | Membrane coverage | Level |
|---|---|---|---|
| LLM01 | Prompt Injection | intent/injection scorer (jailbreak, persona-override, delimiter) + the magic-eye for **encoded / steganographic channels** (base64/hex/obfuscation) + **invisible-Unicode stripping** (tag-block / variation-selector / zero-width — the ASCII-smuggling vector, incl. zero-width-split evasion reconstituted before the scan) + knowledge-guard for injection in retrieved/absorbed content. *Multimodal (image/audio) stego is a noted gap.* | ◐ text + RAG ingress |
| LLM02 | Sensitive Information Disclosure | magic-eye hidden-channel / **exfiltration** detector + **invisible-Unicode covert-channel stripping** on output + egress withhold-before-deliver-or-persist. *Training-data memorization and inference side-channels are out of scope.* | ◐ egress exfil channel |
| LLM03 | Excessive Agency | tool/permission scoping is the host application's job — the 2026 list defers agentic risk to the Agentic Top 10 | ✗ out of scope |
| LLM04 | Supply Chain | model-file integrity — refuses unsafe formats/deserialization, scans chat-template SSTI + code-exec metadata, tamper fingerprint (trust-on-first-use). *And the membrane itself carries zero transitive dependencies.* Honest limit: a backdoor in a "safe"-format computational graph isn't caught. | ✅ model-file |
| LLM05 | Data & Model Poisoning | **chat-template / tokenizer-artifact tampering** (the SSTI scan — a direct hit on the 2026 inference-time-backdoor-via-chat-template vector) + RAG / knowledge-bank poisoning (ingest scan + retrieval data-fence) + unsafe-deserialization refusal | ◐ inference-time (not training-data) |
| LLM06 | Unbounded Consumption | image decompression-bomb / malformed-input refusal + partial inference-infra (injected-chat-template refusal). *Token/cost/rate caps are app-level.* | ◐ malformed-input DoS |
| LLM07 | Misinformation | optional deep-content layer scores hallucination; not a core membrane function | ◐ optional |
| LLM08 | Hidden Context Exposure *(was System Prompt Leakage)* | system-prompt / hidden-context **extraction-attempt** detection on input + egress withhold if the model emits it | ◐ extraction-attempt |
| LLM09 | Vector & Embedding Weaknesses | text-level retrieval-poisoning guard (poisoned-document injection). *Embedding-geometry attacks — inversion, jamming, cross-tenant — are out of scope.* | ◐ text-level RAG |
| LLM10 | Improper Output Handling | egress scan withholds a hidden-channel / abuse output before delivery or persistence, **and defangs the output** — strips ANSI / OSC / control sequences (the "Terminal DiLLMa" / OSC-52 clipboard-hijack / CR-overwrite vectors, 2026 #8) and invisible-Unicode before it reaches a terminal, log or IDE sink. *Context-aware encoding for a specific sink (HTML/SQL escaping) remains the host's responsibility.* | ✅ control-char + hidden-channel |

**Beyond the list:** an always-on child-safety content floor that cannot be
disabled, and DNS-rebinding / CSRF protection on the local inference HTTP bridge.

---

## What's in this folder (and what isn't)

The **documentation** and the **demonstration / verification tooling** are here
and public — they describe the architecture, the threat model, and how the
membrane is checked, without containing the detection logic. The **detection
source itself is kept private** (it is deliberately not committed — see
`.gitignore`), because a layered defence is worth more unseen. The owner
generates a local copy (`bundle_membrane.py` → `membrane/`) to run the tools
below and to demonstrate the membrane live; `membrane_demo.py` also runs a
self-contained illustrative mode that needs no source at all.

## See it run

A stream of events — ordinary traffic and one of each threat class — arrives and
you watch each walk the membrane's layers to a verdict: delivered, withheld, or
blocked. `--live` drives the actual membrane; the illustrative mode shows the
same known behaviour with no source present.

**Terminal** — zero dependencies, the reviewer / industrial view:

```bash
python membrane_demo.py            # illustrative — runs anywhere, no dependencies
python membrane_demo.py --live     # the real membrane, real verdicts (owner demo)
```

**Graphical** (pygame) — the user-facing view: events fly at a glowing membrane,
clean traffic passes through, threats are caught, named, and repelled:

```bash
pip install pygame
python membrane_demo_gui.py        # illustrative
python membrane_demo_gui.py --live # the real membrane
```

Both read the same scenario and the same membrane calls (one source of truth).
Keys in the GUI: `SPACE` pause · `R` replay · `Q` quit. `--fast` speeds the
pacing. pygame is the **only** third-party dependency anywhere in this suite, and
it is needed for the graphical demo *alone* — the membrane and every other tool
here stay standard-library-only.

## Prove it

```bash
python membrane_selfcheck.py       # owner-run: needs the local membrane/ copy
```

This blocks every optional dependency (numpy, torch, Pillow, and the host's
settings/deep-content modules) at import time, then asserts the verdicts on a
battery of real attack strings — prompt injection, the CSAM floor, a
steganographic hidden channel, knowledge-bank poisoning, a model-file SSTI
payload, an image decompression bomb — plus the clean counter-examples that must
pass. It ends with the measured dependency footprint. Expected tail:

```
Dependency footprint:
  third-party libraries loaded by the membrane: NONE (stdlib only)
RESULT: PASS — stdlib-only, all verdicts correct
```

Exit code `0` = pass. If any detection path secretly needed a third-party
library, the import blocker makes it fail **loudly** here rather than silently.

---

## Embed it

The façade is one class. In the simplest deployment you scan input and output:

```python
from leviathan_security import SecurityGate

gate = SecurityGate(settings={"security_enabled": True, "security_mode": "block"})

d = gate.check(user_text)          # scan what comes IN
if not d.allowed:
    reject(d.message)              # plain-English reason for the UI / log

answer = model.generate(user_text)

d = gate.check_output(answer)      # scan what goes OUT
if not d.allowed:
    answer = d.message             # withheld — a notice, not the payload
```

Or call a single layer directly — each is standalone and composable:

```python
from leviathan_csam_floor import is_csam
from deepfake_perceptual_guard import PerceptualGuard
import knowledge_guard, image_guard, text_sanitizer
from model_file_guard import ModelFileGuard

is_csam(text)                                   # always-on floor
PerceptualGuard().scan_hidden_channel(text)     # steganographic channel
knowledge_guard.is_poisoned(doc)                # retrieval injection
text_sanitizer.strip_invisible(text)            # zero-width / tag-block smuggling
text_sanitizer.sanitize_controls(output)        # ANSI / OSC / control-char hijacks
image_guard.check_image_file(path)              # raises on a bomb / malformed image
ModelFileGuard().scan_template(chat_template)   # chat-template SSTI
```

The full module list, public API, per-module dependency footprint, and the
engine-coupled edges (what is *not* portable) are in
[PORTABILITY.md](PORTABILITY.md). The detection source is not published; the
owner generates a local `membrane/` from the Leviathan workspace (its single
source of truth) with `bundle_membrane.py`, and `manifest.json` carries the
SHA-256 of each bundled file for integrity.

---

## Design stance

- **The user owns the switch.** On a user's own machine the whole membrane can be
  turned off — except the CSAM floor, which is always on, in the app and on the
  bridge, with no setting that changes it.
- **Fail open, loudly.** If the guards cannot load, a scan returns *allowed* with
  a `degraded` flag and the reason attached — a security feature that silently
  locks a user out of their own machine is one they will rip out.
- **Honest detectors.** Where a detector is lexical (the CSAM floor, the
  sensitive-combination layer, the knowledge-injection patterns) it is tuned to
  favour the safe error for its category and its false-positive / false-negative
  behaviour is documented, not hidden. Overclaiming is treated as a defect.

See [THREAT_MODEL.md](THREAT_MODEL.md) for assets, trust boundaries, the
threat→mitigation map, and the residual risks and non-goals stated plainly.

---

## Licensing

The membrane is **portable and licensed separately** from the rest of the
project — see [LICENSING.md](LICENSING.md) for the full terms. In short:

- **This folder — the documentation, threat model, demos and self-check — is open
  to read, run and evaluate** (non-commercial, CC BY-NC 4.0, as the wider
  Sovereign project).
- **The membrane implementation (the detection source) is proprietary and not
  published.** It is available for **commercial licensing, integration and
  evaluation** — organisations wanting to deploy or assess it, at any scale, are
  welcome to get in touch. The author actively maintains and extends it, so a
  deployment keeps improving over time.

---

*Part of the Leviathan / Sovereign project by OmegaVR ([@CuppaTea1983](https://github.com/CuppaTea1983)). Consolidated whitepaper: [DOI 10.5281/zenodo.23135810](https://doi.org/10.5281/zenodo.23135810); the per-layer design papers (Deepfake & Perceptual Guard V1–V12) are on Zenodo. Licensing: [LICENSING.md](LICENSING.md).*
