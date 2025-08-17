---
title: Mermaid Rendering Docker
emoji: 🔥
colorFrom: purple
colorTo: red
sdk: docker
app_port: 7860
pinned: false
license: mit
short_description: mermaid-rendering docker version
---

Check out the configuration reference at https://huggingface.co/docs/hub/spaces-config-reference

# Mermaid Live Renderer Web Application

This Flask application provides a web interface for rendering diagrams from [Mermaid](https://mermaid.js.org/) syntax code. It features a live preview that updates as you type and allows downloading the final diagram as PNG, SVG, or PDF.

![Application Screenshot](https://private-user-images.githubusercontent.com/1627206/478743597-f34ee17b-ccd7-4de2-87d8-7190bd22bc5b.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NTU0MDg4MjEsIm5iZiI6MTc1NTQwODUyMSwicGF0aCI6Ii8xNjI3MjA2LzQ3ODc0MzU5Ny1mMzRlZTE3Yi1jY2Q3LTRkZTItODdkOC03MTkwYmQyMmJjNWIucG5nP1gtQW16LUFsZ29yaXRobT1BV1M0LUhNQUMtU0hBMjU2JlgtQW16LUNyZWRlbnRpYWw9QUtJQVZDT0RZTFNBNTNQUUs0WkElMkYyMDI1MDgxNyUyRnVzLWVhc3QtMSUyRnMzJTJGYXdzNF9yZXF1ZXN0JlgtQW16LURhdGU9MjAyNTA4MTdUMDUyODQxWiZYLUFtei1FeHBpcmVzPTMwMCZYLUFtei1TaWduYXR1cmU9M2M1ODlhYWMzZTZlNTkwZGRiMGVkZmMzNTgzM2NhMmEwZWQ1MGY4MDcwZjVlMDVhOGMyNTk5NzA1YmU2NDA4NSZYLUFtei1TaWduZWRIZWFkZXJzPWhvc3QifQ.-XgOhzk8ZbNvsApgRpk1tnKUzeRW0S2s6lByxyNHgz4)
*Screenshot of the Mermaid Live Renderer interface.*


## Hugging Face Space Deployment

This project is deployed at Hugging Face Space
* https://huggingface.co/spaces/liaoch/mermaid-rendering-docker

## Features

*   Web-based interface for entering Mermaid code.
*   Live preview of the diagram (SVG) that updates automatically as you type or change the theme.
*   Zoom and pan controls (buttons and drag-to-pan) for the live preview area.
*   Selectable themes (Default, Forest, Dark, Neutral).
*   Download the rendered diagram as PNG, SVG, or PDF.
*   Uses `@mermaid-js/mermaid-cli` (mmdc) behind the scenes.

## Project Structure

```
.
├── app.py                  # Main Flask application logic
├── mermaid_renderer.py     # Core class for calling mmdc
├── requirements.txt        # Python dependencies (Flask)
├── templates/
│   └── index.html          # HTML template for the web interface
├── Dockerfile              # Instructions to build the Docker image
└── README.md               # This file
```

## Prerequisites

*   [Docker](https://docs.docker.com/get-docker/) installed on your local machine or deployment server.

## Deployment with Docker

This is the recommended way to run the application, as it bundles all dependencies.

1.  **Clone/Download:** Get the application files (`app.py`, `mermaid_renderer.py`, `requirements.txt`, `templates/`, `Dockerfile`).
2.  **Generate Secret Key:** Create a strong secret key for Flask sessions. You can generate one using:
    ```bash
    python -c 'import secrets; print(secrets.token_hex(16))'
    ```
    Keep this key safe and use it in the next step.
3.  **Build the Docker Image:** Navigate to the project directory in your terminal and run:
    ```bash
    # Replace 'mermaid-renderer-app' with your desired image name/tag
    docker build -t mermaid-renderer-app .
    ```
4.  **Run the Docker Container:**
    ```bash
    # Replace 'YOUR_GENERATED_SECRET_KEY' with the key from step 2.
    # -d: Run in detached mode (background)
    # -p 7860:7860: Map port 7860 on the host to port 7860 in the container
    # --name mermaid-app: Assign a name to the container for easier management
    # -e FLASK_SECRET_KEY=...: Set the environment variable inside the container
    # mermaid-renderer-app: The name of the image to run
    docker run -d -p 7860:7860 --name mermaid-app \
      -e FLASK_SECRET_KEY='YOUR_GENERATED_SECRET_KEY' \
      mermaid-renderer-app
    ```
    *Note:* If port 7860 is already in use on your host, choose a different host port (e.g., `-p 8080:7860`).

5.  **Access the Application:** Open your web browser and navigate to `http://localhost` (or `http://your_server_ip` if deploying remotely). If you used a different host port, include it (e.g., `http://localhost:8080`).

### Managing the Container

*   **View logs:** `docker logs mermaid-app`
*   **Stop:** `docker stop mermaid-app`
*   **Start:** `docker start mermaid-app`
*   **Remove (after stopping):** `docker rm mermaid-app`

## Local Development on macOS

To test the application locally on macOS without Docker:

### 1. Install System Dependencies

Install Node.js and Python if not already installed:
```bash
# Using Homebrew (recommended)
brew install node python3

# Or download from official websites:
# Node.js: https://nodejs.org/
# Python: https://www.python.org/downloads/
```

### 2. Install Mermaid CLI

Install the Mermaid CLI globally:
```bash
npm install -g @mermaid-js/mermaid-cli
# Verify installation
mmdc --version
```

### 3. Set Up Python Virtual Environment

Navigate to the project directory and set up the environment:
```bash
# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Deactivate when done (optional)
# deactivate
```

### 4. Run the Application

With the virtual environment activated:
```bash
# Set environment variables (optional but recommended)
export FLASK_SECRET_KEY='your_secret_key_here'
export FLASK_DEBUG=true

# Run the application
python app.py
```

### 5. Access the Application

Open your web browser and navigate to `http://localhost:7860`.

### 6. Development Notes

*   The application will automatically reload when code changes are detected (due to `FLASK_DEBUG=true`)
*   Press `Ctrl+C` to stop the application
*   Remember to activate the virtual environment (`source venv/bin/activate`) before running the application in future sessions
