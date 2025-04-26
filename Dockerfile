# Use an official Python runtime as a parent image, choosing one that includes Node.js
# Check Docker Hub for suitable tags (e.g., python:3.9-slim-bullseye might need Node installed)
# Or use a Node image and install Python. Let's try a Node base and add Python.
FROM node:18-slim

# Install Python, pip, and venv
# 'apt-get update && apt-get install -y --no-install-recommends' is standard practice
# 'rm -rf /var/lib/apt/lists/*' cleans up afterward to keep image size down
# Install Python, pip, venv, and Puppeteer dependencies
# See: https://pptr.dev/troubleshooting#running-puppeteer-on-debian
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
    # Puppeteer dependencies:
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcairo2 \
    libcups2 \
    libdbus-1-3 \
    libexpat1 \
    libfontconfig1 \
    libgbm1 \
    libgcc1 \
    libglib2.0-0 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libstdc++6 \
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    libxrandr2 \
    libxrender1 \
    libxss1 \
    libxtst6 \
    lsb-release \
    wget \
    xdg-utils \
    && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Install mermaid-cli globally
# Use --unsafe-perm if needed for permissions during global install
RUN npm install -g @mermaid-js/mermaid-cli --unsafe-perm=true

# Copy the requirements file first to leverage Docker cache
COPY requirements.txt ./

# Create a virtual environment and install Python dependencies
# This isolates Python packages within the container, similar to local setup
RUN python3 -m venv /app/venv
# Activate venv for the RUN command and install packages
RUN . /app/venv/bin/activate && pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Make port 5001 available to the world outside this container
# This should match the port Flask runs on in app.py (or Gunicorn config)
EXPOSE 5001

# Define environment variables
# IMPORTANT: Set a strong FLASK_SECRET_KEY when running the container!
# Using a placeholder here for demonstration.
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5001
ENV FLASK_SECRET_KEY="replace_this_in_docker_run_with_a_real_secret"
# Add venv's bin to the PATH for subsequent commands (like CMD)
ENV PATH="/app/venv/bin:$PATH"

# Override base image entrypoint so CMD executes directly
ENTRYPOINT []

# Run the application using Gunicorn when the container launches
# Use the full path to gunicorn within the virtual environment
# Bind to 0.0.0.0 to accept connections from outside the container
# Use the port defined by FLASK_RUN_PORT
# The number of workers (e.g., --workers 3) can be adjusted based on server resources
# Use JSON form with the absolute path to gunicorn in the venv to avoid PATH issues
CMD ["/app/venv/bin/gunicorn", "--workers", "3", "--bind", "0.0.0.0:5001", "app:app"]
