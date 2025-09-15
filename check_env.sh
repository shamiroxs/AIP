#!/bin/bash
set -e

echo "[Leo] Checking environment..."

echo "Python version:"
python3 --version

echo "Virtualenv Python version:"
./.venv/bin/python --version || echo "No venv yet."

echo "Checking X11 DISPLAY:"
echo "DISPLAY=$DISPLAY"
echo "XDG_SESSION_TYPE=$XDG_SESSION_TYPE"

echo "Checking active window (may be empty if no X11 app open):"
xdotool getactivewindow getwindowname || echo "No active window detected."

echo "Listing windows with wmctrl:"
wmctrl -l || echo "No windows detected."

echo "Checking audio devices:"
arecord -l || echo "No audio devices found."

echo "Checking ffmpeg presence:"
ffmpeg -version | head -n 1

echo "[Leo] Environment check complete."
