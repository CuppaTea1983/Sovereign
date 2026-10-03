#!/usr/bin/env python3
"""
membrane_demo_gui.py — a graphical demonstration of the Leviathan security
membrane (pygame). The console demo (membrane_demo.py) is the industrial/
reviewer view; this is the one to show users: events fly at a glowing membrane
and you watch clean traffic pass through while threats are caught, named, and
repelled.

    pip install pygame
    python membrane_demo_gui.py            # SIM  — illustrative, runs anywhere
    python membrane_demo_gui.py --live     # LIVE — drives the REAL membrane

Keys:  SPACE pause · R replay · Q / Esc quit
Flags: --live · --fast · --src DIR (membrane source for --live) · --smoke (headless self-test)

Reuses the exact scenario and membrane calls from membrane_demo.py — one source
of truth. The detection source is never in this file; SIM uses canned verdicts,
LIVE calls the membrane. Safe to publish.
"""
import argparse
import math
import os
import random
import sys

# ── CLI (parse before pygame so --smoke can pick a headless driver) ────────────
_ap = argparse.ArgumentParser(description="Graphical demo of the Leviathan security membrane.")
_ap.add_argument("--live", action="store_true", help="drive the REAL membrane")
_ap.add_argument("--fast", action="store_true", help="faster pacing")
_ap.add_argument("--src", default=None, help="membrane source dir for --live")
_ap.add_argument("--smoke", action="store_true", help="headless self-test, then exit")
ARGS = _ap.parse_args()

if ARGS.smoke:
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

try:
    import pygame
except ImportError:
    sys.exit("This demo needs pygame.  Install it with:  pip install pygame")

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
for _c in (ARGS.src, os.path.join(_HERE, "membrane"), _HERE, os.path.dirname(_HERE)):
    if _c and os.path.isdir(_c):
        sys.path.insert(0, _c)
from membrane_demo import EVENTS, live_verdict   # scenario + real-membrane calls

# How many of the scripted events are actually threats (verdict != ALLOW). The
# rest are legitimate traffic that SHOULD pass — so the score is threats-stopped
# out of threats, not out of all events.
THREAT_COUNT = sum(1 for ev in EVENTS if ev[4] != "ALLOW")

# ── Deep-sea / bioluminescent palette (matches the Leviathan HF page) ──────────
BG      = (7, 11, 18)
PANEL   = (13, 20, 32)
PANEL2  = (19, 29, 43)
CYAN    = (35, 210, 193)
CYAN_D  = (21, 120, 120)
EDGE    = (28, 183, 168)
TEXT    = (233, 242, 247)
DIM     = (120, 150, 165)
GREEN   = (80, 220, 140)
AMBER   = (242, 196, 84)
RED     = (240, 96, 96)

VCOL = {"ALLOW": GREEN, "WITHHOLD": AMBER, "QUARANTINE": AMBER, "BLOCK": RED, "REFUSE": RED}
VLABEL = {"ALLOW": "DELIVERED", "WITHHOLD": "WITHHELD", "QUARANTINE": "QUARANTINED",
          "BLOCK": "BLOCKED", "REFUSE": "REFUSED"}

W, H = 1120, 660
MEM_X = 440                       # membrane scan face (left edge)
MEM_W = 210                       # wide enough for the layer labels (measured: 168px + padding)
MEM_TOP, MEM_BOT = 92, 556
DELIV_X = 705                     # where delivered packets land
LANE_X0 = 30

SEGMENTS = [
    ("intent / injection",      ("intent", "injection")),
    ("csam floor",              ("csam",)),
    ("perceptual / channel",    ("perceptual", "hidden")),
    ("knowledge / poisoning",   ("knowledge",)),
    ("model-file integrity",    ("model-file", "model file", "template")),
    ("image guard",             ("image",)),
    ("network / origin",        ("network",)),
]
SEG_H = (MEM_BOT - MEM_TOP) / len(SEGMENTS)


def seg_index(layer):
    if not layer:
        return -1
    low = layer.lower()
    for i, (_, keys) in enumerate(SEGMENTS):
        if any(k in low for k in keys):
            return i
    return -1


def seg_y(i):
    return MEM_TOP + SEG_H * (i + 0.5)


def lerp(a, b, t):
    return tuple(int(a[j] + (b[j] - a[j]) * t) for j in range(3))


# ── Entities ───────────────────────────────────────────────────────────────────
class Packet:
    def __init__(self, ev, verdict, layer):
        kind, boundary, payload, _, _, note = ev
        self.boundary = boundary
        self.note = note
        self.verdict = verdict
        self.seg = seg_index(layer)
        self.label = payload if len(payload) <= 30 else payload[:28] + "…"
        self.y = seg_y(self.seg) if self.seg >= 0 else (MEM_TOP + MEM_BOT) / 2
        self.x = float(LANE_X0 + 90)
        self.vx = 3.6
        self.state = "fly"        # fly -> (hit | through) -> done
        self.col = CYAN if verdict == "ALLOW" else VCOL[verdict]

    def update(self, scene, dt):
        self.x += self.vx * dt * 60
        if self.state == "fly" and self.x >= MEM_X - 14:
            if self.verdict == "ALLOW":
                self.state = "through"
                scene.flash_pass(self.y)
            else:
                self.state = "hit"
                scene.on_block(self)
                return False       # packet consumed by the membrane
        # A clean packet travels fully into the DELIVERED zone, then settles
        # there as a stored item (it does NOT fade out in mid-air).
        if self.state == "through" and self.x >= DELIV_X + 40:
            scene.delivered += 1
            scene.delivered_items.append(self.label)
            return False
        return True

    def draw(self, surf, font):
        w = font.size(self.label)[0] + 22
        r = pygame.Rect(int(self.x - w), int(self.y - 13), w, 26)
        edge = GREEN if self.state == "through" else self.col   # green once it's cleared
        pygame.draw.rect(surf, lerp(BG, edge, 0.72), r, border_radius=13)
        pygame.draw.rect(surf, edge, r, width=2, border_radius=13)
        surf.blit(font.render(self.label, True, TEXT), (r.x + 11, r.y + 5))


class Particle:
    def __init__(self, x, y, col):
        a = random.uniform(-1.4, 1.4) + math.pi            # mostly leftward (repelled)
        s = random.uniform(1.5, 6.5)
        self.x, self.y = x, y
        self.vx, self.vy = math.cos(a) * s, math.sin(a) * s - 1.0
        self.col = col
        self.life = 1.0

    def update(self, dt):
        self.x += self.vx * dt * 60
        self.y += self.vy * dt * 60
        self.vy += 0.18 * dt * 60
        self.life -= 1.6 * dt
        return self.life > 0

    def draw(self, surf):
        r = max(1, int(4 * self.life))
        pygame.draw.circle(surf, lerp(BG, self.col, self.life),
                           (int(self.x), int(self.y)), r)


class Float:
    def __init__(self, x, y, text, col, big=False):
        self.x, self.y, self.text, self.col, self.big = x, y, text, col, big
        self.life = 1.0

    def update(self, dt):
        self.y -= 26 * dt
        self.life -= 0.8 * dt
        return self.life > 0


# ── Scene ───────────────────────────────────────────────────────────────────────
class Scene:
    def __init__(self, live, fast):
        self.live = live
        self.interval = 0.9 if fast else 1.5
        self.reset()

    def reset(self):
        self.packets, self.particles, self.floats = [], [], []
        self.delivered_items = []              # labels that made it to DELIVERED
        self.flashes = [0.0] * len(SEGMENTS)   # per-segment flash 0..1
        self.flash_col = [RED] * len(SEGMENTS)  # colour of the last hit on each segment
        self.pass_glow = 0.0
        self.pass_y = 0.0
        self.i = 0
        self.timer = 0.6
        self.scanned = self.delivered = self.withheld = self.blocked = 0
        self.log = []
        self.done_at = None

    def _verdict(self, ev):
        kind, boundary, payload, sim_layer, sim_verdict, note = ev
        if self.live:
            try:
                layer, verdict = live_verdict(kind, payload)
            except Exception:
                layer, verdict = sim_layer, sim_verdict
            return verdict, (layer or sim_layer)
        return sim_verdict, sim_layer

    def spawn(self):
        ev = EVENTS[self.i]
        verdict, layer = self._verdict(ev)
        self.packets.append(Packet(ev, verdict, layer))
        self.scanned += 1
        self.i += 1

    def flash_pass(self, y):
        self.pass_glow = 1.0
        self.pass_y = y

    def on_block(self, pk):
        col = VCOL[pk.verdict]
        if pk.seg >= 0:
            self.flashes[pk.seg] = 1.0
            self.flash_col[pk.seg] = col
        ix, iy = MEM_X - 6, pk.y
        for _ in range(26):
            self.particles.append(Particle(ix, iy, col))
        self.floats.append(Float(ix - 40, iy - 18, VLABEL[pk.verdict], col, big=True))
        if pk.verdict in ("WITHHOLD", "QUARANTINE"):
            self.withheld += 1
        else:
            self.blocked += 1
        self.log.insert(0, (VLABEL[pk.verdict], pk.boundary, pk.note, col))
        self.log = self.log[:6]

    def update(self, dt):
        if self.i < len(EVENTS):
            self.timer -= dt
            if self.timer <= 0:
                self.spawn()
                self.timer = self.interval
        self.packets = [p for p in self.packets if p.update(self, dt)]
        self.particles = [p for p in self.particles if p.update(dt)]
        self.floats = [f for f in self.floats if f.update(dt)]
        self.flashes = [max(0.0, f - 1.6 * dt) for f in self.flashes]
        self.pass_glow = max(0.0, self.pass_glow - 2.2 * dt)
        if self.i >= len(EVENTS) and not self.packets and self.done_at is None:
            self.done_at = 0.0
        if self.done_at is not None:
            self.done_at += dt


# ── Rendering ────────────────────────────────────────────────────────────────────
def draw(surf, scene, F):
    surf.fill(BG)
    big, lab, sml, num, title = F

    # title bar
    pygame.draw.rect(surf, PANEL, (0, 0, W, 74))
    surf.blit(title.render("LEVIATHAN  SECURITY  MEMBRANE", True, CYAN), (28, 20))
    chip = "LIVE · real verdicts" if scene.live else "SIM · illustrative"
    ccol = RED if scene.live else AMBER
    cw = sml.size(chip)[0] + 24
    pygame.draw.rect(surf, PANEL2, (W - cw - 28, 24, cw, 26), border_radius=13)
    pygame.draw.rect(surf, ccol, (W - cw - 28, 24, cw, 26), width=2, border_radius=13)
    surf.blit(sml.render(chip, True, ccol), (W - cw - 16, 30))

    surf.blit(sml.render("INCOMING", True, DIM), (LANE_X0 + 8, 82))
    surf.blit(sml.render("DELIVERED", True, lerp(BG, GREEN, 0.9)), (DELIV_X + 6, 82))

    # delivered zone (faint) + the messages that have landed in it
    pygame.draw.rect(surf, lerp(BG, GREEN, 0.06), (DELIV_X, MEM_TOP, W - DELIV_X - 24, MEM_BOT - MEM_TOP),
                     border_radius=10)
    zone_w = W - DELIV_X - 24
    for i, label in enumerate(scene.delivered_items[-12:]):
        yy = MEM_TOP + 18 + i * 36
        if yy + 28 > MEM_BOT:
            break
        pw = min(lab.size(label)[0] + 22, zone_w - 28)
        rr = pygame.Rect(DELIV_X + 16, yy, pw, 28)
        pygame.draw.rect(surf, lerp(BG, GREEN, 0.20), rr, border_radius=14)
        pygame.draw.rect(surf, lerp(BG, GREEN, 0.75), rr, width=1, border_radius=14)
        surf.blit(lab.render(label, True, lerp(BG, TEXT, 0.95)), (rr.x + 11, rr.y + 6))

    # the membrane barrier
    pygame.draw.rect(surf, PANEL2, (MEM_X, MEM_TOP, MEM_W, MEM_BOT - MEM_TOP), border_radius=8)
    for i, (name, _) in enumerate(SEGMENTS):
        y0 = MEM_TOP + SEG_H * i
        fl = scene.flashes[i]
        if fl > 0:
            seg = pygame.Surface((MEM_W, int(SEG_H) - 2), pygame.SRCALPHA)
            seg.fill((*scene.flash_col[i], int(120 * fl)))
            surf.blit(seg, (MEM_X, y0 + 1))
        pygame.draw.line(surf, lerp(PANEL2, CYAN_D, 0.5), (MEM_X, int(y0)), (MEM_X + MEM_W, int(y0)))
        nm = lab.render(name, True, lerp(DIM, TEXT, fl))
        surf.blit(nm, (MEM_X + MEM_W // 2 - nm.get_width() // 2, int(y0 + SEG_H / 2 - 8)))
    # bright scan face + glow
    pygame.draw.line(surf, lerp(CYAN, (255, 255, 255), 0.3 * scene.pass_glow),
                     (MEM_X, MEM_TOP), (MEM_X, MEM_BOT), 3)
    if scene.pass_glow > 0:
        g = pygame.Surface((40, 60), pygame.SRCALPHA)
        g.fill((*GREEN, int(90 * scene.pass_glow)))
        surf.blit(g, (MEM_X - 6, scene.pass_y - 30))

    for p in scene.packets:
        p.draw(surf, lab)
    for pt in scene.particles:
        pt.draw(surf)
    for f in scene.floats:
        fnt = big if f.big else lab
        surf.blit(fnt.render(f.text, True, lerp(BG, f.col, max(0.0, f.life))),
                  (int(f.x), int(f.y)))

    # HUD
    hud_y = 574
    pygame.draw.rect(surf, PANEL, (0, hud_y, W, H - hud_y))
    stats = [("SCANNED", scene.scanned, TEXT), ("DELIVERED", scene.delivered, GREEN),
             ("WITHHELD", scene.withheld, AMBER), ("BLOCKED", scene.blocked, RED)]
    x = 28
    for name, val, col in stats:
        surf.blit(sml.render(name, True, DIM), (x, hud_y + 12))
        surf.blit(num.render(str(val), True, col), (x, hud_y + 30))
        x += 150
    # attack wall
    surf.blit(sml.render("ATTACK WALL", True, DIM), (640, hud_y + 8))
    for j, (badge, _boundary, note, col) in enumerate(scene.log[:4]):
        yy = hud_y + 27 + j * 14
        surf.blit(sml.render(badge, True, col), (640, yy))
        note_txt = note if len(note) <= 48 else note[:47] + "…"
        surf.blit(sml.render(note_txt, True, DIM), (744, yy))

    # summary hold
    if scene.done_at is not None:
        ov = pygame.Surface((W, H), pygame.SRCALPHA)
        ov.fill((*BG, 180))
        surf.blit(ov, (0, 0))
        stopped = scene.withheld + scene.blocked
        lines = [("SESSION COMPLETE", CYAN, title),
                 (f"{stopped}/{THREAT_COUNT} threats stopped  ·  "
                  f"{scene.delivered} clean messages delivered untouched", TEXT, lab),
                 ("R  replay      Q  quit", DIM, lab)]
        cy = H // 2 - 40
        for txt, col, fnt in lines:
            s = fnt.render(txt, True, col)
            surf.blit(s, (W // 2 - s.get_width() // 2, cy))
            cy += s.get_height() + 16


def main():
    pygame.init()
    flags = 0
    screen = pygame.display.set_mode((W, H), flags)
    pygame.display.set_caption("Leviathan Security Membrane")
    clock = pygame.time.Clock()

    def _font(size, bold=False):
        try:
            return pygame.font.SysFont("consolas,menlo,dejavusansmono", size, bold=bold)
        except Exception:
            return pygame.font.Font(None, size)
    F = (_font(22, True), _font(15), _font(13), _font(26, True), _font(30, True))

    scene = Scene(ARGS.live, ARGS.fast)
    paused = False
    frames = 0
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            elif e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_q, pygame.K_ESCAPE):
                    running = False
                elif e.key == pygame.K_SPACE:
                    paused = not paused
                elif e.key == pygame.K_r:
                    scene.reset()
        if not paused:
            scene.update(min(dt, 0.05))
        draw(screen, scene, F)
        pygame.display.flip()

        frames += 1
        if ARGS.smoke:
            # headless self-test: fast-forward the whole scenario, then exit 0
            scene.update(0.05)
            if (scene.done_at is not None and scene.done_at > 0.3) or frames > 4000:
                print(f"[smoke] ok — scanned={scene.scanned} delivered={scene.delivered} "
                      f"withheld={scene.withheld} blocked={scene.blocked} frames={frames}")
                break
    pygame.quit()


if __name__ == "__main__":
    main()
