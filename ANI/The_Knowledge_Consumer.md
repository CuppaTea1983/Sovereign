# The Knowledge Consumer

### Why models are replaced for capability, not knowledge — and an architecture that carries knowledge across the gap as text, not weights

**Author:** Michael Ricky Neal (@CuppaTea1983)
**Status:** Position paper / architecture note
**License:** CC BY-NC 4.0
**Version:** 2.0 — 2026-09-27

> **What changed from v1.0 (2026-09-26).** The first version proposed that a retired model's knowledge could be lifted into a live model at the **weight level** — decomposed into a bank and blended through the consumer's eigenbasis. This version reports what happened when that mechanism was measured end-to-end: **it does not work, and the measurement says why.** Two models converge on near-isomorphic internal geometry — a single linear map aligns their representations at ~98% — but that alignment carries *position and identity*, not *decisions*: a donor's answer, mapped into a consumer, decodes at chance. Knowledge does not cross as weights. It crosses as **text**, retrieved on a shared space and read by the consumer. The thesis is unchanged and, if anything, sharper for it. The v1.0 weight-transfer argument is preserved as a measured negative result in §4, because a documented dead end is worth more than a hidden one.

---

## Abstract

Every model generation is replaced by the next, and the industry frames this as progress. It is — but not for the reason the framing implies. Successive frontier and open models rarely replace each other because the newcomer *knows* meaningfully more about the world. They replace each other because the newcomer *reasons* better, follows instructions better, uses tools better, and holds more context. Knowledge is the part that changes least between two models trained months apart; capability is the part that changes most.

Yet replacement discards both. When a model is retired, its still-valid knowledge — and any knowledge its owner added to it — is thrown out alongside the reasoning we actually wanted to upgrade. This is a waste with real cost: training is expensive, some retired and specialist models hold knowledge newer general models lack, and every replacement resets whatever an individual model had accumulated.

This paper argues for separating the two axes the industry currently upgrades as one. **Knowledge** should be transferable and persistent. **Capability** — reasoning and tools — should be upgradable and, where possible, external to the model. It then describes a concrete architecture that realises this separation, and it does so with an honest correction at its centre. The intuitive way to move knowledge between models is at the weight level; this paper reports a thorough measurement showing that path is closed — models align geometrically but do not transfer decisions across the map. The path that *works*, and is demonstrated here, is **text**: a donor's knowledge is distilled to text, banked, projected into a single shared representation space, routed by meaning, and read by whichever model is live. The one-line summary is the inversion at the centre of the design:

> **Dead models become knowledge donors. Live models become knowledge consumers.**

None of the individual techniques here is new. The contribution is the integration — on a persistent, on-device, sovereign substrate — and the lifecycle consequence that falls out of it: a live model that accumulates knowledge across a lineage of donors instead of resetting every generation.

---

## 1. The observation: what actually changes between model generations

Consider what genuinely differs when a lab ships model *N+1* over model *N*, months later:

- **Reasoning depth** — better multi-step problem solving, planning, self-correction.
- **Instruction-following and alignment** — the model does what you asked, refuses what it should, hedges when it should.
- **Tool use** — cleaner function-calling, more reliable agentic behaviour.
- **Context length** — more tokens in the working window.

Now consider what *doesn't* change much: the base factual substrate. The capital of France, the mechanism of an enzyme, the syntax of a language, the events of the twentieth century — the world did not materially change in the months between two training runs, and the two models were largely trained on overlapping corpora. The overwhelming majority of a model's factual knowledge is shared with the generation before it.

So the driver of replacement is **capability, not knowledge**. We replace the model to get the better reasoner and the better tool-user. We take the knowledge refresh as a rounding error — and we pay for the whole retrain to get it.

This is not a criticism of scaling or of new model releases. It is an observation about *what we are actually buying*, and therefore about *what we are needlessly throwing away*.

---

## 2. The waste

Retiring a model discards three things at once:

1. **Upgradable capability** — the reasoning and tool-use we *wanted* to replace. Fine to discard.
2. **Still-valid general knowledge** — the large overlap with the next generation. Discarded for no reason; it did not expire.
3. **Accumulated, owner-specific knowledge** — anything the model was fine-tuned on, adapted with, or (in a persistent system) learned in use. Discarded, and unrecoverable.

Points 2 and 3 are pure loss. It is the equivalent of replacing a library because you hired a better librarian — and burning the books on the way out.

There is a sharper case still. Retired and specialist models sometimes hold knowledge that newer general models *do not*: domain fine-tunes trained on curated corpora, models trained on data that is no longer available or no longer legally scrapable, older systems that captured a snapshot of a field before it drifted. In those cases the retired model is not merely a redundant copy of the new one's knowledge — it is a **unique knowledge asset**, and replacement destroys it.

---

## 3. The proposal: separate knowledge from capability

The fix is to stop upgrading two independent things as if they were one. Treat them as separate axes with separate lifecycles:

| Axis | Property it should have | Lifecycle |
|---|---|---|
| **Knowledge** | Transferable, persistent, attributable | Accumulate; never discard |
| **Capability** (reasoning, tools) | Upgradable, ideally external | Replace and improve freely |

Once separated, the replacement treadmill breaks. You can swap the live model, improve the reasoning layer, and add new tools **without discarding knowledge** — because knowledge no longer lives *only* inside the weights you are replacing. It has been lifted out, banked, and can be routed to whatever consumer you run next, and it persists across sessions rather than resetting.

The rest of this paper describes an architecture that implements exactly this separation. The crucial engineering question is *how knowledge moves from a donor to a consumer*. The next section reports the answer that was tested first and found wanting; the section after it reports the answer that works.

---

## 4. The path that does not work: weight-level transfer (a measured negative)

The intuitive way to move knowledge between models is at the weight level. A donor's knowledge lives in its weights; a consumer's capacity lives in its weights; so — the reasoning goes — decompose the donor's weights, find the shared basis, and blend the donor's directions into the consumer's. Version 1.0 of this paper proposed exactly that. It was the right hypothesis to test. It failed, and the way it failed is instructive enough to keep.

### 4.1 The hypothesis

Different models, trained separately on overlapping data, should occupy overlapping representation spaces. If so, a donor's weight structure could be rotated into a consumer's coordinate system and blended in, so the consumer reasons with the donor's knowledge as if it were its own — no retraining, no prompt tokens.

### 4.2 The measurement: geometry aligns, remarkably well

The first half of the hypothesis is not only true, it is striking. Over the vocabulary two models share, a **single linear map aligns their token-embedding spaces at ~98% held-out retrieval**: take a token's representation in the donor, pass it through the learned map, and it lands on that same token's location in the consumer's space. This is the "relative representations" / "platonic representation" phenomenon (Moschella et al., 2022; Huh et al., 2024) — independently trained networks converge on near-isomorphic geometry.

It holds in depth, too. With representations captured *in context* (feeding both models the same text and matching positions), the alignment stays near-perfect **layer by layer through the full depth** of the network — including the deep, reasoning-bearing layers — between models of different size and different layer count. The geometry of two different models really is a rotation apart.

### 4.3 The measurement: decisions do not survive the map

That is where the good news stops. Alignment at 98% retrieval measures whether the map preserves **identity** — *which* concept, *which* position. It does not measure whether it preserves a **decision** — *which token the model would choose next*. Those turn out to be different things, and only the first survives.

The decisive test took the disagreement subset — cases where donor and consumer would choose *different* next tokens — mapped the donor's final hidden state into the consumer through the aligned map, and asked whether the consumer's own output head then scored the donor's choice above its own. On the aligned, in-distribution set, this came in at **chance** (≈48%, statistically indistinguishable from a coin, over ~1,500 trials). The result did not improve in any structured subspace: denoising to the dominant shared directions made it *worse* (it keeps the shared identity and discards the decision), and stripping the dominant directions to look for a signal hiding underneath recovered only to chance. The decision was not masked. It was **erased** by the map's ~22% reconstruction error — the fine directional detail that distinguishes one model's next-token choice from another's washes out under any linear alignment.

### 4.4 The conclusion, and why it sharpens the thesis

Two independently trained models are geometrically alignable but not decision-transferable. The alignment is real, measurable, and useful as a *measurement of convergence* — but it is not a pipe you can push knowledge through. **Knowledge does not cross between models as weights or hidden states.**

This is not a defeat for the thesis; it removes a wrong turn from it. The separation of knowledge from capability does not *require* weight-level transfer — it requires that knowledge live somewhere other than only inside the weights being replaced. There is a carrier that satisfies that requirement completely, is indifferent to architecture and dimension, needs no alignment map, and is exactly what the geometry *does* preserve losslessly: **text**. The next section is the architecture built on it.

*(The weight-level path is parked, not disproven as an eventual possibility; the measurement here concerns linear transfer between independently trained models. The alignment tooling is retained as a research instrument for measuring convergence, not as a transfer mechanism.)*

---

## 5. The path that works: knowledge as routed text on a shared space (ANI)

If knowledge cannot cross as weights, it crosses as text — and the same geometric convergence that failed to transfer *decisions* is exactly what lets text be **routed by meaning**. This is the working mechanism. It is realised in *Leviathan*, the on-device engine in which this design lives, as a subsystem called **ANI**: a shared-space knowledge router.

### 5.1 The shared space

Every piece of knowledge, and every query, is projected into **one** representation space — a single canonical model's token-embedding manifold, memory-mapped as a lightweight embedder (no model is run to do this; one tensor is read). Because donor knowledge and consumer queries land in the *same* space regardless of which model produced them, knowledge from any architecture or family becomes comparable by construction. This is the "adapts to any model" property, and it is where the geometric convergence of §4.2 is genuinely load-bearing: the shared space *is* the adaptation. It is also where a geometric view of the problem belongs — not at weight transfer, but at retrieval.

### 5.2 Distillation to text — the donor step

A donor model's knowledge is extracted **as text**, before the model is retired: it is prompted across the subjects it knows, and what it can articulate is captured. (A model is only a good donor for what it can actually put into words — a narrow tool-use fine-tune, for instance, is a poor donor; this is a real and measured constraint, not a caveat.) The captured text is folded into a **bank** — a subject-tagged, de-duplicated text store — with provenance recorded, so you can always ask which donor contributed which knowledge. A bank can equally be filled from a curated corpus rather than a model; the mechanism does not care about the source, only that the knowledge arrives as text.

Distillation-to-text is deliberately unglamorous, and that is its strength: it is robust, inspectable, lossless with respect to what was said, and — unlike a weight blend — **dimension- and family-agnostic**. A bank stores text and re-embeds on load into whatever space the live consumer shares, so the same bank serves a 1-billion-parameter consumer and a 70-billion one without change.

### 5.3 Routing — the consumer step

When the user asks a question, ANI projects the query into the shared space and retrieves the most relevant distilled passages **across all banks**, ranked by meaning. The best passages are assembled into a compact context block — with donor attribution, de-duplicated so the consumer never receives the same fact twice — and handed to the live model, which answers and persists what it learned. Nothing crosses as weights; the consumer reads knowledge the way a person reads a well-chosen reference, and the retrieval is what makes the reference well-chosen.

This is retrieval-augmented generation (Lewis et al., 2020) with two deliberate properties: the retrieval space is a *model's own learned geometry* rather than a generic sentence embedder, and the banks are *donor-attributed lineages* rather than an undifferentiated index. The first makes routing agree with how a model actually organises meaning; the second is what turns retrieval into the knowledge-lifecycle mechanism this paper is about.

### 5.4 The consumer (`.lev`) and persistence (`.fqm`)

The **`.lev`** is the live consumer model in a format the engine maps directly to the GPU and runs in-process. It is the "librarian" — reasoning and language capability. It is the component you are free to **replace**, precisely because the knowledge no longer lives only inside it.

The **`.fqm`** ("fractal quantum memory") persists what the model holds — its attention-level memory — across sessions and restarts, so that knowledge received from donors, and knowledge learned in use, survives rather than evaporating when the process ends. Two properties make this safe rather than a liability. First, a **quality gate**: degenerate or garbled generations are refused entry, so one bad inference cannot permanently poison the store. Second, **conversation-only isolation**: ephemeral scaffolding (system prompts, transient instructions, the routed context block itself) is rewound out of durable memory after each turn, and only the clean exchange is retained, so the store accumulates *knowledge* rather than bloating with noise. In validation this kept persisted memory roughly an order of magnitude smaller than a naïve append while remaining faithful to the intended content.

*Lineage and priors:* persistence addresses continual learning — catastrophic forgetting (French, 1999; Kirkpatrick et al., 2017) — from the memory side rather than the training side: instead of protecting weights against forgetting during retraining, it persists a durable, gated memory the running model reads.

### 5.5 Fact-checking — knowledge you can trust before you keep it

A consumer that absorbs knowledge indiscriminately accumulates errors as readily as facts. Verification is therefore first-class, in tiers:

- **On-device, web-free self-consistency.** The primary tier resamples the model's own answers and scores their agreement and support, flagging claims the model is not actually certain of — a self-consistency check in the spirit of SelfCheckGPT (Manakul et al., 2023), requiring no external source and no network. Anchored on numbers and named entities, not embeddings alone, because embedding geometry is blind to the difference between one figure and another.
- **A coherence floor and de-duplication at ingest.** Degenerate text is refused; text already covered by the bank is not stored twice. Verification decides what is *allowed to persist*, so a bank accumulates checked, non-redundant knowledge rather than confident errors or waste.
- **Optional, opt-in verification against cited sources.** As a *separate and non-default* tier — explicitly outside the sovereign, web-free running system — validated sources may be consulted, with citations, to confirm a claim before it enters durable memory. This is a deliberate choice a user makes, never a silent capability of the base system.

### 5.6 Tools — capability without bloating the model

The second reason models get replaced is tools, and the architecture's answer is that **the model does not need to own its tools**. Capabilities that require specialised computation run *externally* and their results are handed back in-context:

- A **structural analyser** that reads any 2-D field as geometry — layout, rank, orientation, structure-versus-noise — regardless of file format, giving a text model a parse-free structural read of an image or document.
- A **recognition tool** that names what an image depicts through an external encoder the model does not have to call — the host drives it and injects the result.

Both are validated in use. The principle they demonstrate is general: a model does not need to *internalise* a capability to *use* it. The host invokes the tool; the answer rides back into the conversation. Upgrading or adding a tool never touches the model's weights — so tool capability, like reasoning, becomes an external axis you improve freely without a retrain.

---

## 6. The proof: routing a foundational knowledge bank

The mechanism in §5 was run end-to-end. The point of the demonstration is not a headline number; it is that the working carrier — text routed on a shared space — surfaces *the right foundational knowledge* for a query, across models, with no retraining and no weight transfer.

**The bank.** A knowledge bank was built from open scholarly abstracts on arXiv, category-scoped to machine-learning subjects, across the core of the ML canon — attention, gradient descent, convolutional networks, batch normalisation, dropout, word embeddings, recurrent/LSTM networks, backpropagation, residual networks, GANs, variational autoencoders, Q-learning, knowledge distillation, optimisation, transfer learning, graph networks. Roughly 150 clean, licence-clear abstracts, each one clean chunk, de-duplicated and coherence-gated on the way in.

**The routing.** Queries were projected into a shared space (the token-embedding manifold of a small, unrelated 1-billion-parameter model — deliberately *not* a model that produced any of the banked text, to show the space is shared, not memorised) and routed against the bank on a CPU, with no model loaded. Representative results:

- *"how does dropout prevent overfitting?"* → dropout-regularisation papers, top score 0.78.
- *"how do variational autoencoders learn a latent representation?"* → *An Introduction to Variational Autoencoders*, 0.76.
- *"what does batch normalization do during training?"* → the paper describing normalising activations to zero mean and unit variance, 0.64.
- *"how does knowledge distillation transfer knowledge from a large model to a small one?"* → *"…train smaller language models via supervision from stronger teachers,"* 0.63.
- *"how does gradient descent optimise a neural network?"* → Ruder's canonical *overview of gradient descent optimization algorithms* in the top results.

Five of six representative queries routed to clean, on-topic, foundational knowledge. The knowledge crossed from source to consumer purely as text on a shared space — dimension-agnostic, family-agnostic, no retraining, no eigenbasis, no weight blend — which is precisely the claim.

**The honest edges,** because the demonstration is only worth as much as its failures are visible:

- **The source is everything; precision beats coverage.** An earlier attempt drew from a general web archive and returned collisions (a query for neural-network "transformers" surfaced *electrical* transformers) and document furniture. The category-scoped scholarly source removed the collision *at source* — a cleaner instrument beats a cleverer filter. The lesson generalised to a rule: *the route is the verdict, not the bank count.* A bank's value is whether the right thing comes back, never how much is in it.
- **Retrieval has generic attractors.** One query in six — *"why does a residual connection help deep networks train?"* — was topped by an abstract beginning *"Why does the Adam optimizer work so well in deep-learning applications?"* The phrasing is a magnet for any "why does X help deep networks" question. This is a genuine limitation of embedding-based retrieval, not a bug in the routing, and it is stated rather than hidden.
- **A routing-scope bug, found and fixed by this demonstration.** Two queries ("knowledge distillation", "transfer learning") initially failed because they fell into the taxonomy's "unclassified" bucket and were then *scoped to it* — searched only against other unclassified entries, hiding the real matches. The fix was principled: a query with no real subject routes over the full bank on pure relevance. This is exactly the kind of defect a live demonstration exists to catch, and it is reported because catching it is the point.
- **Retrieval is proven; the downstream capability gain is the standing next measurement.** This demonstration proves that the right knowledge is *retrieved and delivered*. That retrieval-augmented context improves grounded answers is well established in the literature; the specific, quantified task-delta on this substrate — a held-out battery answered with and without the routed knowledge — is the honest next step, and this paper does not claim it as finished.

---

## 7. The inversion

Put together, the roles reverse from the monolithic model the industry replaces:

- A **retired model** is no longer waste. It is a **donor** — its knowledge is distilled to text, banked with attribution, and made routable to whatever runs next. Even a dead-end architecture nobody would deploy is valuable as a donor: you do not run it, you lift what it can tell you.
- A **live model** is no longer a fixed thing you discard and re-buy. It is a **consumer** — it receives knowledge from a lineage of donors through a shared space, persists what it receives, verifies before it keeps, and reaches for external tools when it needs a capability it does not hold.

> **Dead models become knowledge donors. Live models become knowledge consumers.**

The consumer's reasoning can be upgraded — swap the `.lev`, improve the reasoning layer — without discarding a single fact it has accumulated. Its tools can be upgraded without a retrain. Its knowledge only grows, donor by donor, and persists across every session. The unit the industry currently throws away and re-buys every generation is decomposed into parts with independent lifecycles, and the only part you actually replace is the one you actually wanted to upgrade.

---

## 8. Implications for the industry

- **The replacement treadmill breaks.** Upgrade capability; retain and accumulate knowledge. The next model does not have to relearn — or re-forget — what the last one knew.
- **Reclaimed sunk cost.** Training is the expensive step. Recycling a donor reclaims knowledge that was paid for once and would otherwise be discarded — an economic and sustainability argument, not only a technical one.
- **Provenance and attribution.** Text banks are inspectable and attributable — you can ask which donor contributed which knowledge, and read it. This is a very different posture from an opaque monolith whose knowledge cannot be separated from its behaviour, and it is a *consequence of choosing text as the carrier*, not an add-on.
- **Architecture independence.** Because the carrier is text on a shared space, a donor and consumer need not share a family, a dimension, or a tokenizer. Knowledge from a 70-billion-parameter model routes into a 1-billion-parameter consumer as readily as into a peer — something the weight-level path provably cannot do.
- **Sovereignty and longevity.** On a persistent, on-device substrate, a consumer's value compounds over time rather than resetting each generation. What it has learned and been given stays with it, offline, under the owner's control.
- **Specialist knowledge survives.** Domain models, models trained on now-unavailable data, and older curated systems can be preserved as donors rather than lost when they are retired.

---

## 9. Honest limitations and open questions

This paper would not be worth reading if it hid its edges.

- **Text is the carrier; weights are not.** The central correction of this version. Cross-model weight/hidden transfer aligns geometrically (~98%) but does not transfer decisions (chance). The architecture is built on the carrier that works, but anyone hoping to blend knowledge directly into weights should know that path is closed for independently trained models under linear transfer.
- **A donor gives only what it can articulate.** Distillation-to-text captures what a model can *say*. Knowledge a model uses implicitly but cannot express is not captured this way. Choosing good donors and good prompts is part of the method, not an afterthought.
- **Retrieval quality is the system's quality.** Routing is only as good as the bank and the shared space. Generic-attractor abstracts, taxonomy coverage gaps, and a poorly chosen source all degrade it — the demonstration in §6 shows each of these happening and being addressed. Precision beats coverage, always.
- **Verification cannot manufacture truth.** Self-consistency measures a model's *certainty*, not a claim's *correctness*; judging an external source's soundness requires either cited authorities or human adjudication. The system flags and gates; it does not omnisciently know what is true.
- **Retrieval is proven; the end-to-end capability gain is the next measurement.** §6 proves the right knowledge is retrieved and delivered. The quantified improvement it produces in a consumer's answers, on a held-out battery, is the standing next step.
- **This is a synthesis, not a first invention.** Every component has priors: retrieval-augmentation (Lewis et al., 2020), representation alignment / relative representations (Moschella et al., 2022; Huh et al., 2024), distillation (Hinton et al., 2015), continual learning (French, 1999; Kirkpatrick et al., 2017), self-consistency checking (Manakul et al., 2023), and external tool use (Yao et al., 2022; Schick et al., 2023). The contribution claimed here is their **integration on a persistent, sovereign, on-device substrate**, the *measured* determination that text — not weights — is the carrier, and the model-lifecycle consequence that follows — not the invention of any single part.

*(References are cited by canonical name and approximate year; they should be finalised to full bibliographic form before formal publication.)*

---

## 10. Conclusion

The industry replaces models for capability and pays for a knowledge refresh it did not need, discarding valid and sometimes unique knowledge in the process. The instinctive fix — move the knowledge across at the weight level — was tested and found closed: two models align geometrically but do not transfer decisions. The fix that works is older and humbler. Distil a donor's knowledge to text, project it into a shared space, route it by meaning, verify it before you keep it, and let a replaceable consumer read it and remember it. Then the model stops being a monolith you re-buy every generation and becomes a consumer that accumulates. Retired models stop being waste and become donors. The reasoning improves; the knowledge only grows; and it persists.

The next model does not have to forget.
