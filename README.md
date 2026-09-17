# YT2MP3

A simple Flask web application that converts YouTube videos to MP3 files using yt-dlp and FFmpeg.

## Requirements

* Linux
* Python 3
* FFmpeg
* A YouTube URL

## Installation

### Option 1: Clone with Git

Clone the repository:

```bash
git clone https://github.com/nxs8739/yt2mp3.git
cd yt2mp3
```

### Option 2: Download a Release

Download the latest release ZIP from the **Releases** section and extract it.

GitHub will create a directory based on the release version, such as:

```text
yt2mp3-1.0/
```

Open a terminal inside the extracted project directory.

**All remaining installation commands should be run from inside the project directory.**

### Install FFmpeg

On Debian/Ubuntu-based systems:

```bash
sudo apt update
sudo apt install ffmpeg
```

### Set Up Python

Create the virtual environment **inside the project directory**:

```bash
python3 -m venv venv
```

Activate it:

```bash
source venv/bin/activate
```

Install the required Python packages:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Make the Launcher Executable

Still inside the project directory:

```bash
chmod +x start.sh
```

## Run

Start YT2MP3 from the project directory:

```bash
./start.sh
```

The launcher automatically detects a supported terminal emulator, activates the virtual environment, and starts the application.

Then open:

```text
http://127.0.0.1:5001
```

Enter a YouTube URL and click **Convert**.

## Temporary Files

Converted MP3 files are stored temporarily in the `downloads/` directory.

Files are automatically deleted after 10 minutes.

## Limitations

* YouTube URLs only
* MP3 output at 192 kbps
* FFmpeg must be installed separately
* Requires Python 3
* Designed for local/self-hosted use

## Third-Party Software

YT2MP3 uses the following third-party software:

* [yt-dlp](https://github.com/yt-dlp/yt-dlp) — Unlicense
* [FFmpeg](https://ffmpeg.org/) — LGPL/GPL, depending on the build

These projects are separate from YT2MP3 and remain under their respective licenses.

## License

YT2MP3 is licensed under the [GNU Affero General Public License v3.0](https://github.com/nxs8739/yt2mp3/blob/main/LICENSE).
