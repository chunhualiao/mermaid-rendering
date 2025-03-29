#!/usr/bin/env python3
# Instructions to install dependencies and run the program:
#
# 1. Install Node.js:
#    - Download and install Node.js from https://nodejs.org/
#    - Verify installation by running `node --version` in your terminal.
#
# 2. Install the Mermaid CLI (@mermaid-js/mermaid-cli):
#    - Run `npm install -g @mermaid-js/mermaid-cli` in your terminal.
#    - If you encounter permissions issues, you might need to use `sudo` (for macOS/Linux)
#      or run the command prompt as an administrator (for Windows).
#    - Verify installation by running `mmdc --version`.
#
# 3. Run the script:
#    - You can run the script directly with the embedded example by uncommenting the lines in the `if __name__ == "__main__":` block and running:
#      `python3 mermaid-rendering.py`
#    - Alternatively, you can use the command-line interface:
#      - To render Mermaid code from a string:
#        `python3 mermaid-rendering.py -c "your_mermaid_code"`
#      - To render Mermaid code from a file:
#        `python3 mermaid-rendering.py -f /path/to/your/file.mmd`
#      - You can specify the output file with `-o /path/to/output.png`, output type with `-t [png, pdf, svg]`, and theme with `--theme [default, forest, dark, neutral]`.
#      - For example:
#        `python3 mermaid-rendering.py -f input.mmd -o output.png -t png --theme default`

import os
import sys
import subprocess
import argparse
import tempfile
import json
from pathlib import Path
import textwrap

class MermaidRenderer:
    """
    A Python class to render Mermaid diagrams to various formats
    using puppeteer-mermaid behind the scenes
    """
    
    def __init__(self):
        """Initialize the renderer and check if dependencies are installed"""
        self._check_dependencies()
    
    def _check_dependencies(self):
        """Check if Node.js and puppeteer-mermaid are installed"""
        try:
            # Check for Node.js
            subprocess.run(["node", "--version"], capture_output=True, check=True)
        except (subprocess.SubprocessError, FileNotFoundError):
            sys.exit("Error: Node.js is not installed. Please install Node.js from https://nodejs.org/")
        
        # Check if @mermaid-js/mermaid-cli is installed
        result = subprocess.run(["npm", "list", "-g", "@mermaid-js/mermaid-cli"],
                              capture_output=True, text=True)

        if "mermaid-cli" not in result.stdout:
            print("Installing @mermaid-js/mermaid-cli globally...")
            try:
                subprocess.run(["npm", "install", "-g", "@mermaid-js/mermaid-cli"], check=True)
                print("@mermaid-js/mermaid-cli installed successfully.")
            except subprocess.SubprocessError:
                sys.exit("Error: Failed to install @mermaid-js/mermaid-cli. Please install manually using: npm install -g @mermaid-js/mermaid-cli")

    def render(self, mermaid_code, output_file=None, output_format="png", theme="default"):
        """
        Render Mermaid code to the specified format
        
        Args:
            mermaid_code (str): The Mermaid diagram code
            output_file (str, optional): Output file path. If None, generates a filename based on format.
            output_format (str, optional): Output format. Options: png, pdf, svg. Default: png
            theme (str, optional): Mermaid theme. Default: default
            
        Returns:
            str: Path to the generated file
        """
        # Validate output format
        valid_formats = ["png", "pdf", "svg"]
        if output_format not in valid_formats:
            sys.exit(f"Error: Invalid output format. Choose from: {', '.join(valid_formats)}")
        
        # Create a temporary file for the Mermaid code
        with tempfile.NamedTemporaryFile(mode='w', suffix='.mmd', delete=False) as temp_file:
            temp_file.write(mermaid_code)
            input_path = temp_file.name
        
        # Generate output file name if not provided
        if not output_file:
            output_file = f"diagram.{output_format}"
        
        # Ensure output directory exists
        output_dir = os.path.dirname(output_file)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        # Run puppeteer-mermaid
        try:
            cmd = [
                "mmdc",
                "-i", input_path,
                "-o", output_file,
                "-t", theme,
                "-f", output_format
            ]
            
            subprocess.run(cmd, check=True)
            print(f"Diagram saved to: {output_file}")
            
            # Clean up the temporary file
            os.unlink(input_path)
            
            return output_file
            
        except subprocess.SubprocessError as e:
            os.unlink(input_path)
            sys.exit(f"Error rendering diagram: {str(e)}")

def main():
    """Command line interface for the Mermaid renderer"""
    parser = argparse.ArgumentParser(description="Render Mermaid diagrams to PNG, PDF, or SVG.")
    
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("-c", "--code", help="Mermaid code as a string")
    input_group.add_argument("-f", "--file", help="Path to a file containing Mermaid code")
    
    parser.add_argument("-o", "--output", help="Output file path")
    parser.add_argument("-t", "--type", default="png", choices=["png", "pdf", "svg"],
                        help="Output file type (default: png)")
    parser.add_argument("--theme", default="default", 
                        choices=["default", "forest", "dark", "neutral"],
                        help="Mermaid theme (default: default)")
    
    args = parser.parse_args()
    
    # Get Mermaid code from string or file
    if args.code:
        mermaid_code = args.code
    else:
        try:
            with open(args.file, 'r') as f:
                mermaid_code = f.read()
        except (IOError, FileNotFoundError):
            sys.exit(f"Error: Could not read file {args.file}")
    
    # Create renderer and render the diagram
    renderer = MermaidRenderer()
    renderer.render(mermaid_code, args.output, args.type, args.theme)

# Example usage with multiline string for easy copy-paste
if __name__ == "__main__":
    # You can replace this multiline string with your own Mermaid diagram code
    MERMAID_CODE = """
pie title NETFLIX
         "Time spent looking for movie" : 90
         "Time spent watching it" : 10
    """
    
    # Uncomment and modify these lines to run directly
    renderer = MermaidRenderer()
    renderer.render(MERMAID_CODE, "flowchart.svg", "svg", "default")
    renderer.render(MERMAID_CODE, "flowchart.pdf", "pdf", "default")

    # Or use the command-line interface
    #main()
