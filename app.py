import os
import re
import shutil
import threading
import time
import uuid
from pathlib import Path
from urllib.parse import urlparse

from flask import Flask, render_template, request, send_file
import yt_dlp

BASE_DIR = Path(__file__).resolve().parent
DOWNLOAD_DIR = BASE_DIR / "downloads"
CLEANUP_SECONDS = int(os.getenv("CLEANUP_SECONDS", "600"))
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "5001"))

app = Flask(__name__)
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)


def is_youtube_url(value: str) -> bool:
    try:
        parsed = urlparse(value.strip())
    except ValueError:
        return False
    if parsed.scheme not in {"http", "https"}:
        return False
    hostname = (parsed.hostname or "").lower()
    return hostname in {
        "youtube.com", "www.youtube.com", "m.youtube.com",
        "music.youtube.com", "youtu.be", "www.youtu.be",
    }


def clean_filename(name: str) -> str:
    name = re.sub(r'[\\/:*?"<>|]+', "_", name)
    name = re.sub(r"\s+", " ", name).strip(" .")
    return name[:180] or "audio"


def cleanup_old_files():
    while True:
        now = time.time()
        try:
            for job_dir in DOWNLOAD_DIR.iterdir():
                if not job_dir.is_dir():
                    continue
                if (job_dir / ".active").exists():
                    continue
                try:
                    if now - job_dir.stat().st_mtime >= CLEANUP_SECONDS:
                        shutil.rmtree(job_dir, ignore_errors=True)
                        app.logger.info("Deleted expired job: %s", job_dir.name)
                except (FileNotFoundError, PermissionError, OSError) as exc:
                    app.logger.warning("Cleanup failed for %s: %s", job_dir, exc)
        except FileNotFoundError:
            DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
        time.sleep(30)


def convert_to_mp3(url: str, job_dir: Path):
    output = str(job_dir / "source.%(ext)s")
    options = {
        "format": "bestaudio/best",
        "outtmpl": output,
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
    }
    with yt_dlp.YoutubeDL(options) as ydl:
        info = ydl.extract_info(url, download=True)
        title = clean_filename(info.get("title", "audio"))
    mp3_files = list(job_dir.glob("*.mp3"))
    if not mp3_files:
        raise RuntimeError("FFmpeg did not produce an MP3 file.")
    return mp3_files[0], title


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("index.html")

    url = request.form.get("url", "").strip()
    if not url:
        return render_template("index.html", error="Enter a YouTube URL.")
    if not is_youtube_url(url):
        return render_template("index.html", error="Enter a valid YouTube URL.")

    job_dir = DOWNLOAD_DIR / uuid.uuid4().hex
    job_dir.mkdir(parents=True)
    active = job_dir / ".active"
    active.touch()

    try:
        mp3_path, title = convert_to_mp3(url, job_dir)
        active.unlink(missing_ok=True)
        now = time.time()
        os.utime(job_dir, (now, now))
        return send_file(
            mp3_path,
            as_attachment=True,
            download_name=f"{title}.mp3",
            mimetype="audio/mpeg",
        )
    except yt_dlp.utils.DownloadError:
        app.logger.exception("yt-dlp failed")
        return render_template("index.html", error="The video could not be downloaded."), 400
    except Exception:
        app.logger.exception("Conversion failed")
        return render_template("index.html", error="Conversion failed. Check the server log."), 500
    finally:
        active.unlink(missing_ok=True)


if __name__ == "__main__":
    threading.Thread(target=cleanup_old_files, daemon=True, name="download-cleanup").start()
    app.run(host=HOST, port=PORT)
