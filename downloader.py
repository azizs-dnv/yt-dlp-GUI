import os
from typing import Any, Dict

try:
    import yt_dlp
except ImportError:  
    yt_dlp = None


def get_video_info(url: str, proxy: str = "") -> Dict[str, Any]:
    if yt_dlp is None:
        raise RuntimeError("yt-dlp is not installed.")

    opts: Dict[str, Any] = {"quiet": False, "no_warnings": False}
    if proxy:
        opts["proxy"] = proxy

    with yt_dlp.YoutubeDL(opts) as ydl:
        return ydl.extract_info(url, download=False)


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
        "noplaylist": not playlist,
        "quiet": False,
        "no_warnings": False,
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
            ydl_opts["format"] = "bestvideo+bestaudio/best"
        else:
            height = quality.replace("p", "")
            ydl_opts["format"] = (
                f"bestvideo[height<={height}]+bestaudio/best[height<={height}]"
            )
        ydl_opts["merge_output_format"] = "mp4"

    return ydl_opts
