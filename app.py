import ipaddress
import multiprocessing
import os
import re
import shutil
import signal
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

MAX_CONCURRENT_JOBS = int(os.getenv("MAX_CONCURRENT_JOBS", "2"))
MAX_ACTIVE_JOBS_PER_CLIENT = int(
    os.getenv("MAX_ACTIVE_JOBS_PER_CLIENT", "1")
)

MAX_JOB_SECONDS = int(os.getenv("MAX_JOB_SECONDS", "600"))

MAX_DOWNLOAD_SIZE = int(
    os.getenv(
        "MAX_DOWNLOAD_SIZE",
        str(256 * 1024 * 1024),
    )
)

MAX_OUTPUT_SIZE = int(
    os.getenv(
        "MAX_OUTPUT_SIZE",
        str(12 * 1024 * 1024),
    )
)

MAX_JOB_STORAGE = int(
    os.getenv(
        "MAX_JOB_STORAGE",
        str(512 * 1024 * 1024),
    )
)

MAX_GLOBAL_STORAGE = int(
    os.getenv(
        "MAX_GLOBAL_STORAGE",
        str(2 * 1024 * 1024 * 1024),
    )
)

MIN_FREE_SPACE = int(
    os.getenv(
        "MIN_FREE_SPACE",
        str(2 * 1024 * 1024 * 1024),
    )
)

MAX_VIDEO_DURATION = int(
    os.getenv("MAX_VIDEO_DURATION", "480")
)

RATE_LIMIT_REQUESTS = int(
    os.getenv("RATE_LIMIT_REQUESTS", "6")
)

RATE_LIMIT_WINDOW = int(
    os.getenv("RATE_LIMIT_WINDOW", "600")
)

MAX_REQUEST_BYTES = int(
    os.getenv("MAX_REQUEST_BYTES", "8192")
)

TRUSTED_PROXY_NETWORKS = (
    ipaddress.ip_network("127.0.0.1/32"),
)


app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_REQUEST_BYTES

DOWNLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


active_jobs = 0
active_jobs_by_client = {}
active_jobs_lock = threading.Lock()

rate_history = {}
rate_lock = threading.Lock()


def is_youtube_url(value: str) -> bool:
    try:
        parsed = urlparse(value.strip())
    except ValueError:
        return False

    if parsed.scheme not in {"http", "https"}:
        return False

    hostname = (parsed.hostname or "").lower()

    return hostname in {
        "youtube.com",
        "www.youtube.com",
        "m.youtube.com",
        "music.youtube.com",
        "youtu.be",
        "www.youtu.be",
    }


def clean_filename(name: str) -> str:
    name = re.sub(
        r'[\\/:*?"<>|]+',
        "_",
        name,
    )

    name = re.sub(
        r"\s+",
        " ",
        name,
    ).strip(" .")

    return name[:180] or "audio"


def is_trusted_proxy(address: str) -> bool:
    try:
        ip = ipaddress.ip_address(address)
    except ValueError:
        return False

    return any(
        ip in network
        for network in TRUSTED_PROXY_NETWORKS
    )


def get_client_ip() -> str:
    remote_addr = request.remote_addr or "unknown"

    if is_trusted_proxy(remote_addr):
        forwarded = request.headers.get(
            "CF-Connecting-IP",
            "",
        ).strip()

        try:
            return str(
                ipaddress.ip_address(forwarded)
            )
        except ValueError:
            pass

    return remote_addr


def directory_size(path: Path) -> int:
    total = 0

    try:
        for item in path.rglob("*"):
            try:
                if item.is_file():
                    total += item.stat().st_size
            except (
                FileNotFoundError,
                PermissionError,
                OSError,
            ):
                continue

    except (
        FileNotFoundError,
        PermissionError,
        OSError,
    ):
        pass

    return total


def global_storage_size() -> int:
    total = 0

    try:
        for job_dir in DOWNLOAD_DIR.iterdir():
            if job_dir.is_dir():
                total += directory_size(job_dir)

    except (
        FileNotFoundError,
        PermissionError,
        OSError,
    ):
        pass

    return total


def has_enough_free_space(required_bytes: int = 0) -> bool:
    try:
        usage = shutil.disk_usage(
            DOWNLOAD_DIR
        )

        return (
            usage.free - required_bytes
            >= MIN_FREE_SPACE
        )

    except (
        FileNotFoundError,
        PermissionError,
        OSError,
    ):
        return False


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
                    if (
                        now - job_dir.stat().st_mtime
                        >= CLEANUP_SECONDS
                    ):
                        shutil.rmtree(
                            job_dir,
                            ignore_errors=True,
                        )

                        app.logger.info(
                            "Deleted expired job: %s",
                            job_dir.name,
                        )

                except (
                    FileNotFoundError,
                    PermissionError,
                    OSError,
                ) as exc:
                    app.logger.warning(
                        "Cleanup failed for %s: %s",
                        job_dir,
                        exc,
                    )

        except FileNotFoundError:
            DOWNLOAD_DIR.mkdir(
                parents=True,
                exist_ok=True,
            )

        time.sleep(30)


def check_rate_limit(client_ip: str) -> bool:
    now = time.time()
    cutoff = now - RATE_LIMIT_WINDOW

    with rate_lock:
        timestamps = rate_history.setdefault(
            client_ip,
            [],
        )

        timestamps[:] = [
            timestamp
            for timestamp in timestamps
            if timestamp >= cutoff
        ]

        if len(timestamps) >= RATE_LIMIT_REQUESTS:
            return False

        timestamps.append(now)

        return True


def reserve_job(client_ip: str) -> bool:
    global active_jobs

    with active_jobs_lock:
        if active_jobs >= MAX_CONCURRENT_JOBS:
            return False

        client_jobs = active_jobs_by_client.get(
            client_ip,
            0,
        )

        if (
            client_jobs
            >= MAX_ACTIVE_JOBS_PER_CLIENT
        ):
            return False

        active_jobs += 1

        active_jobs_by_client[client_ip] = (
            client_jobs + 1
        )

        return True


def release_job(client_ip: str):
    global active_jobs

    with active_jobs_lock:
        active_jobs = max(
            0,
            active_jobs - 1,
        )

        client_jobs = active_jobs_by_client.get(
            client_ip,
            0,
        )

        if client_jobs <= 1:
            active_jobs_by_client.pop(
                client_ip,
                None,
            )
        else:
            active_jobs_by_client[client_ip] = (
                client_jobs - 1
            )


def terminate_process_tree(process):
    if not process.is_alive():
        return

    try:
        if os.name == "nt":
            process.terminate()

            process.join(timeout=3)

            if process.is_alive():
                os.system(
                    f"taskkill /PID {process.pid} "
                    "/T /F >NUL 2>&1"
                )

        else:
            try:
                os.killpg(
                    process.pid,
                    signal.SIGTERM,
                )
            except ProcessLookupError:
                pass

            process.join(timeout=3)

            if process.is_alive():
                try:
                    os.killpg(
                        process.pid,
                        signal.SIGKILL,
                    )
                except ProcessLookupError:
                    pass

    except Exception:
        app.logger.exception(
            "Failed to terminate worker process."
        )


def convert_to_mp3_worker(
    url: str,
    job_dir: str,
):
    job_path = Path(job_dir)

    if os.name != "nt":
        try:
            os.setsid()
        except Exception:
            pass

    output = str(
        job_path / "source.%(ext)s"
    )

    def progress_hook(data):
        if data.get("status") != "downloading":
            return

        downloaded = data.get(
            "downloaded_bytes",
            0,
        )

        if downloaded > MAX_DOWNLOAD_SIZE:
            raise yt_dlp.utils.DownloadError(
                "Download exceeded the configured size limit."
            )

        if (
            directory_size(job_path)
            > MAX_JOB_STORAGE
        ):
            raise yt_dlp.utils.DownloadError(
                "Job exceeded the configured storage limit."
            )

        if not has_enough_free_space():
            raise yt_dlp.utils.DownloadError(
                "Server does not have enough free disk space."
            )

    def duration_filter(
        info,
        *,
        incomplete,
    ):
        if MAX_VIDEO_DURATION <= 0:
            return None

        duration = info.get("duration")

        if (
            duration is not None
            and duration > MAX_VIDEO_DURATION
        ):
            return (
                "Video exceeds the configured "
                "duration limit."
            )

        return None

    options = {
        "format": "bestaudio/best",
        "outtmpl": output,
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "socket_timeout": 30,
        "max_filesize": MAX_DOWNLOAD_SIZE,
        "progress_hooks": [
            progress_hook
        ],
        "match_filter": duration_filter,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
        "postprocessor_args": [
            "-nostdin",
            "-fs",
            str(MAX_OUTPUT_SIZE),
        ],
    }

    with yt_dlp.YoutubeDL(options) as ydl:
        info = ydl.extract_info(
            url,
            download=True,
        )

        title = clean_filename(
            info.get(
                "title",
                "audio",
            )
        )

    mp3_files = list(
        job_path.glob("*.mp3")
    )

    if not mp3_files:
        raise RuntimeError(
            "FFmpeg did not produce an MP3 file."
        )

    mp3_path = mp3_files[0]

    if (
        mp3_path.stat().st_size
        > MAX_OUTPUT_SIZE
    ):
        raise RuntimeError(
            "Generated MP3 exceeded the "
            "configured size limit."
        )

    (job_path / ".title").write_text(
        title,
        encoding="utf-8",
    )


def convert_to_mp3(
    url: str,
    job_dir: Path,
):
    worker = multiprocessing.Process(
        target=convert_to_mp3_worker,
        args=(
            url,
            str(job_dir),
        ),
        name="yt2mp3-worker",
    )

    worker.start()

    started = time.monotonic()

    while worker.is_alive():
        worker.join(timeout=0.25)

        elapsed = (
            time.monotonic()
            - started
        )

        if elapsed > MAX_JOB_SECONDS:
            app.logger.warning(
                "Job exceeded maximum lifetime: %s",
                job_dir.name,
            )

            terminate_process_tree(worker)

            raise TimeoutError(
                "Conversion exceeded the "
                "maximum job lifetime."
            )

        if (
            directory_size(job_dir)
            > MAX_JOB_STORAGE
        ):
            app.logger.warning(
                "Job exceeded storage limit: %s",
                job_dir.name,
            )

            terminate_process_tree(worker)

            raise RuntimeError(
                "Job exceeded the "
                "configured storage limit."
            )

        if (
            global_storage_size()
            > MAX_GLOBAL_STORAGE
        ):
            app.logger.warning(
                "Global storage limit reached."
            )

            terminate_process_tree(worker)

            raise RuntimeError(
                "Server storage limit reached."
            )

        if not has_enough_free_space():
            app.logger.warning(
                "Minimum free-space threshold reached."
            )

            terminate_process_tree(worker)

            raise RuntimeError(
                "Server does not have enough "
                "free disk space."
            )

    worker.join()

    if worker.exitcode != 0:
        raise yt_dlp.utils.DownloadError(
            "Download or conversion failed."
        )

    mp3_files = list(
        job_dir.glob("*.mp3")
    )

    if not mp3_files:
        raise RuntimeError(
            "FFmpeg did not produce an MP3 file."
        )

    mp3_path = mp3_files[0]

    if (
        mp3_path.stat().st_size
        > MAX_OUTPUT_SIZE
    ):
        raise RuntimeError(
            "Generated MP3 exceeded the "
            "configured size limit."
        )

    title_path = job_dir / ".title"

    if title_path.exists():
        title = (
            title_path
            .read_text(
                encoding="utf-8"
            )
            .strip()
            or "audio"
        )
    else:
        title = "audio"

    return (
        mp3_path,
        clean_filename(title),
    )


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template(
            "index.html"
        )

    client_ip = get_client_ip()

    if not check_rate_limit(client_ip):
        return (
            render_template(
                "index.html",
                error=(
                    "Too many requests. "
                    "Try again later."
                ),
            ),
            429,
        )

    url = request.form.get(
        "url",
        "",
    ).strip()

    if not url:
        return (
            render_template(
                "index.html",
                error=(
                    "Enter a YouTube URL."
                ),
            ),
            400,
        )

    if not is_youtube_url(url):
        return (
            render_template(
                "index.html",
                error=(
                    "Enter a valid YouTube URL."
                ),
            ),
            400,
        )

    if not has_enough_free_space():
        return (
            render_template(
                "index.html",
                error=(
                    "The server does not "
                    "currently have enough "
                    "free disk space."
                ),
            ),
            503,
        )

    if (
        global_storage_size()
        > MAX_GLOBAL_STORAGE
    ):
        return (
            render_template(
                "index.html",
                error=(
                    "The server storage "
                    "limit has been reached."
                ),
            ),
            503,
        )

    if not reserve_job(client_ip):
        return (
            render_template(
                "index.html",
                error=(
                    "The server is busy. "
                    "Please try again shortly."
                ),
            ),
            429,
        )

    job_dir = (
        DOWNLOAD_DIR
        / uuid.uuid4().hex
    )

    job_dir.mkdir(
        parents=True,
        exist_ok=False,
    )

    active = job_dir / ".active"
    active.touch()

    response_created = False

    try:
        mp3_path, title = convert_to_mp3(
            url,
            job_dir,
        )

        now = time.time()

        os.utime(
            job_dir,
            (now, now),
        )

        response = send_file(
            mp3_path,
            as_attachment=True,
            download_name=f"{title}.mp3",
            mimetype="audio/mpeg",
        )

        response_created = True

        def finish_download():
            active.unlink(
                missing_ok=True
            )

            try:
                now = time.time()

                os.utime(
                    job_dir,
                    (now, now),
                )

            except (
                FileNotFoundError,
                PermissionError,
                OSError,
            ):
                pass

            release_job(client_ip)

        response.call_on_close(
            finish_download
        )

        return response

    except yt_dlp.utils.DownloadError:
        app.logger.exception(
            "yt-dlp failed"
        )

        return (
            render_template(
                "index.html",
                error=(
                    "The video could not "
                    "be downloaded."
                ),
            ),
            400,
        )

    except TimeoutError:
        app.logger.exception(
            "Conversion timed out"
        )

        return (
            render_template(
                "index.html",
                error=(
                    "Conversion took too long "
                    "and was stopped."
                ),
            ),
            413,
        )

    except Exception:
        app.logger.exception(
            "Conversion failed"
        )

        return (
            render_template(
                "index.html",
                error=(
                    "Conversion failed. "
                    "Check the server log."
                ),
            ),
            500,
        )

    finally:
        if not response_created:
            active.unlink(
                missing_ok=True
            )

            release_job(client_ip)


if __name__ == "__main__":
    threading.Thread(
        target=cleanup_old_files,
        daemon=True,
        name="download-cleanup",
    ).start()

    app.run(
        host=HOST,
        port=PORT,
    )
