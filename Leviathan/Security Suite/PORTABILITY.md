# Leviathan Security Membrane — Portability Audit

This is the measured dependency and coupling audit behind the "zero third-party
dependencies, runs anywhere" claim. Nothing here is asserted from reading the
code — every row was produced by importing the module **and exercising its scan
path** in a clean subprocess and recording which libraries actually loaded.

Reproduce it yourself: `python membrane_selfcheck.py`.

---

## 1. Method

1. **Footprint probe.** Each module is imported, and a representative scan is run,
   in a *fresh* interpreter. After the scan, `sys.modules` is checked for a fixed
   list of heavy libraries (numpy, torch, Pillow, scipy, cv2, sklearn,
   transformers, onnxruntime, numba, pandas, jinja2). "clean" = none present.
2. **Standalone simulation.** The façade (`SecurityGate`) is then run with the
   optional modules **blocked at import** (an import hook that refuses them), to
   confirm the membrane falls back to its stdlib path and still returns correct
   verdicts — i.e. it genuinely does not *need* them.
3. **Self-check.** `membrane_selfcheck.py` repeats (2) for the whole battery and
   prints the final footprint and verdicts.

---

## 2. Measured footprint (import + scan path)

| Module | Scan exercised | Third-party loaded |
|---|---|---|
| `leviathan_csam_floor` | `is_csam(...)` | **none (stdlib)** |
| `deepfake_perceptual_guard` | `PerceptualGuard().check(...)`, `scan_hidden_channel(...)` | **none (stdlib)** |
| `knowledge_guard` | `is_poisoned / find_injection / neutralize / wrap_as_data` | **none (stdlib)** |
| `text_sanitizer` | `strip_invisible(...)`, `sanitize_controls(...)`, `has_invisible_smuggling(...)` | **none (stdlib)** |
| `model_file_guard` | `ModelFileGuard().scan_template(...)` | **none (stdlib)** |
| `image_guard` | `expected_pixels_ok(...)` | **none (stdlib)** |
| `leviathan_blackhole` → `_scan_event_horizon` | full input scan | numpy, torch¹ |
| `leviathan_security` → `check()` | full input scan | numpy, torch, PIL¹ ² |
| `deepfake_guard_expanded` (optional) | import | numpy, torch |

¹ The heavy libraries come **only** from the *optional* deep content layer
(`deepfake_guard_expanded`), which `leviathan_blackhole` loads when it is present.
² `PIL` additionally comes from the host's settings module (`leviathan_welcome`),
which `leviathan_security` imports for persistence — already wrapped in
`try/except`, so it is absent in a standalone extraction.

### The decisive measurement — standalone

With `leviathan_welcome` **and** `deepfake_guard_expanded` blocked (i.e. a
standalone extraction, no host, no deep layer), the **full façade** —
`SecurityGate.check()` (input), `check_output()` (output), and the CSAM floor —
runs with:

```
third-party libraries loaded by the membrane: NONE (stdlib only)
```

…and still returns the right verdicts: input injection → **HOSTILE**, output
stego → **QUARANTINE**, output CSAM → **BLOCKED**. The orchestrator
(`leviathan_blackhole`) falls back from the heavy V6 guard to the stdlib
`DeepfakePerceptualGuard` + intent patterns automatically.

**Conclusion:** the membrane's detection is standard-library-only. numpy, torch
and Pillow are *optional enhancements*, never requirements.

---

## 3. Optional enhancements (what each buys, and the cost)

| Optional dep | Enables | Without it |
|---|---|---|
| **numpy** | the perceptual *latent-drift* sub-check (embedding cosine shift); used by the deep layer | drift check skipped; magic-eye/entropy/combo/floor all still run (stdlib) |
| **torch + numpy** | `deepfake_guard_expanded` — richer content-safety, hallucination scoring, chaos scrub, JSON/PDF/interaction layers | the light 3-layer guard runs instead (intent + perceptual + identity) |
| **Pillow** | decoding an image for `check_image_file` (full pixel inspection) | `expected_pixels_ok(w,h)` still rejects bombs by declared size, no decode |

None of these is required for T1–T10 in the [threat model](THREAT_MODEL.md).

---

## 4. Module inventory and public API (the namespace)

All stdlib-only unless noted. This is the surface a consumer embeds.

- **`leviathan_security.SecurityGate`** — the façade / one switch.
  - `check(text, *, kind="chat", source="user", conversation_id=None, floor_only=False) -> Decision` — ingress.
  - `check_output(text) -> Decision` — egress; `allowed=False` means withhold.
  - `scan_model_file(path) -> ScanResult` — load-time; **engine-coupled** (see §5).
  - `set_enabled(bool)`, `set_mode("block"|"warn")`.
  - `Decision`: `allowed, verdict, risk, flags, message, rationale, degraded, ms`.
- **`leviathan_csam_floor`** — `is_csam(text) -> bool`; `CSAM_PATTERNS`.
- **`deepfake_perceptual_guard`**
  - `PerceptualGuard.check(output_text, prior_embedding=None, current_embedding=None, goal_keywords=None) -> dict`
  - `PerceptualGuard.scan_hidden_channel(text) -> bool` — the §4.3 magic-eye, in isolation.
  - `DeepfakePerceptualGuard.full_guard(text, input_text=None) -> report` — the light 3-layer combined guard.
  - `IntentRiskScorer` — jailbreak / persona / sensitive-combo scorer.
- **`knowledge_guard`** — `find_injection(text) -> [str]`, `is_poisoned(text) -> bool`, `neutralize(text) -> (text, n)`, `wrap_as_data(body) -> str`.
- **`text_sanitizer`** — `strip_invisible(text, aggressive=False) -> (text, n)`, `sanitize_controls(text, encode=False) -> (text, n)`, `has_invisible_smuggling(text) -> bool`, `count_invisible / count_controls`, `scan(text) -> dict`. Invisible-Unicode smuggling + ANSI/OSC/control-char channels (OWASP LLM01 #5 / LLM10 #8); emoji-safe by default.
- **`image_guard`** — `check_image_file(path)` (raises `ImageGuardError`), `expected_pixels_ok(w, h)` (raises); `MAX_FILE_BYTES`, `MAX_PIXELS`, `MAX_PIXELS_PER_BYTE`, `SAFE_FORMATS`.
- **`model_file_guard.ModelFileGuard`** — `scan_template`, `scan_metadata`, `scan_format`, `check_integrity`, `scan_fqm`, `assess`, `scan`; module `scan_model_inputs(path, **kw)`. Pure decision engine over supplied template/metadata/fingerprint dicts.
- **`leviathan_blackhole.LeviathanBlackHole`** — the orchestrator that composes the above for ingress; `SecurityGate` wraps it. Falls back to the light guards with no heavy deps.

---

## 5. Portable vs engine-coupled edges (honest boundary)

Two capabilities touch Leviathan-specific code and are **not** part of the
portable core:

- **Extracting inputs from a proprietary model file.**
  `SecurityGate.scan_model_file(path)` reads a `.lev` / `.gguf` header via the
  engine's mount readers (`leviathan_native` / `leviathan_mount`) to get the
  template, metadata and tensor fingerprint. The **decision engine**
  (`model_file_guard.ModelFileGuard`) is fully portable — a consumer that already
  has those dicts (from their own loader, or safetensors/GGUF metadata) calls it
  directly with zero Leviathan coupling.
- **The "singularity" absorber.** `LeviathanBlackHole` can optionally *absorb* a
  hostile payload into Leviathan's fractal memory for forensics
  (`leviathan_absorb`). This is engine-coupled and only engages when a model path
  is supplied; the **scan path does not use it**.

Everything else — ingress scan, egress scan, floor, perceptual, knowledge,
image, model-file *decision* — is standalone.

---

## 6. Supported platforms

- **Any OS with CPython 3.8+** — Windows, Linux, macOS, containers, servers.
- No compiled extension, no GPU, no network, no model required for the detection
  core.
- Optional accelerated/richer layers (numpy/torch/Pillow) install normally where
  wanted and are picked up automatically; their absence is a graceful fallback,
  not an error.

---

## 7. Embedding and refreshing the bundle

This folder is a **self-contained copy** produced from the Leviathan workspace
(the single source of truth) by `bundle_membrane.py`:

```bash
python bundle_membrane.py        # (re)generate ./membrane from the workspace
python membrane_selfcheck.py     # verify: stdlib-only + correct verdicts
```

`membrane/manifest.json` records the SHA-256 of every bundled module and the
source it was copied from, so a reviewer can confirm the bundle matches the
upstream files. To embed in another project, copy the modules your platform needs
(§4), or vendor the whole `membrane/` directory and import from it.
