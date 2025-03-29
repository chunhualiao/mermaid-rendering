---
title: Mermaid Rendering Docker
emoji: 🚀
colorFrom: indigo
colorTo: yellow
sdk: docker
pinned: false
license: mit
---

Check out the configuration reference at https://huggingface.co/docs/hub/spaces-config-reference

# Mermaid Live Renderer Web Application

This Flask application provides a web interface for rendering diagrams from [Mermaid](https://mermaid.js.org/) syntax code. It features a live preview that updates as you type and allows downloading the final diagram as PNG, SVG, or PDF.

![Application Screenshot](sample.png)
*Screenshot of the Mermaid Live Renderer interface.*

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
├── venv/                   # Python virtual environment (created locally/on server)
└── README.md               # This file
```

## Prerequisites

### Local Machine (for testing)

*   Python 3 & pip
*   Node.js & npm
*   `@mermaid-js/mermaid-cli` installed globally (`npm install -g @mermaid-js/mermaid-cli`)

### Azure Ubuntu VM (for deployment)

*   An Azure Virtual Machine running Ubuntu (e.g., Ubuntu 20.04 LTS or later).
*   SSH access to the VM.
*   Ability to configure Network Security Groups (NSGs) in Azure portal.
*   `sudo` privileges on the VM.

## Local Testing

1.  **Clone/Download:** Get the application files (`app.py`, `mermaid_renderer.py`, `requirements.txt`, `templates/`).
2.  **Install Prerequisites:** Ensure Python 3, pip, Node.js, npm, and `@mermaid-js/mermaid-cli` are installed locally.
3.  **Create Virtual Environment:**
    ```bash
    cd /path/to/project/directory
    python3 -m venv venv
    source venv/bin/activate
    ```
4.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
5.  **Run Development Server:**
    ```bash
    python app.py
    ```
6.  **Access:** Open your browser to `http://127.0.0.1:5001` (or the port specified in `app.py`).

## Deployment to Azure Ubuntu VM

These steps guide you through deploying the application using Gunicorn and Nginx.

### 1. Connect to your VM

Connect to your Azure Ubuntu VM using SSH:
```bash
ssh your_username@your_vm_ip_address
```

### 2. Install System Dependencies

Update package lists and install necessary software:
```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv nodejs npm nginx gunicorn
```
*   `python3`, `python3-pip`, `python3-venv`: For running the Python application.
*   `nodejs`, `npm`: Required by `@mermaid-js/mermaid-cli`.
*   `nginx`: Web server to act as a reverse proxy.
*   `gunicorn`: WSGI server to run the Flask application.

Verify Node.js and npm installation: `node -v`, `npm -v`.

### 3. (Optional but Recommended) Install Mermaid CLI Globally

While the `mermaid_renderer.py` script attempts to install `mmdc` if not found, it's often more reliable to install it manually on the server first:
```bash
# Use --unsafe-perm if needed, especially when running as root/sudo
sudo npm install -g @mermaid-js/mermaid-cli --unsafe-perm=true --allow-root
# Verify installation
mmdc --version
```

### 4. Transfer Application Files

*   Create a directory for the application on the VM:
    ```bash
    sudo mkdir -p /var/www/mermaid-app
    # Set appropriate ownership (replace 'your_vm_user' with your actual user)
    sudo chown your_vm_user:your_vm_user /var/www/mermaid-app
    cd /var/www/mermaid-app
    ```
*   From your **local machine**, copy the application files to the VM using `scp` or `rsync`. Replace placeholders:
    ```bash
    scp -r /path/to/local/app.py /path/to/local/mermaid_renderer.py /path/to/local/requirements.txt /path/to/local/templates your_username@your_vm_ip_address:/var/www/mermaid-app/
    ```

### 5. Set Up Python Virtual Environment

On the VM, navigate to the application directory and set up the environment:
```bash
cd /var/www/mermaid-app
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate # Deactivate for now, systemd will handle activation
```

### 6. Configure systemd for Gunicorn

Create a systemd service file to manage the Gunicorn process.

*   Create the file:
    ```bash
    sudo nano /etc/systemd/system/mermaid-app.service
    ```
*   Paste the following content. **Important:**
    *   Replace `your_vm_user` with the Linux user that should run the application (this user needs permissions for the app directory and potentially for npm global installs if `mmdc` wasn't pre-installed). Using your own user is fine for single-user setups. `www-data` is common if Nginx runs as `www-data`.
    *   **Set a strong, unique `FLASK_SECRET_KEY`!** Generate one using `python -c 'import os; print(os.urandom(24))'`.

    ```ini
    [Unit]
    Description=Gunicorn instance to serve Mermaid Live Renderer
    After=network.target

    [Service]
    User=your_vm_user
    Group=your_vm_user # Or www-data if User is www-data
    WorkingDirectory=/var/www/mermaid-app
    # Add venv's bin to the PATH and set the secret key
    Environment="PATH=/var/www/mermaid-app/venv/bin"
    Environment="FLASK_SECRET_KEY=replace_with_your_strong_random_secret_key"
    # Command to start Gunicorn
    ExecStart=/var/www/mermaid-app/venv/bin/gunicorn --workers 3 --bind unix:/var/www/mermaid-app/mermaid-app.sock -m 007 app:app

    Restart=always

    [Install]
    WantedBy=multi-user.target
    ```

*   Save and close the file (Ctrl+X, then Y, then Enter in `nano`).
*   Start and enable the service:
    ```bash
    sudo systemctl start mermaid-app
    sudo systemctl enable mermaid-app
    # Check status (look for 'active (running)')
    sudo systemctl status mermaid-app
    # Check for errors if it failed
    # sudo journalctl -u mermaid-app
    ```
    *Troubleshooting:* If the service fails, check permissions on `/var/www/mermaid-app` and the socket file (`mermaid-app.sock` which Gunicorn creates). Ensure the `User` specified can write the socket file. The `-m 007` in the `ExecStart` makes the socket group-writable, which helps if Nginx runs as a different group (like `www-data`).

### 7. Configure Nginx as Reverse Proxy

Configure Nginx to forward web requests to the Gunicorn socket.

*   Create an Nginx configuration file:
    ```bash
    sudo nano /etc/nginx/sites-available/mermaid-app
    ```
*   Paste the following, replacing `your_domain_or_vm_ip` with your VM's public IP address or a domain name pointing to it:
    ```nginx
    server {
        listen 80;
        server_name your_domain_or_vm_ip;

        location / {
            include proxy_params;
            # Forward requests to the Gunicorn socket
            proxy_pass http://unix:/var/www/mermaid-app/mermaid-app.sock;
        }
    }
    ```
*   Save and close the file.
*   Enable the site by creating a symbolic link:
    ```bash
    # Remove default site if it exists and conflicts
    # sudo rm /etc/nginx/sites-enabled/default
    sudo ln -s /etc/nginx/sites-available/mermaid-app /etc/nginx/sites-enabled/
    ```
*   Test Nginx configuration and restart:
    ```bash
    sudo nginx -t
    # If syntax is OK:
    sudo systemctl restart nginx
    ```

### 8. Configure Firewall

*   **Azure NSG:** In the Azure portal, go to your VM's Networking settings. Add an inbound security rule to allow traffic on port 80 (HTTP) from the internet (Source: `Any` or `Internet`).
*   **VM Firewall (ufw):** If `ufw` is active on the VM, allow Nginx traffic:
    ```bash
    sudo ufw allow 'Nginx Full'
    # Check status if needed: sudo ufw status
    ```

### 9. Access the Application

Open your web browser and navigate to `http://your_domain_or_vm_ip`. You should see the Mermaid Live Renderer interface.
