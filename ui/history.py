import os

import customtkinter as ctk
from tkinter import messagebox

from config import APP_NAME


class HistoryMixin:
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

            win = ctk.CTkToplevel(self)
            win.title("Download History")
            win.geometry("760x650")
            win.minsize(560, 420)
            win.grid_columnconfigure(0, weight=1)
            win.grid_rowconfigure(1, weight=1)

            success_count = sum(1 for entry in entries if entry.get("ok"))
            failed_count = len(entries) - success_count
            header = ctk.CTkFrame(win, fg_color="transparent")
            header.grid(row=0, column=0, padx=20, pady=(14, 8), sticky="ew")
            ctk.CTkLabel(
                header,
                text="Download history",
                font=ctk.CTkFont(size=24, weight="bold"),
            ).pack(anchor="w")
            ctk.CTkLabel(
                header,
                text=f"{success_count} successful  |  {failed_count} failed  |  {len(entries)} records",
                text_color=("gray35", "gray70"),
                font=ctk.CTkFont(size=13),
            ).pack(anchor="w", pady=(2, 0))

            history_frame = ctk.CTkScrollableFrame(win, label_text="Recent downloads")
            history_frame.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="nsew")
            history_frame.grid_columnconfigure(0, weight=1)

            for index, entry in enumerate(entries[:50]):
                ok = bool(entry.get("ok"))
                status_text = "SUCCESS" if ok else "FAILED"
                status_color = ("#18794e", "#55d695") if ok else ("#b42318", "#ff8b82")
                title = entry.get("title") or "Unknown video"
                url = entry.get("url") or "Link is unavailable"

                record = ctk.CTkFrame(history_frame, corner_radius=10)
                record.grid(row=index * 2, column=0, padx=5, pady=(5, 0), sticky="ew")
                record.grid_columnconfigure(0, weight=1)
                ctk.CTkLabel(
                    record,
                    text=status_text,
                    text_color=status_color,
                    font=ctk.CTkFont(size=12, weight="bold"),
                ).grid(row=0, column=0, padx=14, pady=(12, 2), sticky="w")
                ctk.CTkLabel(
                    record,
                    text=title,
                    anchor="w",
                    justify="left",
                    wraplength=680,
                    font=ctk.CTkFont(size=15, weight="bold"),
                ).grid(row=1, column=0, padx=14, pady=(0, 5), sticky="ew")
                ctk.CTkLabel(
                    record,
                    text=f"URL: {url}",
                    anchor="w",
                    justify="left",
                    wraplength=680,
                    text_color=("gray35", "gray70"),
                    font=ctk.CTkFont(size=11),
                ).grid(row=2, column=0, padx=14, pady=(0, 2), sticky="ew")
                ctk.CTkLabel(
                    record,
                    text=f"Downloaded: {entry.get('time', 'Unknown time')}",
                    anchor="w",
                    text_color=("gray45", "gray60"),
                    font=ctk.CTkFont(size=11),
                ).grid(row=3, column=0, padx=14, pady=(0, 12), sticky="w")

                if index < min(len(entries), 50) - 1:
                    ctk.CTkLabel(
                        history_frame,
                        text="* * * * * * * * * * * * * * * * * * * * *",
                        text_color=("gray65", "gray35"),
                        font=ctk.CTkFont(size=11),
                    ).grid(row=index * 2 + 1, column=0, pady=2)
        except Exception as exc:
            messagebox.showerror(APP_NAME, f"Cannot read history: {exc}")
