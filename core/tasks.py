import os
import subprocess
from pathlib import Path
from django.conf import settings

from video.utils import hls_root

def convert720px(input_path):
    base, ext = os.path.splitext(input_path)
    output_path = f"{base}_720p.mp4"

    cmd = [
        "ffmpeg",
        "-i", input_path,
        "-s", "hd720",
        "-c:v", "libx264",
        "-crf", "23",
        "-c:a", "aac",
        "-strict", "-2",
        output_path,
    ]

    subprocess.run(cmd, check=True)
    return output_path

def convert_to_hls_480p(movie_id: int, input_path: str) -> str:
    """
    Convert the given video to 480p HLS and store it under:
    <HLS_ROOT>/<movie_id>/480p/
    Returns the path to the generated index.m3u8.
    """
    # Base HLS folder: usually MEDIA_ROOT / "hls"
    base_dir = hls_root()
    output_dir = base_dir / str(movie_id) / "480p"
    output_dir.mkdir(parents=True, exist_ok=True)

    playlist_path = output_dir / "index.m3u8"
    segment_pattern = output_dir / "segment_%03d.ts"

    cmd = [
        "ffmpeg",
        "-y",                       
        "-i", input_path,          
        "-vf", "scale=-2:480",      
        "-c:v", "h264",
        "-c:a", "aac",
        "-hls_time", "6",           
        "-hls_playlist_type", "vod",
        "-hls_segment_filename", str(segment_pattern),
        str(playlist_path),
    ]

    subprocess.run(cmd, check=True)
    return str(playlist_path)