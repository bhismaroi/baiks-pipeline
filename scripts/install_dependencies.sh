#!/bin/bash
# Install system dependencies
sudo apt update
sudo apt install -y docker.io docker-compose python3-pip

# Install Python dependencies
pip install --user -r requirements.txt