import queue
import threading

import customtkinter as ctk

from config import APP_NAME, APP_VERSION, DEFAULT_DOWNLOAD_DIR
from downloader import yt_dlp
from storage import load_history
from .downloads import DownloadMixin
from .history import HistoryMixin
from .layout import LayoutMixin


class DownloaderApp(DownloadMixin, HistoryMixin, LayoutMixin, ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title(f"{APP_NAME} {APP_VERSION}")
        self.geometry("1200x1350")
        self.minsize(1020, 930)

        self.msg_queue = queue.Queue()
        self.download_thread = None
        self.cancel_event = threading.Event()
        self.is_downloading = False
        self.playlist = False
        self.url_queue = []
        self.current_url_index = 0

        self.output_dir = ctk.StringVar(value=DEFAULT_DOWNLOAD_DIR)
        self.url_var = ctk.StringVar()
        self.format_var = ctk.StringVar(value="Video (mp4)")
        self.quality_var = ctk.StringVar(value="Best quality")
        self.proxy_var = ctk.StringVar()
        self.auto_open_var = ctk.BooleanVar(value=True)
        self.notify_var = ctk.BooleanVar(value=True)

        self.stats = {"total": 0, "success": 0, "failed": 0}
        self.stats = load_history(self.stats)

        self._build_ui()
        self._poll_queue()

        if yt_dlp is None:
            self._log("WARNING: yt-dlp not found. Run: pip install yt-dlp")

    def _poll_queue(self):
        try:
            while True:
                kind, payload = self.msg_queue.get_nowait()
                if kind == "progress":
                    self.progress_bar.set(payload)
                elif kind == "status":
                    self._set_status(payload)
                elif kind == "log":
                    self._log(payload)
                elif kind == "info_done":
                    self.info_btn.configure(state="normal", text="Get Info")
                    self._set_status("Ready")
                elif kind == "done":
                    self._log(f"Done: {payload}")
                    self.current_url_index += 1
                    if self.current_url_index < len(self.url_queue):
                        self._process_next_in_queue()
                    else:
                        self._set_status("All downloads completed")
                        self._finish_all_downloads()
                elif kind == "error":
                    self._log(f"Error: {payload}")
                    self.current_url_index += 1
                    if self.current_url_index < len(self.url_queue):
                        self._process_next_in_queue()
                    else:
                        self._set_status("Queue finished with errors")
                        self._finish_all_downloads()
                elif kind == "cancelled":
                    self._log("Download cancelled")
                    self._set_status("Cancelled")
                    self._finish_all_downloads()
                elif kind == "update_stats":
                    self._update_stats_label()
        except queue.Empty:
            pass
        self.after(150, self._poll_queue)


def main():
    app = DownloaderApp()
    app.mainloop()
