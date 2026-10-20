#!/usr/bin/env python3
"""
FilmCraft + Remotion Timeline Bridge
------------------------------------
Bridge tool connecting FilmCraft NLE timeline data with Remotion React graphics engine.
Translates exact integer tick timestamps (Filmcraft) into exact frame counts (Remotion)
and automates rendering transparent alpha motion graphics overlays.
"""

import json
import os
import subprocess
import sys
from typing import Dict, Any, List

# Filmcraft exact time constant: 254,016,000,000 integer ticks per second
FILMCRAFT_TICKS_PER_SECOND = 254_016_000_000

def get_filmcraft_cli_path() -> str:
    """Locate the compiled filmcraft-cli executable."""
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "filmcraft-standalone"))
    candidate = os.path.join(base_dir, "target", "debug", "filmcraft-cli.exe")
    if os.path.exists(candidate):
        return candidate
    return "filmcraft-cli"

def invoke_filmcraft_cli(subcommand: str, args: List[str] = None, demo: bool = True) -> Dict[str, Any]:
    """Execute a headless FilmCraft CLI command and parse JSON output."""
    cli_path = get_filmcraft_cli_path()
    cmd = [cli_path]
    if demo:
        cmd.append("--demo")
    cmd.append(subcommand)
    if args:
        cmd.extend(args)
    
    env = os.environ.copy()
    mingw_bin = r"C:\Users\DELL\AppData\Local\Microsoft\WinGet\Packages\BrechtSanders.WinLibs.POSIX.UCRT_Microsoft.Winget.Source_8wekyb3d8bbwe\mingw64\bin"
    env["PATH"] = f"{mingw_bin};{env.get('PATH', '')}"

    result = subprocess.run(cmd, capture_output=True, text=True, env=env)
    if result.returncode != 0:
        raise RuntimeError(f"filmcraft-cli failed: {result.stderr or result.stdout}")
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"raw_output": result.stdout}


def ticks_to_frames(ticks: int, fps: int = 30) -> int:
    """Convert FilmCraft ticks to Remotion frame index."""
    seconds = ticks / FILMCRAFT_TICKS_PER_SECOND
    return int(round(seconds * fps))

def frames_to_ticks(frames: int, fps: int = 30) -> int:
    """Convert Remotion frame count back to FilmCraft ticks."""
    seconds = frames / fps
    return int(round(seconds * FILMCRAFT_TICKS_PER_SECOND))

def export_remotion_overlay(
    remotion_dir: str,
    composition_id: str,
    output_path: str,
    props: Dict[str, Any] = None,
    codec: str = "prores",
) -> bool:
    """
    Renders a Remotion composition with transparent alpha channel.
    Codecs supported:
      - 'prores': Apple ProRes 4444 (with alpha, native for NLE tracks)
      - 'vp8' / 'vp9': WebM transparent
      - 'png': PNG image sequence
    """
    cmd = [
        "npx",
        "remotion",
        "render",
        composition_id,
        output_path,
    ]
    if codec == "prores":
        cmd.extend(["--codec=prores", "--prores-profile=4444"])
    elif codec in ["vp8", "vp9"]:
        cmd.extend([f"--codec={codec}"])

    if props:
        cmd.append(f"--props={json.dumps(props)}")

    print(f"[Bridge] Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=remotion_dir, shell=True)
    return result.returncode == 0

def create_fcpxml_clip_entry(clip_name: str, start_frame: int, duration_frames: int, fps: int = 30) -> str:
    """Generates an FCPXML clip snippet to be placed onto FilmCraft V2 track."""
    return f"""
    <clip name="{clip_name}" offset="{start_frame}/{fps}s" duration="{duration_frames}/{fps}s" start="0s">
        <video ref="r_remotion_{clip_name}" />
    </clip>"""

if __name__ == "__main__":
    print("FilmCraft <-> Remotion Timeline Bridge loaded successfully.")
    print(f"Timebase: {FILMCRAFT_TICKS_PER_SECOND:,} ticks/sec")
    # Quick sanity check: 1 sec at 30fps = 30 frames
    assert ticks_to_frames(FILMCRAFT_TICKS_PER_SECOND, 30) == 30
    print("Sanity check passed: 1s == 30 frames at 30fps.")
