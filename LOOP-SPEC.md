# Monday Loop — Integration & Specification v1.0

**Component**: `monday-loop.js` (vanilla ES module)

**Purpose**: Provide a projector-ready, full-bleed, keyboard-driven visual layer that can be dropped into an existing web-based "Ludi" layering framework without build tooling.

---

## 1. Context and Goals

### 1.1 Problem Statement

Operators want a looping, music-synchronized visual that overlays an existing “Ludi” table app. The visual must:

* Fill the browser viewport and scale cleanly in windowed or fullscreen modes.
* Behave as a discrete layer, not disturbing existing layers or Python-driven logic.
* Offer simple keyboard control for performance use.
* Export a seamlessly looping video for projection when live rendering is not desired.

### 1.2 Non-Goals

* No dependency on React, bundlers, or TypeScript at runtime.
* No audio analysis or beat detection (visual timing is tempo-driven, not microphone-driven).
* No persistence of settings across sessions (kept intentionally ephemeral for performance sets).

---

## 2. High-level Design

`monday-loop.js` mounts a full-bleed `<canvas>` into a designated container element and renders a time-parametrized loop. The loop period is derived from two parameters: BPM and number of bars. The animation is phase-based: `phase = (t % loopSeconds) / loopSeconds`. Because every visual element is computed from `phase`, the frame at `phase = 0` matches the frame at `phase → 1`, which guarantees perfect seams in both live looping and recorded export.

**Render passes** (in order):

1. Gradient background + lower dark band (to echo the physical table edge).
2. Global rotation transform (for mild aesthetic tilt).
3. Concentric rings and ring pulses.
4. Network path with traveling pulse.
5. Two bead clusters (NW/NE) with quiet wobble.
6. Skein diagonals and center beads.
7. Coil glyph (SE) with tri-dot motif.
8. Optional border and calibration ticks (grid).

A deterministic PRNG (`mulberry32`) seeds micro-variations so the pattern feels alive but remains consistent for a given seed.

---

## 3. Requirements

### 3.1 Functional Requirements

* **FR1**: Mount an overlay canvas into `#monday-layer` if present; otherwise create one and append it to `document.body`.
* **FR2**: Render a loop with period `loopSeconds = (60 / bpm) * bars`.
* **FR3**: Keyboard controls (global):

  * `F` toggle fullscreen.
  * `G` toggle grid overlay.
  * `R` record and download one exact loop as WebM (VP9), file named `monday-loop_<bpm>bpm_<bars>bars_<timestamp>.webm`.
  * `P` cycle color palettes.
  * `+`/`-` increment/decrement BPM within \[40, 220].
  * `[`/`]` decrement/increment bars within \[4, 64].
  * `0` reset visual settings to defaults and restart loop clock.
* **FR4**: Scaling must be full-bleed to the viewport, including during window resize and fullscreen changes.
* **FR5**: Respect existing layer stacking by using a predictable `z-index` class (default `.layer-6 { z-index: 80 }`).
* **FR6**: Provide three curated color palettes.
* **FR7**: Limit devicePixelRatio to a sane maximum (2x) for performance stability.

### 3.2 Non-Functional Requirements

* **NFR1 (Performance)**: Target 60 FPS on modern laptop GPUs; avoid pathological reflows; keep per-frame allocations minimal.
* **NFR2 (Integration)**: Single-file ES module; no global namespace pollution beyond the event listeners and the created `<canvas>`.
* **NFR3 (Portability)**: Work in Chromium-based browsers and Firefox; gracefully fall back to VP8 if VP9 encoder is unavailable.
* **NFR4 (Reliability)**: The recorded loop must be seam-clean when the video is played on repeat.
* **NFR5 (Accessibility)**: Keyboard-only operation; no mandatory pointer input; provide high-contrast palettes.

### 3.3 Out-of-Scope (current version)

* URL-driven configuration and interop with “magic URLs”.
* External control via `postMessage` or custom events.
* Persisted profiles, presets, or UI panels (kept separate in React version).

---

## 4. Integration Guide

### 4.1 HTML Hook

Add the following near the end of `index.html`:

```html
<div id="monday-layer" class="layer-6 tag full-width"></div>
<script type="module" src="monday-loop.js"></script>
```

### 4.2 CSS Notes

Ensure the layer stacks correctly and does not introduce scrollbars:

```css
html, body { height: 100%; margin: 0; background: #000; overflow: hidden; }
.layer-6 { z-index: 80; position: relative; }
```

`monday-loop.js` injects a minimal `html, body` reset and a `.layer-6` rule as a safety net. Local styles take precedence if declared after the script.

### 4.3 Coexistence with Other Layers

* The canvas is `position: absolute; top:0; left:0; width:100vw; height:100vh; z-index:80` inside `#monday-layer`.
* Keyboard listeners are attached to `window`. Avoid assigning the same keys elsewhere, or gate other handlers behind modifier keys.

---

## 5. Configuration Surface

Runtime configuration object (internal):

```js
cfg = {
  bpm: 92,
  bars: 16,
  rotateDeg: 0,
  glow: 0.7,        // 0..1
  grid: true,
  darkBand: 0.45,   // 0..1
  palette: 'cyanMagenta',
  seed: 1337,
}
```

Colour palettes:

```js
palettes = {
  cyanMagenta: { bg1:'#05151e', bg2:'#0b2733', line:'#66e0ff', accent:'#ff5cc8', bead:'#eaffff' },
  amberTeal:   { bg1:'#1b1306', bg2:'#2e2413', line:'#04d4bd', accent:'#ffb84d', bead:'#fff6e6' },
  violetMint:  { bg1:'#120a1c', bg2:'#221238', line:'#5ef2bf', accent:'#bd7bff', bead:'#f5efff' },
}
```

**Timing model**: `phase = ( (now - start) % loopSeconds ) / loopSeconds`.

**Determinism**: `mulberry32(seed)` used for clustered offsets; seeded by spatial hashes to keep clusters visually stable per session.

---

## 6. Recording Pipeline

* Uses `HTMLCanvasElement.captureStream(60)` to obtain a 60 FPS media stream.
* Encodes via `MediaRecorder` with `video/webm;codecs=vp9`.
* Guard: if the MIME type is unsupported, change to `video/webm;codecs=vp8` or `video/webm`.
* Calls `MediaRecorder.stop()` after `loopSeconds * 1000` to capture exactly one loop.
* On `onstop`, assembles a Blob from chunks and triggers an `a[href=ObjectURL]` download.
* Seam assurance: Because all visuals are `phase`-driven and `phase` is modulo `loopSeconds`, frame 0 equals the final frame, so the video loops cleanly.

---

## 7. Rendering Details

* **Background**: linear gradient `bg1→bg2` plus a dark rectangle for the lower band.
* **Rings**: 5 concentric arcs; pulse dots orbit at ring radii with phase offsets.
* **Network**: fixed normalized node path; traveling accent dot follows segment interpolation keyed to `phase`.
* **Clusters**: two randomized but seed-stable constellations with subtle sinusoidal wobble.
* **Skeins**: bead lines built from jittered interpolation between anchor points; bead radius breathes with `phase`.
* **Coil**: parametric spiral with tri-dot satellite.
* **Grid**: border rectangle and tick marks to support alignment during projection.
* **DPR Strategy**: clamp effective devicePixelRatio to `≤ 2` to avoid excessive fill costs.

---

## 8. Error Handling and Edge Cases

* If `MediaRecorder` fails to construct with VP9, fall back to VP8 or omit the codec string.
* If the container or canvas context is unavailable, the script no-ops gracefully.
* Window resize and `fullscreenchange` events retrigger a redraw sizing pass.
* Frame loop is canceled and restarted when size changes to avoid stale transforms.

---

## 9. Security and Privacy

* No network calls; no external data loaded.
* No user data stored or transmitted.
* Recording occurs entirely client-side; the resulting file is offered as a local download.

---

## 10. Accessibility Considerations

* Keyboard control only; no UI chrome required.
* High-contrast palettes supported; grid aids alignment for viewers at distance.
* Caution: Contains motion and strobing elements. Provide a static fallback layer for photosensitive users.

---

## 11. Testing & Acceptance Criteria

### 11.1 Manual Test Checklist

* [ ] Canvas fills viewport on load; no scrollbars.
* [ ] Fullscreen toggles with `F` and via `Esc` exit.
* [ ] Resize window; content remains centered and scaled.
* [ ] Press `G`; grid toggles.
* [ ] Adjust BPM with `+`/`-`; loop speed changes proportionally.
* [ ] Adjust bars with `[`/`]`; loop period changes accordingly.
* [ ] Press `R`; a WebM downloads after exactly one loop. When repeated, the video seam is not visible.
* [ ] Cycle palette with `P`.
* [ ] Reset with `0` restores defaults and restarts phase.

### 11.2 Acceptance Criteria

* AC1: Drop-in integration requires no modifications to existing Python/Brython logic.
* AC2: Loop video produced at default settings plays seamlessly on repeat in a standard player.
* AC3: Keybindings do not break existing “magic URL” handlers (keys are simple letters; no global `preventDefault` except for F/R).

---

## 12. Extensibility (Future Work)

* **URL Parameter Bridge**: Read `?monday_bpm=`, `?monday_bars=`, `?monday_palette=`, etc. once on load.
* **PostMessage API**: Listen for `window.postMessage({ type:'MONDAY_CFG', patch:{...} }, '*')` to allow remote control from another frame or controller.
* **Preset Loader**: Import/export JSON presets for rapid show setup.
* **MIDI Bridge**: Optional WebMIDI input to map CC/notes to parameters (guarded by feature detection).
* **OSC/WebSocket**: Controlled over LAN for multi-screen synchronization.

---

## 13. File Layout & Embedding

* `index.html` — host page with layer container.
* `play.css` — site-wide styles; ensure no conflicting `overflow` or fixed margins on `html, body`.
* `monday-loop.js` — this module; include with `<script type="module">`.

**Embed snippet** (reference):

```html
<div id="monday-layer" class="layer-6 tag full-width"></div>
<script type="module" src="monday-loop.js"></script>
```

---

## 14. Versioning and Change Log

* **v1.0**: Initial vanilla JS module; full-bleed scaling; keyboard controls; deterministic loop; WebM export; safety CSS injection; palette cycling; seed-stable variability.

---

## 15. License & Attribution

* Intended for private performance use by the Ludi collective. You may copy, modify, and remix within your show stack. If redistributed, keep this header block intact.

---

## 16. Appendix: Key Map

```
F  Fullscreen toggle
G  Grid on/off
R  Record exact one-loop WebM
P  Cycle palette
+  Increase BPM
-  Decrease BPM
[  Decrease bars
]  Increase bars
0  Reset defaults and restart loop clock
```

