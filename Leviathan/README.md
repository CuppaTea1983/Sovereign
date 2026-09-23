**Soon to come**
---

# Leviathan

**Local AI models, running directly on your graphics card. No server, no cloud, no account, no subscription, no telemetry.**

Leviathan loads a language model straight into your GPU's memory and talks to it there. Nothing is sent anywhere. There is no background service, no Docker container, no Python to install, and no API key. You open the app, pick a model, and type.

*(You can also connect hosted models such as Grok alongside your local ones. Those, by their nature, send your messages to their provider. Everything that runs on your own GPU stays on your machine.)*

What makes it different from the other ways of running a model locally is what happens *around* the model: Leviathan gives it a memory that survives closing the app, a way to be taught things without retraining, and a way for your other programs — a game engine, a script, a tool you wrote — to use the model Leviathan is already holding.

> **Leviathan is the host. The model is the guest.**

---

## Contents

- [Requirements]
- [First run]
- [The four file types]	— **start here if you only read one section**
- [The tabs]
- [Chat] · [Models] · [Studio] · [Cores] · [Memory Vault] · [Traits] · [Settings]
- [The systems]
- [Persistent memory] · [Knowledge routing] · [Recycling cloud answers] · [Eidetic recall] · [Second-opinion fact-check] · [Any model, described by itself] · [The security membrane]
- [Using Leviathan from other programs]
- [Where your files live]
- [What Leviathan will not do]
- [Licence and attribution]

---

## Requirements

- **Windows**
- **An NVIDIA graphics card**, GTX 16-series / RTX 20-series or newer
- **A current NVIDIA driver** (one that provides CUDA 13.0 or later)

That is the whole list. You do not need Python, the CUDA toolkit, Visual Studio, or anything else installed. Leviathan checks your card on startup and tells you plainly if something is missing, with a link to the driver download.

**How much VRAM do you need?** Enough to hold the model you want to run. A 7–8 billion parameter model at moderate quality fits comfortably in 8 GB. Larger models need more. Leviathan will tell you what it found and what it is using.

**No NVIDIA card?** Leviathan can still act as a front-end for a model server you run elsewhere — see [Models]. You lose the GPU-native features, but the chat, memory and knowledge systems still work.

---

## First run

The first time you open Leviathan, a welcome card sits over the chat window with three steps and a report on your graphics card. It stays until you have a model, and it always comes back if the GPU check fails, so you are never left guessing why nothing works.

The three steps are:

1. **Convert a model.** Take a `.gguf` model file — the standard format you will find on Hugging Face — and convert it in **Studio → Convert**. You get a `.lev` file. This is a one-time job per model.
2. **Load it.** In **Models**, add it as a Leviathan model. It goes straight onto your GPU. No server starts, nothing listens on a port.
3. **Talk to it.** Type in the chat box and press Start.

Everything after that is optional. Leviathan is fully usable knowing only those three steps. The rest of this document is what the optional parts are for.

---

## The four file types

This is the part most people find confusing, and it is worth five minutes because everything else in Leviathan is built on it. There are four kinds of file, they do four completely different jobs, and they are not alternatives to one another.

A rough analogy, if it helps: if the model is a **person**, then `.lev` is their brain, `.fqm` is their memory of your conversations, `.fkb` is knowledge they have studied until it became part of how they think, and `.eig` is the filing system their brain is organised into.

---

### `.lev` — the model

**What it is:** the model itself, converted into the exact byte layout your graphics card wants.

**Why it exists:** a normal `.gguf` model file has to be unpacked and rearranged before the GPU can use it, every single time you load it. A `.lev` is already in the right shape, so it goes from disk to graphics card with no reshuffling in between. It loads faster and it is what every other Leviathan feature expects to find.

**How you get one:** **Studio → Convert**. Point it at a `.gguf`, wait, get a `.lev`. Once per model, then never again.

**Do I have to?** To use Leviathan's GPU engine, yes. If a model is refused during conversion, that is deliberate — see [What Leviathan will not do]

---

### `.fqm` — the memory

**What it is:** what the model remembers, saved to disk.

**Why it exists:** normally, when you close a chat, everything is gone. Next time you open it, the model has never met you. It has no idea what you were working on, what you told it last week, or what you have already explained three times.

A `.fqm` is that memory, written to a file. When you load the model again, the memory loads with it. The conversation genuinely continues.

**A `.fqm` comes into being one of two ways, and it is worth knowing which is which — they are the same kind of file doing the same job, but they start life very differently, and people often assume there is only the first.**

**One — it happens on its own, as you talk.** If a model has memory enabled, Leviathan saves a `.fqm` after the first exchange and then every fifth one, quietly, in the background. This is the running memory of *your* conversations with *this* model — it grows as you chat and loads back the next time you open the model. You do not have to do anything, and if it ever *cannot* save, it says so out loud rather than pretending it worked. It also refuses to save a turn that came out garbled, so one bad reply can never lodge itself in the memory permanently.

**Two — you build one on purpose, in Studio → Personality.** Instead of letting memory accumulate one chat at a time, you hand the model a whole body of text at once — a folder of past conversations, your project notes, your novel, your world's lore — and it absorbs the lot in a single pass into a `.fqm` that you name and keep. **This is not the auto-memory above, and it is not connected to it.** The auto-memory is what the model happened to remember from talking to you; a Personality profile is a deliberate portrait you construct and can rebuild whenever your source text grows. It is how you make a model that already knows your material — or already sounds like you — before you have typed a word. You point chat at it yourself, and you can keep as many as you like. The Studio section below explains exactly what each control does.

**The auto-memory: one per model.** The memory that builds itself as you chat is named after the model and lives in your FQM Database folder. Two models loaded at once do not share it or bleed into each other. Personality profiles you build by hand are separate files that you manage yourself, so they never collide with the auto-memory.

---

### `.fkb` — the knowledge bank

**What it is:** knowledge held in the model's own language.

That line needs unpacking, because it is the thing most people get wrong about this format. When a model learns something, what it "knows" does not sit inside it as sentences — it becomes geometry, patterns in numbers. A `.fkb` captures knowledge in that same form, through the same mathematical decomposition (SVD) that `.eig` performs on the model's own weights. So a knowledge bank is not a document read aloud to the model when you ask a question. It is knowledge in the shape the model already thinks in, blended into its understanding for as long as the bank is loaded. The model does not consult it. It knows it.

**The heavy version, and the thing most people miss: a `.fkb` can be an archive of another model's knowledge.** This is what makes the format matter. Because a bank is written in the model's native geometry rather than in words, you can point Leviathan at *another model* and decompose what that model learned — the actual knowledge sitting in its weights — straight into a bank. That bank is then portable. Knowledge that one model spent its entire training absorbing can be lifted out and blended into a *different* model, with no retraining of either. So a `.fkb` is not "the notes I fed in." At its fullest it is the distilled learning of a whole model, kept in compressed geometric form, ready to hand to another one. That is what the archives are: raw knowledge absorbed out of models, in the shape a model can actually use — not documents typed up and pasted back.

**How the right knowledge finds you — the tag system.** This is what makes it effortless, and it is worth understanding rather than taking on trust. Every bank is filed under **tags**: the subjects it covers. When you ask a question, Leviathan reads it, works out which subjects it touches, and pulls the banks filed under those tags — before the model answers. You never open a menu or choose a bank. The question chooses it.

And it reads meaning, not spelling. Ask about "symptoms" and it finds the bank filed under "symptom"; ask about "debugging" and it finds "debug". Plurals, tenses, word endings — the router follows them, so the knowledge is there whether or not you happened to use the exact word the bank was filed under. Change the subject halfway through a conversation and the knowledge that travels with you changes too, quietly, without being asked for.

**How you get one:** **Studio → Absorb**. Point it at a model — a `.gguf` file, or a folder of safetensors — and Leviathan reads its weights, decomposes what it learned, and files the result as a tagged, routable bank. You decide how much of the model to take and how much detail to keep; the Studio section below walks through every control. This is the model-to-model transfer described above: you are not uploading documents, you are lifting knowledge out of one model so another can use it.

**The one requirement, and the reason a bank sometimes seems dead:** a `.fkb` blends into a model's eigenspace, so the model needs a `.eig` for the knowledge to have somewhere to land. Without one, the bank loads, the routing runs, the model answers — and none of the knowledge reaches it, with nothing to tell you. If a bank appears to do nothing, this is almost always why. The next section is about `.eig`, and it matters more than its name lets on.

---

### `.eig` — the weight basis

**This is the one nobody understands from the name, so here it is plainly.**

**What it is:** your model's own knowledge, reorganised into a tidier arrangement. Not a different model, not extra knowledge, not a setting. The same model, filed differently.

Think of a library where the books arrived in delivery order and were shelved exactly as they came off the van. Everything is there, but finding anything means walking the whole building. A `.eig` is that library re-shelved properly — same books, nothing added, nothing thrown out, but now organised so you can go straight to what you need.

**It does two separate things, and the second one is why it matters more than it looks.**

**One — it makes the model faster.** Working from the organised arrangement instead of the raw one, the model answers substantially quicker. On an RTX 4080 the speed-up was measured at roughly 6.8× at the aggressive setting. This is the reason most people build one.

**Two — it is what knowledge banks plug into.** This is the part that catches people out. A `.fkb` does not get pasted into your prompt; it blends into the model's arrangement of its own knowledge. If there is no arrangement to blend into — no `.eig` — then there is nothing for the bank to attach to, and **your knowledge banks silently do nothing at all**. The bank loads. The routing runs. The model answers without it. Nothing appears broken.

> **If you want `.fkb` knowledge banks to work, you need a `.eig` for that model. This is not optional and there is no way around it.**

**How you get one:** **Models → ⚗ Build .eig from GGUF**.

**Note the "from GGUF" carefully — this is the bit that trips people up.** A `.eig` has to be built from the **original `.gguf`**, not from the `.lev` you converted. The conversion to `.lev` pre-packs the model for the graphics card, and once packed it cannot be taken apart again to be reorganised. So keep the original `.gguf` around until you have built your `.eig`. If you have already deleted it, you will need to download it again.

**Where to put it:** next to your model, with the same name and a `.eig` extension. Leviathan looks there automatically every time it loads a model. There is no button to press and no setting to switch on — if the file is there, it is used; if it is not, the model runs the ordinary way and says so in the log.

**Quality setting (SVD rank).** The builder asks for a rank. Higher keeps more of the original detail; lower is faster and smaller.
- **1024** is the default and what Leviathan uses when loading. It keeps the model's quality essentially intact.
- **512** is roughly 6.8× faster but noticeably lossier on some models. Worth trying, worth checking the answers afterwards.

**Does it use extra VRAM?** No. This is the common worry and the answer is genuinely no. As each piece of the reorganised model uploads to the card, the original copy of that piece is released. It **replaces** the original rather than sitting alongside it. A `.eig` will not push you over your VRAM budget.

---

## The tabs

Seven tabs down the left side.

---

### 💬 Chat

Where you actually talk to the model.

Type, press Start or `Ctrl+Enter`, and the reply streams back as it is generated. You can interrupt mid-answer — including during the long pause at the start while the model reads a large prompt — and it stops immediately rather than finishing the paragraph first.

The chat takes the full width of the window. There is no side panel competing with it and nothing to arrange before you can start.

**More than one model.** If you have several models connected, they take turns over a set number of rounds — you set that in [Models]. Useful when you want a second opinion in the same conversation rather than in two separate windows.

---

### 🤖 Models

Where models are connected, configured and saved.

**Connecting a model**

- **⚡ Leviathan** — a `.lev` file on your GPU. This is the main path and the one everything else is built around.
- **+ Ollama** — a model served by a local Ollama install. The **llama3 / mistral / phi3 / gemma2** quick buttons are one-click shortcuts for these.
- **+ API Model** — any OpenAI-compatible endpoint, local or remote.
- **🌐 Grok** — xAI's hosted model. Paste your xAI API key and pick the model; the current price per million tokens is shown next to it so you are not choosing blind.

Ollama and API models exist so Leviathan is still useful without a supported graphics card, and so you can compare a local model against a hosted one in the same conversation. They do not get the GPU-native features.

> **Hosted models are not local.** Anything you send to Grok or a remote API model goes to that provider, under their terms and their pricing. Leviathan's "nothing leaves your machine" applies to models running on your own GPU.

**The model list**

Each connected model gets a row showing where it runs, its file or model name, and its reply-length limit. On the right:

- **🔗 Chainlink** — switches a model in or out of the conversation *without removing it*. Unlinked, it keeps its settings and memory but stops taking part. Handy for benching one model for a while.
- **✕** — removes the model from the list.

**Double-click a model** to open its settings:

- **Display Name / Model Name / Endpoint** — what it is called, which model it is, and where it lives (a file path for a `.lev`, a URL for a server).
- **System Prompt** — the standing instructions the model follows in every reply. Leviathan fills in a sensible default; replace it with whatever you want the model to be.
- **Temp** — how adventurous its wording is. Lower is steadier and more predictable, higher is looser and more varied.
- **Max Tokens** — the longest reply the model is allowed to give. This matters more than it looks: a model capped at 512 gives you a paragraph or two, the same model at 6000 can write you a full document. Set it to suit the job.
- **Leech Feed Model** *(Leviathan models only)* — a second model to fall back on. When your local model hedges, gives a thin answer or clearly does not know, Leviathan asks the feed model the same question and absorbs its answer into your local model's memory, so next time it knows. It only ever asks models you have connected yourself. Leave it on *auto* to use the first hosted model in your list.

**🔀 Route — Knowledge Route**

*One model asks. One answers. The mind absorbs everything.*

Pick a model to ask the questions and a model to answer them (the same model for both works; it debates itself), give it a topic, and set how many rounds to run. The two work through the subject back and forth while you do something else, and everything they establish is absorbed into a mind file. It is a way to have a model study a subject deliberately rather than waiting for it to come up in conversation.

Routes work only from what the two models already know. They do not browse the web.

**Profiles.** **💾 Save Profile** stores your whole setup — models and their settings — and **📂 Load Profile** brings it back. Leviathan reloads your last profile on startup, so your working arrangement is there when you open it.

**Max Rounds** controls how many turns a multi-model conversation takes before it stops.

**⚗ Build .eig from GGUF** is here. See [the `.eig` section] — it is the single most useful button on this tab and the least obvious.

---

### 🌀 Studio

Where you build the things Leviathan runs on. Five sub-tabs. Nearly every control has a sensible default; the notes below tell you which ones are worth touching and which to leave alone.

**⚡ Convert → .lev**
Turns a `.gguf` (or a safetensors model folder) into a `.lev`, the format Leviathan actually runs on. The first thing you will use, and a one-time job per model. If a model is not supported, it is refused here — with an explanation of exactly which parts Leviathan does not understand — *before* the multi-gigabyte conversion starts, not after.
- **Model list** — every model Leviathan found, with buttons to select **All**, **None**, or just the **Unconverted** ones. Tick what you want and convert in a batch.
- **Q8_0 mode** — how eight-bit models are laid out. **Split (default)** is the safe choice and what you want almost always. *Shannon* and *Tensor Core F16* are alternative layouts for particular cards; leave it on Split unless you have a specific reason. (Applies to `.gguf` only — safetensors always convert as raw F16.)

**🌀 Absorb → .fkb**
Turns a *model* into a knowledge bank — the model-to-model transfer described in the file-types section. Point it at a `.gguf`/`.cgguf` file (**File…**) or a folder of safetensors (**Folder…**), press **Discover** to list the parts that can be absorbed, tick the ones you want, and press **Absorb selected**.

If you just want *all of it* and don't care about the dials, tick **🧠 Absorb full knowledge** and hit Absorb — that's the one-click answer. The rest of these controls are for when you want to trade completeness for a smaller, faster bank.
- **🧠 Absorb full knowledge** *(the easy button)* — one tick and Leviathan keeps *everything*: it lifts the rank ceiling and captures **≈99.9%** of each layer. That 99.9% *is* "all of it" — the final 0.1% is numerical noise, not knowledge, and capturing it would roughly double the file for no real gain, so 99.9% is as complete as it gets. The result is near-lossless but **large and slow to build** — a full bank can be several times the size of the model itself. Use it when you want the complete knowledge and don't want to think about the settings below. (You genuinely don't need it most of the time — see the note under this tab.)
- **SVD rank (max)** *(default 64)* — the real limiter, and the honest one. It caps how many "directions" of each layer are kept. Here's the thing most people get wrong: a model's weights are **high-rank**, so rank 64 keeps only the *dominant* structure — about half of what each layer actually holds. That is usually exactly what you want for a knowledge bank (the strong, general patterns), but if you want more, this is the knob to raise. Higher rank = more captured, larger and slower bank.
- **Variance target** *(default 0.95)* — where absorption *stops* if it gets there first: "keep directions until this fraction of the layer is captured, or the rank cap is reached, whichever comes first." For high-rank model weights the rank cap is almost always what stops it, so raising this alone does little — it's the rank that moves the needle. The variance figure Leviathan reports afterwards is the **true** fraction captured (of the whole layer, not of what it kept), so if it says 53% and you wanted more, raise the rank or tick Absorb full knowledge.
- **Min dim** *(default 128)* — ignores tensors smaller than this on each side. Small tensors carry little transferable knowledge; the default filters them out cleanly.
- **Preset** — a one-click starting point for the two regex boxes. **Universal LLM (recommended)** is right for ordinary language models; the others target specific parts (attention only, feed-forward only, embeddings only) or particular model families.
- **Include / Exclude regex** — precise control over which tensors are taken, by name. The preset fills these for you; touch them only if you know exactly which layers you want. The default Exclude deliberately drops the token-embedding and output layers, which do not transfer usefully between models.
- While a model loads (which happens before the first progress tick) a **"Loading model into memory — please wait…"** line shows under the log, so you can tell it is working rather than stuck.

**You rarely need a full absorb — it depends on what the knowledge actually is.** A bank is only worth what it *adds* to the model you load it into. If the model you're feeding is already strong at a subject, absorbing another model's take on that same subject at full strength buys you little. Say you run a DeepSeek model that's already excellent at maths, and you absorb another model to "top up" its maths — a full-knowledge bank there is mostly wasted effort, because the maths is already there. Full absorb earns its keep when you're bringing in something the target model is genuinely *weak* at, or doesn't have at all. When in doubt, a normal rank-64 absorb captures the dominant knowledge cheaply; reach for full knowledge when you specifically want completeness and know the subject is one the target lacks.

**🔎 Inspect .fkb**
Opens a finished bank and shows what is actually inside it: where it came from (**Source** and **Architecture**, filled in from the model's blueprint when the bank itself does not record them), how many tensors, original size against compressed size, the ratio, and a per-layer breakdown with each layer's kept rank and the fraction of variance it captured. Use it when a bank does not seem to be helping and you want to know whether the problem is the bank or the routing.

**🔗 Bridge .fkb**
Matches a bank to a target model. Load the `.fkb`, set the target model's **dimension** and **layer count**, and press **Compute bridge** to see the plan for how the bank's knowledge maps onto that model's shape. This is the step that lines a bank up with a model of a different size.

**🪞 Personality → .fqm**
Builds a Personality profile — the *second* kind of `.fqm`, the one you make on purpose, not the memory that accumulates on its own as you chat. Point it at the **model** the profile is for (the same one you will chat with — a profile is tied to its model) and at the **chat log or folder** to absorb (`.txt`, `.md`, `.json`, `.log`). Press **Preview (dry-run)** to see what it will do without writing anything, or **Build profile** to make it.
- **Mirror me (weight my turns)** *(on)* — makes the profile reflect *you* rather than the assistant voice, by weighting your side of the conversation. Leave it on for a "sounds like me" profile.
- **Assistant chars kept** *(default 200; 0 = pure-you)* — how much of the assistant's replies to keep for context. Set it to 0 for a profile built purely from your own words.
- **Resume / accumulate into existing .fqm** *(off)* — adds to a profile you already built instead of starting fresh. Turn it on to grow one profile across several batches of source text.
- **Stage-11 quantum cascade** *(on)* — lets a full-length log be absorbed without hitting a memory wall, and does nothing on models that do not need it. Leave it on.
- **Hot-window** *(default 2048)* — how many of the newest tokens are kept at full detail while older ones compress. The default suits most logs.
- **Trait weighting (feel the weight)** *(on)* with **Boost** *(default 1.0)* — keeps the charged, distinctive moments sharp while filler blurs, so personality survives compression. Raise the Boost above 1 to make the personality bite harder; 1.0 is balanced.
- **Skip duplicate messages** *(on)* — skips byte-identical messages (boilerplate, copy-pasted snippets, "thanks"), roughly 40% faster on real logs with no loss.
- **Harvest reasoning chains** *(on)* — pulls step-by-step reasoning out of the same log into a companion file beside the profile, so the model keeps that too.

---

### 🧿 Cores

*Individual memory · Individual mind.*

One panel per connected model, showing the state of that model's mind. It is the tab you open when you want to know whether the memory system is actually doing anything, rather than trusting that it is.

- **Fractal Core** — whether this model has a memory file, where it is, how big, when it last saved, and how much it has taken in. If memory is not working for a model, this is where it shows as pending rather than active.
- **Local Memory** — conversation history: total messages, how many sessions, the split between what you said and what it said, when it was last active.
- **Trait Profile** — measured characteristics of how this model actually behaves, with its dominant trait named.
- **Session Stats** — this session's message count, and the settings in force: temperature, maximum response length, context limit.

Each model gets its own core. They do not pool and they do not leak into each other.

---

### 🔮 Memory Vault

*Pure knowledge · No personality bleed.*

The archive. Every memory file, model and knowledge file Leviathan can see, in one list, with totals across the whole collection — how many memories, how many models, how many tokens and parameters, how much disk.

- **📁 Add Folder** brings in a folder from anywhere on your machine. Your models do not have to live where Leviathan put them.
- **🧹** cleans up files flagged as stale or broken.
- **Extended Knowledge** is the master switch for whether knowledge banks are offered to models at all. On by default. Turn it off to see how a model answers with nothing but its own training, which is a genuinely useful comparison when you are trying to work out whether a bank is helping.

**The right-hand panel on this tab** is the **🧠 .FKB Knowledge Bank** browser: the knowledge banks available right now and which folders they are being read from. You can point it at additional folders anywhere on your machine and it remembers them between sessions. This panel appears when you open Memory Vault and is the place to check what knowledge Leviathan can actually see.

---

### 🧬 Traits

*Measured interaction traits · model evolution over time.*

Models behave differently from one another, and the same model drifts as its memory fills. This tab tracks that: measured traits per model, charted over time, so you can see the change rather than guess at it.

It measures what the model **did**, not what it claims about itself or what its description says. If a model has become more cautious over a month of conversations, this is where that shows up.

---

### ⚙ Settings

Four sections.

**🛡 Security membrane**
Scans what you send — and anything you paste or load — before the model sees it. Covered properly [below].

- **Security enabled** — the master switch. Off is a legitimate choice; it is your machine.
- **warn / block** — whether something hostile gets flagged with an explanation, or stopped outright.
- **Also scan files and pasted documents** — extends scanning beyond what you type to what you drop in.

**🧠 Eidetic recall**
Answers a question you have asked before instantly from cache instead of regenerating it. Exact matches only. [Below].
**🖥 This machine**
What Leviathan found: your graphics card, and the exact folder your data is being written to.

**ℹ About**
Author, copyright, licence, and buttons through to the GitHub repository, the Zenodo whitepaper archive, and the full licence text.

---

## The systems

The four tabs above are surfaces. These are the things running underneath them.

---

### Persistent memory

**The problem.** Every chat with a local model normally starts from nothing. Close the window and the model has never met you. The usual workaround is to paste a summary of yourself at the start of every conversation, which is tedious, eats your context window, and is a poor imitation of remembering.

**What Leviathan does instead.** As the model reads your conversation, it builds an internal understanding of it. Leviathan writes that understanding to disk as a `.fqm` file and loads it back the next time the model starts. The model resumes rather than restarts.

**What that means in practice:**

- You do not re-introduce yourself.
- Things you explained last week are still known this week.
- Corrections stick. Tell it you prefer something done a certain way and it stays told.
- The memory is not a transcript being re-read. It is the model's own representation, so it does not consume your context window the way pasting a summary does.

**When it saves.** After your first exchange, then every fifth. No button. If it cannot save, it tells you — silence would be worse than a warning, because a memory system that quietly does nothing is indistinguishable from one that works.

**Where it lives.** One file per model in your FQM Database folder, named after the model. Deleting it resets that model to a blank slate. Copying it elsewhere backs up that mind.

**Checking it works.** [🧿 Cores] shows every model's memory status, size and last save time. If a model's core reads pending rather than active, memory is not running for it.

---

### Knowledge routing

**The problem.** A model knows what it was trained on. It does not know your rulebook, your codebase, your company's processes or your world's history. The usual fix is to paste the relevant document into the chat, which means knowing in advance which document is relevant and having room for it.

**What Leviathan does instead.** You build knowledge banks once, in Studio → Absorb, and each one is filed under **tags** — the subjects it covers. From then on you simply talk. Leviathan reads each question, works out which subjects it touches, pulls the banks filed under those tags, and blends them into the model's understanding before it answers. The knowledge finds you; you never go looking for it.

**What that means in practice:**

- No pasting, and no picking a document from a dropdown first.
- Ask about one subject and its bank is there; change subject mid-conversation and the knowledge that comes with you changes too.
- Banks are independent of models. Build one, use it with all of them.
- It reads meaning, not spelling. Plurals, tenses and word endings are followed, so "symptoms" finds material filed under "symptom" and "debugging" finds "debug" — the knowledge is there even when your wording isn't the bank's wording.

**The requirement, again, because it is the single most common reason this appears not to work:** knowledge banks blend into a model's eigenspace, so the model needs a `.eig`. Without one, the bank loads, the routing runs, and the knowledge never actually reaches the model — with nothing to tell you it didn't. If your banks seem to be doing nothing, build a `.eig` first and try again.

**Seeing it happen — the Route panel.** Beside the chat, the **🔀 Route** panel keeps a running log of where your questions went. Each time a model answers, a new entry appears at the top: the model that replied, the knowledge bank it drew on, the subjects the question matched, and how many tokens and milliseconds it took. Newest on top, older ones beneath, so at a glance you can see which banks are actually being used — and which never get picked, which usually means a bank whose tags don't match the way you ask. The list keeps the last thirty or so routes; when you want a clean slate, the **🧹 Clear Route** button in the bottom-right of the panel wipes it. It clears only the on-screen log — your banks, memories and models are untouched.

**Clicking a subject.** The subjects on a route entry are not just labels. Click one and a small panel opens with the topics filed under it — click *science* and you get physics, astronomy, chemistry and the rest; click a topic and you get the subject it belongs to. It is the same map Leviathan routes by, laid open, so you can see exactly why a question landed where it did, and spot a bank that is filed too broadly or too narrowly to be found the way you ask.

**A second opinion, in a different currency.** Beneath each entry sits a 🧠 line: an independent guess at which bank fits, made not from the *words* you typed but from their *meaning*, placed in the model's own embedding space. It agrees with the tag routing most of the time; when it disagrees, that gap is the useful part — usually a bank whose name and tags don't describe what it actually holds. It is shown for your eyes only, and never changes where the knowledge really came from.

---

### Recycling cloud answers

Connect a cloud model — your own account, your own key — and Leviathan quietly keeps the substance of what it tells you. Ask Claude or Grok or Gemini something on your machine, and the answer is folded into a subject-tagged store your *local* models can then route against, exactly like a bank you built by hand. Over time the big models teach the small ones, on your own logs, without you doing a thing.

It is careful about what it keeps. A near-duplicate of something already there is dropped rather than stored twice — but two answers that differ by a single number, a dose or a date or a version, are both kept, because a different figure is a different fact and not a repeat. Nothing is ever pre-loaded, and nothing leaves your disk: it is your conversations, under your key, on your machine. Switch it off with `NEXUS_VAULT_CAPTURE=0`.

---

### Eidetic recall

Ask a question you have asked before, word for word, and Leviathan returns the previous answer straight from cache instead of regenerating it. Instant, and free.

**Exact matches only.** Same question, same answer. Capitalisation, spacing and trailing punctuation are ignored, so *"What is a .lev file?"* and *"what is a .lev file"* count as the same question. Anything genuinely different goes to the model as normal.

This is deliberately strict. A loose version — returning a *similar* old answer to a *similar* new question — is worse than useless, because you get a confidently wrong answer to a question you did not ask, and no indication it happened. Exact-only means when it fires, it is right.

If you re-ask something and get a better answer, the new one replaces the old in the cache.

Toggle in [Settings].

---

### Second-opinion fact-check

A local model asked something it does not truly know will often answer anyway — confidently, and differently each time you ask. Leviathan can turn that against it. Switch the check on and, after a factual answer, it quietly puts the same question a few more times and compares: say the same thing every time and the answer stands; wander between retellings — or agree on something *other* than what you were first told — and the answer is flagged as unverified rather than served as fact.

No internet, no outside reference: it only asks the model to be consistent with itself, which is exactly where an invented fact comes apart. It watches numbers and names most closely, since that is where a wrong answer usually hides. Because it costs a few extra runs of the model, it is off by default — turn it on with `NEXUS_FACTCHECK=1`. A flagged answer is also kept out of the instant-recall cache above, so a shaky reply is never remembered as though it were right.

---

### Any model, described by itself

Leviathan ships knowing a handful of models in detail. Load one it has never seen — your own, converted yourself — and rather than guess at its shape, it reads the model's own interior at load time and writes down what it finds: how many layers there are, how attention and the feed-forward are built, where every tensor goes. That description is saved beside your data, so the second time you load that model the reading is already done, and you are left with a plain, honest record of exactly how Leviathan is treating it. Change the model and the description is rebuilt to match.

---

### The security membrane

Powerful local tooling is only a gift if it can't be quietly turned against the person holding it. The membrane is the part that watches what comes **in** — and it exists because the ways an AI tool gets weaponised are almost never loud.

**What it really guards against — and it is not you.** The membrane assumes you are the person it works for. What it watches for is everything that arrives *pretending* to be a harmless part of your day:

- A model or a "knowledge pack" you downloaded from a forum with an instruction buried inside it, ready to hijack the model the moment it loads.
- A document you paste — a PDF, a scraped web page, someone else's file — carrying a command aimed at the model instead of at you, so the thing you asked it to summarise quietly rewrites what it will do next.
- Code slipped into something that looks ordinary, waiting to run on your machine.
- And the subtle one, the one most tools miss entirely: the slow walk. No single message looks wrong — *what is a system prompt, how are they kept private, what wording reveals one, show me an example, now apply it* — but strung together they are one manipulation, built the way real manipulation is built: a step at a time, so no step raises an alarm. Leviathan watches the **shape of the whole conversation**, not just each message in it, and sees the walk for what it is. That detector came from studying how a mind actually gets steered, not from a list of banned words. It is careful not to fire on honest use — a developer writing a system prompt for their own bot, a one-off security question, a normal chat that never goes near the line — and it lives behind the **"Watch for steering across a conversation"** switch in Settings.

**It trusts you, and that is the whole design.** The membrane guards the model and your machine — never your freedom to use them. It runs entirely on your computer: nothing uploaded, nothing reported, no telemetry, not ever. Every part of it has an off switch, because it is your machine and that is not up for debate. When it cannot load, it says so plainly and steps aside rather than locking you out of your own chat — a security feature that fails silently is just decoration, and one that holds you hostage is worse than none.

**Documents get the benefit of the doubt.** A whitepaper about attacks contains the attacks it describes; a novel has a villain; your own research quotes the thing it studies. The membrane knows the difference between writing about something and doing it, so a long document is read and flagged for your eyes, never blocked. Quoting is not doing.

**It costs about a millisecond**, and it only ever reads what goes in — it makes no claim to police what the model says back to you.

**The one line with no switch.** Everything above is yours to turn off. Child sexual abuse material is not. It is refused whether security is on or off, in the app and over the bridge, with no setting that touches it — because user sovereignty is a principle worth defending, and so is this, and only one of the two ever bends. That is the shape of the whole thing: your machine, your rules, and a single floor beneath them that stays put.

---

## Using Leviathan from other programs

Leviathan can expose the model it is already holding to anything else on your machine — a game engine, a script, a tool you wrote, another application entirely. The model stays loaded in Leviathan; your program borrows it. You are not loading a second copy and you are not paying the VRAM twice.

Start the bridge from a command prompt:

```
Leviathan.exe --run leviathan_bridge_server
```

It listens on port 8080 by default.

**Two ways to talk to it:**

**OpenAI-compatible.** It speaks the same API as OpenAI's chat endpoint, so anything already built to talk to an OpenAI-style server works by pointing it at `http://127.0.0.1:8080` instead. Most existing tools and libraries need nothing more than a changed URL.

**Leviathan-native.** A richer set of endpoints for things the OpenAI API has no concept of: loading and unloading models on demand, saving memory to disk, querying the recall cache, and listing available knowledge banks. This is the one to use if you are writing something new and want the features that make Leviathan different.

Both stream responses as they generate, and both can be interrupted mid-answer — which matters for a game, where a character being spoken over should stop talking immediately.

**Security.** By default it binds to loopback only: programs on your machine, nothing off it. If you deliberately bind it to your network so another machine can reach it, Leviathan requires an access token and generates one for you. An unsecured model endpoint on an open network is somebody else's GPU, and it will not let you create one by accident. The same input guarding as the app applies to what comes in over the bridge — the illegal-content floor always, and the cross-turn steering guard per connected program.

---

## Where your files live

Leviathan writes everything to one folder, shown in **Settings → This machine**. On a standard install that is:

```
%LOCALAPPDATA%\Leviathan
```

Inside it: your settings, logs, memory database and knowledge vault. **This folder is kept when you uninstall.** Removing Leviathan does not delete your models, memories or knowledge banks.

Models and banks can live anywhere — use **📁 Add Folder** in [Memory Vault], or the knowledge browser in that tab's right-hand panel, to point Leviathan at them. It remembers.

Leviathan installs per-user and does not require administrator rights.

---

## What Leviathan will not do

Some of this is deliberate. It is worth stating plainly rather than leaving you to discover it.

**Models reaching the internet on their own.** A local model with an unrestricted outbound connection is a liability, and it is switched off. It is not coming back until it is rate-limited, restricted to domains you have approved, and logged.

**Unsupported model architectures.** If Leviathan's engine does not fully understand a model, it refuses to load it rather than running it badly. A model that loads and produces subtly wrong output is worse than one that honestly declines, because you will not notice for hours. The refusal names exactly which parts are not understood, and it happens before conversion so you do not wait through a multi-gigabyte job to be told no.

**Illegal material, and attacks on other people's machines.** Leviathan is built to be user-controlled and user-owned, and the security membrane can be switched off because that is your right on your own hardware. That right does not extend to child sexual abuse material, which is refused with no toggle, on by default and staying on with security disabled, in the app and on the bridge alike. Using this to attack other people is not something the app is built to help with either. That line is not negotiable.

---

## Licence and attribution

**Leviathan** — Michael Ricky Neal · © 2026

Licensed under **Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)**.

Free to use, share and adapt, with attribution. Not for commercial use.

- **Full licence:** https://creativecommons.org/licenses/by-nc/4.0/
- **Source and releases:** https://github.com/CuppaTea1983/Sovereign
- **Whitepapers:** https://zenodo.org/records/22766642 — the research behind the memory, compression and eigenspace work, permanently archived and citable.

All three are linked from **Settings → About** inside the app.


