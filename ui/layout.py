import customtkinter as ctk
from tkinter import filedialog


class LayoutMixin:
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
            placeholder_text="https://example.com/video-or-playlist",
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

        self.cancel_btn = ctk.CTkButton(
            btn_frame,
            text="Cancel",
            height=36,
            fg_color="#b42318",
            hover_color="#8f1d14",
            state="disabled",
            command=self._cancel_download,
        )
        self.cancel_btn.grid(row=1, column=0, pady=(8, 0), sticky="ew")

        ctk.CTkButton(
            btn_frame, text="History", width=100, height=46, command=self._show_history
        ).grid(row=0, column=1, padx=(10, 0))

        self.progress_bar = ctk.CTkProgressBar(self, height=18)
        self.progress_bar.set(0)
        self.progress_bar.grid(row=10, column=0, padx=20, pady=(5, 5), sticky="ew")

        self.status_label = ctk.CTkLabel(
            self,
            text="Ready",
            anchor="w",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=("gray25", "gray80"),
        )
        self.status_label.grid(row=11, column=0, padx=20, pady=(2, 8), sticky="ew")

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
