# app.py
import os
import logging
import base64
import textwrap # Import the missing module
from flask import Flask, request, render_template, send_file, flash, redirect, url_for, jsonify
from mermaid_renderer import MermaidRenderer # Import the refactored class

# Configure logging (optional but recommended)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
# Required for flashing messages
# In a real deployment, use a persistent, environment-variable-based secret key
# Using a fixed key for simplicity here, replace in production
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'a_very_secret_key_change_in_prod')

# Initialize the renderer (could potentially be done once at startup)
# Handle potential init errors
renderer = None
try:
    renderer = MermaidRenderer()
    logging.info("MermaidRenderer initialized successfully.")
except RuntimeError as e:
    logging.critical(f"Failed to initialize MermaidRenderer: {e}. The rendering endpoint will be unavailable.")
    # Keep renderer as None to indicate failure

@app.route('/', methods=['GET'])
def index():
    """Simple health check for the root path."""
    return "Mermaid Renderer App is running!", 200

@app.route('/render', methods=['POST'])
def render_mermaid():
    """
    Handle form submission.
    Handle form submission for final download.
    Re-renders the diagram based on form data and sends it as an attachment.
    """
    if renderer is None:
        flash("Mermaid rendering service is unavailable. Cannot process request.", "error")
        return redirect(url_for('index'))

    mermaid_code = request.form.get('mermaid_code', '')
    output_format = request.form.get('output_format', 'png')
    theme = request.form.get('theme', 'default')

    if not mermaid_code.strip():
        flash("Mermaid code cannot be empty.", "warning")
        return redirect(url_for('index'))

    output_path = None
    input_path = None
    try:
        logging.info(f"Download request: format={output_format}, theme={theme}")
        if not renderer:
            raise RuntimeError("Renderer not initialized.")

        output_path, input_path = renderer.render(mermaid_code, output_format, theme)

        mime_types = {'png': 'image/png', 'svg': 'image/svg+xml', 'pdf': 'application/pdf'}
        mime_type = mime_types.get(output_format, 'application/octet-stream')

        return send_file(
            output_path,
            mimetype=mime_type,
            as_attachment=True,
            download_name=f'diagram.{output_format}'
        )
    except (ValueError, RuntimeError) as e:
        logging.error(f"Download rendering failed: {e}")
        flash(f"Error generating download: {e}", "error")
        return redirect(url_for('index'))
    except Exception as e:
        logging.exception("An unexpected error occurred during rendering.") # Log full traceback
        flash("An unexpected server error occurred. Please try again later.", "error")
        return redirect(url_for('index'))
    finally:
        # IMPORTANT: Clean up temporary files after sending the response or on error
        if output_path and os.path.exists(output_path):
            try:
                # If it was PDF, send_file might hold the handle, but unlinking should still work on Unix-like systems
                # On Windows, this might cause issues if send_file hasn't finished.
                # A more robust solution might involve background tasks or different cleanup strategies.
                os.unlink(output_path)
                logging.info(f"Cleaned up temporary output file: {output_path}")
            except OSError as e:
                logging.error(f"Error deleting temporary output file {output_path}: {e}")
        if input_path and os.path.exists(input_path):
             try:
                 os.unlink(input_path)
                 logging.info(f"Cleaned up temporary input file: {input_path}")
             except OSError as e:
                 logging.error(f"Error deleting temporary input file {input_path}: {e}")

@app.route('/preview', methods=['POST'])
def preview_mermaid():
    """
    Handles asynchronous preview requests.
    Renders PNG/SVG and returns image data as JSON.
    """
    if renderer is None:
        return jsonify({"error": "Mermaid rendering service is unavailable."}), 503

    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid request data."}), 400

    mermaid_code = data.get('mermaid_code', '')
    # Preview only supports PNG and SVG for embedding
    output_format = data.get('output_format', 'svg') # Default to SVG for preview
    if output_format not in ['png', 'svg']:
         output_format = 'svg' # Force SVG if invalid format requested for preview
    theme = data.get('theme', 'default')

    if not mermaid_code.strip():
        return jsonify({"error": "Mermaid code cannot be empty."}), 400

    output_path = None
    input_path = None
    preview_data = None
    try:
        logging.info(f"Preview request: format={output_format}, theme={theme}")
        if not renderer:
            raise RuntimeError("Renderer not initialized.") # Should be caught above, but defensive

        output_path, input_path = renderer.render(mermaid_code, output_format, theme)

        with open(output_path, 'rb') as f:
            file_content = f.read()

        if output_format == 'png':
            preview_data = base64.b64encode(file_content).decode('utf-8')
        elif output_format == 'svg':
            try:
                preview_data = file_content.decode('utf-8')
            except UnicodeDecodeError:
                 logging.error("SVG content is not valid UTF-8 for preview.")
                 raise RuntimeError("Generated SVG is not valid UTF-8.")

        return jsonify({
            "format": output_format,
            "data": preview_data
        })

    except (ValueError, RuntimeError) as e:
        logging.error(f"Preview rendering failed: {e}")
        return jsonify({"error": f"Error rendering preview: {e}"}), 500
    except Exception as e:
        logging.exception("An unexpected error occurred during preview generation.")
        return jsonify({"error": "An unexpected server error occurred during preview."}), 500
    finally:
        # Ensure cleanup after preview generation
        if output_path and os.path.exists(output_path):
            try:
                os.unlink(output_path)
                logging.info(f"Cleaned up temporary output file after download: {output_path}")
            except OSError as e:
                logging.error(f"Error deleting temporary output file {output_path} after download: {e}")
        if input_path and os.path.exists(input_path):
             try:
                 os.unlink(input_path)
                 logging.info(f"Cleaned up temporary input file after download: {input_path}")
             except OSError as e:
                 logging.error(f"Error deleting temporary input file {input_path} after download: {e}")

@app.route('/healthz')
def healthz():
    return "OK", 200

if __name__ == '__main__':
    # For local development only (use Gunicorn/Waitress in production)
    # Use 0.0.0.0 to be accessible on the network
    # Set debug=False for production-like testing, or True for development features
    is_debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    # Changed default port from 5000 to 5001 to avoid conflicts
    app.run(debug=is_debug, host='0.0.0.0', port=int(os.environ.get('PORT', 5001)))
