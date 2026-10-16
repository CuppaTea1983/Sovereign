# Persistent Quantum Memory
### Saving a language model's working memory between sessions — what it keeps, how it stays safe, and what we measured

**Michael Ricky Neal** · OmegaVR (@CuppaTea1983)
**Version 2** — 17 October 2026 · *(version 1, 2 April 2026, was an unpublished draft)*
Licence: CC BY-NC 4.0 · Part of the Sovereign papers: <https://github.com/CuppaTea1983/Sovereign>
Implementation: Leviathan — <https://github.com/CuppaTea1983/Leviathan> · Project page: <https://huggingface.co/spaces/Omega-Dev/Leviathan>

---

## Abstract

A transformer keeps its working memory of a conversation in its key–value (KV) cache, and throws it away when the session ends. Leviathan, a local inference engine for consumer NVIDIA GPUs, keeps it. The KV cache is organised as a multi-resolution *fractal cascade*: the most recent tokens are held exactly, and older ones are folded into progressively coarser summaries (a centroid plus its principal directions per group). The whole cascade is written to disk as a `.fqm` file and restored when the model next loads. This revision describes the system as it now stands: a CUDA implementation; atomic, verified writes; a selectable storage stage (half-precision by default, about 2× smaller at 0.02 % error); turn-boundary compaction so files plateau instead of growing; a structural health check; and a way to read a memory back, which turns out to matter for privacy. It also reports what the memory does and does not keep. Restored memory carries the gist, tone and continuity of past sessions. Specific facts that have been folded into the compressed levels do not survive, even with lossless storage. Exact recall belongs in text, and Leviathan pairs the `.fqm` with a text layer for it. We correct several claims made in the April draft.

---

## 1. The problem

Every conversation with a language model starts from nothing. Context windows have grown from 4K tokens to millions, but a larger window is still a window: when the session ends, everything in it is gone, and the next session begins with a stranger. The usual workarounds — pasting a summary of yourself into every chat, or retrieving old messages from a database — re-feed text through the model each time. That costs context and compute, and it is a poor imitation of remembering.

The model already has a memory of the conversation while it is running: the KV cache, the keys and values every layer computes for every token it has read. Attention reads that cache on every step. It is not a transcript; it is the model's own representation of what it has read. The question this work asks is simple: what happens if you keep it?

## 2. The idea

Save the KV cache when the session ends, and load it back when the model starts again, so the model resumes rather than restarts. Two things stand in the way. A flat cache grows without limit as a conversation runs for weeks. And a memory file is only useful if it can be trusted: it must never be half-written, silently corrupted, or bloated by things that were never part of the conversation.

The first problem is solved by a data structure — a cascade that keeps recent memory exact and older memory summarised, at a bounded size. The second is solved by engineering: atomic writes, verification, compaction and gates. Both are described below, followed by measurements of what the saved memory actually holds.

## 3. How it works today

### 3.1 The cascade *is* the cache

A `.fqm` is not a copy of a KV cache taken from somewhere else. When memory is enabled, Leviathan does not allocate a flat cache at all: the fractal cascade is the live KV store, attention reads it directly (through an "attention view" assembled from every level), and the `.fqm` file is the serialisation of that store. Saving is reading the GPU buffers back; loading is uploading them again. The engine's model file (`.lev`) holds weights only; whether the KV cache is flat or fractal is a runtime choice.

### 3.2 Levels and groups

The cascade has a number of levels (eight by default).

- **Level 0** holds tokens at full resolution, one entry per token, exactly as attention produced them. Its size is the model's context length (8,192 tokens by default; the user can set it from 2,048 up to the model's trained maximum).
- **Each deeper level** holds *groups*. A group summarises `g` entries of the level above (`g = 8` by default), so a group at level *L* stands for `8^L` tokens. Each level holds up to `context ÷ g` groups (1,024 by default).

When level 0 needs room, its oldest entries are compressed into groups and pushed to level 1; when a deeper level fills, the same thing happens one level down.

With the defaults, the cascade spans `8,192 + 1,024 × (8 + 8² + … + 8⁷) ≈ 2.45 billion` token positions, while the attention view stays at a fixed `8,192 + 7 × 1,024 × 5 = 44,032` entries per layer, however long the conversation runs. Attention cost and VRAM are bounded. **The span is arithmetic, not recall**: it counts positions whose information has been folded into the memory somewhere, with less detail at every level. Section 7 measures how much detail survives.

### 3.3 Why "quantum"

The name is borrowed, not literal; no quantum computing is involved. It comes from the unscented transform used in Kalman filtering, where a distribution is represented by a small set of carefully chosen *sigma points* rather than stored in full. When a group of entries is compressed (in the default "quantum" mode), Leviathan keeps:

1. the **centroid** — the mean of the group's keys (and, separately, values);
2. the top **k** principal directions of how the entries vary (k = 2 by default), with their eigenvalues.

To rebuild the group for attention, it generates `2k + 1` sigma points: the centroid, and one point either side of it along each principal direction, scaled by the eigenvalue. With k = 2, a group of eight entries becomes five attention entries that preserve the group's mean, spread and main directions of variation. Two other modes exist, a plain average and a "Shannon" mode that stores scaled deltas, but quantum is the default.

### 3.4 Compaction: the exact window and the plateau

In the April prototype, compression happened only when level 0 filled. Once the context length was raised to 8,192, that almost never happened in normal use: the memory stayed flat and full-precision, and the file grew with every turn. The current system compacts at **turn boundaries** instead. After each exchange, everything in level 0 except the newest `W` tokens is folded into the cascade (`W = 2,048` by default; the user can choose Off, 1,024, 2,048, 4,096 or 8,192). The most recent part of the conversation stays exact. Everything older ages into the summarised levels, and the file size plateaus. Compaction runs only between turns, never mid-generation, so it cannot disturb a reply in progress.

## 4. The file

### 4.1 Container

```
FQM1          4 bytes    magic
header_len    8 bytes    length of the JSON header
header        variable   JSON (below)
buffer_0..N   variable   one compressed block per GPU buffer
```

The JSON header records the format version, the backend, the mode, the model geometry (layers, KV heads, head dimension), the cascade geometry (level size, levels, group size, components), the per-layer entry and group counts, how many tokens the memory has taken in, how many cascade events have happened, and a manifest giving every block's name, raw size and compressed size. Blocks are named by layer, level and role (`fkv/{layer}/0/k`, `fkv/{layer}/3/k_eigvec` and so on). On load, the geometry is checked against the running model, and any mismatch fails loudly instead of overrunning a GPU buffer.

### 4.2 Storage stages

Each block is compressed independently, and the reader recognises the stage from the block's first bytes (a zstd frame always begins `28 B5 2F FD`; the half-precision stage writes `F16Z`; the Shannon stage writes `DF16`). Stages can therefore be mixed in one file, and none needs a format field. We measured all three on real memory files:

| Stage | Size vs raw f32 | Error | Status |
|---|---|---|---|
| Lossless (zstd) | 1.08× smaller | none | available |
| **Half-size (float16, then zstd)** | **≈ 2.01× smaller** | **0.02 % relative** | **default** |
| Shannon (DFloat11-style mantissa coding, 8 mantissa bits) | ≈ 2.18× smaller | 0.22 % worst per block | experimental |

Two findings shaped this. First, **lossless compression is a dead end for KV data.** Float32 activations are close to incompressible as bytes: zstd at level 3 or 19 gives 1.08×, and LZMA gives 1.09×. Second, float16 is the safe lever. It is the precision KV caches are commonly computed in anyway, its error is negligible, and the half-size stage falls back to lossless storage for any block whose values fall outside the float16 range or are not finite, so it can never corrupt one. In a live chat, one model's memory went from 175.5 MB to 79.0 MB (55 % smaller) on the default stage. The Shannon stage is gentler on size than its headline suggests once it is held to a KV-safe error (2.3–2.6× below 1 % error, not 5×), and it stays experimental until a fidelity test clears it (section 10).

## 5. Making it safe to rely on

A memory that can corrupt itself is worse than no memory, because nobody notices until the model starts behaving strangely.

### 5.1 Atomic writes

The original writer opened the target file for writing, which truncated the good copy the instant it opened. A crash, a full disk or a power cut mid-write then left a torn file, with the previous memory already gone. Every save now goes through one gate:

1. the new memory is scanned first, and a store containing NaN or infinity is refused (it would poison attention on reload);
2. it is written to a temporary file in the same folder and flushed to disk (`fsync`);
3. its on-disk size is checked against the header's manifest, which catches short writes;
4. it replaces the old file in a single atomic rename.

If anything fails at any step, the previous good memory is untouched and the temporary file is removed. A memory can fail to save, and Leviathan says so when it does, but it cannot tear. Tests cover a crash during the final rename, a refused non-finite store and a truncated write. In every case the old file survived byte for byte.

### 5.2 A structural health check

Atomic writes catch files that are torn or malformed. They cannot catch a file that is complete, the right size and full of valid numbers, but whose structure is dead: a scrambled write, or a memory that stopped tracking the conversation. Leviathan runs a structural test on load. It compares the stored keys of level 0 against a shuffled null (the same values, structure destroyed) and returns *alive*, *degraded* or *dead*. On test data, a real memory scored z = 3,628 and pure noise z = 1.15. A real memory with its values shuffled, which passes every byte-level check, scored z = 0.0. Real memory with heavy added noise was still clearly alive (z = 342). Real conversation memories score between z ≈ 9,000 and 10,600, so false alarms are not a practical risk. The check warns by default; a setting makes it refuse a dead memory and start fresh.

### 5.3 What goes into a memory

- **Substance, not scaffolding.** Before each reply, Leviathan wraps the turn in context: reasoning guidance, safety checks, and knowledge it has retrieved for that one answer. That context steers the reply. Then the turn is rewound and only the user's message and the model's answer are absorbed into memory. The memory keeps the conversation, not the machinery around it, so it stays lean.
- **No garbled turns.** A reply detected as degenerate (looping or broken) is not saved, so one bad turn cannot lodge itself in the memory permanently.
- **When it saves.** After the first exchange, then after every fifth. No button.
- **Gated when knowledge routing is off.** If the user switches off Leviathan's knowledge layer (ANI), the in-session memory still works, but the durable save is skipped. A session without grounding cannot bake its mistakes into memory that a grounded session later inherits.
- **Tools keep their own headspace.** The coding studio, the node graph and the 3D planner use throwaway memory scopes. A model's tool work never lands in its conversation memory.
- **One memory per persona.** Two copies of the same model loaded under different names (say, "Bill" and "Bob") get separate files, and renaming a model carries its memory with it.

### 5.4 A bug worth reporting

The first version of compaction occasionally turned recent memory into gibberish. The cause was a single GPU copy: compaction shifted the surviving entries to the front of level 0 with a device-to-device `cudaMemcpy`, and when the source and destination ranges overlapped (which they do in the normal shape: keep 2,048, compress about 384), the result is undefined, and it corrupted the very entries being kept. Our CPU test harness hid the bug, because the numpy stand-in for the copy behaves like `memmove`, which handles overlapping ranges safely. The fix stages overlapping shifts through host memory, and the test harness's copy now *raises* on an overlapping copy, so the stand-in is faithful to the undefined behaviour and not merely to the API. The lesson generalises: a mock that is more forgiving than the hardware is a mock that lies.

## 6. Privacy: a memory can be read back

A `.fqm` contains no text, only numbers. That does not make it anonymous. In layer 0, a token's value vector depends on the token alone: the token's embedding, normalised and projected, with no position and no context mixed in. Every stored layer-0 value can therefore be matched against the model's recomputed values for its whole vocabulary, and decoded.

We built this as Leviathan's memory inspector (Studio → *Inspect .fqm*), and it recovers the recent part of a memory exactly:

| Memory | Recovered |
|---|---|
| Llama 3.2 1B (F16) | 46/46 tokens, 2.8 s |
| A 3B model (Q6_K) | 131/131 tokens, 4.8 s |
| The April 2026 prototype's memory + Qwen2.5-Coder-7B | 63/63 tokens |

The worst exact match differed from the stored vector by 0.08 %, and the nearest wrong token was at least 31 % away. A different model recovers nothing (0/46 with a rotated copy), so read-back also proves which model a memory belongs to.

The practical consequence: **treat a `.fqm` like the transcript of the conversation it came from.** Keep it, back it up and share it on those terms; the inspector says so in the interface. The inspector also accounts for every byte (the tag, the JSON header and the blocks add up exactly to the file's size, so nothing else can hide in a memory file), unpacks every block, and confirms that a memory file is only numbers and that nothing in it is ever run as code.

## 7. What it remembers — measured

### 7.1 Inside the exact window

Within a session, a Leviathan model follows the conversation through this memory. The engine sends the model only the new turn, and everything before it is in the cascade. The exact window (the newest `W` tokens of level 0) is the conversation's own KV state, verbatim; section 6 shows the tokens can be recovered from it exactly. That window is saved and restored at full stored precision.

### 7.2 After a cold reload: gist, not specifics

The question that matters most is whether a fact from an earlier session can be recalled exactly after the model is closed and reloaded. We built a recall test for it. It drives the bare engine with nothing else that could carry a fact — no knowledge layer, no text memory, no answer cache. It plants five facts, pads the conversation with filler until the cascade folds them into the compressed levels, saves, reloads under matched conditions (lossless, half-size, and half-size with compaction), and grades each answer as *recalled*, *honest gap* or *confabulated*.

The result: **exact recall of facts that had been folded into the compressed levels was weak even with lossless storage, on both 3B and 7B models.** A 3B model asked for a name it had been told replied that it had no information about "your dog's name". It had registered that a dog had been discussed, but could not extract the specific value. The test refused to give a verdict on the storage stages, correctly, because the lossless baseline itself could not do the task.

A second measurement explains why. On six facts and six queries over the same stored keys, we compared ways of pulling a fact back out of the memory:

| Retrieval over stored keys | Top-1 accuracy |
|---|---|
| Mean-pooled cosine | 17 % (chance) |
| Linear subspace (principal angles) | 17 % (chance) |
| **Per-token angular match (late interaction)** | **83 %** (mean reciprocal rank 0.92) |

The information needed to find a specific fact lives in the per-token directions of the keys. Linear summaries (means and principal directions) discard it, and the compressed levels of the cascade *are* linear summaries. So the cascade keeps what a passage was about and how it went, and loses the detail that pins down a specific value. (The test set is small, and every query shared at least one word with its fact, so this shows per-token matching surviving where linear summaries destroy it. It does not yet show meaning-level matching with no shared vocabulary.)

### 7.3 Disposition

What restored memory reliably carries is disposition: tone, register, themes and the shape of a relationship. The clearest demonstrations are personality memories, built by reading a person's chat logs through the model and saving the result. Loaded into the model, the result reads unmistakably as its source ("yeah, it's me"), including a 6,000-token profile built for a DeepSeek mixture-of-experts model. These are qualitative judgements, and we report them as such. The April prototype's three-session test points the same way: told in session 1 who Michael was and what he builds, the model reloaded in session 2 and continued "Leviathan can also…" with "simulate…", top prediction with a logit of 19.86. That is thematic continuation from restored memory, consistent with everything above.

### 7.4 Exact recall lives in text

The conclusion is a division of labour. The `.fqm` carries the state of a relationship: what the conversation was about, how it went, and the model's settled sense of who it is talking to. Exact facts belong in text. Leviathan has two text layers for that:

- **Episodic memory.** Each model's own past turns are stored as text and linked by tags, so recalling one tag walks the links ("remember Pepper" brings back the turn about Pepper and the turns linked to it, verbatim). Recall is scoped to the model's own turns and never crosses to another model, because cross-model recall was found to blend personalities. Tests confirm the right turns come back word for word and that one model never receives another's.
- **ANI**, the knowledge layer: subject-tagged text banks that any model can draw on, behind a membrane that admits only vetted material.

Text recall is measurable, and it measured well. On Leviathan's code-reasoning bank (1,451 entries) we ran 400 paraphrased queries, each written from a trace's answer rather than its problem, so none of the queried text exists in the bank. The right entry came first 62 % of the time and was in the top five 77 % of the time. Keyword search scored 43 % and 67 %, and chance is 0.07 %. Cleaning the data mattered as much as the method. Once the banks were cleared of years of chat logs and narrowed to verifiable code, on-topic and off-topic queries separated cleanly: a similarity gap of 0.066, against 0.004 on the uncleaned corpus (13 hand-written queries).

Taken together, the two kinds of memory give a model both continuity and exactness: the `.fqm` makes it the same model it was yesterday, and the text layers let it quote what was said.

## 8. Models with compressed attention (MLA)

DeepSeek-style models use multi-head latent attention (MLA), which caches a compressed latent per token rather than full keys and values. Their memory is saved in the same container. The latent cache lives in host RAM, so it uses no VRAM and is bounded by system memory. A memory can also be built while streaming the model's layers through the GPU a few at a time: DeepSeek-V2-Lite builds an identical memory file in 1.4 GB of VRAM instead of 14.4 GB, about 15 % slower. Batched prefill raised the speed at which such a model takes in text for its memory from 5.2 to 33.5 tokens per second. An optional quantum cascade for the latent cache bounds attention to a fixed view, as the cascade in section 3 does.

## 9. What the April draft claimed, and what held up

| April 2026 claim | Status now |
|---|---|
| "Over 1 billion tokens in 58 MB" / "1.1 billion tokens of effective context" | **Arithmetic, restated.** It is the span of positions the cascade can fold in (≈ 2.45 billion with today's defaults), not tokens available for recall. Detail falls with every level. |
| "The compression doesn't degrade output quality" | **Withdrawn as stated.** Never measured as output quality. Measured since: linear compression removes the per-token detail that fact recall needs (17 % vs 83 %), and folded facts do not survive a reload. |
| "There is no context window problem" | **Withdrawn.** Exact work still happens in the exact window. The cascade extends gist and continuity, not exact context. |
| "The model keeps that knowledge forever" | **Revised.** The memory persists across sessions and ages gracefully. Knowledge that must stay exact is kept as text. |
| "The file gets smaller as sessions accumulate" | **Superseded.** That was the shape of one short test. Files now plateau by design (compaction). |
| Session 2 continued "Leviathan can also…" from restored memory | **Holds,** as thematic continuation (section 7.3). |
| Speed and VRAM tables (OpenGL engine, Groq-8B) | **Historical.** Measured on the April OpenGL prototype with a model no longer used; not re-measured on the CUDA engine, and not claimed here. |

## 10. Open problems

- **Fidelity of the compressed levels, measured properly.** Recall tests answer only a yes-or-no question. The right measure is whether the next-token distribution moves between a lossless memory and a compacted one on a fixed probe (a logit or negative-log-likelihood comparison). That needs an evaluation operator that has not been built yet. The Shannon stage stays experimental until it passes this test.
- **Meaning-level retrieval from keys.** The 83 % result had shared words in every query. A disjoint-vocabulary test would show whether per-token matching recovers meaning and not only matching words.
- **Keeping per-token structure deeper.** If facts live in per-token directions, deeper levels could keep a small nonlinear or per-token code instead of a purely linear summary.
- **Bit-rot after writing.** Atomic writes protect the moment of saving. Per-block checksums would let a loader skip a block corrupted later on disk.
- **Gentler aging.** Sixteen finer levels instead of eight would let memory fade more gradually. This hypothesis is parked and untested.
- **Live injection of retrieved memory.** Attending over a retrieved stretch of an old memory in the middle of a turn, rather than loading a whole memory at startup, remains unbuilt.
- **Read-back for MLA memories** is not yet offered, because it has not been verified on one.

## 11. Related work

Several parts of this system have precedents, and we claim the synthesis, not first invention. Transformer-XL (Dai et al., 2019) carried a cache of earlier segments across steps. The Compressive Transformer (Rae et al., 2019) is the closest relative: it compresses old memories into a coarser secondary memory. It learns its compression functions during training, while this cascade is training-free and runs on frozen, off-the-shelf weights. StreamingLLM (Xiao et al., 2023) showed that a few retained "attention sink" tokens plus a recent window keep streaming generation stable. H2O (Zhang et al., 2023) evicts all but the most-attended entries, and KV quantisation work such as KIVI (Liu et al., 2024) shrinks the cache's precision. Inference servers cache and restore prompt prefixes (llama.cpp's prompt cache and slot save/restore; vLLM's prefix caching) to save recomputation, not to carry a conversation across sessions. At the text level, retrieval-augmented generation (Lewis et al., 2020) and MemGPT (Packer et al., 2023) manage memory as documents. The per-token matching in section 7.2 is ColBERT's late interaction (Khattab and Zaharia, 2020), and the sigma points come from the unscented transform (Julier and Uhlmann, 1997). *(Full citations to be completed before formal publication.)*

What is new here is the combination: a training-free, multi-resolution cascade that *is* the KV cache of a frozen model; saved atomically and verified across sessions on a single consumer GPU; with a structural health check and an honest privacy property; paired with text layers for exact recall; and measured for what each layer actually keeps.

## 12. Links and implementation

- **Sovereign** (this paper and its companions): <https://github.com/CuppaTea1983/Sovereign>
- **The Knowledge Consumer** (companion position paper: models are replaced for capability, not knowledge; knowledge should be transferable and persistent): in the Sovereign repository
- **Shannon's Ceiling** (the compression work behind the storage stages): in the Sovereign repository
- **Leviathan** (the engine; MIT licence): <https://github.com/CuppaTea1983/Leviathan>
- **Project page:** <https://huggingface.co/spaces/Omega-Dev/Leviathan>

| Module | Role |
|---|---|
| `leviathan_cuda_fractal.py` | the cascade: store, attention view, compaction, save and load |
| `fqm_atomic.py` | the atomic write gate and load-side verification |
| `fqm_codec.py` | the storage stages, recognised per block on read |
| `fqm_recode.py` | re-encodes a memory under another stage (matched pairs for comparisons) |
| `fqm_recall_gate.py` | the recall test in section 7.2 |
| `fqm_viewer.py` | the inspector and read-back |
| `tag_chain.py` | episodic memory's linked recall |
| `fractal_memory_ingestor.py` | builds a memory from logs (personality memories; layer streaming for MLA models) |
| `leviathan_runner.py` | out-of-process save and load |

*Not every module may be in the public repository at a given time.*

---

**Acknowledgements.** Written with Claude (Anthropic): the April draft with Opus 4.6, this revision with Opus 5.5, from the engineering logs of the work itself. Every number in this version comes from a measurement recorded in those logs.

*Built on an RTX 4080 by a self-taught engineer from Essex who was told he'd never amount to much.*
