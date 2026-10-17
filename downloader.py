import os
from typing import Any, Dict

try:
    import yt_dlp
    from yt_dlp.networking.impersonate import ImpersonateTarget
except ImportError:  
    yt_dlp = None
    ImpersonateTarget = None


def _add_impersonation(opts: Dict[str, Any]) -> None:
    if ImpersonateTarget is not None:
        opts["impersonate"] = ImpersonateTarget("chrome")


def get_video_info(url: str, proxy: str = "") -> Dict[str, Any]:
    if yt_dlp is None:
        raise RuntimeError("yt-dlp is not installed.")

    opts: Dict[str, Any] = {
        "quiet": False,
        "no_warnings": False,
        "js_runtimes": {"node": {}},
        "remote_components": ["ejs:github"],
        "extractor_args": {"youtube": {"player_client": ["android", "web"]}},
        "retries": 10,
        "extractor_retries": 3,
        "socket_timeout": 30,
    }
    _add_impersonation(opts)
    if proxy:
        opts["proxy"] = proxy

    with yt_dlp.YoutubeDL(opts) as ydl:
        return ydl.extract_info(url, download=False)


def get_playlist_entries(url: str, proxy: str = "") -> list[str]:
    if yt_dlp is None:
        raise RuntimeError("yt-dlp is not installed.")

    opts: Dict[str, Any] = {
        "quiet": False,
        "no_warnings": False,
        "extract_flat": True,
        "noplaylist": False,
        "js_runtimes": {"node": {}},
        "remote_components": ["ejs:github"],
        "extractor_args": {"youtube": {"player_client": ["android", "web"]}},
        "retries": 10,
        "extractor_retries": 3,
        "socket_timeout": 30,
    }
    _add_impersonation(opts)
    if proxy:
        opts["proxy"] = proxy

    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=False)

    if info.get("_type") != "playlist":
        return [url]

    entries = info.get("entries") or []
    playlist_entries = []
    for entry in entries:
        if not entry:
            continue
        entry_url = entry.get("webpage_url") or entry.get("url")
        if entry_url:
            playlist_entries.append(entry_url)
    return playlist_entries


def build_download_options(
    out_dir: str,
    quality: str,
    is_audio: bool,
    playlist: bool,
    proxy: str,
    progress_hook,
) -> Dict[str, Any]:
    ydl_opts: Dict[str, Any] = {
        "outtmpl": os.path.join(out_dir, "%(title)s.%(ext)s"),
        "progress_hooks": [progress_hook],
        "noplaylist": True,
        "js_runtimes": {"node": {}},
        "remote_components": ["ejs:github"],
        "extractor_args": {"youtube": {"player_client": ["android", "web"]}},
        "quiet": False,
        "no_warnings": False,
        "retries": 10,
        "fragment_retries": 10,
        "file_access_retries": 5,
        "extractor_retries": 3,
        "socket_timeout": 30,
        "concurrent_fragment_downloads": 1,
    }
    _add_impersonation(ydl_opts)

    if proxy:
        ydl_opts["proxy"] = proxy

    if is_audio:
        ydl_opts["format"] = "bestaudio/best"
        ydl_opts["postprocessors"] = [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ]
    else:
        if quality == "Best quality":
            ydl_opts["format"] = (
                "bestvideo[ext=mp4]+bestaudio/"
                "best[ext=mp4]/best"
            )
        else:
            height = quality.replace("p", "")
            ydl_opts["format"] = (
                f"bestvideo[height<={height}][ext=mp4]+"
                f"bestaudio/best[height<={height}][ext=mp4]/"
                f"best[height<={height}]/best"
            )
        ydl_opts["merge_output_format"] = "mp4"

    return ydl_opts
