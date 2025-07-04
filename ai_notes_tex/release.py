#!/usr/bin/env python3

import argparse
import os
import signal
import sys
from datetime import datetime

import requests
from dotenv import load_dotenv

# Import the combine_lectures module
try:
    import combine_lectures
except ImportError:
    print("Error: combine_lectures.py not found. Make sure it's in the same directory.")
    sys.exit(1)

# Load environment variables from .env file
load_dotenv()

# Configuration from environment variables
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_OWNER = os.getenv("REPO_OWNER", "alessandroamella")
REPO_NAME = os.getenv("REPO_NAME", os.path.basename(os.getcwd()))
RELEASE_PREFIX = os.getenv("RELEASE_PREFIX", "appunti")

# Global variable to track files that need cleanup
temp_files_to_cleanup = []


def cleanup_temp_files():
    """Clean up temporary files"""
    global temp_files_to_cleanup
    for file_path in temp_files_to_cleanup:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"Deleted: {file_path}")
        except Exception as e:
            print(f"Warning: Could not delete {file_path}: {e}")
    temp_files_to_cleanup.clear()


def signal_handler(signum, frame):
    """Handle Ctrl+C interruption"""
    print("\nInterrupted! Cleaning up temporary files...")
    cleanup_temp_files()
    sys.exit(1)


def validate_config():
    """Validate required environment variables"""
    if not GITHUB_TOKEN:
        print("Error: GITHUB_TOKEN is required in your .env file")
        sys.exit(1)

    print(f"Repository: {REPO_OWNER}/{REPO_NAME}")
    print(f"Release prefix: {RELEASE_PREFIX}")


def generate_pdf():
    """Generate PDF using combine_lectures.py"""
    global temp_files_to_cleanup

    # Create output filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"{RELEASE_PREFIX}_{timestamp}"
    tex_path = f"{output_filename}.tex"
    pdf_path = f"{output_filename}.pdf"

    # Add files to cleanup list
    temp_files_to_cleanup.extend([tex_path, pdf_path])

    try:
        print("Generating PDF using combine_lectures.py...")
        print(f"Output file: {output_filename}")

        # Temporarily clear sys.argv to avoid argument conflicts with combine_lectures
        original_argv = sys.argv[:]
        sys.argv = [sys.argv[0]]  # Keep only the script name

        try:
            # Call the main function from combine_lectures
            combine_lectures.main(tex_path)
        finally:
            # Restore original sys.argv
            sys.argv = original_argv

        # Check if PDF was generated
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file {pdf_path} was not generated")

        print(f"PDF generated successfully: {pdf_path}")
        return pdf_path, output_filename

    except Exception as e:
        print(f"Error generating PDF: {e}")
        cleanup_temp_files()
        sys.exit(1)


def create_github_release(pdf_path, output_filename, custom_message=""):
    """Create a GitHub release with the generated PDF"""
    try:
        # Create release data
        timestamp = int(datetime.now().timestamp())
        release_tag = f"release-{timestamp}"
        formatted_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        release_name = f"{RELEASE_PREFIX.capitalize()} {formatted_date}"

        # Create release body
        release_body = f"Appunti aggiornati al {formatted_date}."
        if custom_message:
            release_body += f"\n\n{custom_message}"

        # GitHub API headers
        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json",
        }

        # Create release
        print("Creating GitHub release...")
        release_data = {
            "tag_name": release_tag,
            "name": release_name,
            "body": release_body,
            "draft": False,
            "prerelease": False,
        }

        response = requests.post(
            f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases",
            headers=headers,
            json=release_data,
        )

        if response.status_code != 201:
            raise Exception(
                f"Failed to create release: {response.status_code} - {response.text}"
            )

        release_info = response.json()
        print(f"GitHub release created: {release_name}")

        # Upload PDF asset
        print("Uploading PDF to release...")
        upload_url = release_info["upload_url"].replace("{?name,label}", "")

        with open(pdf_path, "rb") as pdf_file:
            upload_response = requests.post(
                f"{upload_url}?name={output_filename}.pdf",
                headers={
                    "Authorization": f"token {GITHUB_TOKEN}",
                    "Content-Type": "application/pdf",
                },
                data=pdf_file.read(),
            )

        if upload_response.status_code != 201:
            raise Exception(
                f"Failed to upload PDF: {upload_response.status_code} - {upload_response.text}"
            )

        print(f"PDF uploaded successfully: {output_filename}.pdf")
        print(f"Release URL: {release_info['html_url']}")

    except Exception as e:
        print(f"Error creating GitHub release: {e}")
        sys.exit(1)


def cleanup_files(pdf_path, tex_path):
    """Clean up generated .tex and .pdf files"""
    # Use the global cleanup function
    cleanup_temp_files()


def main():
    """Main function"""
    # Set up signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)

    parser = argparse.ArgumentParser(description="Simple GitHub Release Script")
    parser.add_argument("-m", "--message", help="Custom message for the release")

    args = parser.parse_args()

    validate_config()

    try:
        pdf_path, output_filename = generate_pdf()
        create_github_release(pdf_path, output_filename, args.message or "")
        print("Release completed successfully.")
    finally:
        # Always clean up generated files, even if interrupted
        cleanup_temp_files()
        print("Cleanup completed.")


if __name__ == "__main__":
    main()
