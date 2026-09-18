# YT2MP3

A small, self-hosted Flask application for converting YouTube videos to MP3 using `yt-dlp` and FFmpeg.

YT2MP3 is designed for simple local or self-hosted deployment without a database, job queue, or other external services.

## Features

* Convert YouTube videos to MP3
* 192 kbps MP3 output
* Uses `yt-dlp` for downloading
* Uses FFmpeg for audio conversion
* Simple Flask web interface
* Automatic temporary-file cleanup
* Per-job directory isolation
* Resource and storage limits
* Request rate limiting
* Concurrent-job limits
* Cloudflare Tunnel client-IP support
* No database required

## Requirements

* Linux recommended
* Python 3
* FFmpeg
* `git` (if cloning the repository)
* Internet access

Ubuntu/Debian:

```bash
sudo apt update
sudo apt install python3 python3-venv ffmpeg git
```

## Installation

Clone the repository:

```bash
git clone https://github.com/nxs8739/yt2mp3.git
cd yt2mp3
```

Create a Python virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

Upgrade pip:

```bash
python -m pip install --upgrade pip
```

Install the current `yt-dlp` release into the virtual environment:

```bash
python -m pip install --upgrade yt-dlp
```

Install the remaining Python dependencies:

```bash
python -m pip install -r requirements.txt
```

### Why install yt-dlp separately?

Ubuntu and Debian repositories can provide an older version of `yt-dlp`.

YT2MP3 therefore installs `yt-dlp` directly into its Python virtual environment so the application uses the current Python package rather than relying on the operating system's packaged version.

If your system uses an externally managed Python environment, the virtual environment installation above avoids modifying the system Python installation.

A separate user-level installation is also possible if desired:

```bash
python3 -m pip install --user --upgrade yt-dlp
```

The application itself still uses the copy installed inside `venv`.

## Running YT2MP3

Activate the virtual environment:

```bash
source venv/bin/activate
```

Run the application:

```bash
python app.py
```

By default, YT2MP3 listens on:

```text
127.0.0.1:5001
```

The host and port can be changed with environment variables:

```bash
HOST=127.0.0.1 PORT=5001 python app.py
```

### start.sh

The included `start.sh` launcher can also be used:

```bash
./start.sh
```

The launcher is intended to make starting the application convenient on systems with a terminal.

## Job Lifecycle

Each conversion receives its own randomly generated job directory.

While conversion is running:

```text
downloads/<job-id>/
├── .active
└── source.<format>
```

The `.active` file indicates that the conversion is currently in progress.

Once conversion finishes successfully:

1. The MP3 is prepared for download.
2. The download response is created.
3. `.active` is removed immediately.
4. The job is considered completed.
5. The completed job directory is automatically deleted after 2 minutes.

The application does not wait for the browser to finish receiving the file before marking the job completed.

### Stuck or abandoned jobs

An active job cannot remain indefinitely.

Active jobs have a maximum lifetime of 10 minutes. Jobs that exceed this limit are terminated and eventually removed by the cleanup process.

The cleanup thread runs periodically, so deletion can occur slightly after the configured interval.

## Resource Limits

YT2MP3 includes multiple safeguards against excessive resource consumption.

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

These values can be overridden with environment variables.

For example:

```bash
MAX_CONCURRENT_JOBS=4 python app.py
```

## Security and Abuse Protection

YT2MP3 is intended to remain lightweight while providing several layers of protection against excessive resource consumption.

Protection includes:

* YouTube hostname allowlisting
* Playlist downloads disabled
* Per-client request rate limiting
* Per-client active-job limits
* Global concurrency limits
* Maximum video duration
* Maximum download size
* Maximum output size
* Maximum per-job storage
* Maximum global storage
* Minimum free-disk-space protection
* Maximum processing time
* Download progress monitoring
* Job storage monitoring
* Automatic worker termination when limits are exceeded
* Child-process termination
* Random per-job directories
* Sanitized output filenames
* HTTP request-size limiting

## Cloudflare Tunnel

YT2MP3 can run behind Cloudflare Tunnel.

When the direct connection to Flask comes from the trusted local tunnel endpoint, the application can use the `CF-Connecting-IP` header to identify the original client.

Direct clients cannot spoof this header because it is only trusted when the immediate connection comes from the configured trusted proxy address.

By default, the trusted proxy is:

```text
127.0.0.1/32
```

If the Cloudflare header is missing or invalid, the application falls back to the direct peer address.

## Storage

Temporary conversion files are stored under:

```text
downloads/
```

Each conversion receives a unique directory.

Completed jobs are automatically removed after the configured post-download cleanup interval.

The default cleanup interval for completed jobs is:

```text
120 seconds
```

Active jobs have a separate hard cleanup ceiling of:

```text
600 seconds
```

No database or persistent job storage is used.

## Limitations

YT2MP3 currently:

* Supports YouTube URLs only
* Produces MP3 audio
* Produces 192 kbps MP3 files
* Does not support playlists
* Limits videos to 8 minutes by default
* Uses local temporary storage
* Does not provide user accounts
* Does not provide persistent conversion history
* Does not determine whether a browser has completely finished downloading a file

The application is intended for small, self-hosted deployments rather than large public conversion services.

## Third-Party Software

YT2MP3 relies on:

* Flask
* yt-dlp
* FFmpeg

`yt-dlp` handles media retrieval while FFmpeg performs the audio conversion.

## Upgrading

From v1.1, update the application files and dependencies as needed.

If using the existing virtual environment:

```bash
source venv/bin/activate
python -m pip install --upgrade pip
python -m pip install --upgrade yt-dlp
python -m pip install -r requirements.txt
```

No database migration or persistent-data migration is required.

## License

YT2MP3 is licensed under the **GNU Affero General Public License v3.0**.

[View the AGPL-3.0 License](https://github.com/nxs8739/yt2mp3/blob/main/LICENSE)
