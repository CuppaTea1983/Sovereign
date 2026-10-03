# Licensing — Leviathan Security Membrane

The security membrane is **portable** and licensed **separately** from the rest
of the Leviathan / Sovereign project. This file is the single source of truth for
its terms.

## Two parts, two treatments

**1. The public artifacts in this `Security Suite/` folder** — the documentation
(`README.md`, `THREAT_MODEL.md`, `PORTABILITY.md`), the demonstrations
(`membrane_demo.py`, `membrane_demo_gui.py`), the self-check
(`membrane_selfcheck.py`) and the bundler (`bundle_membrane.py`):

> Published for **evaluation and education** under **Creative Commons
> Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)** — the same licence
> as the wider Sovereign project. You may read, run, and share them
> non-commercially with attribution. They describe and exercise the membrane;
> they do not contain its detection logic.

**2. The membrane implementation** — the detection source itself (the guard
modules the tools above load from a private `membrane/` directory):

> **Proprietary. Not published.** All rights reserved. It is available under a
> **separate commercial licence** for deployment, integration, OEM/embedding, and
> evaluation. A layered defence is worth more unseen, so the source is held back;
> the architecture, threat model and behaviour are fully documented here so it can
> be assessed before any licence is discussed.

## Commercial licensing

The membrane is offered for commercial use — including at infrastructure scale,
inside a product, or as an embedded component. Terms are flexible (evaluation,
per-deployment, OEM, source-escrow by arrangement). The author actively maintains
and extends the membrane, so a licensed deployment receives ongoing improvement
rather than a frozen drop.

If your organisation wants to **deploy, integrate, or evaluate** the membrane,
get in touch:

- GitHub: [@CuppaTea1983](https://github.com/CuppaTea1983) — open an issue or
  reach out directly.
- Licensing contact: wedowhatwemust99@gmail.com

## Why this split

Open documentation + a reproducible, dependency-free design lets a reviewer
assess the membrane honestly without exposing the detection internals that make
it effective. Evaluate it in the open; license the implementation when there's a
fit.

---

*Leviathan Security Membrane © OmegaVR / @CuppaTea1983. "Leviathan" and
"Sovereign" are the author's project names. This licensing statement governs the
`Security Suite/` folder; the wider Sovereign repository is CC BY-NC 4.0.*
