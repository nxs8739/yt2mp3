# YT2MP3

A simple Flask web application that converts YouTube videos to MP3 files using yt-dlp and FFmpeg.

## Platform

YT2MP3 is designed around a **local Ubuntu/Debian desktop environment**.

This README and the included `start.sh` launcher are specifically tailored for Ubuntu/Debian-based Linux systems with a graphical desktop and terminal emulator.

The Flask application itself does **not** require a graphical interface and can be run manually on a headless system. However, configuring YT2MP3 as a persistent service or headless application is outside the scope of this project.

The application may also be adaptable to other Linux distributions or Windows. Supporting those platforms is outside the scope of this project. If you want to adapt YT2MP3 for another environment, you can modify the installation instructions and `start.sh` to suit your system.

## Requirements

* Ubuntu/Debian-based Linux
* Graphical desktop environment
* Terminal emulator
* Python 3
* pip
* Python virtual environment support
* FFmpeg
* A YouTube URL

## Installation

### Option 1: Clone with Git

Clone the repository:

```bash id="9gqv20"
git clone https://github.com/nxs8739/yt2mp3.git
cd yt2mp3
```

### Option 2: Download a Release

Download the latest release ZIP from the **Releases** section and extract it.

GitHub will create a directory based on the release version, such as:

```text id="6a7n2r"
yt2mp3-1.0/
```

Open a terminal inside the extracted project directory.

**All remaining installation commands should be run from inside the project directory.**

### Install Python and Required System Packages

On Ubuntu/Debian-based systems:

```bash id="jz3q6v"
sudo apt update
sudo apt install python3 python3-pip python3-venv ffmpeg
```

This installs Python 3, pip, virtual environment support, and FFmpeg.

### Set Up Python

From inside the project directory, create the virtual environment:

```bash id="r4w8a1"
python3 -m venv venv
```

Activate it:

```bash id="h5n9s2"
source venv/bin/activate
```

Install the required Python packages:

```bash id="k3d7q6"
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Make the Launcher Executable

Still inside the project directory:

```bash id="p8x1m4"
chmod +x start.sh
```

## Run

Start YT2MP3 from the project directory:

```bash id="v6c2z9"
./start.sh
```

The launcher automatically detects a supported terminal emulator, activates the virtual environment, and starts the application.

Then open:

```text id="e3n7w5"
http://127.0.0.1:5001
```

Enter a YouTube URL and click **Convert**.

## Headless / Manual Run

The included `start.sh` launcher is intended for desktop environments with a graphical terminal emulator.

If running YT2MP3 on a headless system, the application can be started manually from the project directory:

```bash id="t2f8k1"
source venv/bin/activate
python app.py
```

Configuring YT2MP3 to run automatically as a system service is outside the scope of this project.

## Temporary Files

Converted MP3 files are stored temporarily in the `downloads/` directory.

Files are automatically deleted after 10 minutes.

## Limitations

* YouTube URLs only
* MP3 output at 192 kbps
* Installation instructions are tailored for Ubuntu/Debian-based systems
* The included launcher is designed for graphical desktop environments
* Windows and other Linux distributions are not officially supported by this project
* The included `start.sh` may need to be modified for other environments
* Requires Python 3, pip, virtual environment support, and FFmpeg
* Designed primarily for local/self-hosted desktop use

## Third-Party Software

YT2MP3 uses the following third-party software:

* [yt-dlp](https://github.com/yt-dlp/yt-dlp) — Unlicense
* [FFmpeg](https://ffmpeg.org/) — LGPL/GPL, depending on the build

These projects are separate from YT2MP3 and remain under their respective licenses.

## License

YT2MP3 is licensed under the [GNU Affero General Public License v3.0](https://github.com/nxs8739/yt2mp3/blob/main/LICENSE).

