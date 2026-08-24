#!/usr/bin/env python3
"""
Romio Cafe & Restaurant — Windows-native asset encoder.

Does the same two jobs as encode.sh, but works on Windows without Bash/cwebp:

  1. Convert the rendered PNG stills  ->  optimized .webp   (via Pillow)
  2. Re-encode every dive/connector .mp4 for smooth scroll-scrubbing (via ffmpeg):
     no audio, crf 20, small GOP (-g 8), +faststart, light unsharp.

Usage (from the frontend/ folder):
    python encode.py

Raw clips are read from assets/vid/*.mp4 and encoded IN PLACE (a .bak copy of each
original is kept the first time). Stills are read from assets/*.png -> assets/*.webp.
"""

import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")
VID = os.path.join(ASSETS, "vid")

STILLS = ["terrace", "bar", "dining", "events", "finale"]
CLIPS = ["terrace", "bar", "dining", "events", "finale",
         "conn1", "conn2", "conn3", "conn4"]

WEBP_QUALITY = 84
WEBP_MAX_WIDTH = 1800


def find_ffmpeg():
    """Locate ffmpeg + ffprobe. Prefer PATH, then a winget Gyan.FFmpeg install,
    then the pip 'imageio-ffmpeg' bundled binary (ffmpeg only — ffprobe may be None)."""
    exe = shutil.which("ffmpeg")
    probe = shutil.which("ffprobe")
    if exe:
        return exe, probe
    # winget install location (PATH may not be refreshed in this session).
    base = os.path.join(os.environ.get("LOCALAPPDATA", ""),
                        "Microsoft", "WinGet", "Packages")
    if os.path.isdir(base):
        for root, _dirs, files in os.walk(base):
            if "ffmpeg.exe" in files:
                exe = os.path.join(root, "ffmpeg.exe")
                if "ffprobe.exe" in files:
                    probe = os.path.join(root, "ffprobe.exe")
                return exe, probe
    # pip fallback: imageio-ffmpeg bundles a static ffmpeg (no ffprobe).
    try:
        import imageio_ffmpeg
        exe = imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        pass
    return exe, probe


def convert_stills():
    try:
        from PIL import Image
    except ImportError:
        print("  ! Pillow not installed — skipping still conversion. Run: pip install pillow")
        return
    print("== Converting stills PNG -> WebP ==")
    for name in STILLS:
        src = os.path.join(ASSETS, name + ".png")
        dst = os.path.join(ASSETS, name + ".webp")
        if not os.path.isfile(src):
            print(f"  SKIP {name}: {name}.png not found")
            continue
        img = Image.open(src).convert("RGB")
        if img.width > WEBP_MAX_WIDTH:
            h = round(img.height * WEBP_MAX_WIDTH / img.width)
            img = img.resize((WEBP_MAX_WIDTH, h), Image.LANCZOS)
        img.save(dst, "WEBP", quality=WEBP_QUALITY, method=6)
        kb = os.path.getsize(dst) // 1024
        print(f"  OK  {name}.webp  ({img.width}x{img.height}, {kb} KB)")


def encode_clips(ffmpeg, only=None):
    print("== Re-encoding clips for smooth scrubbing ==")
    names = only if only else CLIPS
    for name in names:
        src = os.path.join(VID, name + ".mp4")
        if not os.path.isfile(src):
            print(f"  SKIP {name}: vid/{name}.mp4 not found")
            continue
        bak = os.path.join(VID, name + ".orig.mp4")
        # Preserve the original once, then always encode FROM the original.
        if not os.path.isfile(bak):
            shutil.copy2(src, bak)
        tmp = os.path.join(VID, name + ".enc.mp4")
        cmd = [
            ffmpeg, "-y", "-i", bak,
            "-an", "-vf", "unsharp=5:5:0.8:5:5:0.0",
            "-c:v", "libx264", "-preset", "medium", "-crf", "20",
            "-pix_fmt", "yuv420p",
            "-g", "8", "-keyint_min", "8", "-sc_threshold", "0",
            "-movflags", "+faststart", tmp,
        ]
        print(f"  encoding {name} ...", flush=True)
        r = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        if r.returncode != 0:
            print(f"  ! FAIL {name}\n{r.stderr.decode(errors='replace')[-800:]}")
            if os.path.isfile(tmp):
                os.remove(tmp)
            continue
        os.replace(tmp, src)
        kb = os.path.getsize(src) // 1024
        print(f"  OK  vid/{name}.mp4  ({kb} KB)")


def report(ffprobe):
    print("== Validation (dimensions / duration / audio) ==")
    for name in CLIPS:
        src = os.path.join(VID, name + ".mp4")
        if not os.path.isfile(src):
            continue
        def probe(stream, entries):
            out = subprocess.run(
                [ffprobe, "-v", "error", "-select_streams", stream,
                 "-show_entries", entries, "-of", "csv=p=0", src],
                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            ).stdout.decode().strip()
            return out
        vinfo = probe("v:0", "stream=width,height").replace("\n", "")
        dur = probe("v:0", "format=duration")  # note: format-level below
        dur = subprocess.run(
            [ffprobe, "-v", "error", "-show_entries", "format=duration",
             "-of", "csv=p=0", src],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
        ).stdout.decode().strip()
        atracks = subprocess.run(
            [ffprobe, "-v", "error", "-select_streams", "a",
             "-show_entries", "stream=index", "-of", "csv=p=0", src],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
        ).stdout.decode().strip()
        audio = "audio!" if atracks else "no-audio"
        try:
            dur = f"{float(dur):.1f}s"
        except ValueError:
            dur = "?"
        print(f"  {name:8} {vinfo:>10}  {dur:>6}  {audio}")


def main():
    # Optional CLI args:
    #   python encode.py                -> stills + all clips + report
    #   python encode.py stills         -> only convert PNG stills
    #   python encode.py clips a b c    -> only encode the named clips
    #   python encode.py report         -> only print the validation table
    args = sys.argv[1:]
    mode = args[0] if args else "all"

    if mode == "stills":
        convert_stills()
        return

    ffmpeg, ffprobe = find_ffmpeg()
    if not ffmpeg:
        print("\n! ffmpeg not found. Install with:  pip install imageio-ffmpeg")
        print("  (or:  winget install Gyan.FFmpeg), then re-run:  python encode.py")
        sys.exit(1)

    if mode == "report":
        if ffprobe:
            report(ffprobe)
        else:
            print("ffprobe not available.")
        return

    if mode == "clips":
        only = args[1:] or None
        print(f"(using ffmpeg: {ffmpeg})")
        encode_clips(ffmpeg, only=only)
        return

    # default: everything
    convert_stills()
    print(f"(using ffmpeg: {ffmpeg})")
    encode_clips(ffmpeg)
    if ffprobe:
        report(ffprobe)
    else:
        print("== Validation skipped (ffprobe not available) ==")
    print("\nDone. Now run:  python -m http.server 8000   (from this folder)")


if __name__ == "__main__":
    main()
