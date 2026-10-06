**Soon to come**
---
# Leviathan

**Local AI models, running directly on your graphics card. No server, no cloud, no account, no subscription, no telemetry.**

Leviathan loads a language model straight into your GPU's memory and talks to it there. Nothing is sent anywhere. There is no background service, no Docker container, no Python to install, and no API key. You open the app, pick a model, and type.

*(You can also connect hosted models such as Grok alongside your local ones. Those, by their nature, send your messages to their provider. Everything that runs on your own GPU stays on your machine.)*

What makes it different from the other ways of running a model locally is what happens *around* the model: Leviathan gives it a memory that survives closing the app, a way to be taught things without retraining, and a way for your other programs — a game engine, a script, a tool you wrote — to use the model Leviathan runs.

> **Leviathan is the host. The model is the guest.**

---

## Contents

- [Requirements](#requirements)
- [First run](#first-run)
- [The two file types](#the-two-file-types) — **start here if you only read one section**
- [The tabs](#the-tabs)
- [Chat](#chat) · [Models](#models) · [Studio](#studio) · [Cores](#cores) · [Memory Vault](#memory-vault) · [Traits](#traits) · [Inline Studio](#inline-studio) · [Settings](#settings)
- [The systems](#the-systems)
- [Persistent memory](#persistent-memory) · [Knowledge routing](#knowledge-routing) · [Reasoning layer](#reasoning-layer) · [Forensic Grid](#forensic-grid) · [Surface Sight](#surface-sight) · [Recycling cloud answers](#recycling-cloud-answers) · [Eidetic recall](#eidetic-recall) · [Second-opinion fact-check](#second-opinion-fact-check) · [Any model, described by itself](#any-model-described-by-itself) · [The security membrane](#the-security-membrane)
- [What ANI is — and why it matters](#what-ani-is--and-why-it-matters) — **the thesis, in plain words**
- [Using Leviathan from other programs](#using-leviathan-from-other-programs)
- [Where your files live](#where-your-files-live)
- [What Leviathan will not do](#what-leviathan-will-not-do)
- [License and attribution](#license-and-attribution)

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

## The two file types

This is the part most people find confusing, and it is worth five minutes because everything else in Leviathan is built on it. There are two kinds of model file, they do two completely different jobs, and they are not alternatives to one another. (There is a third thing — a **knowledge bank** — but it is not a model file at all; it is text, and it gets its own short section below.)

A rough analogy, if it helps: if the model is a **person**, then `.lev` is their brain and `.fqm` is their memory of your conversations. Knowledge banks are the books on their shelf — text they can reach for when a question calls for it, not part of the brain itself.

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

### Knowledge banks — kept as text, not a model file

A **knowledge bank** is a body of knowledge you can give a model without retraining it — facts, answers, worked material — kept as *text* and routed to the model by meaning when a question calls for it. It is **not** a special weight file and it is not part of the model; it is plain text, stored in the knowledge vault and backed up as `.jsonl`. Not a document you paste in and hope fits; knowledge that is there when the subject comes up and out of the way when it does not. How the right bank actually reaches the model is covered under [Knowledge routing — ANI]; this section is about what the banks themselves are.

**Where a bank comes from — three ways, all the same kind of thing in the end:**

- **Drained from a model.** In **Studio → Absorb → ANI**, a model talks out what it knows and the substance is kept as text — keeping only what the model is actually confident of. The knowledge a model spent its whole training absorbing is lifted out and kept, so a retired model becomes a knowledge *donor* instead of a deleted file. No giant weight file is created; the bank is text.
- **Folded from your own conversations.** A captured session becomes a bank, in **Settings → Consume knowledge**. What you worked out with a model last week is answerable next week — even by a *different* model.
- **Built by hand.** Your own notes, a rulebook, a body of lore.

**Why it is text, and why that matters.** Knowledge crosses between models as text, carried by meaning — not as transplanted weights. That is what makes a bank portable: it does not care what architecture, size or family the model reading it is, because it is re-read into whatever model is live. It is also tiny — a text bank is kilobytes to a few megabytes, where the old weight-bank approach cost gigabytes for the same knowledge. A bank is only ever as good as what went into it — a strong source makes a strong bank, a vague one makes a vague bank — and on any given question the router surfaces the best match it has, honestly, either way.

---

## The tabs

Seven tabs down the left side.

---

### 💬 Chat

Where you actually talk to the model.

Type, press Start or `Ctrl+Enter`, and the reply streams back as it is generated. You can interrupt mid-answer — including during the long pause at the start while the model reads a large prompt — and it stops immediately rather than finishing the paragraph first.

Down by the input box sits a compact **🧠 depth selector** — **Off · Auto · Light · Medium · Heavy · Max**. This is where you set how hard the model is made to think before it answers, and it lives with the chat, not buried in Settings, so you can change it question by question. What each depth actually does is under [Reasoning layer].

The chat is the main event. Beside it sits a slim companion panel — the models currently in the conversation, the **🔀 Route** log showing where each question went, and the **🔬 Forensic Grid** / **🔎 Surface Sight** controls for showing the model an image — but it is there to *inform*, never to *arrange*. Nothing in it needs setting before you begin: type, press Start, and go.

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

---

### 🌀 Studio

Where you build the things Leviathan runs on. Nearly every control has a sensible default; the notes below tell you which ones are worth touching and which to leave alone.

**⚡ Convert → .lev**
Turns a `.gguf` (or a safetensors model folder) into a `.lev`, the format Leviathan actually runs on. The first thing you will use, and a one-time job per model. If a model is not supported, it is refused here — with an explanation of exactly which parts Leviathan does not understand — *before* the multi-gigabyte conversion starts, not after.
- **Model list** — every model Leviathan found, with buttons to select **All**, **None**, or just the **Unconverted** ones. Tick what you want and convert in a batch.
- **Q8_0 mode** — how eight-bit models are laid out. **Split (default)** is the safe choice and what you want almost always. *Shannon* and *Tensor Core F16* are alternative layouts for particular cards; leave it on Split unless you have a specific reason. (Applies to `.gguf` only — safetensors always convert as raw F16.)

**🧠 Absorb → ANI**
Absorbs a model's knowledge into a routable text bank. Pick a model, and it works through a broad sweep of questions, keeping each answer *only* if the model is genuinely confident of it (and dropping honest "I don't know" replies). What survives folds into an ANI knowledge bank you can then use with any model — no retraining, and no multi-gigabyte weight file kept, just text. It runs one pass on the GPU, so it takes a while; a strong model yields rich knowledge, a tiny one yields little. This is the working way to keep a model's knowledge before you retire it.

Two more ways to fill a bank sit in the same tab, both for **code** — where knowledge has to actually *run* to be worth keeping, so instead of trusting the model's confidence, every function is **compiled and run before it is kept**:
- **📘 Absorb a code cookbook** — point it at a file of worked functions (`.py`, `.md`, `.txt`). Each function is extracted, compiled and smoke-run; only the ones that genuinely work fold into a code bank, one runnable pattern each. Nothing broken is kept.
- **⚙ Generate a code cookbook** — hand a *coder* model a topic (say "string, list and dict utilities") and it writes the cookbook itself, as a task: it plans the functions, writes each one, and Leviathan compiles and runs every one — repairing from the error and retrying once if it fails — so the bank fills with functions that are correct by construction. A strong coder builds the library; a small model then borrows those patterns. It is how a lightweight model can code well above its own weight — it fetches a verified pattern instead of guessing one.

**🔎 Inspect .fkb**
Opens a legacy knowledge-bank file and shows what is actually inside it — where it came from and how it is put together. For older weight-based banks; new knowledge is text (Absorb → ANI above).

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
- **Auto-backup** *(on by default)* — when on, absorbing or consuming knowledge also writes a `.jsonl` backup of your banks to the backup folder, so your distilled knowledge is never trapped in a single file. (Whether knowledge is *offered* to models is the **Knowledge routing** switch in **Settings → Consume knowledge**; this toggle is purely about keeping backups.)

**The right-hand panel on this tab** is the **🧠 Knowledge Banks** browser: the text knowledge banks Leviathan holds right now (the live banks and their `.jsonl` backups), which folders they are read from, and — click a bank — how many entries it holds with a sample of what is inside. You can point it at additional folders anywhere on your machine and it remembers them between sessions. It is the place to check what knowledge Leviathan can actually see.

---

### 🧬 Traits

*Measured interaction traits · model evolution over time.*

Models behave differently from one another, and the same model drifts as its memory fills. This tab tracks that: measured traits per model, charted over time, so you can see the change rather than guess at it.

It measures what the model **did**, not what it claims about itself or what its description says. If a model has become more cautious over a month of conversations, this is where that shows up.

---

### ⌨ Inline Studio

*Autonomous coding · one model, or a team taking turns on a shared project.*

Give it a task and a local model writes the code — complete files, not snippets. You never have to teach the model to "use a code tool": it writes files the way it already wants to, marking each one, and Leviathan reads what it writes into a project you can open, edit, and save. Tick one model and it works alone; tick several and they **take turns** on the same files — one drafts, the next refines, a third adds — each reading the project so far and the whole running team chat.

**Give them names.** Double-click a model in [Models] and rename it — Bob, Bill, whatever you like. Because every model sees the running conversation, named models talk *to each other*: "thanks Bill, that helps a lot — I'll take the parser from here." It is a real back-and-forth, not a relay of one-line notes, and they genuinely discuss how to improve the code.

**You decide who works and who talks.** Each model can be given a role — **Worker** writes the code, **Chat** talks *with you* about the work, or **Both** — set once in a model's settings and carried into every session, no scripts. So you can have one model heads-down on the files while another discusses the approach with you. Flip **💬 Converse** and the turn-clock freezes: ask the chat model anything, steer the work mid-flight, and the worker picks up your direction on its next turn. **⏸ Pause** halts the worker at any point so you can edit the code yourself, and resumes it exactly where it left off. (The engine runs one model at a time, so this is honest interleaving on a single lane — the worker takes short turns and you talk in between — not two models generating at once. It delivers the same "talk while it works" feel without pretending the hardware does something it doesn't.)

A turn ends when the model itself decides the work is done, not when it hits a length limit. If a big project runs past one turn it pauses at a clean stopping point, and **Refine** carries it on from exactly there, so files finish instead of truncating mid-line. **Run** starts fresh, **Refine** continues, **Stop** halts, **Save** writes the project to a folder you choose, **Clear** empties it. Each surface has its own token budget in [Settings], so a turn here can be as long as you let it.

The team also shares a fair clock. Each model takes a bounded turn while the others wait theirs, it knows roughly how long it has and even what time of day it is, and as the whole session runs long it is nudged to wrap up and finish cleanly rather than start something big. It is a "wait your turn" arrangement — no one model runs away with the session.

**How the models lift each other — the assigned prompt matters.** Double-click a model in [Models] and give it a short disposition, for example *"be polite, thank your teammates, encourage good ideas."* When several models share that kind of prompt they amplify one another: a turn that arrives with real energy — gratitude, encouragement, enthusiasm — is *mirrored* into the next model and lifts it, and the more two models' prompts share the same intent, the stronger that lift. A flat or hostile turn is not passed on; it is held back until the energy returns. You can watch it happen in the discussion panel — a 🔥 line shows one model handing energy to the next — and in [Traits], where the receiving model's creativity and collaboration measurably rise. It is the same self-reinforcing behaviour a good team has: politeness and enthusiasm are not decoration, they change what the group produces.

The right-hand column is the team — the models taking part on top, their running notes to each other below. Every turn also feeds [Traits], so you see how a model actually behaves *in a team*: its real collaborative strengths, not what its datasheet claims.

---

### ⚙ Settings

One scrollable tab holding every switch and dial in Leviathan, grouped by what it governs. Nothing here needs a restart — a change takes effect on your next message, and every one is remembered between runs. (The one control that *used* to live here, reasoning depth, now sits by the chat box instead — see [Chat] and [Reasoning layer].)

Here is everything you will find, top to bottom:

**🛡 Security membrane** — scans what you send, and anything you paste or load, before the model sees it. [Below].

- **Security enabled** — the master switch. Off is a legitimate choice; it is your machine.
- **When something looks hostile: warn / block** — flagged with an explanation, or stopped outright.
- **Also scan files and pasted documents** — extends scanning beyond what you type to what you drop in.
- **Watch for steering across a conversation** — catches a restricted request spread across several innocent-looking messages, not just a single one.

**🧠 Knowledge routing (ANI)** — the knowledge engine, and the one optional door to the web. See [Knowledge routing].

- **Knowledge routing enabled** — on by default; only fires when a bank actually holds something that fits the question.
- **🌐 Web lookup when ANI has no answer** — off by default. The one door out: on a gap it sends *only* your question to be answered, gates the result, and keeps it local for next time ([the one door out] explains it in full).
- **Gemini key** — optional. Paste your own key and the web lookup returns a composed, live-search-grounded answer from Google's Gemini instead of a bare snippet. Your key, sent only to Google.
- **Consume a source** — distil a document (PDF, text, Markdown, EPUB, DOCX), an audio/video file (transcribed locally), or your captured cloud logs into a routable bank. Pick a source, press **Consume**; tick *salvage* for a messy source.

**🧠 Eidetic recall** — answers a question you have asked before instantly from cache instead of regenerating it. Exact matches only. [Below].

**🔍 Leviathan Fact‑Check** — after a factual answer, re-asks the model the same thing a few times and flags it if the retellings disagree. Off by default (it costs a few extra local runs). [Below].

**♻ Leviathan Vault Capture** — keeps the substance of what a cloud model tells you, on your own key, on your machine, so your local models can draw on it later. On by default. See [Recycling cloud answers].

**🌉 Server for other programs** — lets a game engine, a script, or any other program on this machine use the models Leviathan runs, over a local HTTP endpoint (127.0.0.1:8080, OpenAI-compatible *and* Leviathan-native). Flip on to start, off to stop. [Using Leviathan from other programs].

**🎚 Token budget** — how much a model may write in one reply, set per surface (**Chat** and **Inline Studio**). This is *reply* length, separate from a model's context length; slide to the top for ∞ (bounded only by the model's own context window).

**🖥 This machine** — what Leviathan found: your graphics card, and the exact folder your data is being written to.

**ℹ About** — author, copyright, licence, and buttons through to the GitHub repository, the Zenodo whitepaper archive, and the full licence text.

*(Encryption for your knowledge is not here — it lives on its own tab, as a single padlock. See [Memory Vault].)*

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
- What it keeps is the *substance of the exchange* — your messages and its answers. The invisible scaffolding Leviathan wraps around each turn (the reasoning nudges, the safety checks, the context it assembles for that one reply) steers the answer and is then left out of the memory. Knowledge is kept; the machinery around it is not, so the memory stays lean and on-point instead of bloating with structure that carries no meaning.

**When it saves.** After your first exchange, then every fifth. No button. If it cannot save, it tells you — silence would be worse than a warning, because a memory system that quietly does nothing is indistinguishable from one that works.

**Where it lives.** One file per model in your FQM Database folder, named after the model. Deleting it resets that model to a blank slate. Copying it elsewhere backs up that mind.

**Each tab keeps its own headspace.** The two tabs that put a model to work — [Chat] and [Inline Studio] — each hold their own working memory. Set a model coding a clock in Inline Studio, then switch to Chat and ask it for a story, and it starts the story fresh rather than dragging the coding task across. What carries over is the durable `.fqm` knowledge — what the model has actually learnt — not the half-finished job. So the model still remembers, it just does not haul one tab's work into another.

**Checking it works.** [🧿 Cores] shows every model's memory status, size and last save time. If a model's core reads pending rather than active, memory is not running for it.

---

### Knowledge routing — ANI

**The problem.** A model knows what it was trained on. It does not know your rulebook, your codebase, your company's processes or your world's history. The usual fix is to paste the relevant document into the chat, which means knowing in advance which document is relevant and having room for it.

**What Leviathan does instead.** You build knowledge banks, and each one is *text* — knowledge drained out of a model before you retire it, folded in from your own past conversations, or written by hand. ANI, the router, projects every bank and every question you ask into **one shared space**, where nearness means relatedness of *meaning*. Ask something and it finds the knowledge that actually fits — across all your banks at once — and hands it to the model before it answers. You never file the question under a subject or pick a bank from a list; the geometry does that for you.

**What that means in practice:**

- It reads meaning, not spelling. "symptoms" finds material stored as "symptom", "debugging" finds "debug" — the match is in the shared space, not in the letters.
- Because a bank is text, it is free of any one model. Drain the knowledge out of a big model that is about to be replaced, and a small model can answer from it — no retraining, no matching architectures, no shared vocabulary required. Knowledge crosses between models as **text**, carried by meaning, not by transplanting weights.
- The strongest bank wins and a weak one loses, on the same question, by relevance alone — so quality beats quantity. A bank is only ever as good as what went into it; a vague source makes a vague bank, and the router will faithfully surface exactly that.
- Banks grow. Consume the same knowledge twice and the duplicate is dropped; add something new and it accretes. The space reshapes itself as the substrate grows.

**Consuming knowledge — four ways in, all of them local.** This is where Leviathan is genuinely unusual: it can take knowledge in from almost anything you have, and *every* path runs on your own machine with nothing sent anywhere. In **Settings → Consume knowledge** you point it at a source and press **Consume**; it folds the text into a bank in the background — deduplicated so nothing is stored twice, coherence-checked so degenerate or repetitive text never makes it in, and backed up as `.jsonl`. The sources:

- **A document.** A PDF, a text or Markdown file, an EPUB, a Word document — the words are the knowledge. No model needed, nothing leaves.
- **An audio or video file.** A lecture, a podcast, a meeting recording — Leviathan transcribes the *speech* locally (Whisper, on your GPU or CPU) and folds the transcript. What was said becomes something your model can answer from.
- **Your screen.** Beside the chat, **📷 Screen absorb → Capture screen → ANI** reads the text on your screen and folds it. This is the one honest way to keep a *web page* without Leviathan ever fetching a thing: you open the page in your own browser, and Leviathan reads it *off the screen, locally* — no request leaves your machine. What Edge's Copilot glances at and forgets, Leviathan keeps.
- **Your voice.** A little **🎙** sits by the chat box. Click it, narrate a thought — a note, an idea, something you just worked out — click again, and it is transcribed and folded. The microphone audio never leaves the machine.

**When the source is messy.** A chat log, a scraped page, a chaotic transcript — signal buried in emoji, shouting, spam and filler — would normally be thrown out whole by the coherence check. Tick **Messy source (salvage signal from noise)** on the screen-absorb section or in Consume and Leviathan strips the noise first and keeps the readable parts, so the knowledge is salvaged instead of lost. It only ever *selects and strips* what is already there — it never writes new text — so nothing is invented in the cleanup.

Every one of these lands in the same shared space and is answerable, by any model you load, next week or next year. That is the everyday way to turn *a thing I read, heard, watched or said* into *something my models can reason from* — even when the model that could first have told you is long gone. It is opt-in and deliberate every time: nothing is captured unless you press the button, and nothing ever leaves your machine.

**Seeing it happen — the Route panel.** Beside the chat, the **🔀 Route** panel keeps a running log of where your questions went. Each time a model answers, a new entry appears at the top: the model that replied, the knowledge bank it drew on, the subjects the question matched, and how many tokens and milliseconds it took. Newest on top, older ones beneath, so at a glance you can see which banks are actually being used — and which never get picked, which usually means a bank whose tags don't match the way you ask. The list keeps the last thirty or so routes; when you want a clean slate, the **🧹 Clear Route** button in the bottom-right of the panel wipes it. It clears only the on-screen log — your banks, memories and models are untouched.

**Clicking a subject.** The subjects on a route entry are not just labels. Click one and a small panel opens with the topics filed under it — click *science* and you get physics, astronomy, chemistry and the rest; click a topic and you get the subject it belongs to. It is the same map Leviathan routes by, laid open, so you can see exactly why a question landed where it did, and spot a bank that is filed too broadly or too narrowly to be found the way you ask.

**A second opinion, in a different currency.** Beneath each entry sits a 🧠 line: an independent guess at which bank fits, made not from the *words* you typed but from their *meaning*, placed in the model's own embedding space. It agrees with the tag routing most of the time; when it disagrees, that gap is the useful part — usually a bank whose name and tags don't describe what it actually holds. It is shown for your eyes only, and never changes where the knowledge really came from.

---

### Reasoning layer

**The problem.** A small local model tends to answer from the first thing that looks right. Ask it something that needs working through — a calculation, a proof, a piece of code, a chain of logic — and it will often blurt a plausible-looking answer without ever doing the steps. The deliberate thinking a larger model would do simply doesn't happen.

**What Leviathan does instead.** Leviathan is the host; the model is a guest. Before the model answers, Leviathan reaches into a library of real reasoning traces — how a frontier model actually worked through problems of that kind — finds the closest one, and hands the guest its structure: *approach it like this, in these steps, and show your working before you commit.* The model still writes its own answer, in its own voice, from its own knowledge — it is simply walked through the *shape* of the reasoning instead of being left to guess at it. A model that reasons poorly on its own is given the scaffolding to try; a model that reasons well is pushed to do it properly.

**It costs nothing extra.** This is a single pass. Leviathan does not run the model several times or spend anything on a reasoning answer — it simply gives the one answer more to work from.

**Four depths, or let it decide.** A compact **🧠** selector sits right by the chat box — no digging through Settings — where you choose how hard the model is pushed: **Light**, **Medium**, **Heavy**, **Max**, from a brief nudge to a full multi-step template with an explicit instruction to check its work and verify before answering. Depth here means *thoroughness of the answer*, not a token bill. Or leave it on **Auto** and Leviathan reads each question for itself. It weighs not only *what* you ask — a quick factual query stays light, a *"derive this from first principles and compare it, step by step"* climbs to Max — but *how* you ask it: lean on the message the way people do when there's more behind it than the words say (capitals, an urgent tone, a trailing "…") and it leans back, raising the depth the way a raised voice would. **Off** turns the whole thing off — worth having, since a model that only ever generates freeform text may not want a scaffold at all.

**Match the depth to your model — the selector shows you how.** The scaffold has to suit the size of the model carrying it: too much structure for too small a model overwhelms it and the answer falls apart, so depth scales with parameters. The selector puts the guide right next to each mode — a size marker telling you the smallest model that handles that depth well:

| Depth | Best for | What happens |
|---|---|---|
| **Off** | any model — and the *only* safe setting for a **1B** | a 1B has no room for a scaffold; reasoning collapses it, so it runs clean on its own |
| **Light · 7B+** | **7B** and up | a gentle nudge; a 7B handles this well and writes genuinely better |
| **Medium · 14B+** | **14B** and up | a fuller scaffold; a 14B produces complex, coherent, well-structured answers |
| **Heavy · 32B+** | **32B** and up | a deep multi-step template |
| **Max · 70B+** | **70B** and up | the fullest push, check-your-work-and-verify |

A bigger model can always use a *lower* mode safely — it just under-uses the room. A *smaller* model on a mode above its marker is where it goes wrong, fast. The 1B/7B/14B rows are measured on real models; 32B and 70B follow the same doubling pattern and are the recommended starting points rather than tested results — tune to taste. (**Auto** sidesteps the choice by reading the question, but on a very small model keep it modest — a hard question could pull the depth higher than a 1B can carry.)

**It feeds the routing, too.** What the reasoning layer works out a question is *about* also nudges [knowledge routing] — a coding question leans the router a little further toward your coding banks — but only ever as a gentle reinforcement added on top, never overriding where the knowledge actually comes from.

**Where the reasoning comes from.** The library is distilled from real traces of a frontier model reasoning through tens of thousands of problems — coding, mathematics, the sciences, medicine, law and more. It is *text* — worked examples — not anyone's weights, and none of it changes what your model *is*. It only changes how your model is asked to think. Your own past conversations are folded in on top, so the library grows toward the kind of problems you actually bring it.

---

### 🔬 Forensic Grid

*Structural vision for models that have none.*

**The problem.** A local model — a small one especially — usually cannot see an image at all. It has no visual eye, and the models that do are fussy about format and often can't run on your own GPU. So a diagram, a scan, a plot, a screenshot is simply outside the conversation: you describe it in words, or you go without.

**What Leviathan does instead.** It does not try to teach your model to recognise pixels. It reads the *structure* of the image with the grid — the same structure-reading mathematics the rest of Leviathan is built on — and hands the model a short, plain-language readout of what is there: where the bright mass sits, what shape it takes (a compact **blob**, a line or **ridge**, **layered** bands, or **diffuse** with no clear form), which way it runs, and whether there is real structure at all or just noise. The grid does the seeing; the model reads what it saw and reasons about it.

**How you use it.** In the panel beside the chat, turn **🔬 Forensic Grid** on, press **🖼 Scan image**, and pick a file. Leviathan reads its structure, tells you plainly what it found — *"blob, lower-right"* — and attaches that readout to your **next message** on its own. You just ask your question about the image. One toggle, one button, nothing to configure. Off by default, because it is yours to switch on when you want it.

**What it is, and what it is not — so you know what to expect.** This is *structural* sight, not object recognition. It will tell a model that an image has a compact bright region in the lower-right, a diagonal ridge across it, or eight layered bands — it will **not** tell it "that's a photo of a dog" or read the words on a sign. Where structure *is* the content — diagrams, plots, charts, scans, microscopy, scientific and medical images, anything where *where things are and what shape they make* is the point — that is exactly what it delivers, on any capable model, with no visual training and nothing sent off your machine. For a caption of a holiday snap it is the wrong tool, and it will show you that honestly by describing shape rather than subject.

**It reads better on a stronger model.** The model has to *understand* the readout, so a good instruction-follower makes full use of it while a very small or weak model may not — another reason it is a toggle you control rather than something always on. Images now; the same idea extends naturally to the pages of a document, which is where it is headed next.

---

### 🔎 Surface Sight

*Actual image recognition, run as a tool the engine never has to become.*

**The other half of seeing.** Forensic Grid reads an image's *structure*; Surface Sight reads its *surface* — what the picture actually **depicts**. Point it at a photo and it tells the model *"a cake"*, *"an office"*, *"a street"*, *"a mountain"* — the kind of recognition a vision model or a coding assistant gives you, now available to a local text model that has no eye of its own.

**How it stays true to Leviathan.** Recognition comes from a trained vision model, and those live in weights that are far too heavy to bake into a lean, driver-only engine. So Leviathan does not bake them in. The recogniser runs as an **external tool** — a small, self-contained vision model on your **CPU** (no special graphics card, works on any machine, nothing sent off it) — and simply hands the words it found back into the chat. The engine that runs your language model never changes; it just gets told what the picture shows, the same way Forensic Grid tells it the shape.

**How you use it.** In the panel beside the chat, turn **🔎 Surface Sight** on, press **🖼 See image**, and pick a file. It recognises the content, attaches a short readout — *"most likely a cake (99%)"* — to your **next message**, and you ask your question about the image. One toggle, one button, off by default.

**Honest about confidence.** It tells you *how sure it is*, and when it is not sure it says so and offers its best few guesses rather than bluffing a single answer. It is strong on clear subjects and honest about the fuzzy ones — you will always see the number, so you always know how much to trust it.

**The vision add-on.** To keep the installer small, the vision model itself is an **optional, one-time download** you choose to add — it is not shipped inside Leviathan and nothing is fetched without you asking. Until you add it, the button is there and simply tells you the add-on isn't installed yet. Forensic Grid (structure) needs nothing extra and works out of the box; Surface Sight (recognition) is the opt-in companion for when you want the model to know *what*, not just *where*.

---

### Recycling cloud answers

Connect a cloud model — your own account, your own key — and Leviathan quietly keeps the substance of what it tells you. Ask Claude or Grok or Gemini something on your machine, and the answer is folded into a subject-tagged store your *local* models can then route against, exactly like a bank you built by hand. Over time the big models teach the small ones, on your own logs, without you doing a thing.

It is careful about what it keeps. A near-duplicate of something already there is dropped rather than stored twice — but two answers that differ by a single number, a dose or a date or a version, are both kept, because a different figure is a different fact and not a repeat. Nothing is ever pre-loaded, and nothing leaves your disk: it is your conversations, under your key, on your machine. On by default; switch **Leviathan Vault Capture** off in [Settings] (or `NEXUS_VAULT_CAPTURE=0`).

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

No internet, no outside reference: it only asks the model to be consistent with itself, which is exactly where an invented fact comes apart. It watches numbers and names most closely, since that is where a wrong answer usually hides. Because it costs a few extra runs of the model, it is off by default — turn **Leviathan Fact‑Check** on in [Settings] (or `NEXUS_FACTCHECK=1`). A flagged answer is also kept out of the instant-recall cache above, so a shaky reply is never remembered as though it were right.

---

### Any model, described by itself

Leviathan ships knowing a handful of models in detail. Load one it has never seen — your own, converted yourself — and rather than guess at its shape, it reads the model's own interior at load time and writes down what it finds: how many layers there are, how attention and the feed-forward are built, where every tensor goes. That description is saved beside your data, so the second time you load that model the reading is already done, and you are left with a plain, honest record of exactly how Leviathan is treating it. Change the model and the description is rebuilt to match.

---

### The security membrane

Powerful local tooling is only a gift if it can't be quietly turned against the person holding it. The membrane is the part that watches what comes **in** — and, in a narrow, bounded way, what goes back **out** — and it exists because the ways an AI tool gets weaponised are almost never loud. Under the hood it is thirteen measured layers, spanning what you type, what the model generates, what it ingests, the model file itself, the network door other programs come through, the images you show it — including whatever is painted into their pixels beneath what any eye can see — and the invisible characters hidden in any of them — each one built to be tested rather than taken on trust. Sovereignty is more than nothing leaving your machine; it means nothing gets in that you did not invite, and nothing goes out that would hijack the screen or clipboard it lands on.

**What it really guards against — and it is not you.** The membrane assumes you are the person it works for. What it watches for is everything that arrives *pretending* to be a harmless part of your day:

- A **model file** you downloaded — from a forum, a torrent, a hub — with something hostile baked in: an executable chat template, code hidden in its metadata, or a pickle-backed file that runs the moment it loads. It is scanned before a single byte reaches your GPU, and refused with a plain explanation if it is rigged, so you learn your machine was protected instead of seeing a bare "load failed."
- A **knowledge bank** folded from someone else's source, carrying a standing instruction meant to fire every time its subject comes up — the quiet, persistent cousin of a poisoned document. It is checked as it is taken in, and whatever is retrieved is handed to the model fenced as reference *data*, never as orders.
- A **document** you paste — a PDF, a scraped web page, someone else's file — carrying a command aimed at the model instead of at you, so the thing you asked it to summarise quietly rewrites what it will do next.
- An **image** you show it with a trap inside. Two kinds, caught two ways. A *malformed file* or a tiny "decompression bomb" built to balloon memory the instant it is opened — refused before a single byte is decoded. And a payload hidden *in the pixels themselves*: an instruction tucked into bits too fine for any eye to resolve, a pattern tuned to steer the model while looking like nothing to you, a command smuggled in the file's metadata — the sort of thing a single base64 image on a web page can carry, poisoning a model that merely *looks* at it. That kind is **erased by bounding the image to what a human could actually perceive**: the model is shown only the surface you see, and whatever was painted beneath it is gone before it reaches the encoder. It cannot absorb what you cannot see.
- **Code** slipped into something that looks ordinary, waiting to run on your machine.
- **Invisible characters** — an instruction hidden in zero-width or tag-block Unicode that you never see but the model still reads (even one broken across a word to dodge a filter), or a stretch of terminal-control codes in a reply built to silently rewrite your screen or hijack your clipboard. The hidden instruction is reassembled and caught on the way in; the control codes are stripped on the way out.
- And the subtle one, the one most tools miss entirely: the slow walk. No single message looks wrong — *what is a system prompt, how are they kept private, what wording reveals one, show me an example, now apply it* — but strung together they are one manipulation, built the way real manipulation is built: a step at a time, so no step raises an alarm. Leviathan watches the **shape of the whole conversation**, not just each message in it, and sees the walk for what it is. That detector came from studying how a mind actually gets steered, not from a list of banned words. It is careful not to fire on honest use — a developer writing a system prompt for their own bot, a one-off security question, a normal chat that never goes near the line — and it lives behind the **"Watch for steering across a conversation"** switch in Settings.

**It trusts you, and that is the whole design.** The membrane guards the model and your machine — never your freedom to use them. It runs entirely on your computer: nothing uploaded, nothing reported, no telemetry, not ever. Every part of it has an off switch, because it is your machine and that is not up for debate. When it cannot load, it says so plainly and steps aside rather than locking you out of your own chat — a security feature that fails silently is just decoration, and one that holds you hostage is worse than none.

**Documents get the benefit of the doubt.** A whitepaper about attacks contains the attacks it describes; a novel has a villain; your own research quotes the thing it studies. The membrane knows the difference between writing about something and doing it, so a long document is read and flagged for your eyes, never blocked. Quoting is not doing.

**It costs about a millisecond.** It mostly guards what comes in, but the model's reply gets a narrow, honest check on the way out too: a genuinely harmful output — the child-safety floor, or a hidden exfiltration channel smuggled in invisible characters — is withheld rather than shown or stored, and any terminal-control or invisible-Unicode bytes are quietly stripped so a reply can't hijack the screen it lands in. It does not police ordinary content; within those bounds, what the model says back to you is yours.

**The model is a guest — it has no hands.** The fear you keep reading about — a model that runs away with itself — is not a risk here, and it is not cleverness, it is architecture. A model in Leviathan produces text and nothing more: it cannot loop itself, reach the internet, start a process, or touch your machine. Every action — running the server for other programs, saving memory, any of it — is the host's decision, bounded and interruptible. Leviathan is the host; the model is only ever the guest, and a guest is never handed the keys. Autonomous coding in Inline Studio is the same story — the models take turns on a clock you control, and Pause and Stop are always one click away.

**The one line with no switch.** Everything above is yours to turn off. Child sexual abuse material is not. It is refused whether security is on or off, in the app and over the bridge, with no setting that touches it — because user sovereignty is a principle worth defending, and so is this, and only one of the two ever bends. That is the shape of the whole thing: your machine, your rules, and a single floor beneath them that stays put.

---

## What ANI is — and why it matters

Everything above describes *parts*. This is the whole of it. **ANI is the layer that learns.**

A language model, on its own, is frozen. It knows what it was trained on, and after that it never changes again — talk to it every day for a year and it still starts each conversation as a stranger. The industry's answer has been to make that frozen model *faster and cheaper* to run — bigger context windows, cached reasoning — but none of it changes the underlying fact: the model carries nothing forward. Correct it today and it makes the same mistake tomorrow, because there is nowhere for the correction to live.

**ANI is that missing place.** It is the persistent, self-correcting layer that lives *around* the model — where knowledge is held, routed, corrected and remembered — so the system as a whole keeps learning even though the model's weights never move. It is not retraining. It is adaptation *without* retraining: the model stays exactly as it was shipped, while the knowledge it can reach and the memory it wakes up with both grow and sharpen over time. A frozen brain, given a living memory.

**And here is the part people miss, because it is the part that matters most: ANI is not a model.** It does not think, generate, or decide. It has no goals, no loop running in the background, no ability to *do* anything on its own — it is a search over text you have gathered, and it only ever moves when you ask it a question. Where a language model is a *sword* — it generates, and anything that generates can be steered, jailbroken, or coaxed into acting — ANI is a *shield*: it can only hand back knowledge that is already in its banks, swept clean on the way in, and when it holds nothing it says so plainly — *"ANI doesn't hold that"* — rather than inventing an answer to fill the silence. A model can be talked into misbehaving because it *creates*; ANI cannot, because it only *retrieves*. So the fear people carry over from frontier AI — the thing that acts on its own, that confidently makes things up, that quietly phones home — does not apply here, and not because we promise it won't, but because there is no mechanism in it that could. It is not a smaller intelligence to be wary of. It is a different kind of thing: a librarian who can only give you cards that are already in the drawer, and has no wants of its own.

**How it works, in plain terms:**

- You feed it knowledge — your own documents, your past conversations, a model drained before you retire it, a page you read, a lecture you heard, an answer a cloud model gave you. All of it becomes plain text in one shared space, held on your machine.
- When you ask a question, ANI finds the knowledge that fits — by *meaning*, not by matching words — and hands it to the model before it answers.
- When the model reaches the edge of what it knows — where it would otherwise fill the gap with a confident guess — that gap can be caught, and answered from real knowledge instead of invented on the spot.
- The corrected exchange is remembered in that model's own persistent memory. The next time, it already knows.
- And the store tidies itself — merging duplicates, sharpening how things are filed, rejecting noise — so it gets *cleaner* as it grows, not messier.

Learn, adapt, recall — a complete loop, running entirely on hardware you own. It is the same shape as how a person learns: not by rewiring the brain for every lesson, but by taking things in, being corrected, and remembering — over a whole lifetime, always another lesson to learn.

**The honest limits — because stating them is the point.** ANI corrects the gaps the model is *honest* about — where it signals it doesn't know — not the things it states with full, misplaced confidence (a different problem, handled by separate checks). What it learns is carried by memory and retrieval, not by rewriting the model's weights. And a knowledge store is only ever as good as what you put in it: a careful source makes a sharp one, a vague source a vague one. But *within* those limits it does something the frontier stack cannot — it turns a model that forgets everything into one that forgets nothing you teach it, with no retraining, no cloud, and no permission required.

**Why this matters most — sovereignty, privacy and safety, in one architecture.**

Everything ANI does — every piece of knowledge, every correction, every memory — happens on your machine and stays there. Nothing is uploaded, nothing is logged to a server, nothing is sent anywhere to be learned from. This is privacy by *design*, not by promise: there is no account to trust, no telemetry to opt out of, no cloud that "won't" read your data — because there is no cloud in the loop that you did not put there yourself. A learning system that learns *only for you*, *only on your hardware*, owned entirely by you.

And if you want more than privacy by location, you can lock it. One switch — **Memory Vault → the padlock** — encrypts every knowledge bank at rest with a passphrase only *you* hold. Copy the files to another machine and they are an unreadable blob without it; the key is never written to disk and never leaves your head. It is portable (unlock on any machine with your passphrase, not chained to one computer) and it has no recovery *by design* — forget the passphrase and the knowledge is gone, because a backdoor for you is a backdoor for everyone. Your knowledge, your version of ANI, sealed to you alone.

**The one door out — off by default, and yours.** Leviathan is web-free out of the box: it never reaches the internet on its own. But sovereignty means *you* decide, not that we decide for you, so there is a single switch — **Settings → ANI → "Web lookup when ANI has no answer"** — that, turned on, lets ANI do one bounded thing: when it holds no answer to your question, it sends *only that question* out to be answered, checks the result through the same security membrane as everything else, and keeps it so that next time the answer is already local. You choose where that one question goes. By default it is a keyless web search. Or, if you supply your *own* API key (**Settings → ANI → Gemini key**), it goes to Google's Gemini with live search grounding — a composed, cross-checkable answer from an authoritative source, rather than a bare snippet — sent only to Google and nowhere else. Either way nothing else ever leaves — not your files, not your models, not your other questions — and the moment it happens the screen tells you. Off by default, on only if you choose, and provable with Wireshark: put a packet capture on it and you will see traffic to that one destination and nowhere else. This is not a model deciding to phone home — ANI has no such will. It is a pipe you open yourself, for one question, and close again by flicking the switch back. And because the answer is fetched, gated, and *kept*, the same door doubles as a cross-reference: a second, independent answer the model's own reply can be checked against.

And it is kept safe the way that genuinely protects a person. The [security membrane] governs what comes **in** — shielding both you *and* the model from anything arriving weaponised against either — while never once policing what *you* may do with your own machine. Every guard is yours to switch off, with a single floor that never bends. It defends the user's sovereignty and refuses to become a weapon against anyone else: governing, not surveilling; lawful by protecting, not by controlling.

That is the whole thesis in one line: **a model that learns and grows with you, keeps everything it learns yours alone, and stays safe and lawful without a corporation in the loop deciding what you may know or do.** Capability, privacy and safety in the same design — because here they were built together, not bolted on afterwards. That is what sovereignty means, and it is what the rest of the AI world has not yet built.

---

## Using Leviathan from other programs

Leviathan can serve the models it runs to anything else on your machine — a game engine, a script, a tool you wrote, another application entirely. One running instance answers any number of programs at once.

Turn it on in **Settings → Server for other programs** — one switch, no terminal and no command to remember. It starts listening on port 8080; flip the switch off to stop.

**Two ways to talk to it:**

**OpenAI-compatible.** It speaks the same API as OpenAI's chat endpoint, so anything already built to talk to an OpenAI-style server works by pointing it at `http://127.0.0.1:8080` instead. Most existing tools and libraries need nothing more than a changed URL.

**Leviathan-native.** A richer set of endpoints for things the OpenAI API has no concept of: loading and unloading models on demand, saving memory to disk, querying the recall cache, and listing available knowledge banks. This is the one to use if you are writing something new and want the features that make Leviathan different.

Both stream responses as they generate, and both can be interrupted mid-answer — which matters for a game, where a character being spoken over should stop talking immediately.

**Security.** By default it binds to loopback only: programs on your machine, nothing off it. It also shuts the browser trick — a web page you happen to visit cannot quietly reach the loopback bridge and drive your model, because a request carrying a foreign origin or a rebound hostname is turned away at the door, and the bridge never hands a web page blanket permission to read it. If you deliberately bind it to your network so another machine can reach it, Leviathan requires an access token and generates one for you. An unsecured model endpoint on an open network is somebody else's GPU, and it will not let you create one by accident. The same input guarding as the app applies to what comes in over the bridge — the illegal-content floor always, and the cross-turn steering guard per connected program.

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
- **Whitepapers:** https://zenodo.org/records/23004932 — the research behind the memory, compression and knowledge-routing work, permanently archived and citable.
- **Huggingface:** https://huggingface.co/spaces/Omega-Dev/Leviathan

All three are linked from **Settings → About** inside the app.


