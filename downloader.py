import os
from typing import Any, Dict

try:
    import yt_dlp
except ImportError:  
    yt_dlp = None


def get_video_info(url: str, proxy: str = "") -> Dict[str, Any]:
    if yt_dlp is None:
        raise RuntimeError("yt-dlp is not installed.")

    opts: Dict[str, Any] = {
        "quiet": False,
        "no_warnings": False,
        "retries": 10,
        "extractor_retries": 3,
        "socket_timeout": 30,
    }
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
        "retries": 10,
        "extractor_retries": 3,
        "socket_timeout": 30,
    }
    if proxy:
        opts["proxy"] = proxy

    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=False)

    if info.get("_type") != "playlist":
        return [url]

    entries = info.get("entries") or []
    return [entry["url"] for entry in entries if entry and entry.get("url")]


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
        "quiet": False,
        "no_warnings": False,
        "retries": 10,
        "fragment_retries": 10,
        "file_access_retries": 5,
        "extractor_retries": 3,
        "socket_timeout": 30,
        "concurrent_fragment_downloads": 1,
    }

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
                "bestvideo[ext=mp4]+bestaudio[ext=m4a]/"
                "best[ext=mp4]/best"
            )
        else:
            height = quality.replace("p", "")
            ydl_opts["format"] = (
                f"bestvideo[height<={height}][ext=mp4]+"
                f"bestaudio[ext=m4a]/best[height<={height}][ext=mp4]/"
                f"best[height<={height}]/best"
            )
        ydl_opts["merge_output_format"] = "mp4"

    return ydl_opts
