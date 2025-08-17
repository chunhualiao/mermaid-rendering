# mermaid_renderer.py
import os
import sys
import subprocess
import tempfile
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class MermaidRenderer:
    """
    A Python class to render Mermaid diagrams using @mermaid-js/mermaid-cli.
    """
    def __init__(self):
        """Initialize the renderer and check if dependencies are installed"""
        self._check_dependencies()

    def _check_dependencies(self):
        """Check if Node.js and npx are installed"""
        try:
            subprocess.run(["node", "--version"], capture_output=True, check=True, text=True)
            logging.info("Node.js found.")
        except (subprocess.SubprocessError, FileNotFoundError) as e:
            logging.error(f"Node.js check failed: {e}")
            # In a web context, exiting might not be ideal. Log error.
            # Consider raising an exception or handling this state in the Flask app.
            raise RuntimeError("Error: Node.js is not installed or not found in PATH.")

        # Check if npx is available
        try:
            subprocess.run(["npx", "--version"], capture_output=True, check=True, text=True)
            logging.info("npx found.")
        except (subprocess.SubprocessError, FileNotFoundError) as e:
            logging.error(f"npx check failed: {e}")
            raise RuntimeError("Error: npx is not installed or not found in PATH.")

    def render(self, mermaid_code, output_format="png", theme="default"):
        """
        Render Mermaid code to the specified format into a temporary file.

        Args:
            mermaid_code (str): The Mermaid diagram code.
            output_format (str, optional): Output format (png, pdf, svg). Default: png.
            theme (str, optional): Mermaid theme. Default: default.

        Returns:
            tuple: (path_to_temp_output_file, temp_input_file_path) or raises Exception on error.
                   The caller is responsible for deleting these files.
        """
        valid_formats = ["png", "pdf", "svg"]
        if output_format not in valid_formats:
            raise ValueError(f"Invalid output format '{output_format}'. Choose from: {', '.join(valid_formats)}")

        valid_themes = ["default", "forest", "dark", "neutral"]
        if theme not in valid_themes:
             raise ValueError(f"Invalid theme '{theme}'. Choose from: {', '.join(valid_themes)}")

        # Create temporary files (ensure they are deleted by the caller)
        # Input file for mermaid code
        temp_input_file = tempfile.NamedTemporaryFile(mode='w', suffix='.mmd', delete=False)
        # Output file for the generated diagram
        temp_output_file = tempfile.NamedTemporaryFile(suffix=f'.{output_format}', delete=False)

        input_path = temp_input_file.name
        output_path = temp_output_file.name

        try:
            temp_input_file.write(mermaid_code)
            temp_input_file.close() # Close file before passing to subprocess

            cmd = [
                "npx", "@mermaid-js/mermaid-cli",
                "-i", input_path,
                "-o", output_path,
                "-t", theme,
                # No -f flag needed for mmdc, format is determined by -o extension
                # However, explicitly setting background color might be needed for transparency
                # "-b", "transparent" # Example: if you want transparent background for PNG/SVG
            ]
            logging.info(f"Running mmdc command: {' '.join(cmd)}")

            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            logging.info(f"mmdc execution successful. Output saved to: {output_path}")
            if result.stderr:
                logging.warning(f"mmdc stderr: {result.stderr}")

            # Return paths for Flask to handle; caller must delete files
            return output_path, input_path

        except subprocess.CalledProcessError as e:
            logging.error(f"Error rendering diagram with mmdc: {e}")
            logging.error(f"mmdc stderr: {e.stderr}")
            # Clean up files on error before raising
            temp_output_file.close()
            os.unlink(output_path)
            if os.path.exists(input_path): # Input file might already be closed/deleted
                os.unlink(input_path)
            raise RuntimeError(f"Error rendering diagram: {e.stderr or e}")
        except Exception as e:
            # Catch any other unexpected errors
            logging.error(f"Unexpected error during rendering: {e}")
            # Ensure cleanup
            temp_input_file.close()
            temp_output_file.close()
            if os.path.exists(input_path): os.unlink(input_path)
            if os.path.exists(output_path): os.unlink(output_path)
            raise # Re-raise the caught exception
