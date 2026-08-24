#!/bin/bash
# ============================================================================
# Romio Café & Restaurant — encode raw dives/connectors for smooth scroll-scrubbing.
# Run from the frontend/ folder AFTER you've rendered every raw clip.
#
# Put your freshly-rendered (un-encoded) clips in ./raw/ with the SAME names as the
# final outputs, e.g. ./raw/terrace.mp4, ./raw/conn1.mp4, ...
# This script re-encodes each into ./assets/vid/ at the settings the engine needs:
#   native resolution (don't downscale), crf 20, small GOP (-g 8), faststart, no audio,
#   plus a light unsharp to counter video softness. (see lets-scroll pipeline.md §6)
# ============================================================================
set -e
mkdir -p assets/vid

CLIPS="terrace bar dining events finale conn1 conn2 conn3 conn4"

enc() { # in out
  ffmpeg -y -i "$1" -an -vf "unsharp=5:5:0.8:5:5:0.0" \
    -c:v libx264 -preset slow -crf 20 -pix_fmt yuv420p \
    -g 8 -keyint_min 8 -sc_threshold 0 -movflags +faststart "$2"
}

for c in $CLIPS; do
  if [ -f "raw/$c.mp4" ]; then
    echo "encoding $c ..."
    enc "raw/$c.mp4" "assets/vid/$c.mp4"
  else
    echo "SKIP $c — raw/$c.mp4 not found"
  fi
done

echo "Done. Encoded clips are in assets/vid/"

# --- Convert stills PNG -> WebP (if you rendered PNGs into ./raw/) -----------
# Requires cwebp (from libwebp). Comment out if you already have .webp stills.
for n in terrace bar dining events finale; do
  if [ -f "raw/$n.png" ]; then
    cwebp -quiet -q 84 -resize 1800 0 "raw/$n.png" -o "assets/$n.webp"
    echo "webp $n ok"
  fi
done
