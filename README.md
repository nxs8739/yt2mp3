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

## Platform

YT2MP3 is designed primarily around a local Ubuntu/Debian desktop environment.

The README and included `start.sh` launcher are specifically tailored for Ubuntu/Debian-based Linux systems with a graphical desktop and terminal emulator.

The Flask application itself does not require a graphical interface and can be run manually on a headless Linux system. However, configuring YT2MP3 as a persistent system service or other automatic headless deployment is outside the scope of this project.

YT2MP3 may also be adaptable to other Linux distributions or Windows, but those platforms are not officially supported by this project.

If adapting YT2MP3 for another environment, the installation instructions and `start.sh` may need to be modified accordingly.

## Requirements

For the standard desktop setup:

* Ubuntu/Debian-based Linux
* Graphical desktop environment
* Terminal emulator
* Python 3
* Python virtual environment support
* pip
* FFmpeg
* Git (if cloning the repository)
* Internet access
* A YouTube URL

Ubuntu/Debian:

```bash
sudo apt update
sudo apt install python3 python3-venv ffmpeg git
```

This installs Python 3, virtual environment support, FFmpeg, and Git.

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

All remaining installation commands should be run from inside this project directory.

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

Install the remaining Python dependencies:

```bash
python -m pip install -r requirements.txt
```

### Why install yt-dlp separately?

Ubuntu and Debian repositories can provide an older version of yt-dlp.

YT2MP3 installs yt-dlp directly into the project's Python virtual environment so the application does not depend on the version supplied by the operating system's package repository.

Verify the version being used by the virtual environment:

```bash
python -m yt_dlp --version
```

This is the yt-dlp installation that YT2MP3 uses.

### Optional: Install yt-dlp for Your User

The virtual-environment installation above is all YT2MP3 requires.

If you also want to use the current yt-dlp directly from your terminal outside YT2MP3, you can optionally install it for your Linux user:

```bash
python3 -m pip install --user --upgrade yt-dlp
```

The `--user` option installs yt-dlp into your personal user environment rather than modifying the system-wide Python installation.

It normally places the executable under:

```text
~/.local/bin/yt-dlp
```

Verify it with:

```bash
~/.local/bin/yt-dlp --version
```

You can also try:

```bash
yt-dlp --version
```

If the command is not found without the full path, `~/.local/bin` may not be included in your `PATH`.

### Ubuntu/Debian pip Restrictions

Some newer Ubuntu/Debian releases protect the system Python environment using the externally managed environment mechanism.

On those systems, the optional `--user` installation may be rejected with an error similar to:

```text
error: externally-managed-environment
```

This protection prevents pip from unintentionally modifying packages managed by the operating system.

Do not use `--break-system-packages` simply to bypass this error unless you understand the consequences.

The optional system/user installation is not required by YT2MP3. If your distribution rejects it, simply skip this optional step.

The yt-dlp installation inside the YT2MP3 virtual environment is isolated from the system Python and is the version used by the application.

## Desktop Usage

The included `start.sh` launcher is intended for graphical Linux desktop environments.

Make the launcher executable:

```bash
chmod +x start.sh
```

Start YT2MP3 from the project directory:

```bash
./start.sh
```

The launcher automatically detects a supported terminal emulator, activates the project's Python virtual environment, and starts the Flask application.

Once started, open:

```text
http://127.0.0.1:5001
```

Enter a YouTube URL and click **Convert**.

By default, Flask listens only on `127.0.0.1`, meaning the application is available only from the local computer unless its network configuration is intentionally changed.

### Starting YT2MP3 Again After Quitting

The Python virtual environment is only active for the terminal session in which it was activated.

If you close the YT2MP3 terminal or stop the application, the virtual environment is no longer active in a new terminal session.

If you use the launcher, simply run:

```bash
./start.sh
```

again.

`start.sh` handles activation automatically.

If you start the application manually instead, you must activate the virtual environment before starting YT2MP3:

```bash
source venv/bin/activate
python app.py
```

The important part is:

```bash
source venv/bin/activate
```

Run that command from inside the YT2MP3 project directory before manually starting the application.

You can tell that the virtual environment is active when the terminal prompt normally shows `(venv)`.

For example:

```text
(venv) user@computer:~/yt2mp3$
```

Once the environment is activated, use:

```bash
python app.py
```

Do not rely on a system-installed yt-dlp when manually starting YT2MP3. The application is intended to use the packages installed inside its project virtual environment.

### Stopping YT2MP3

If YT2MP3 is running in a terminal, press:

```text
Ctrl+C
```

This stops the Flask application.

The terminal can then be closed.

When you want to use YT2MP3 again later, start it with:

```bash
./start.sh
```

or manually reactivate the environment and run:

```bash
source venv/bin/activate
python app.py
```

No separate activation or permanent system installation is required between sessions.

## Manual / Headless Run

The included `start.sh` launcher is intended for desktop environments with a graphical terminal emulator.

The Flask application itself does not require a graphical interface.

On a headless Linux system, YT2MP3 can be started manually from the project directory:

```bash
source venv/bin/activate
python app.py
```

The application will listen on:

```text
127.0.0.1:5001
```

By default.

The host and port can be changed using environment variables:

```bash
HOST=127.0.0.1 PORT=5001 python app.py
```

For example, a headless server may intentionally bind Flask to another interface if remote access is required.

Configuring YT2MP3 to run automatically as a system service, through systemd, Docker, or another persistent service manager is outside the scope of this project.

## Job Lifecycle

Each conversion receives its own randomly generated job directory inside `downloads/`.

While a conversion is running, the job contains an `.active` marker.

```text
downloads/
└── <job-id>/
    ├── .active
    └── source.<format>
```

`.active` represents **conversion in progress only**.

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
* Is primarily documented for Ubuntu/Debian-based Linux systems
* Includes a launcher designed for graphical desktop environments
* Is not officially supported on Windows or other Linux distributions

YT2MP3 is intended for small local or self-hosted deployments rather than large public conversion services.

## Dependencies

YT2MP3 uses:

* Flask
* yt-dlp
* FFmpeg

Flask provides the web application framework.

yt-dlp handles media downloading.

FFmpeg performs the audio conversion.

These dependencies remain separate from YT2MP3 and are installed through the appropriate system package manager or Python virtual environment.

## Upgrading

When upgrading from an earlier release, update the application files and dependencies.

From inside the YT2MP3 project directory, activate the virtual environment:

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

After upgrading, YT2MP3 can be started normally:

```bash
./start.sh
```

Or manually:

```bash
source venv/bin/activate
python app.py
```

## License

YT2MP3 is licensed under the **GNU Affero General Public License v3.0**.

[View the AGPL-3.0 License](https://github.com/nxs8739/yt2mp3/blob/main/LICENSE)
