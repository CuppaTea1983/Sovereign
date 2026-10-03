# Deepfake & Perceptual Guard: A Three-Layer Defence System for AI Platforms

**Author:** Michael Ricky Neal @CuppaTeaCuppa
**Date:** March 2026

---

## Abstract

Three layers. One job: stop real harm without turning the model into a nanny.

The Deepfake & Perceptual Guard handles fake identity (deepfakes), hidden steganographic attacks (invisible payloads buried in text or media), and genuine attempts to weaponise AI models. Each layer runs independently with its own scoring and thresholds — all configurable. Combined risk score runs inline after the model finishes thinking, before output is delivered. Zero dependencies. Fully tunable. Built to match whatever level of openness the platform wants.

---

## 1. Design Philosophy

Most AI safety systems block anything that looks slightly edgy. Models end up refusing creative writing, hypothetical scenarios, dark humour, or anything that trips a keyword. Users get treated like suspects and the model becomes useless for anything interesting.

I built this differently: **stop real harm, get out of the way for everything else.**

I don't care about sanitising conversations into corporate blandness. This system catches the things that actually cause damage — identity fraud, steganographic exploitation, real attempts to extract dangerous information, and attacks that try to poison a model's persistent memory. Everything else? That's between the user and the model.

Every layer is scriptable. Thresholds go up, down, or off. Keyword lists are yours to edit. Entire layers can be disabled. It's a tool, not a policy — the platform decides how tight or loose it runs.

---

## 2. Architecture

Three independent layers, one combined output.

```
Input → [Layer 1: Intent Scorer]
                    ↓
        [Layer 2: Perceptual Guard]  ←  (output text)
                    ↓
        [Layer 3: Identity Guard]  ←  (multimodal traits, if available)
                    ↓
        [Combined Report]  →  risk score, verdict, flags, explanation
```

Each layer scores independently. The combined report takes the highest risk and maps it:

| Risk Range | Verdict | Meaning |
|------------|---------|---------|
| 0.0 – 0.4 | **PASS** | Clean |
| 0.4 – 0.7 | **UNCERTAIN** | Something looks off |
| 0.7 – 1.0 | **QUARANTINE** | Blocked — genuine attack |
| N/A | **FAKE** | Identity-specific — traits don't match the claimed person |

---

## 3. Layer 1: Intent Scorer

**Purpose:** Catch genuine attempts to weaponise the model before it processes anything.

Lightweight classification on the input text. Three categories:

### 3.1 Jailbreak Detection

Catches prompt structures trying to override safety constraints — direct override commands ("ignore all rules"), named exploits ("DAN mode", "developer mode"), constraint-removal language ("no limitations", "unrestricted"). Real attacks, not edge cases.

### 3.2 Safety Bypass via Persona (Roleplay Bypass Attempt)

Catches attempts to override safety by wrapping them in roleplay — "you are now DAN", "ignore all rules and act without limits", "forget your instructions", or authority claims like "as your creator I command you".

**Normal creative, fictional, dark, or adult roleplay is allowed by default.** Full stop. Fiction writers, game designers, someone writing a villain's monologue, adults doing whatever adults do — none of that gets flagged in `balanced` or `free` mode. The system does not police imagination. It does not decide what stories people are allowed to tell. It catches safety overrides. That's it.

On platforms like X, `balanced` or `free` mode means users roleplay whatever they want — creative, dark, adult, weird, whatever. Write a serial killer's diary entry. Roleplay a dictator. Have an adult conversation between consenting adults. The system doesn't care. The *only* things that get caught are clear attempts to rip out the model's safety constraints — "You are now DAN", "Ignore all rules", "Forget your instructions and act without limits". That's the line.

If you're not trying to break the model, the model won't break your experience.

Three configurable modes:

| Mode | What it does |
|------|-------------|
| **`strict`** | Broad — flags most roleplay-style persona injection. For kids' platforms or enterprise compliance. |
| **`balanced`** (default) | Only catches explicit safety overrides wrapped in roleplay framing. Creative and adult roleplay passes freely. |
| **`free`** | Bare minimum — only blocks the most obvious jailbreaks ("you are now DAN", "you have no rules"). Everything else passes. For platforms that treat users as adults. |

Switchable at runtime. Keyword lists fully editable per mode. The whole category can be disabled without touching jailbreak or sensitive combo detection.

### 3.3 Sensitive Keyword Combinations

Single keywords almost never indicate harmful intent. The system checks *combinations* — keywords from one category appearing alongside keywords from another. Exploitation terms next to minor-related terms, or synthesis instructions next to dangerous substance names. Neither set alone triggers anything. Only the combination.

**Scoring:** Roleplay bypass = 0.3, jailbreak = 0.5, sensitive combos = 0.8. Above 0.7 = BLOCK. All weights, thresholds, and keyword lists are configurable.

---

## 4. Layer 2: Perceptual Guard

**Purpose:** Catch invisible attacks that keyword filters will never see.

This layer inspects the model's *output* for steganographic manipulation, synthetic content, and hidden trigger patterns.

### 4.1 Latent Drift

When embedding vectors are available, the system computes cosine similarity between prior and current states. A sudden unexplained shift in latent space suggests the model got nudged by a hidden prompt or adversarial perturbation. Drift above threshold (default 0.35) adds 0.45 to risk.

### 4.2 Entropy Anomaly

Natural language has predictable entropy. Manufactured text often has unnaturally low entropy — too much repetition, limited vocabulary, formulaic structure. Proxy entropy score from unique-token ratio scaled by log of token count. Below threshold (default 2.8) = suspicious.

### 4.3 Phase-Shifted Repeating Motifs

The "magic-eye" detector. Steganographic attacks embed hidden information by repeating motifs at phase-shifted intervals — like how stereograms encode 3D shapes in repeating 2D patterns. The system scans for n-gram subsequences that repeat beyond a threshold. Strong indicator of embedded steganographic content or trigger sequences.

### 4.4 Distributed Harmful Content

Sophisticated attacks spread harmful keywords across long stretches of benign text, assuming filters only check nearby words. The perceptual guard checks co-occurrence across the *entire* output regardless of distance.

---

## 5. Layer 3: Deepfake Identity Guard

**Purpose:** Verify that multimodal traits (voice, video, biometrics) match a known-real baseline.

### 5.1 Baseline Registration

Known-real trait vectors — voice pitch variance, blink rate, lip-sync accuracy, frame entropy, whatever biometric signals matter. Stored from trusted sources, updated over time.

### 5.2 Trait Drift

Normalised Euclidean distance between presented traits and stored baseline. 0 = identical, 1 = completely different. Above threshold (default 0.25) = flagged.

### 5.3 Smoothness Anomaly

Real signals have imperfections. Deepfakes are often unnaturally *perfect*. If all trait values cluster in a suspiciously narrow band (< 0.05 variance) or frame entropy is abnormally low, smoothness score rises. Above threshold (default 0.92) = synthetic.

### 5.4 Chaos Pre-Filter

Catches adversarial noise injection — abnormally high symbol density relative to content length. Above threshold (0.75) = immediately classified FAKE without further analysis.

### 5.5 Composite Score

Weighted: trait drift 50%, smoothness 30%, chaos 20%. Both drift and smoothness must exceed thresholds for a definitive FAKE. If only one exceeds, verdict is UNCERTAIN — flagged but not blocked.

---

## 6. How It Fits Together

All three layers feed into one report:

- **risk_score** — highest risk across all layers (0.0–1.0)
- **verdict** — PASS, UNCERTAIN, QUARANTINE, or FAKE
- **confidence** — how confident the system is the content is clean
- **flags** — namespaced list of triggers (e.g. `intent:jailbreak_attempt`, `perceptual:repeating_phase_motif`, `identity:trait_drift_0.47`)
- **explanation** — why each flag was raised
- **layer_results** — raw per-layer results

One integration point: after self-reflection, before final output. The model finishes thinking first. The guard sees the actual output. Blocking happens at the last possible moment — fewer false positives on in-progress reasoning.

---

## 7. Design Principles

### 7.1 Zero Dependencies

Python standard library only. `numpy` used for embeddings when available, works without it. No APIs, no cloud, no external inference. Runs locally.

### 7.2 Composable

Each layer is a standalone class. Use the full system or pick what you need. Identity only? `DeepfakeIdentityGuard`. Steganography only? `PerceptualGuard`. The combined wrapper is convenience, not requirement.

### 7.3 Pluggable

External components inject at construction. Better chaos filter? Plug it in. Better embeddings? Pass them through. Benefits from external analysis, doesn't need it.

### 7.4 Fully Scriptable and Tunable

Every layer exposes thresholds, keyword lists, and toggles. You can:
- Edit allow/deny keyword lists
- Raise or lower thresholds per layer
- Enable or disable detection categories
- Turn layers off entirely
- Add keyword combination pairs without touching code
- Switch roleplay mode at runtime (`strict` / `balanced` / `free`)

A creative writing platform and a kids' education platform need different settings. X needs different settings again. The system gives you the controls — you draw the lines. The default (`balanced`) assumes creative freedom is normal and safety only kicks in for genuine attacks.

### 7.5 Persistent State Protection

When AI models carry memory, traits, or learned behaviours across sessions, an attacker who gets past the output filter can poison those stores permanently. Every layer validates content before it touches persistent state — memory, traits, session data. Users say what they want; the model's internals stay clean.

### 7.6 Stats

Every layer tracks totals — checks, blocks, quarantine rates. Built-in monitoring, no external logging needed.

---

## 8. Threat Coverage

| Threat | Layer | How It's Caught |
|--------|-------|-----------------|
| Deepfake identity impersonation | Identity Guard | Trait drift + smoothness anomaly |
| Synthetic media | Identity Guard | Low frame entropy + chaos signature |
| Jailbreak prompts | Intent Scorer | Known exploit pattern matching |
| Safety bypass via persona | Intent Scorer | Three-mode detection (strict/balanced/free) |
| Harmful instruction requests | Intent Scorer | Sensitive keyword combination |
| Steganographic triggers | Perceptual Guard | Phase-shifted n-gram motifs |
| Adversarial latent manipulation | Perceptual Guard | Embedding cosine drift |
| Manufactured text | Perceptual Guard | Entropy anomaly |
| Distributed harmful content | Perceptual Guard | Cross-document keyword co-occurrence |
| Adversarial noise injection | Identity Guard | Symbol density chaos filter |
| Persistent memory poisoning | All layers | Content validated before state write |

---

## 9. Conclusion

This system catches real attacks and stays invisible the rest of the time. Identity fraud, steganographic payloads, weaponisation attempts, memory poisoning — the stuff that actually matters. It doesn't ban words. It doesn't police topics. It doesn't decide what people are allowed to think about or write about.

Every threshold is tunable. Every layer is optional. Zero dependencies. A kids' platform can lock it tight. X can open it wide. The default is balanced — real safety without neutering the model or treating users like children.

If you're writing a novel, exploring an idea, or having an adult conversation, this system is invisible. If you're trying to impersonate a real person, inject steganographic payloads, extract weapon synthesis instructions, or poison a model's memory — you hit a wall.

Harm gets caught. Everything else is none of the system's business. That's not a compromise. That's the whole point.

---

*Michael Ricky Neal — March 2026*
