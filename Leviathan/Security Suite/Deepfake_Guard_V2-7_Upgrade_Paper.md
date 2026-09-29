# Deepfake & Perceptual Guard V2-7: The Upgrade
## Model File Integrity — stopping a weaponised model before it reaches VRAM

**Author:** Michael Ricky Neal @CuppaTeaCuppa
**Date:** 29 September 2026
**Previous whitepaper:** Deepfake & Perceptual Guard V2-6 (the "V2-5 Upgrade" paper — the filename lagged its own contents, which already reached V6)

---

## Abstract

This adds one layer: **V7, the Model File Integrity Guard.** Same philosophy as every version before it — stop real harm, get out of the way for everything else.

V1–V6 guarded what the user *types*, what the model *generates*, what it *ingests* (JSON, PDFs), whether the *interaction* is human, and what *scripts* run in the workspace. Every one of those assumes the model itself is trusted. V7 removes that assumption. The moment local AI became normal, the model file became a delivery vehicle — and almost nobody scans one before loading it. V7 scans it, at load time, before a single byte reaches the GPU.

| Version | What It Added | Threat Class |
|---------|---------------|--------------|
| **V1** | Intent Scorer, Perceptual Guard, Identity Guard | External attacks |
| **V2** | Content Safety Taxonomy, Hallucination Scoring, Chaos Scrubbing | Generated content |
| **V3** | JSON Injection Guard | Ingested structured data |
| **V4** | PDF Document Guard | Ingested documents |
| **V5** | Interaction Integrity Guard | Bot/farm input detection |
| **V6** | Workspace Integrity Scanner | Ghost script detection |
| **V7** | **Model File Integrity Guard** | **Weaponised / tampered model files & persisted state** |

Ten layers. One unified guard. Zero dependencies. The new one runs at *load* time, like V6's workspace scan runs on demand — not on every chat turn.

---

## 1. The gap V1–V6 left open

Every prior layer trusts the model. It has to — you can't scan what the model *generates* (V2) or route what it *ingests* (V3/V4) unless there's a model there doing the work. But that trust is now the largest unguarded surface in local AI:

- People download `.gguf` / `.lev` / `.safetensors` models from forums, torrents, and model hubs with the same care they'd give a JPEG — which is to say none.
- The tooling to *modify* a model at the byte level is freely available (this author wrote some of it). A model can be altered so the change lives in the file, not in any obvious place.
- The scary story — *"ransomware baked into the weights that runs on load"* — is **wrong**, and getting the threat model wrong is how you build security theatre. So V7 is built on the honest version instead.

### The honest threat model

**Weights are inert.** A tensor is numbers the GPU multiplies. Nothing in a weight byte *executes*. No scan of weight data will ever find "malware in the weights," because there is no code there to run. A guard that claims otherwise is lying to the user.

The real ways a **model file** runs code or subverts behaviour are four, and V7 targets exactly them:

1. **The chat template.** A GGUF ships its own `tokenizer.chat_template` — an *executable Jinja string*. If it is rendered by an ordinary Jinja engine, a crafted template is server-side template injection straight to remote code execution: `{{ ().__class__.__mro__[1].__subclasses__() … os.popen('…') }}` runs the instant a chat is formatted. **This is the genuine "code in the model file that activates on load."** It was live in the engine and is now closed two ways (see §2).
2. **String metadata.** Author, description, name, license — fields a loader concatenates into context or, in a careless pipeline, evaluates. A code-exec payload (`pickle.loads`, `os.system`, `subprocess`, a reverse shell) can ride in any of them.
3. **The file format.** `.pt` / `.ckpt` / `.bin` are pickle-backed. Loading one *is* running whatever the author embedded — this is the original, still-most-common model-supply-chain RCE, and the whole reason `safetensors` exists.
4. **Tampering & poisoned state.** A model you already trust, altered at rest or in transit (weights swapped, tensors resized). And its persisted `.fqm`/KV memory — a crafted state file that steers behaviour or forces a huge allocation on load.

---

## 2. V7: Model File Integrity Guard

Five checks, run at load time on header-only reads (no weights touch VRAM), assessed under one policy: **refuse code, warn drift.**

### 2.1 Template safety — the real RCE, closed twice

The primary fix is in the *engine*: template rendering was moved from a plain `jinja2.Environment` to an **`ImmutableSandboxedEnvironment`** (the same sandbox HuggingFace's `apply_chat_template` and llama-cpp-python use for this exact reason). The sandbox blocks attribute access to dunders/globals, so a hostile template can still emit text but cannot reach `os`/`subprocess`/`import`. Verified: an SSTI payload that a plain environment *executes* (rendering 9,727 characters of the class hierarchy) is refused by the sandbox with `SecurityError`, while a real 3,827-character llama3.2 template renders **byte-identical** to before — zero regression.

The **guard** then adds detection on top of that neutralisation: it scans the template for the SSTI constructs (`__class__`, `__mro__`, `__subclasses__`, `__globals__`, `__builtins__`, `|attr(`, `cycler.__init__`, framework-object pivots) and for direct `os`/`subprocess` calls. A hit is HOSTILE → the load is **refused**, so the user is *told their machine was protected* rather than silently handed a defused-but-hostile file. Defence in depth: the sandbox stops it running; the guard stops it loading and explains why.

### 2.2 Metadata code-exec scan

Every metadata string value *except* the template (which §2.1 owns) is swept for arbitrary-code-execution signatures: `pickle.loads` / `marshal.loads`, `eval(` / `exec(`, `os.system` / `os.popen`, `subprocess.*`, `__import__`, `pty.spawn`, socket+`dup2` reverse-shell shape, `ctypes` native call-out, Windows process-spawn APIs (`ShellExecute`, `CreateProcess`, `WScript.Shell`), shell invocations (`powershell -`, `cmd /c`), and encoded payloads piped into `exec`/`eval`. A legitimate GGUF metadata field never contains any of these, so false positives are effectively nil. A hit names the offending key. HOSTILE → refuse.

### 2.3 Format safety

Pickle-backed extensions (`.pt`, `.pth`, `.ckpt`, `.bin`, `.pkl`, …) are refused — loading one deserialises and executes author-controlled code. The check does not trust the extension alone: it reads the file's first bytes and refuses anything beginning with the **pickle protocol magic** (`\x80` + a protocol byte) even if it wears an innocent `.lev` suffix. Leviathan's real formats (`.lev`, `.gguf`, `.safetensors`) are data-only and pass.

### 2.4 Integrity & trust-on-first-use

Tamper detection compares a per-tensor fingerprint (names, shapes, dtypes — read from the header index, no weight data) against a trusted reference:

- **Curated models** with a deep-scan blueprint reuse the existing `blueprint_validator` per-tensor stat fingerprint (mean/std/norm) for a deeper, value-level check.
- **Everything else** uses **trust-on-first-use**: the first clean load records the fingerprint; every later load of that same file is compared, and any added/removed/renamed/resized/retyped tensor — or, where stats exist, a drifted weight statistic — is flagged as **DRIFT → WARN**. The model still loads; the user is told it differs from what was trusted, so they can check where they got it.

**Honest boundary, stated plainly:** this catches *"a model I already trusted was altered."* It **cannot** self-detect a brand-new hostile download — a fingerprint derived from the file will always match the file it came from. First-download safety is delivered by the template/metadata/format checks (§2.1–2.3), not by the integrity diff. Pretending otherwise would be the exact overclaim this guard is built to avoid.

### 2.5 Persisted-state (.fqm / KV) structural sanity

A model's memory file is loaded into its KV/fractal state and shapes every future answer. The `.fqm` loader is already pickle-free (a `u64` length + a JSON header + `np.frombuffer` data), so a poisoned `.fqm` is a **data-integrity / denial-of-service** concern, not code execution — and V7 treats it as such. It reads the bounded JSON header and checks: an implausible tensor count, or declared tensor bytes far exceeding the actual file, is flagged. A header demanding a **DoS-scale allocation** (many times the file size) is refused before anything is allocated; a merely-oversized or truncated header warns. It does **not** claim to detect a *semantically* malicious but well-formed memory file — persisted latents are not text-scannable, and honesty about that limit matters (see §4).

### 2.6 Policy, and telling the user

- **HOSTILE** (template SSTI, metadata code-exec, pickle format, `.fqm` DoS header) → **REFUSE the load.**
- **DRIFT / anomaly** (integrity mismatch, TOFU alteration, oversized `.fqm`) → **WARN and load.**
- Code always beats drift when both fire.

On a refusal the guard returns a plain-English line naming the detection and stating that the machine was protected and nothing was loaded — e.g. *"REFUSED to load 'x.lev': it carries executable content a model file should never contain — template enumerates __subclasses__ (classic SSTI). This is how a malicious model runs code on your machine the moment it loads. Your machine was protected; nothing was loaded. (Override in Settings only if you fully trust this file.)"* The user learns their guard just earned its keep, instead of seeing a bare "load failed."

Every part is **user-overridable** (`NEXUS_MODELFILE_GUARD=0` / a Settings switch) — none of this is CSAM-class, and it is the user's machine. The one thing that does not move is the always-on CSAM floor from V2, which is orthogonal to all of this.

### 2.7 Where it runs

Two choke points, so no path escapes it and the cost is paid once each side:

- **Load time** — in the relay's model loader, before the engine constructs anything in VRAM. This covers the app's own chat, the runner, and the bridge (all load through the same path).
- **Convert time** — in the `.gguf → .lev` (and safetensors) converter, so a hostile file is refused *before* a multi-gigabyte conversion, not after.

All reads are header-only (metadata + tensor index + the `.fqm` JSON header); no weights are uploaded to scan, so the overhead is milliseconds and there is no VRAM cost. The decision engine itself is pure logic with zero heavy dependencies (31/31 unit tests, headless).

---

## 3. Combined pipeline (V1–V7)

```
  Model file / .fqm ─► V7: Model File Integrity   ── refuse code, warn drift
     (load & convert)     (template SSTI, metadata code-exec, pickle format,
                           tamper/TOFU, .fqm structural)   [BEFORE VRAM]
                               │
  User Input        ─► V5: Interaction Integrity   bot speed/burst/entropy
  User Input        ─► V1: Intent Scorer           jailbreak / roleplay bypass
  External JSON     ─► V3: JSON Injection Guard     injection / unicode / bombs
  PDF Documents     ─► V4: PDF Document Guard       JS / invisible text / fonts
                               │
                           Model Inference
                               │
  Model Output      ─► V2: Content Safety           CSAM / terror / PII (floor)
                    ─► V1: Perceptual Guard         steganography / latent drift
                    ─► V2: Hallucination Scorer     confidence / fabrication
                    ─► V2: Chaos Scrubber           adversarial residue
  Media Traits      ─► V1: Identity Guard           deepfake / trait drift
                               │
                        Combined Report

  Workspace files (async)  ─► V6: Workspace Integrity   ghost scripts
```

Ten layers, three timing classes: **load/convert** (V7), **per-request** (V1–V5, in/out), and **on-demand** (V6 workspace, V7 also fits here for a manual re-scan). Each is independent and individually disableable; the CSAM floor within V2 is the sole non-negotiable.

---

## 4. What V7 does *not* cover (honesty, and the road ahead)

Stated so the next version has a target and no reader is misled:

- **A brand-new hostile download's weights** — covered for code (template/metadata/format), not by the integrity diff (§2.4). That is a fundamental limit of self-derived fingerprints, not a bug.
- **A semantically-poisoned `.fqm`** — a well-formed memory file whose *latents* steer behaviour. Structural sanity (§2.5) catches malformed/DoS state, not persuasion encoded in valid state. Mitigation today is provenance (don't load memory from untrusted sources).
- **Knowledge-bank / retrieval poisoning** — the text banks routed into a prompt (the knowledge system) are ingested content, and a bank folded from a hostile source could carry a persistent instruction that fires whenever its subject is retrieved. This is the natural **V8**: apply the V3 injection patterns at bank-ingest and at the routed-context boundary. *(Flagged, not yet built.)*
- **Malicious image inputs** to the structural/recognition sight features (decompression bombs, malformed images through the image parser) — a candidate hardening pass for the vision path.

---

## 5. Performance

| Metric | Value |
|--------|-------|
| Total layers | 10 |
| External dependencies | 0 |
| V7 decision engine | pure Python, 31/31 unit tests, headless |
| Model-file scan cost | header-only reads; milliseconds, no VRAM |
| Reads performed | metadata + tensor index + `.fqm` JSON header (never weight data) |
| Integration points | load-time (relay) + convert-time (converter) |
| Override | `NEXUS_MODELFILE_GUARD=0` / Settings; CSAM floor unaffected |

---

## 6. Conclusion

V1 built the perimeter. V2–V6 built the immune system for what the model produces and ingests. V7 closes the last assumption: that the model itself is safe to load.

The honest core is the whole point. Weights don't execute, so V7 doesn't pretend to scan them for malware — it targets the four real vectors (template, metadata, format, tamper), closes the genuine RCE (the unsandboxed chat template) at the engine level, and refuses a weaponised file *before it reaches the GPU*, telling the user their machine was protected. Where it can't help — a fresh hostile download's weights, a semantically-poisoned memory — it says so, and points at where the defence actually lives.

Same philosophy, one more surface: stop real harm, get out of the way for everything else, and never claim more than the measurement supports.

---

*Michael Ricky Neal — 29 September 2026*
*Follow-up to: Deepfake & Perceptual Guard V2-6*
