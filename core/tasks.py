import os
import subprocess
from pathlib import Path

from django.conf import settings
from django_rq import job

from authentication.utils import send_activation_email
from authentication.models import User
from video.utils import hls_root



_VIDEO_ALLOWED_RESOLUTIONS = getattr(
    settings,
    "VIDEO_ALLOWED_RESOLUTIONS",
    ["480p", "720p"],  
)

ALLOWED_RESOLUTIONS = {
    str(res).strip().lower()
    for res in _VIDEO_ALLOWED_RESOLUTIONS
    if str(res).strip()
}

RESOLUTION_HEIGHTS = {
    "120p": 120,
    "360p": 360,
    "480p": 480,
    "720p": 720,
    "1080p": 1080,
}


def get_resolution_height(resolution: str) -> int:
    """
    Validate the resolution string (e.g. "480p") and return its height.
    Raises ValueError if the resolution is not allowed or unknown.
    """
    resolution = resolution.lower()

    if resolution not in ALLOWED_RESOLUTIONS:
        raise ValueError(
            f"Resolution '{resolution}' is not in allowed resolutions: "
            f"{sorted(ALLOWED_RESOLUTIONS)}"
        )

    try:
        return RESOLUTION_HEIGHTS[resolution]
    except KeyError as exc:
        raise ValueError(
            f"Unknown resolution '{resolution}'. "
            f"Supported: {sorted(RESOLUTION_HEIGHTS.keys())}"
        ) from exc


# -------------------------------------------------------------------
# MP4 conversion
# -------------------------------------------------------------------

def convert_to_mp4(input_path: str, resolution: str) -> str:
    """
    Convert the given video file to MP4 at the specified resolution,
    using the naming pattern: <base>_<resolution>.mp4

    Example: /path/video.mp4 + "480p" -> /path/video_480p.mp4
    """
    height = get_resolution_height(resolution)

    base, ext = os.path.splitext(input_path)
    output_path = f"{base}_{resolution.lower()}.mp4"

    cmd = [
        "ffmpeg",
        "-y",                          # overwrite output
        "-i", input_path,
        "-vf", f"scale=-2:{height}",   # keep aspect ratio, set height
        "-c:v", "libx264",
        "-crf", "23",
        "-c:a", "aac",
        "-strict", "-2",
        output_path,
    ]

    subprocess.run(cmd, check=True)
    return output_path


def convert720px(input_path: str) -> str:
    """
    Legacy wrapper for 720p MP4 conversion.
    """
    return convert_to_mp4(input_path, "720p")


# -------------------------------------------------------------------
# HLS conversion
# -------------------------------------------------------------------

def convert_to_hls(movie_id: int, input_path: str, resolution: str) -> str:
    """
    Convert the given video to HLS at the specified resolution and store it under:
        <HLS_ROOT>/<movie_id>/<resolution>/

    Returns the path to the generated index.m3u8.
    """
    height = get_resolution_height(resolution)
    resolution = resolution.lower()

    base_dir: Path = hls_root()
    output_dir = base_dir / str(movie_id) / resolution
    output_dir.mkdir(parents=True, exist_ok=True)

    playlist_path = output_dir / "index.m3u8"
    segment_pattern = output_dir / "segment_%03d.ts"

    cmd = [
        "ffmpeg",
        "-y",
        "-i", input_path,
        "-vf", f"scale=-2:{height}",
        "-c:v", "libx264",
        "-c:a", "aac",
        "-hls_time", "6",
        "-hls_playlist_type", "vod",
        "-hls_segment_filename", str(segment_pattern),
        str(playlist_path),
    ]

    subprocess.run(cmd, check=True)
    return str(playlist_path)


def convert_to_hls_480p(movie_id: int, input_path: str) -> str:
    """
    Legacy wrapper for 480p HLS conversion.
    """
    return convert_to_hls(movie_id, input_path, "480p")


# -------------------------------------------------------------------
# Async jobs
# -------------------------------------------------------------------

@job
def send_activation_email_async(user_id: int) -> None:
    user = User.objects.get(pk=user_id)
    send_activation_email(user)
