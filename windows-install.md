# YT2MP3 — Windows Installation

This guide explains how to install and run YT2MP3 on Windows.

YT2MP3 is a Python/Flask application. The application itself does not require Linux, but the included start.sh launcher is intended for Linux desktop environments.

On Windows, run the application directly with Python.

## Requirements

* Windows
* Python 3
* FFmpeg
* Git (optional)
* Internet connection

1. Install Python

---

Install Python using the current Python installer/manager from:

https://www.python.org/downloads/

After installation, open PowerShell and verify Python:

```
python --version
```

## 2. Install FFmpeg

YT2MP3 requires FFmpeg for MP3 conversion.

Install a Windows build of FFmpeg and make sure the FFmpeg executable is available in your system PATH.

Verify the installation from PowerShell:

```
ffmpeg -version
```

If Windows cannot find the `ffmpeg` command, FFmpeg is either not installed or its location has not been added to PATH.

3. Get YT2MP3

---

Using Git:

```
git clone https://github.com/nxs8739/yt2mp3.git
cd yt2mp3
```

Or download the project ZIP from GitHub and open PowerShell inside the extracted project directory.

4. Create the Python Virtual Environment

---

From inside the YT2MP3 project directory:

```
python -m venv venv
```

## 5. Activate the Virtual Environment

If using PowerShell:

```
.\venv\Scripts\Activate.ps1
```

If using Command Prompt instead:

```
venv\Scripts\activate.bat
```

After activation, the terminal should show `(venv)` before the command prompt.

6. Install Python Dependencies

---

Run:

```
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## 7. Start YT2MP3

From the project directory, with the virtual environment activated:

```
python app.py
```

The application will start on:

```
http://127.0.0.1:5001
```

Open that address in your web browser.

8. Using YT2MP3

---

Enter a YouTube URL and click Convert.

The converted MP3 file will be downloaded by the browser.

Temporary files are automatically deleted by the application after 10 minutes.

## Notes

* `start.sh` is not used on Windows.
* The Windows installation uses the same Python virtual-environment and requirements.txt system as the Linux installation.
* FFmpeg must be installed separately because it is a system dependency, not a Python package.
* The `venv/` directory is created locally and is not included in the GitHub repository.
* If PowerShell prevents the virtual-environment activation script from running, use Command Prompt instead or adjust your PowerShell execution-policy settings according to your Windows configuration.

For the Linux installation, see README.md.
