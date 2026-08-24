# Romio Café & Restaurant — Asset Handoff Spec

This page (`frontend/`) is a **scroll-scrubbed camera-flight** landing page built on
the `lets-scroll` engine. Scroll drives a pre-rendered camera that flies **into** each
scene, then a **connector** clip flies from one scene to the next — as one unbroken
shot. The page is already wired; it just needs the 14 rendered assets dropped into
`frontend/assets/`.

## Brand
- **Name:** Romio Café & Restaurant
- **Concept:** Rooftop café & restaurant — skyline dining above the city
- **Background colour (must match every still):** cream `#F5EDE0`
- **Palette:** terracotta `#C85C3A` · gold `#D4A843` · olive `#6B7C3E` · mauve `#9B6B8A` · deep plum `#3A2230` · cream `#F5EDE0`
- **Art direction:** soft isometric clay diorama (tilt-shift miniature)
- **Camera style:** fly-through (dives + aerial connectors)
- **CTA:** "Reserve a Table" → set `RESERVE_URL` in `index.html` to your District website URL.

## Journey (5 scenes)
1. `terrace` — The Rooftop
2. `bar` — The Craft Bar
3. `dining` — The Table
4. `events` — Private Events
5. `finale` — Reserve Tonight (hero dish + cocktail, carries the CTA)

## The ONE rule (seams)
Connector clips must be **frame-identical** at the seam. A connector's start frame =
the **actual last frame of the previous dive's rendered video**, and its end frame =
the **actual first frame of the next dive's rendered video**. Never condition a
connector on a fresh still — extract the frames from the rendered `.mp4`s. Getting this
wrong produces a visible "pop" between scenes.

Render order: **all 5 dives first → extract their first/last frames → then the 4 connectors.**

## Stills — 5 files (render at 3:2 landscape, high res, then convert to .webp)
Every still prompt already embeds the shared style preamble (`style-preamble.txt`) verbatim.

| # | Prompt file            | Output file (webp)      | Status  |
|---|------------------------|-------------------------|---------|
| 1 | `still_terrace.txt`    | `assets/terrace.webp`   | pending |
| 2 | `still_bar.txt`        | `assets/bar.webp`       | pending |
| 3 | `still_dining.txt`     | `assets/dining.webp`    | pending |
| 4 | `still_events.txt`     | `assets/events.webp`    | pending |
| 5 | `still_finale.txt`     | `assets/finale.webp`    | pending |

## Dive clips — 5 files (start-image = the matching still; 16:9, ~8s, 1080p)

| # | Prompt file            | Start image (conditioning) | Output file             | Status  |
|---|------------------------|----------------------------|-------------------------|---------|
| 1 | `dive_terrace.txt`     | `assets/terrace.webp`      | `assets/vid/terrace.mp4`| pending |
| 2 | `dive_bar.txt`         | `assets/bar.webp`          | `assets/vid/bar.mp4`    | pending |
| 3 | `dive_dining.txt`      | `assets/dining.webp`       | `assets/vid/dining.mp4` | pending |
| 4 | `dive_events.txt`      | `assets/events.webp`       | `assets/vid/events.mp4` | pending |
| 5 | `dive_finale.txt`      | `assets/finale.webp`       | `assets/vid/finale.mp4` | pending |

## Connector clips — 4 files (16:9, ~5s, 1080p). Need a model that accepts start AND end frame.

| # | Prompt file    | Start frame (from rendered video) | End frame (from rendered video)   | Output file           | Status  |
|---|----------------|-----------------------------------|-----------------------------------|-----------------------|---------|
| 1 | `conn_1.txt`   | LAST frame of `terrace.mp4`       | FIRST frame of `bar.mp4`          | `assets/vid/conn1.mp4`| pending |
| 2 | `conn_2.txt`   | LAST frame of `bar.mp4`           | FIRST frame of `dining.mp4`       | `assets/vid/conn2.mp4`| pending |
| 3 | `conn_3.txt`   | LAST frame of `dining.mp4`        | FIRST frame of `events.mp4`       | `assets/vid/conn3.mp4`| pending |
| 4 | `conn_4.txt`   | LAST frame of `events.mp4`        | FIRST frame of `finale.mp4`       | `assets/vid/conn4.mp4`| pending |

## Extracting seam frames (ffmpeg / ffprobe)
```bash
# FIRST frame of a clip:
ffmpeg -i assets/vid/bar.mp4 -frames:v 1 first_bar.png
# LAST frame of a clip:
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 assets/vid/terrace.mp4)
ffmpeg -ss "$DUR" -i assets/vid/terrace.mp4 -frames:v 1 -update 1 last_terrace.png
```

## Encoding (after rendering)
Run `frontend/encode.sh` (or the commands inside it) on every raw dive/connector so all
14 clips scrub smoothly (native res, crf 20, small GOP, faststart, no audio).

## Validation checklist before "done"
- 5 `.webp` stills + 9 `.mp4` clips (5 dives + 4 connectors) present at the exact paths above.
- Every clip 16:9, ~duration, no audio.
- Each connector's frame 0 matches the previous dive's last frame (composition, not raw PSNR).
- Open `index.html` via a local server, scroll top→bottom: camera flies in/out with no pops.
- Set `RESERVE_URL` in `index.html`.
