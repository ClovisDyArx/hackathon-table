#!/bin/bash

# Install audio dependencies for voice synthesis
echo "Installing audio dependencies..."

# Update package list
sudo apt update

# Install ffmpeg (includes ffprobe)
sudo apt install -y ffmpeg

# Install additional audio libraries
sudo apt install -y libasound2-dev portaudio19-dev

echo "Audio dependencies installed successfully!"
echo "You may need to restart your application for changes to take effect."
