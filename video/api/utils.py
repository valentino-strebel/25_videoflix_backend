"""
Utility functions for resolving, validating, and serving HLS video files.
Ensures secure path handling and provides helpers for HLS manifest and segment delivery.
"""

from pathlib import Path
from django.conf import settings
from django.http import FileResponse, Http404, HttpResponse


def allowed_resolutions():
    """
    Return a list of allowed video resolutions defined in settings.

    The setting may be a list, tuple, or a comma-separated string. Values
    are normalized into a clean list of strings.

    Returns:
        list[str]: The allowed resolutions (e.g. ["480p", "720p"]).
    """
    raw = getattr(
        settings,
        "VIDEO_ALLOWED_RESOLUTIONS",
        ["120p", "480p", "360p", "720p", "1080p"],
    )
    return raw if isinstance(raw, (list, tuple)) else [
        s.strip() for s in str(raw).split(",") if s.strip()
    ]


def hls_root():
    """
    Return the base directory used for storing HLS output.

    Uses the HLS_ROOT setting if present, otherwise defaults to:
        MEDIA_ROOT / "hls"

    Returns:
        Path: Filesystem path to the HLS root folder.
    """
    root = getattr(settings, "HLS_ROOT", None)
    return Path(root) if root else Path(settings.MEDIA_ROOT) / "hls"


def safe_hls_path(movie_id: int, resolution: str, filename: str):
    """
    Construct an absolute, sanitized filesystem path to an HLS file.

    Ensures that the resolved path is inside the configured HLS root,
    preventing directory traversal attacks.

    Args:
        movie_id (int): The video ID folder.
        resolution (str): Resolution folder (e.g. "480p").
        filename (str): Name of the file (manifest or segment).

    Returns:
        Path: The resolved absolute path to the requested file.

    Raises:
        Http404: If the resolved path escapes the HLS root.
    """
    base = hls_root().resolve()
    path = (base / str(movie_id) / resolution / filename).resolve()

    if base not in path.parents and base != path:
        raise Http404("Not found")

    return path


def serve_m3u8(movie_id: int, resolution: str):
    """
    Serve the HLS playlist (index.m3u8) for a given movie and resolution.

    Args:
        movie_id (int): Identifier of the video.
        resolution (str): Resolution directory.
    
    Returns:
        FileResponse: The playlist response.

    Raises:
        Http404: If the resolution is invalid or the file does not exist.
    """
    if resolution not in allowed_resolutions():
        raise Http404("Not found")

    path = safe_hls_path(movie_id, resolution, "index.m3u8")
    if not path.exists():
        raise Http404("Not found")

    resp = FileResponse(
        open(path, "rb"),
        content_type="application/vnd.apple.mpegurl",
    )
    resp["Content-Disposition"] = 'inline; filename="index.m3u8"'
    return resp


def serve_segment(movie_id: int, resolution: str, segment: str):
    """
    Serve an HLS segment file for a given movie and resolution.

    Args:
        movie_id (int): Identifier of the video.
        resolution (str): Resolution directory.
        segment (str): The filename of the segment.

    Returns:
        FileResponse: The video segment.

    Raises:
        Http404: If the resolution is invalid, filename is unsafe, or file is missing.
    """
    if resolution not in allowed_resolutions():
        raise Http404("Not found")

    if "/" in segment or "\\" in segment:
        raise Http404("Not found")

    path = safe_hls_path(movie_id, resolution, segment)
    if not path.exists():
        raise Http404("Not found")

    resp = FileResponse(
        open(path, "rb"),
        content_type="video/MP2T",
    )
    resp["Content-Disposition"] = f'inline; filename="{segment}"'
    return resp
