# YT2MP3

A simple self-hosted YouTube-to-MP3 converter built with Flask, yt-dlp, and FFmpeg.

YT2MP3 is designed for small local or self-hosted deployments. It does not require a database, job queue, or other external services.

## Features

* Convert YouTube videos to MP3
* 192 kbps MP3 output
* Uses yt-dlp for downloading
* Uses FFmpeg for audio conversion
* Simple Flask web interface
* Automatic temporary-file cleanup
* Unique per-job directories
* Resource and storage limits
* Request rate limiting
* Concurrent-job limits
* Cloudflare Tunnel client IP support
* No database required

## Requirements

* Python 3
* FFmpeg
* Git (if cloning the repository)
* Internet access

Ubuntu/Debian:

```bash
sudo apt update
sudo apt install python3 python3-venv ffmpeg git
```

## Installation

### Option 1: Clone with Git

```bash
git clone https://github.com/nxs8739/yt2mp3.git
cd yt2mp3
```

### Option 2: Download a Release

You can download YT2MP3 without using Git.

Open the project's **Releases** page on GitHub and download the latest release.

Under **Assets**, GitHub provides:

* **Source code (zip)**
* **Source code (tar.gz)**

For example, a v1.1 release download extracts into a directory named:

```text
yt2mp3-1.1/
```

A v1.2 release will similarly use:

```text
yt2mp3-1.2/
```

After extracting the archive, open a terminal inside the extracted project directory.

The directory should contain files such as:

```text
app.py
requirements.txt
start.sh
templates/
```

The remaining installation commands below should be run from this directory.

## Python Virtual Environment

Create a virtual environment:

```bash
python3 -m venv venv
```

Activate it:

```bash
source venv/bin/activate
```

Upgrade pip:

```bash
python -m pip install --upgrade pip
```

Install yt-dlp into the project's virtual environment:

```bash
python -m pip install --upgrade yt-dlp
```

Install the remaining dependencies:

```bash
python -m pip install -r requirements.txt
```

### Why install yt-dlp separately?

Ubuntu and Debian repositories can provide an older version of yt-dlp.

YT2MP3 installs yt-dlp directly into the project's Python virtual environment so the application does not depend on the version supplied by the operating system's package repository.

A separate user-level installation is also possible:

```bash
python3 -m pip install --user --upgrade yt-dlp
```

This is optional. The application uses the copy installed inside its virtual environment.

## Starting YT2MP3

Make the launcher executable:

```bash
chmod +x start.sh
```

Then run:

```bash
./start.sh
```

The application listens on:

```text
http://127.0.0.1:5001
```

You can also start it directly:

```bash
source venv/bin/activate
python app.py
```

By default, Flask listens only on `127.0.0.1`.

The host and port can be changed using environment variables:

```bash
HOST=127.0.0.1 PORT=5001 python app.py
```

## Job Lifecycle

Each conversion receives its own randomly generated job directory inside `downloads/`.

While a conversion is running, the job contains an `.active` marker.

```text
downloads/
└── <job-id>/
    ├── .active
    └── source.<format>
```

`.active` now represents **conversion in progress only**.

When conversion successfully finishes:

1. The MP3 is prepared for download.
2. The download response is created.
3. `.active` is removed immediately.
4. The job is considered completed.
5. The completed job directory is automatically deleted after 2 minutes.

YT2MP3 does not wait for the browser to report that the file has completely finished downloading.

### Active Jobs

Active jobs have a maximum lifetime of 10 minutes.

If a conversion exceeds this limit, the worker process is terminated and the job is eventually removed by the cleanup system.

### Completed Jobs

Completed jobs are retained for 2 minutes before automatic cleanup.

The cleanup process runs periodically, so actual deletion may occur slightly after the configured interval.

## Resource Limits

YT2MP3 includes multiple resource controls intended to prevent excessive consumption of server resources.

Default limits:

| Limit                          |                 Default |
| ------------------------------ | ----------------------: |
| Maximum video duration         |               8 minutes |
| Maximum source download        |                 256 MiB |
| Maximum MP3 output             |                  12 MiB |
| Maximum individual job storage |                 512 MiB |
| Maximum total storage          |                   2 GiB |
| Minimum free disk space        |                   2 GiB |
| Maximum job lifetime           |              10 minutes |
| Maximum concurrent jobs        |                       2 |
| Maximum active jobs per client |                       1 |
| Request rate                   | 6 requests / 10 minutes |
| Maximum request body           |              8192 bytes |
| Completed-job cleanup          |               2 minutes |
| Active-job cleanup ceiling     |              10 minutes |

These limits can be changed using environment variables.

## Security & Abuse Protection

YT2MP3 uses several layers of protection against excessive resource consumption from conversion requests.

These include:

* YouTube hostname allowlisting
* Playlist downloads disabled
* Per-client request rate limiting
* Per-client active-job limits
* Concurrent-job limits
* Maximum video duration
* Maximum source download size
* Maximum MP3 output size
* Maximum per-job storage
* Maximum global storage
* Minimum free-disk-space protection
* Maximum job lifetime
* Download progress monitoring
* Storage monitoring
* Automatic worker termination when limits are exceeded
* Child-process termination
* Unique per-job directories
* Sanitized filenames
* Request body-size limiting

## Cloudflare Tunnel

YT2MP3 can be placed behind a Cloudflare Tunnel.

When Flask receives a connection from the trusted local tunnel endpoint, the application can use Cloudflare's `CF-Connecting-IP` header to identify the original client.

The header is only trusted when the immediate connection comes from the configured trusted proxy address.

Direct clients cannot spoof the Cloudflare client IP header.

The default trusted proxy network is:

```text
127.0.0.1/32
```

If the Cloudflare header is missing or invalid, YT2MP3 falls back to the direct connection address.

## Temporary Files

Temporary conversion files are stored under:

```text
downloads/
```

Each conversion uses a unique directory.

Completed job directories are automatically removed after 2 minutes.

Active jobs are protected from normal completed-job cleanup while conversion is running, but cannot remain active indefinitely because of the 10-minute maximum job lifetime.

No database or persistent conversion history is used.

## Limitations

YT2MP3 currently:

* Supports YouTube URLs only
* Does not support playlists
* Produces MP3 audio
* Produces 192 kbps MP3 files
* Limits videos to 8 minutes by default
* Uses temporary local storage
* Does not provide user accounts
* Does not provide persistent conversion history
* Does not track whether a browser has completely finished downloading a file

YT2MP3 is intended for small local or self-hosted deployments rather than large public conversion services.

## Dependencies

YT2MP3 uses:

* Flask
* yt-dlp
* FFmpeg

yt-dlp handles media downloading and FFmpeg performs the audio conversion.

## Upgrading

When upgrading from an earlier release, update the application files and dependencies.

Activate the virtual environment:

```bash
source venv/bin/activate
```

Update yt-dlp:

```bash
python -m pip install --upgrade yt-dlp
```

Update the Python dependencies:

```bash
python -m pip install -r requirements.txt
```

No database migration or other persistent-data migration is required.

## License

YT2MP3 is licensed under the **GNU Affero General Public License v3.0**.

[View the AGPL-3.0 License](https://github.com/nxs8739/yt2mp3/blob/main/LICENSE)
