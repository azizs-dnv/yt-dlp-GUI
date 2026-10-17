# YT Downloader Pro

A desktop GUI for downloading video and audio from YouTube, TikTok, and other websites supported by [yt-dlp](https://github.com/yt-dlp/yt-dlp).

![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)

## Features

- Download videos via URL from any site supported by yt-dlp, including YouTube and TikTok
- Extract audio to MP3 format
- Select video quality (Best, 1080p, 720p, 480p, 360p)
- Choose a destination folder to save files
- Real-time progress bar and download log
- Modern dark-themed interface powered by CustomTkinter
- Download a single video or all items from a supported playlist
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
2. Install [FFmpeg](https://ffmpeg.org/download.html). It is required for merging separate video/audio streams and converting to MP3. Ensure that the `ffmpeg` command is accessible in your terminal.
3. Clone the repository, create a virtual environment, install dependencies, and run the app:

```bash
git clone [https://github.com/azizs10/yt-dlp-GUI.git](https://github.com/azizs10/yt-dlp-GUI.git)
cd yt-dlp-GUI
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

The `curl-cffi` dependency enables browser impersonation used by TikTok and some other sites that reject ordinary HTTP clients. It is installed automatically with the requirements file.

## Supported URLs

The application delegates URL handling to yt-dlp rather than maintaining a site-specific downloader. This includes supported video pages, audio pages, channels, and playlists from the sites listed in the [yt-dlp supported sites](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md) documentation.

Paste one URL, or paste several URLs separated by commas or new lines. In **Playlist** mode, the application asks yt-dlp to enumerate the playlist and then downloads each item using the selected format and quality. A normal video URL still downloads as a single item.

Some sites require login, cookies, age verification, a supported browser session, or a region-appropriate proxy. The application can use a proxy configured in **Advanced**, but it does not bypass access controls or download content that yt-dlp cannot legally or technically access.

## Formats and quality

- **Video (mp4)** selects the best available video/audio combination and merges it to MP4 when possible.
- **Audio only (mp3)** downloads the best available audio and converts it to 192 kbps MP3 through FFmpeg.
- Quality choices limit the maximum video height when the site exposes height metadata. If an exact MP4 format is unavailable, yt-dlp uses its configured fallback formats.

## Troubleshooting

- **`ffmpeg not found`**: install FFmpeg and make sure `ffmpeg -version` works in the same terminal environment used to start the application.
- **A site returns an extractor error**: update dependencies with `pip install -U -r requirements.txt`. Site APIs and anti-bot protections can change independently of this application.
- **TikTok or similar sites reject the request**: confirm that `curl-cffi` is installed from `requirements.txt`; try the site's URL in a normal browser and configure a proxy if the site is region-restricted.

Please give it a star; that would really help me out.
