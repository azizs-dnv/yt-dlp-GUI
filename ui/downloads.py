import os
import threading
import time
from datetime import datetime
from tkinter import messagebox

from config import APP_NAME, DEFAULT_DOWNLOAD_DIR
from downloader import build_download_options, get_playlist_entries, get_video_info, yt_dlp
from helpers import open_folder, parse_urls, play_bell
from storage import save_history


class DownloadMixin:
    def _get_video_info(self):
        if yt_dlp is None:
            messagebox.showerror(APP_NAME, "yt-dlp is not installed.")
            return

        url = self.url_var.get().strip()
        if not url:
            messagebox.showwarning(APP_NAME, "Please enter a URL first.")
            return

        self.info_btn.configure(state="disabled", text="Loading...")
        self._set_status("Fetching info...")
        threading.Thread(target=self._info_worker, args=(url,), daemon=True).start()

    def _info_worker(self, url: str):
        try:
            info = get_video_info(url, self.proxy_var.get().strip())
            title = info.get("title", "N/A")
            duration = info.get("duration")
            uploader = info.get("uploader", "N/A")
            dur_str = time.strftime("%H:%M:%S", time.gmtime(duration)) if duration else "N/A"
            msg = (
                f"Info:\n"
                f"   Title:    {title}\n"
                f"   Channel:  {uploader}\n"
                f"   Duration: {dur_str}\n"
                f"   -------------------------"
            )
            self.msg_queue.put(("log", msg))
        except Exception as exc:
            self.msg_queue.put(("log", f"Info error: {exc}"))
        finally:
            self.msg_queue.put(("info_done", None))

    def _start_download(self):
        if self.is_downloading:
            messagebox.showinfo(APP_NAME, "Download already in progress.")
            return
        if yt_dlp is None:
            messagebox.showerror(APP_NAME, "yt-dlp not installed.\nRun: pip install yt-dlp")
            return

        raw = self.url_var.get().strip()
        if not raw:
            messagebox.showwarning(APP_NAME, "Please enter a video URL.")
            return

        urls = parse_urls(raw)
        if not urls:
            messagebox.showwarning(APP_NAME, "No valid URLs found.")
            return

        self.url_queue = urls
        self.current_url_index = 0

        out_dir = self.output_dir.get().strip() or DEFAULT_DOWNLOAD_DIR
        os.makedirs(out_dir, exist_ok=True)

        self.is_downloading = True
        self.cancel_event.clear()
        self.download_btn.configure(state="disabled", text="Installing...")
        self.cancel_btn.configure(state="normal")
        self.progress_bar.set(0)
        self._set_status(f"Queue: 1/{len(self.url_queue)}")
        self._log(f"Starting queue with {len(self.url_queue)} URL(s)")

        self._process_next_in_queue()

    def _cancel_download(self):
        if not self.is_downloading:
            return

        self.cancel_event.set()
        self.cancel_btn.configure(state="disabled")
        self._set_status("Cancelling...")
        self._log("Cancellation requested")

    def _process_next_in_queue(self):
        if self.current_url_index >= len(self.url_queue):
            self._finish_all_downloads()
            return

        url = self.url_queue[self.current_url_index]
        self._log(f"\n[{self.current_url_index + 1}/{len(self.url_queue)}] {url}")
        self._set_status(f"Downloading {self.current_url_index + 1}/{len(self.url_queue)}")
        self.download_thread = threading.Thread(
            target=self._download_worker, args=(url,), daemon=True
        )
        self.download_thread.start()

    def _download_worker(self, url: str):
        out_dir = self.output_dir.get().strip() or DEFAULT_DOWNLOAD_DIR

        def progress_hook(d):
            if self.cancel_event.is_set():
                raise yt_dlp.utils.DownloadCancelled()

            if d.get("status") == "downloading":
                total = d.get("total_bytes") or d.get("total_bytes_estimate")
                downloaded = d.get("downloaded_bytes", 0)
                if total:
                    self.msg_queue.put(("progress", downloaded / total))
                speed = d.get("_speed_str", "").strip()
                pct = d.get("_percent_str", "").strip()
                eta = d.get("_eta_str", "").strip()
                self.msg_queue.put(
                    (
                        "status",
                        f"Video {self.current_url_index + 1}/{len(self.url_queue)}  |  "
                        f"Progress: {pct}  |  Speed: {speed}  |  ETA: {eta}",
                    )
                )
            elif d.get("status") == "finished":
                self.msg_queue.put(("status", "Processing..."))
                self.msg_queue.put(("progress", 1.0))

        quality = self.quality_var.get()
        is_audio = self.format_var.get().startswith("Audio only")
        ydl_opts = build_download_options(
            out_dir=out_dir,
            quality=quality,
            is_audio=is_audio,
            playlist=self.playlist,
            proxy=self.proxy_var.get().strip(),
            progress_hook=progress_hook,
        )

        ok = False
        title = "unknown"
        try:
            download_urls = (
                get_playlist_entries(url, self.proxy_var.get().strip())
                if self.playlist
                else [url]
            )
            if not download_urls:
                raise RuntimeError(
                    "The playlist could not be read or contains no downloadable videos."
                )

            for playlist_index, download_url in enumerate(download_urls, 1):
                if self.cancel_event.is_set():
                    raise yt_dlp.utils.DownloadCancelled()
                if self.playlist:
                    self.msg_queue.put(
                        (
                            "status",
                            f"Playlist video {playlist_index}/{len(download_urls)}",
                        )
                    )
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(download_url, download=True)
                    title = info.get("title", "video")
            ok = True
            self.msg_queue.put(("done", title))
        except yt_dlp.utils.DownloadCancelled:
            self.msg_queue.put(("cancelled", None))
        except Exception as exc:
            self.msg_queue.put(("error", str(exc)))

        self.stats["total"] += 1
        if ok:
            self.stats["success"] += 1
        else:
            self.stats["failed"] += 1

        save_history(
            self.stats,
            {
                "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "title": title,
                "url": url,
                "ok": ok,
            },
        )
        self.msg_queue.put(("update_stats", None))

    def _finish_all_downloads(self):
        self.is_downloading = False
        self.download_btn.configure(state="normal", text="Download")
        self.cancel_btn.configure(state="disabled")
        self.progress_bar.set(1.0 if self.stats["success"] > 0 else 0)

        if self.notify_var.get():
            play_bell()
            if self.current_url_index >= len(self.url_queue):
                messagebox.showinfo(
                    APP_NAME,
                    f"Queue finished!\nSuccess: {self.stats['success']}\nFailed: {self.stats['failed']}"
                )

        if self.auto_open_var.get():
            out_dir = self.output_dir.get().strip() or DEFAULT_DOWNLOAD_DIR
            open_folder(out_dir)
