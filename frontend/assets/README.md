# assets/ — drop your rendered files here

The page (`../index.html`) reads exactly these paths. Filenames must match.

## Stills (webp) — go in this folder
- `terrace.webp`   ← from `../prompts/still_terrace.txt`
- `bar.webp`       ← from `../prompts/still_bar.txt`
- `dining.webp`    ← from `../prompts/still_dining.txt`
- `events.webp`    ← from `../prompts/still_events.txt`
- `finale.webp`    ← from `../prompts/still_finale.txt`

## Clips (mp4) — go in assets/vid/
Dives (one per scene):
- `vid/terrace.mp4`  ← from `../prompts/dive_terrace.txt`
- `vid/bar.mp4`      ← from `../prompts/dive_bar.txt`
- `vid/dining.mp4`   ← from `../prompts/dive_dining.txt`
- `vid/events.mp4`   ← from `../prompts/dive_events.txt`
- `vid/finale.mp4`   ← from `../prompts/dive_finale.txt`

Connectors (scene → scene; render AFTER the dives, conditioned on their real frames):
- `vid/conn1.mp4`  terrace → bar    ← `../prompts/conn_1.txt`
- `vid/conn2.mp4`  bar → dining     ← `../prompts/conn_2.txt`
- `vid/conn3.mp4`  dining → events  ← `../prompts/conn_3.txt`
- `vid/conn4.mp4`  events → finale  ← `../prompts/conn_4.txt`

See `../prompts/HANDOFF.md` for the full spec, seam rule, and validation checklist.
Encode raw clips with `../encode.sh` before shipping.

## Preview the page
The engine loads clips as blobs via `fetch`, so serve over HTTP (not file://):
```
# from the frontend/ folder
python -m http.server 8000
# then open http://localhost:8000/
```
The page works right now with just the `.webp` stills present (static posters + copy);
scroll-scrubbed video activates once the `.mp4`s are added.
