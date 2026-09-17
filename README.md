# YouTube → MP3 Flask Converter

Small Flask app using yt-dlp for the source download and FFmpeg for MP3 conversion.

## Requirements

- Python 3
- FFmpeg installed and available in PATH

Ubuntu/Kubuntu:

```bash
sudo apt update
sudo apt install ffmpeg
```

## Install and run

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5001`.

The server listens on `127.0.0.1:5001` by default, so another LAN device can't connect to the host's LAN IP.

## Cleanup

Completed job directories are deleted after 10 minutes. Cleanup checks every 30 seconds.

Change the retention time with an environment variable, for example 30 minutes:

```bash
CLEANUP_SECONDS=1800 python app.py
```

Use only for content you are authorized to download.
