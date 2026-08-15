import os
import queue
import threading
import time
from datetime import datetime

import customtkinter as ctk
from tkinter import filedialog, messagebox

from config import APP_NAME, APP_VERSION, DEFAULT_DOWNLOAD_DIR
from downloader import build_download_options, get_video_info, yt_dlp
from helpers import open_folder, parse_urls, play_bell
from storage import load_history, save_history


class DownloaderApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title(f"{APP_NAME} {APP_VERSION}")
        self.geometry("800x900")
        self.minsize(680, 620)

        self.msg_queue = queue.Queue()
        self.download_thread = None
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

    def _show_history(self):
        if not os.path.exists(os.path.expanduser("~/.yt_downloader_history.json")):
            messagebox.showinfo(APP_NAME, "No download history yet.")
            return

        try:
            import json

            history_path = os.path.expanduser("~/.yt_downloader_history.json")
            with open(history_path, "r", encoding="utf-8") as handle:
                data = json.load(handle)

            entries = data.get("entries", [])
            if not entries:
                messagebox.showinfo(APP_NAME, "History is empty.")
                return

            text = f"Stats: {self.stats['success']} success / {self.stats['total']} total\n"
            text += "-" * 50 + "\n"
            for i, entry in enumerate(entries[:20], 1):
                status = "success" if entry.get("ok") else "failed"
                text += f"{i}. {status} | {entry.get('time', '?')} | {entry.get('title', '?')[:40]}\n"

            win = ctk.CTkToplevel(self)
            win.title("Download History")
            win.geometry("600x500")
            box = ctk.CTkTextbox(win, font=ctk.CTkFont(size=12))
            box.pack(fill="both", expand=True, padx=10, pady=10)
            box.insert("1.0", text)
            box.configure(state="disabled")
        except Exception as exc:
            messagebox.showerror(APP_NAME, f"Cannot read history: {exc}")

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)

        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=20, pady=(15, 0), sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header_frame,
            text="YT Downloader Pro",
            font=ctk.CTkFont(size=26, weight="bold"),
        ).grid(row=0, column=0, sticky="w")

        self.theme_btn = ctk.CTkButton(
            header_frame,
            text="Dark mode",
            width=120,
            height=32,
            command=self._toggle_theme,
        )
        self.theme_btn.grid(row=0, column=1, padx=(10, 0))

        ctk.CTkLabel(
            self,
            text="Download videos from YouTube and other sites powered by yt-dlp",
            font=ctk.CTkFont(size=13),
            text_color=("gray30", "gray70"),
        ).grid(row=1, column=0, padx=20, pady=(0, 5), sticky="w")

        self.stats_label = ctk.CTkLabel(
            self,
            text=f"Total: {self.stats['total']}  Success: {self.stats['success']}  Failed: {self.stats['failed']}",
            font=ctk.CTkFont(size=11),
            text_color=("gray40", "gray60"),
        )
        self.stats_label.grid(row=2, column=0, padx=20, pady=(0, 5), sticky="w")

        self.radio_var = ctk.IntVar(value=1)
        radio_frame = ctk.CTkFrame(self, fg_color="transparent")
        radio_frame.grid(row=3, column=0, padx=20, pady=(0, 5), sticky="w")
        ctk.CTkLabel(
            radio_frame, text="Mode:", font=ctk.CTkFont(size=13, weight="bold")
        ).pack(side="left", padx=(0, 10))
        ctk.CTkRadioButton(
            radio_frame, text="Video", variable=self.radio_var, value=1, command=self._radio_event
        ).pack(side="left", padx=(0, 15))
        ctk.CTkRadioButton(
            radio_frame, text="Playlist", variable=self.radio_var, value=2, command=self._radio_event
        ).pack(side="left")

        url_frame = ctk.CTkFrame(self, corner_radius=12)
        url_frame.grid(row=4, column=0, padx=20, pady=8, sticky="ew")
        url_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            url_frame, text="Video URL (you can paste multiple URLs separated by commas or new lines)",
            font=ctk.CTkFont(size=13, weight="bold")
        ).grid(row=0, column=0, columnspan=2, padx=15, pady=(10, 2), sticky="w")

        self.url_entry = ctk.CTkEntry(
            url_frame,
            textvariable=self.url_var,
            placeholder_text="https://www.youtube.com/watch?v=...",
            height=40,
            font=ctk.CTkFont(size=14),
        )
        self.url_entry.grid(row=1, column=0, padx=(15, 5), pady=(0, 10), sticky="ew")

        self.info_btn = ctk.CTkButton(
            url_frame, text="Get Info", width=90, height=38, command=self._get_video_info,
        )
        self.info_btn.grid(row=1, column=1, padx=(0, 15), pady=(0, 10))

        opts_frame = ctk.CTkFrame(self, corner_radius=12)
        opts_frame.grid(row=5, column=0, padx=20, pady=8, sticky="ew")
        opts_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(
            opts_frame, text="Format", font=ctk.CTkFont(size=13, weight="bold")
        ).grid(row=0, column=0, padx=15, pady=(10, 2), sticky="w")
        ctk.CTkOptionMenu(
            opts_frame, variable=self.format_var, values=["Video (mp4)", "Audio only (mp3)"], height=36
        ).grid(row=1, column=0, padx=15, pady=(0, 10), sticky="ew")

        ctk.CTkLabel(
            opts_frame, text="Quality", font=ctk.CTkFont(size=13, weight="bold")
        ).grid(row=0, column=1, padx=15, pady=(10, 2), sticky="w")
        ctk.CTkOptionMenu(
            opts_frame, variable=self.quality_var,
            values=["Best quality", "1080p", "720p", "480p", "360p"], height=36
        ).grid(row=1, column=1, padx=15, pady=(0, 10), sticky="ew")

        adv_frame = ctk.CTkFrame(self, corner_radius=12)
        adv_frame.grid(row=6, column=0, padx=20, pady=8, sticky="ew")

        ctk.CTkLabel(
            adv_frame, text="Advanced", font=ctk.CTkFont(size=13, weight="bold")
        ).grid(row=0, column=0, columnspan=2, padx=15, pady=(10, 2), sticky="w")

        ctk.CTkLabel(
            adv_frame, text="Proxy (optional):", font=ctk.CTkFont(size=12)
        ).grid(row=1, column=0, padx=15, pady=(0, 10), sticky="w")
        ctk.CTkEntry(
            adv_frame, textvariable=self.proxy_var,
            placeholder_text="http://user:pass@proxy:8080", height=34
        ).grid(row=1, column=1, padx=15, pady=(0, 10), sticky="ew")
        adv_frame.grid_columnconfigure(1, weight=1)

        folder_frame = ctk.CTkFrame(self, corner_radius=12)
        folder_frame.grid(row=7, column=0, padx=20, pady=8, sticky="ew")
        folder_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            folder_frame, text="Save Folder", font=ctk.CTkFont(size=13, weight="bold")
        ).grid(row=0, column=0, columnspan=2, padx=15, pady=(10, 2), sticky="w")

        ctk.CTkEntry(
            folder_frame, textvariable=self.output_dir, height=36
        ).grid(row=1, column=0, padx=(15, 5), pady=(0, 10), sticky="ew")
        ctk.CTkButton(
            folder_frame, text="Browse...", width=100, height=36, command=self._choose_folder
        ).grid(row=1, column=1, padx=(0, 15), pady=(0, 10))

        chk_frame = ctk.CTkFrame(self, fg_color="transparent")
        chk_frame.grid(row=8, column=0, padx=20, pady=(0, 5), sticky="w")
        ctk.CTkCheckBox(
            chk_frame, text="Open folder when done", variable=self.auto_open_var
        ).pack(side="left", padx=(0, 20))
        ctk.CTkCheckBox(
            chk_frame, text="Show notification", variable=self.notify_var
        ).pack(side="left")

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=9, column=0, padx=20, pady=(5, 5), sticky="ew")
        btn_frame.grid_columnconfigure(0, weight=1)

        self.download_btn = ctk.CTkButton(
            btn_frame,
            text="Download",
            height=46,
            font=ctk.CTkFont(size=16, weight="bold"),
            command=self._start_download,
        )
        self.download_btn.grid(row=0, column=0, sticky="ew")

        ctk.CTkButton(
            btn_frame, text="History", width=100, height=46, command=self._show_history
        ).grid(row=0, column=1, padx=(10, 0))

        self.progress_bar = ctk.CTkProgressBar(self, height=14)
        self.progress_bar.set(0)
        self.progress_bar.grid(row=10, column=0, padx=20, pady=(5, 5), sticky="ew")

        self.status_label = ctk.CTkLabel(
            self, text="Ready", font=ctk.CTkFont(size=12)
        )
        self.status_label.grid(row=11, column=0, padx=20, pady=(0, 5), sticky="w")

        self.grid_rowconfigure(12, weight=1)
        self.log_box = ctk.CTkTextbox(
            self, corner_radius=12, font=ctk.CTkFont(size=12)
        )
        self.log_box.grid(row=12, column=0, padx=20, pady=(0, 15), sticky="nsew")
        self.log_box.configure(state="disabled")

    def _radio_event(self):
        self.playlist = self.radio_var.get() == 2

    def _toggle_theme(self):
        current = ctk.get_appearance_mode()
        new = "light" if current == "Dark" else "dark"
        ctk.set_appearance_mode(new)
        self.theme_btn.configure(text="Light mode" if new == "light" else "Dark mode")

    def _choose_folder(self):
        folder = filedialog.askdirectory(initialdir=self.output_dir.get() or ".")
        if folder:
            self.output_dir.set(folder)

    def _log(self, text: str):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", text + "\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def _set_status(self, text: str):
        self.status_label.configure(text=text)

    def _update_stats_label(self):
        self.stats_label.configure(
            text=f"Total: {self.stats['total']}  Success: {self.stats['success']}  Failed: {self.stats['failed']}"
        )

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
        self.download_btn.configure(state="disabled", text="Downloading...")
        self.progress_bar.set(0)
        self._set_status(f"Queue: 1/{len(self.url_queue)}")
        self._log(f"Starting queue with {len(self.url_queue)} URL(s)")

        self._process_next_in_queue()

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
            if d.get("status") == "downloading":
                total = d.get("total_bytes") or d.get("total_bytes_estimate")
                downloaded = d.get("downloaded_bytes", 0)
                if total:
                    self.msg_queue.put(("progress", downloaded / total))
                speed = d.get("_speed_str", "").strip()
                pct = d.get("_percent_str", "").strip()
                eta = d.get("_eta_str", "").strip()
                self.msg_queue.put(
                    ("status", f"[{self.current_url_index + 1}/{len(self.url_queue)}] {pct} | {speed} | ETA {eta}")
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
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                title = info.get("title", "video")
            ok = True
            self.msg_queue.put(("done", title))
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
                elif kind == "update_stats":
                    self._update_stats_label()
        except queue.Empty:
            pass
        self.after(150, self._poll_queue)

    def _finish_all_downloads(self):
        self.is_downloading = False
        self.download_btn.configure(state="normal", text="Download")
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


def main():
    app = DownloaderApp()
    app.mainloop()


if __name__ == "__main__":
    main()
