#!/bin/bash
set -e

echo "[Leo] Updating package index..."
sudo apt update

echo "[Leo] Installing system dependencies..."
sudo apt install -y \
  xdotool wmctrl x11-utils imagemagick scrot \
  ffmpeg sox portaudio19-dev pulseaudio alsa-utils \
  python3-venv python3-dev build-essential \
  libasound2-dev libportaudio2 libportaudiocpp0 \
  git curl

echo "[Leo] Creating Python virtual environment..."
python3 -m venv .venv
source .venv/bin/activate

echo "[Leo] Upgrading pip..."
pip install --upgrade pip

echo "[Leo] Installing Python dependencies..."
pip install -r requirements.txt

echo "[Leo] Environment setup complete."
echo "Activate venv with: source venv/bin/activate"
