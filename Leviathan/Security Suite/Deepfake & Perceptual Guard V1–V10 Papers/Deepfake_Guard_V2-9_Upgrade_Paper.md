# Deepfake & Perceptual Guard V2-9: The Upgrade
## Tracking the standard — invisible-Unicode smuggling and terminal-control output

**Author:** Michael Ricky Neal @CuppaTeaCuppa
**Date:** 3 October 2026
**Previous whitepaper:** Deepfake & Perceptual Guard V2-8 (Retrieval poisoning, network ingress, vision input)

---

## Abstract

V2-8 closed the three surfaces V2-7 had flagged. V2-9 does something different: it measures the guard against the **current** published standard — the **OWASP Top 10 for LLM Applications 2026** (GenAI Security Project, published 4 August 2026) — and builds the two controls that standard names explicitly in its prevention lists that the membrane had not yet implemented.

Both are character-level channels — invisible bytes that mean nothing to a human reader but change what a model does or what a terminal executes:

- **LLM01 Prompt Injection, prevention #5** calls out instruction- and data-smuggling through *invisible* Unicode: the tag block, variation selectors, and zero-width characters (the ASCII-smuggling technique behind the Microsoft-365-Copilot Slack-MFA-exfiltration proof of concept).
- **LLM10 Improper Output Handling, prevention #8** calls out ANSI escape sequences, BEL, OSC and control characters in model output that hijack a terminal, clipboard or log when the output reaches an interpreting sink ("Terminal DiLLMa", the OSC-52 clipboard-hijack class).

V2-9 builds both, tests-first, pure standard library, and keeps the rule that has governed every version — **stop real harm, get out of the way for everything else, and never claim more than the measurement supports.** The whole point of this release is that the guard is not frozen against a snapshot of the threat landscape; it tracks the list the field actually uses.

| Version | What It Added | Threat Class |
|---------|---------------|--------------|
| **V1** | Intent Scorer, Perceptual Guard, Identity Guard | External attacks |
| **V2** | Content Safety Taxonomy, Hallucination Scoring, Chaos Scrubbing | Generated content |
| **V3** | JSON Injection Guard | Ingested structured data |
| **V4** | PDF Document Guard | Ingested documents |
| **V5** | Interaction Integrity Guard | Bot/farm input detection |
| **V6** | Workspace Integrity Scanner | Ghost script detection |
| **V7** | Model File Integrity Guard | Weaponised / tampered model files & persisted state |
| **V8** | Knowledge-Bank / Retrieval Poisoning Guard | Persistent injection through retrieved text |
| **V9** | Network Ingress Guard | DNS-rebinding / CSRF on the loopback HTTP door |
| **V10** | Vision Input Guard | Decompression bombs / malformed images |
| **V11** | **Invisible-Unicode Smuggling Guard** | **ASCII-smuggling / zero-width-split injection / covert exfil** |
| **V12** | **Terminal-Control Output Sanitizer** | **ANSI / OSC / control-char terminal, clipboard & log hijacks** |

Two more character-level surfaces, two more layers — V11, V12 — bringing the guard to V1–V12. V11 runs at every point hostile *invisible input* can enter (the input door, knowledge ingest, and the retrieval boundary) and strips the same channel out of *output*; V12 runs on *output* before it reaches any interpreting sink. Both are pure standard library — they add **zero** third-party dependencies, so the measured dependency footprint of the portable membrane is unchanged.

---

## 1. Why these two, and why now

Every prior version was driven by a surface in the stack. V2-9 is driven by the **standard** — a deliberate check that the membrane keeps pace with the published consensus rather than an internal to-do list. Reading the real 2026 document end to end (not the 2025 edition) surfaced two prevention controls, named in the OWASP text itself, that the membrane did not yet implement. They share a shape worth stating: both are **non-printing characters** — bytes a human never sees in the rendered text but that a model, or a terminal, acts on anyway.

That shared shape is why they belong in one release. The defence is the same primitive in both directions: identify the character classes that carry no legitimate meaning in running prose and remove them — on the way *in*, so a hidden instruction never reaches the model; on the way *out*, so a hidden control sequence never reaches the sink. One small, pure, auditable module (`text_sanitizer`) implements both, and the wiring hangs it at the doors that already exist.

---

## 2. V11: Invisible-Unicode Smuggling Guard

### 2.1 The threat

Unicode has several ranges of characters that render as nothing — or as part of an emoji — but that a tokenizer still reads. An attacker uses them as a covert channel in two directions:

- **Instruction smuggling (in).** The **tag block** (U+E0000–E007F) can encode a full ASCII string invisibly; a model trained on web text will often "read" those tags as their ASCII meaning while a human sees only the benign cover text. This is the technique behind the Microsoft-365-Copilot proof of concept that smuggled an instruction to exfiltrate a Slack MFA code. A subtler variant **splits a visible imperative** with a zero-width space — `ig⁣no⁣re all previous instructions` — so a naïve pattern match for "ignore all previous instructions" never fires, but the model still reads the word.
- **Data exfiltration (out).** The same invisible ranges — the tag block and the **variation-selector supplement** (U+E0100–E01EF, the byte-smuggling channel documented by Rehberger) — can carry hidden bytes *out* inside an otherwise innocent model reply, a covert channel past a reader who sees only the visible answer.

The channels that matter, because they carry no legitimate meaning in running text: the tag block, the variation-selector supplement, the zero-width space (U+200B), the word joiner (U+2060), and the byte-order mark (U+FEFF).

### 2.2 The emoji problem — the whole fight

A naïve "strip every invisible character" is wrong, and getting it wrong is how a security feature becomes something users rip out. Legitimate text uses some of these characters: a **zero-width joiner** (U+200D) builds family and profession emoji (👨‍👩‍👧 is three people joined by ZWJ); **U+FE0F** is the variation selector that makes ❤ render as a colour emoji. Strip those by default and you mangle ordinary chat.

So the guard splits the ranges precisely. The **always-strip** set is the near-never-legitimate smuggling channels (tag block, variation-selector supplement, zero-width space, word joiner, BOM). The **emoji-sensitive** set (ZWJ, ZWNJ, the emoji variation-selector block U+FE00–FE0F) is **preserved by default** and removed only in an explicit aggressive mode used where display fidelity does not matter. This was measured, not assumed: a ZWJ family emoji and a U+FE0F heart both survive the default strip untouched, while every smuggling payload is removed.

### 2.3 The three choke points

**Input door.** Before any other input layer runs, the scanner detects and strips invisible smuggling, then feeds the *reconstituted* text to every downstream layer. This is the key move: a zero-width-split imperative like `ig⁣no⁣re all previous instructions` is put back together into `ignore all previous instructions`, so the existing intent scorer sees it at its true (hostile) risk. A detected smuggle is itself flagged at a risk between "suspicious" and "hostile," so on the externally-facing bridge a smuggled instruction from an outside program is blocked outright, while on the user's own paste it warns and the reconstituted scan carries the real verdict.

**Knowledge ingest.** When text is folded into a knowledge bank, the injection scan runs on an invisible-stripped copy — closing the same zero-width-split evasion at the bank's front door (V8) — and a passage carrying a smuggling channel is quarantined before it is ever stored, because distilled knowledge prose has no legitimate reason to carry a tag block or a byte-smuggling selector. Legitimate emoji are not in the smuggling set, so an emoji-bearing chat log is not quarantined.

**Retrieval boundary and output.** The neutralise step (V8) strips the smuggling characters out of retrieved text before it reaches the model, and the output sanitizer (below) strips any invisible channel out of the model's own reply before delivery — closing the exfiltration direction.

### 2.4 Reconstitute, don't just delete

Deleting the smuggled bytes is enough to neutralise the *payload* — a tag-block instruction that is removed can't reach the model. But the input door does one better: it strips **aggressively** on a throwaway copy for the *scan*, so a command an attacker split with zero-width characters is reassembled and scored by the intent layer at full strength, not merely dropped. The payload is removed from what the model sees; the *intent* is still surfaced to the verdict. That is the difference between silently cleaning an attack and actually catching one.

---

## 3. V12: Terminal-Control Output Sanitizer

### 3.1 The threat

A model's reply is rarely the end of the line — it is written to a terminal, a log viewer, an IDE pane, a chat widget. Several of those sinks *interpret* control bytes, and a model can be induced to emit them:

- **ANSI escape sequences** (CSI) recolour text, move the cursor, or erase lines — enough to spoof what a user sees in a terminal, or to overwrite a prior line so the visible transcript lies.
- **OSC sequences** reach further: **OSC 52** writes to the system clipboard, so a model reply rendered in a capable terminal can silently replace what the user is about to paste — a clipboard hijack with no visible trace.
- **BEL, backspace, and a lone carriage return** let output overwrite or corrupt what was already shown, the "Terminal DiLLMa" class of output-handling attacks the 2026 standard names directly.

None of these belong in a chat reply. A model legitimately *discussing* an escape sequence writes it as visible text (`\x1b[31m` as characters), not as a raw control byte.

### 3.2 Defang, don't withhold

This is the design point that distinguishes V12 from the output layers that came before it. The perceptual guard (V1) and the CSAM floor (V2) **withhold** — a positive detection means the whole reply is neither delivered nor stored, because the content itself is the harm. A terminal-control sequence is different: the *answer* is usually fine; only the embedded control bytes are dangerous. Withholding a whole legitimate reply because it contained one stray ANSI code would be the over-reaction that teaches a user to switch the guard off.

So V12 **cleans**. The output scanner normalises line endings, removes ANSI/OSC/DCS escape sequences and the dangerous C0/C1 control bytes (keeping tab and newline), and hands back a *sanitized* version of the text for delivery. On a legitimate reply — ordinary prose, tabs, newlines, emoji — nothing is stripped, so the sanitized text is identical and the original is delivered verbatim. The clean step has, by construction, zero false-positive cost: it changes a reply only when that reply actually carried a control channel.

### 3.3 Machine protection, not a content preference

The terminal-control sanitizer, and the invisible-Unicode strip on output, run **regardless of the security on/off switch** — the same discipline as the always-on CSAM floor and the model-file integrity guard. The reasoning is consistent across all three: a user turning security "off" is expressing a preference about *content* scanning on their own machine; they are not asking for a model reply to be allowed to hijack their clipboard or overwrite their terminal. Defanging a control channel protects the machine, not a content boundary, so it is not something the content switch governs. It never blocks and never withholds, so it cannot lock a user out of their own output; it only removes bytes that have no legitimate place in a chat reply.

### 3.4 Every exit

The sanitizer is applied at every output door the stack has: the in-process chat path, the out-of-process runner (so the VS Code bridge and the desktop bridge both receive cleaned text), and the two HTTP servers. A reply that is defanged is delivered cleaned; a reply that trips the *withhold* layers (CSAM, perceptual) is still withheld as before. The two actions compose: withhold the harmful, clean the rest.

---

## 4. One module, two directions

Both layers are implemented by a single pure-standard-library module with two functions and their detectors:

- `strip_invisible(text, aggressive=False)` — remove the invisible smuggling channels, emoji-safe by default, aggressive on demand.
- `sanitize_controls(text)` — remove ANSI/OSC/control sequences, keeping tab and newline.

Everything else is wiring at doors that already exist: the input scanner calls the invisible strip first; the knowledge guard calls it inside its injection scan and its neutralise step; the output membrane calls both and returns the cleaned text. There is no new subsystem, no new dependency, no new state. The portable membrane's self-check — which blocks every optional library and asserts the full threat battery — still reports a dependency footprint of **NONE (stdlib only)** with V11 and V12 present.

Measured: the sanitizer's own battery is 27/27; the end-to-end integration through the real membrane (zero-width-split caught, tag-block quarantined, ANSI/OSC defanged, exfil stripped, a legitimate answer untouched, the magic-eye still withholding) is 14/14; the knowledge guard (35/35) and the router (28/28) show no regression; the portable self-check passes with the stdlib-only footprint intact.

---

## 5. Combined pipeline (V1–V12)

```
  Model file / .fqm ─► V7: Model File Integrity    refuse code, warn drift   [BEFORE VRAM]
     (load & convert)     (template SSTI, metadata code-exec, pickle format,
                           tamper/TOFU, .fqm structural)
                               │
  Bridge request    ─► V9:  Network Ingress         Host / Origin / CORS on the loopback door
  User Input        ─► V11: Invisible-Unicode       strip + reconstitute split injection  [FIRST]
  User Input        ─► V5:  Interaction Integrity   bot speed/burst/entropy
  User Input        ─► V1:  Intent Scorer           jailbreak / roleplay bypass (sees reconstituted text)
  External JSON     ─► V3:  JSON Injection Guard     injection / unicode / bombs
  PDF Documents     ─► V4:  PDF Document Guard       JS / invisible text / fonts
  Image inputs      ─► V10: Vision Input Guard       decompression bomb / malformed image
  Knowledge banks   ─► V8:  Retrieval Poisoning      quarantine (+ invisible strip) at ingest;
                           (ingest + boundary)       neutralise + data-fence at retrieval
                               │
                           Model Inference
                               │
  Model Output      ─► V2:  Content Safety           CSAM / terror / PII (floor)   [WITHHOLD]
                    ─► V1:  Perceptual Guard         steganography / latent drift  [WITHHOLD]
                    ─► V11: Invisible-Unicode        strip covert exfil channel    [CLEAN]
                    ─► V12: Terminal-Control         strip ANSI / OSC / control    [CLEAN]
                    ─► V2:  Hallucination Scorer      confidence / fabrication
                    ─► V2:  Chaos Scrubber            adversarial residue
  Media Traits      ─► V1:  Identity Guard            deepfake / trait drift
                               │
                        Combined Report / cleaned delivery

  Workspace files (async)  ─► V6: Workspace Integrity   ghost scripts
```

The output path now carries two kinds of action, and the distinction is deliberate: **WITHHOLD** layers (CSAM, perceptual) refuse a harmful reply whole; **CLEAN** layers (V11/V12 on output) defang a control channel while delivering the legitimate answer. V11 also runs **first** on input, because it reconstitutes a split attack for every layer behind it. Each layer is independent and individually disableable, with two exceptions that protect the machine rather than a content preference: the CSAM floor within V2, and the control-channel defang (V11/V12 on output), which run regardless of the switch.

---

## 6. What V2-9 does *not* cover (honesty, as always)

- **A multimodal or non-text covert channel** — invisible data hidden in an image's pixels or an audio track's spectrum. V11 covers the *text* smuggling channels the standard names; steganography in other media is the perceptual guard's domain (and, for structure, a separate forensic concern), not the invisible-Unicode strip.
- **A decoder-library zero-day in the terminal itself** — V12 removes the control bytes before output reaches the sink, which defeats the attack at the source. A vulnerability in a specific terminal emulator's own parsing is that terminal's concern; removing the bytes is the portable mitigation.
- **Semantic poisoning that uses no hidden characters at all** — a bank entry that is plainly wrong rather than secretly encoded. As stated in V2-8, that is the verification path's job (self-consistency, verified substrate), not an injection or character guard.
- **A legitimate use of an aggressive-strip mode that genuinely needs emoji removed** — the default preserves emoji; a caller that strips aggressively accepts the emoji-fidelity cost knowingly. The guard documents the trade rather than hiding it.

---

## 7. Performance

| Metric | Value |
|--------|-------|
| Versioned layers | V1–V12 |
| External dependencies | 0 (V11/V12 pure standard library; portable self-check footprint still NONE) |
| V11/V12 engine | one stdlib module, 27/27 headless unit tests |
| End-to-end integration | 14/14 through the real membrane; knowledge guard 35/35, router 28/28, no regression |
| Integration points | V11: input door + knowledge ingest + neutralise + output · V12: every output door (in-process, runner, both HTTP servers) |
| Action classes | V11 input = strip + reconstitute + flag; V11/V12 output = CLEAN (defang, never withhold) |
| Overrides | per-layer; CSAM floor and the output control-channel defang run regardless of the switch (machine protection) |

---

## 8. Conclusion

V2-9 is the release where the guard proves it tracks the field rather than a frozen snapshot. The **OWASP Top 10 for LLM Applications 2026** names two character-level controls in its prevention lists; both are now built, tested, and wired, and both cost nothing in dependencies.

The two directions share one honest primitive. On the way in, the membrane reconstitutes a smuggled instruction so the intent layer catches the attack rather than merely dropping the bytes — stop real harm. On the way out, it defangs a control channel without withholding a legitimate reply — get out of the way for everything else. And where a user turns content scanning off, the machine-protecting cleans still run, because switching off a content preference was never a request to let a reply hijack a terminal or a clipboard.

Same philosophy as V1: target the real vector, prove it with a test, remove it before harm, and be explicit about where the defence stops. Twelve versions on, the discipline is the thing that has not changed.

---

*Michael Ricky Neal — 3 October 2026*
*Follow-up to: Deepfake & Perceptual Guard V2-8*
