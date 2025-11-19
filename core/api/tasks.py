"""
Utilities for video conversion (MP4 and HLS) and async email-related tasks.
"""

import os
import subprocess
from pathlib import Path

from django.conf import settings
from django_rq import job

from authentication.api.utils import send_activation_email
from authentication.models import User
from video.api.utils import hls_root


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

    Args:
        resolution (str): Resolution label including 'p' (e.g. "480p").

    Returns:
        int: The vertical height in pixels for the given resolution.

    Raises:
        ValueError: If the resolution is not allowed or unknown.
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


def convert_to_mp4(input_path: str, resolution: str) -> str:
    """
    Convert a video file to MP4 at the specified resolution.

    The output file name follows the pattern:
        <base>_<resolution>.mp4

    Example:
        /path/video.mp4 + "480p" -> /path/video_480p.mp4

    Args:
        input_path (str): Path to the input video file.
        resolution (str): Resolution label such as "480p" or "720p".

    Returns:
        str: Path to the converted MP4 file.

    Raises:
        ValueError: If the resolution is invalid.
        CalledProcessError: If ffmpeg fails.
    """
    height = get_resolution_height(resolution)

    base, ext = os.path.splitext(input_path)
    output_path = f"{base}_{resolution.lower()}.mp4"

    cmd = [
        "ffmpeg",
        "-y",
        "-i", input_path,
        "-vf", f"scale=-2:{height}",
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
    Legacy wrapper that converts a video to 720p MP4.

    Args:
        input_path (str): Path to the input video file.

    Returns:
        str: Path to the converted 720p MP4 file.
    """
    return convert_to_mp4(input_path, "720p")


def convert_to_hls(movie_id: int, input_path: str, resolution: str) -> str:
    """
    Convert a video file to HLS at the specified resolution.

    The output is stored under:
        <HLS_ROOT>/<movie_id>/<resolution>/

    Args:
        movie_id (int): Identifier used to build the output directory path.
        input_path (str): Path to the input video file.
        resolution (str): Resolution label such as "480p" or "720p".

    Returns:
        str: Path to the generated HLS playlist (index.m3u8).

    Raises:
        ValueError: If the resolution is invalid.
        CalledProcessError: If ffmpeg fails.
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
    Legacy wrapper that converts a video to 480p HLS.

    Args:
        movie_id (int): Identifier used to build the output directory path.
        input_path (str): Path to the input video file.

    Returns:
        str: Path to the generated 480p HLS playlist (index.m3u8).
    """
    return convert_to_hls(movie_id, input_path, "480p")


@job
def send_activation_email_async(user_id: int) -> None:
    """
    Asynchronous task to send an activation email to a user.

    Args:
        user_id (int): Primary key of the user who should receive the email.
    """
    user = User.objects.get(pk=user_id)
    send_activation_email(user)
