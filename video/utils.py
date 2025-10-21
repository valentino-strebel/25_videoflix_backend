from pathlib import Path
from django.conf import settings
from django.http import FileResponse, Http404, HttpResponse


def allowed_resolutions():
    raw = getattr(settings, "VIDEO_ALLOWED_RESOLUTIONS", ["120p", "360p", "720p", "1080p"])
    return raw if isinstance(raw, (list, tuple)) else [s.strip() for s in str(raw).split(",") if s.strip()]


def hls_root():
    root = getattr(settings, "HLS_ROOT", None)
    return Path(root) if root else Path(settings.MEDIA_ROOT) / "hls"


def safe_hls_path(movie_id: int, resolution: str, filename: str):
    base = hls_root().resolve()
    path = (base / str(movie_id) / resolution / filename).resolve()
    if base not in path.parents and base != path:
        raise Http404("Not found")
    return path


def serve_m3u8(movie_id: int, resolution: str):
    if resolution not in allowed_resolutions():
        raise Http404("Not found")
    path = safe_hls_path(movie_id, resolution, "index.m3u8")
    if not path.exists():
        raise Http404("Not found")
    resp = FileResponse(open(path, "rb"), content_type="application/vnd.apple.mpegurl")
    resp["Content-Disposition"] = f'inline; filename="index.m3u8"'
    return resp


def serve_segment(movie_id: int, resolution: str, segment: str):
    if resolution not in allowed_resolutions():
        raise Http404("Not found")
    if "/" in segment or "\\" in segment:
        raise Http404("Not found")
    path = safe_hls_path(movie_id, resolution, segment)
    if not path.exists():
        raise Http404("Not found")
    resp = FileResponse(open(path, "rb"), content_type="video/MP2T")
    resp["Content-Disposition"] = f'inline; filename="{segment}"'
    return resp
