#!/bin/bash

cd "$(dirname "$0")"

if command -v konsole >/dev/null 2>&1; then
    konsole --hold -e bash -c 'source venv/bin/activate && python app.py'
elif command -v gnome-terminal >/dev/null 2>&1; then
    gnome-terminal -- bash -c 'source venv/bin/activate && python app.py; exec bash'
elif command -v xfce4-terminal >/dev/null 2>&1; then
    xfce4-terminal --hold -e 'bash -c "source venv/bin/activate && python app.py; exec bash"'
elif command -v mate-terminal >/dev/null 2>&1; then
    mate-terminal -- bash -c 'source venv/bin/activate && python app.py; exec bash'
elif command -v xterm >/dev/null 2>&1; then
    xterm -hold -e bash -c 'source venv/bin/activate && python app.py'
else
    echo "No supported terminal emulator was found."
    echo
    echo "Run the application manually with:"
    echo "  source venv/bin/activate"
    echo "  python app.py"
    exit 1
fi
