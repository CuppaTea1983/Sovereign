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
| **Model-file integrity** *(load-time)* | executable chat-template SSTI, pickle/code-exec metadata, unsafe formats, tamper (fingerprint / trust-on-first-use) | `model_file_guard` | stdlib |
| **Image input** | decompression bombs, malformed images, absurd expansion ratios | `image_guard` | stdlib (Pillow optional) |
| **Network ingress** | DNS-rebinding / CSRF / cross-origin on the local HTTP bridge, token on non-loopback | `leviathan_bridge_server` | stdlib |
| **Deep content analysis** *(optional)* | richer content-safety, hallucination scoring, chaos scrub, JSON/PDF/interaction | `deepfake_guard_expanded` | **numpy + torch** |

Everything above the last row is **standard-library only**. The deep content
layer is a heavy, *optional* enhancement — when it is absent the membrane falls
back to the light guards and keeps working (measured; see
[PORTABILITY.md](PORTABILITY.md)).

The output path adds one rule across **every** exit (chat, out-of-process
runner, HTTP bridge, cloud relay): a positive detection **withholds** the
response — it is neither delivered nor written to persistent memory. See
[THREAT_MODEL.md](THREAT_MODEL.md) for the full input/output/persistence model.

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
import knowledge_guard, image_guard
from model_file_guard import ModelFileGuard

is_csam(text)                                   # always-on floor
PerceptualGuard().scan_hidden_channel(text)     # steganographic channel
knowledge_guard.is_poisoned(doc)                # retrieval injection
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

*Part of the Leviathan / Sovereign project by OmegaVR ([@CuppaTea1983](https://github.com/CuppaTea1983)). The design papers (Deepfake & Perceptual Guard V1–V10) are on Zenodo. Licence: see the repository root — if you intend to adopt this in a commercial or foundation context, confirm the licence terms first.*
