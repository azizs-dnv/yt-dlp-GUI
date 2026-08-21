# YT Downloader Pro

A modern desktop application with a modern GUI for downloading video and audio from YouTube and other websites supported by [yt-dlp](https://github.com/yt-dlp/yt-dlp).

![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-Apache%202.0-green)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)

## Features

- Download videos via link (YouTube and hundreds of other websites via yt-dlp)
- Extract audio to MP3 format
- Select video quality (Best, 1080p, 720p, 480p, 360p)
- Choose a destination folder to save files
- Real-time progress bar and download log
- Modern dark-themed interface powered by CustomTkinter
- You can choose to download 1 video or all the playlist
- Download multiple URLs at once (queue support — paste URLs separated by commas or new lines)
- Preview video info before downloading (title, channel, duration)
- Proxy support for downloads
- Download history with auto-save (last 200 entries)
- Live download statistics (Total / Success / Failed counters)
- Auto-open destination folder when download completes
- Sound notification and popup alert when queue finishes
- Toggle between Dark and Light themes

## Interface

The application consists of:
- An input field for pasting the video link (supports multiple URLs);
- A "Get Info" button to preview video details without downloading;
- Mode selector: Video or Playlist;
- Format (video/audio) and quality selectors;
- Advanced section with optional proxy configuration;
- A destination folder selection field with a "Browse..." button;
- Checkboxes for "Open folder when done" and "Show notification";
- A "Download" button and a "History" button;
- A progress bar with live status (speed, percentage, ETA);
- A log window showing detailed operations.

## Installation

1. Make sure you have **Python 3.9+** installed.
2. Install [FFmpeg](https://ffmpeg.org/download.html) — it is required by yt-dlp for merging video/audio tracks and converting to MP3. Ensure that the `ffmpeg` command is accessible in your terminal.
3. Clone the repository and install the dependencies:
4. Run main.py file 

```bash
git clone [https://github.com/&lt;your-username&gt;/yt-downloader.git](https://github.com/azizs10/yt-dlp-GUI)
cd yt-downloader
pip install -r requirements.txt
python main.py
