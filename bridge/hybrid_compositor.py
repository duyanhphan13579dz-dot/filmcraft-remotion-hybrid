#!/usr/bin/env python3
"""
FilmCraft + Remotion Hybrid Compositor
--------------------------------------
Automated workflow:
1. Trims/Slices footage (FilmCraft logic or direct ffmpeg pipeline)
2. Renders dynamic React elements from Remotion (Lower-thirds, Kinetic text, Captions)
3. Merges them onto Track V2 with precise time alignment
"""

import argparse
import os
import subprocess
import sys
from timeline_bridge import ticks_to_frames, export_remotion_overlay

REMOTION_STUDIO_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "remotion-studio"))

def composite_video(
    base_video: str,
    overlay_video: str,
    output_video: str,
    overlay_start_seconds: float = 1.0,
):
    """
    Overlays a transparent video (rendered from Remotion) on top of base video
    at overlay_start_seconds using hardware-accelerated ffmpeg filter.
    """
    filter_complex = f"[0:v][1:v]overlay=0:0:enable='gte(t,{overlay_start_seconds})':eof_action=pass[outv]"
    cmd = [
        "ffmpeg",
        "-i", base_video,
        "-i", overlay_video,
        "-filter_complex", filter_complex,
        "-map", "[outv]",
        "-map", "0:a?",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-c:a", "copy",
        output_video,
        "-y"
    ]
    print(f"[Compositor] Executing: {' '.join(cmd)}")
    res = subprocess.run(cmd)
    if res.returncode == 0:
        print(f"[Compositor] Successfully generated hybrid master: {output_video}")
    else:
        print(f"[Compositor] Error combining tracks (code {res.returncode})")
    return res.returncode == 0

if __name__ == "__main__":
    print(f"Hybrid Compositor initialized. Connected to Remotion Studio at:\n  {REMOTION_STUDIO_DIR}")
