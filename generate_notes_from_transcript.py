#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()  # take environment variables

# --- IMPORTANT ---
# This script requires the 'google-genai' library.
# Install it with: pip install -q -U google-genai
try:
    from google import genai
except ImportError:
    print("Error: The 'google-genai' library is not installed.")
    print("Please install it using: pip install -q -U google-genai")
    exit(1)


# --- CONFIGURATION ---

# 1. API Key Configuration
# The script expects the Gemini API key to be set as an environment variable.
# Example: export GEMINI_API_KEY="YOUR_API_KEY"
if not os.getenv("GEMINI_API_KEY"):
    print("Error: GEMINI_API_KEY environment variable not set.")
    print("Please set your API key to run this script.")
    exit(1)

# Configure the generative AI client
# genai.configure(api_key=os.environ["GEMINI_API_KEY"])


# 2. File and Directory Paths
# The script assumes it's running from this base directory.
BASE_DIR = Path("/var/www/files/appunti/info_teorica")
PDF_DIR = BASE_DIR / "pdfs"
TXT_DIR = BASE_DIR / "subtitles" / "txt"
TEX_OUTPUT_DIR = BASE_DIR / "ai_notes_tex"
PROMPT_FILE = BASE_DIR / "prompt.md"


# 3. Model and API Configuration
# Using a powerful model like 1.5 Pro is recommended for this complex task.
# It handles large documents and complex instructions well.
MODEL_NAME = "gemini-2.5-flash"
# Delay in seconds between processing batches to respect API rate limits.
API_CALL_DELAY = 5
# Number of lectures to process simultaneously
BATCH_SIZE = 2


def setup_directories():
    """Creates the output directories if they don't exist."""
    print("Setting up output directories...")
    TEX_OUTPUT_DIR.mkdir(exist_ok=True)
    print(f" -> LaTeX output: {TEX_OUTPUT_DIR}")


def load_prompt():
    """Loads the prompt from the prompt.md file."""
    if not PROMPT_FILE.exists():
        print(f"Error: Prompt file not found at '{PROMPT_FILE}'")
        print("Please create the prompt.md file in the base directory.")
        exit(1)

    try:
        prompt_content = PROMPT_FILE.read_text(encoding="utf-8")
        print(f"Successfully loaded prompt from {PROMPT_FILE}")
        return prompt_content
    except Exception as e:
        print(f"Error reading prompt file: {e}")
        exit(1)


def get_lecture_numbers():
    """Scans the subtitles directory to find all available lecture numbers."""
    if not TXT_DIR.exists():
        print(f"Error: Subtitles directory not found at '{TXT_DIR}'")
        return []

    lecture_files = sorted(TXT_DIR.glob("lecture-*.txt"))
    lecture_numbers = []
    for f in lecture_files:
        match = re.search(r"lecture-(\d+)\.txt", f.name)
        if match:
            lecture_numbers.append(match.group(1))

    print(f"Found {len(lecture_numbers)} lectures.")
    return lecture_numbers


def clean_latex_output(text):
    """Removes the markdown-style code fences that the AI might add."""
    text = re.sub(r"^```latex\n", "", text, flags=re.MULTILINE)
    text = re.sub(r"\n```$", "", text, flags=re.MULTILINE)
    return text.strip()


def process_lecture_batch(lecture_batch, client, prompt):
    """
    Processes a batch of lectures simultaneously using threading.
    """
    print(f"\n----- Processing Batch: Lectures {', '.join(lecture_batch)} -----")

    with ThreadPoolExecutor(max_workers=BATCH_SIZE) as executor:
        futures = []
        for lecture_num in lecture_batch:
            future = executor.submit(process_lecture, lecture_num, client, prompt)
            futures.append(future)

        # Wait for all lectures in the batch to complete
        for future in futures:
            future.result()


def process_lecture(lecture_num, client, prompt):
    """
    Processes a single lecture: generates LaTeX directly from transcript and PDF.
    """
    print(f"  -> Processing Lecture {lecture_num}")

    txt_path = TXT_DIR / f"lecture-{lecture_num}.txt"
    pdf_path = PDF_DIR / f"lecture-{lecture_num}.pdf"
    tex_output_path = TEX_OUTPUT_DIR / f"lecture-{lecture_num}.tex"

    # 1. Check if final output already exists to make the script resumable
    if tex_output_path.exists():
        print(f"  -> Skipping: LaTeX file for lecture {lecture_num} already exists.")
        return

    # 2. Check for source files
    if not txt_path.exists() or not pdf_path.exists():
        print(f"  -> Warning: Missing source files for lecture {lecture_num}.")
        if not txt_path.exists():
            print(f"     -> Missing: {txt_path}")
        if not pdf_path.exists():
            print(f"     -> Missing: {pdf_path}")
        return

    # Using the File API is robust for handling large files.
    # We will upload the files, use them, and then delete them.
    uploaded_pdf = None
    uploaded_txt = None
    try:
        print(f"  -> Generating LaTeX notes for lecture {lecture_num}...")
        print(f"     -> Uploading {pdf_path.name}...")
        uploaded_pdf = client.files.upload(file=pdf_path)
        print(f"     -> Uploading {txt_path.name}...")
        uploaded_txt = client.files.upload(file=txt_path)

        print(f"     -> Sending request to Gemini API for lecture {lecture_num}...")
        response = client.models.generate_content(
            model=MODEL_NAME, contents=[uploaded_pdf, uploaded_txt, prompt]
        )

        latex_content = clean_latex_output(response.text)
        tex_output_path.write_text(latex_content, encoding="utf-8")
        print(
            f"  -> Successfully saved LaTeX for lecture {lecture_num} to {tex_output_path}"
        )

    except Exception as e:
        print(f"  -> An error occurred while processing lecture {lecture_num}:")
        print(f"     -> Error Type: {type(e).__name__}")
        print(f"     -> Error Details: {e}")
        print("     -> Moving to the next lecture.")

    finally:
        # Clean up uploaded files from the Gemini API to manage storage
        print(f"  -> Cleaning up uploaded API files for lecture {lecture_num}...")
        if uploaded_pdf:
            try:
                client.files.delete(name=uploaded_pdf.name)
                print(f"     -> Deleted {uploaded_pdf.name}")
            except Exception as e:
                print(f"     -> Failed to delete {uploaded_pdf.name}: {e}")
        if uploaded_txt:
            try:
                client.files.delete(name=uploaded_txt.name)
                print(f"     -> Deleted {uploaded_txt.name}")
            except Exception as e:
                print(f"     -> Failed to delete {uploaded_txt.name}: {e}")


def main():
    """Main function to orchestrate the note generation process."""
    print("======================================================")
    print("=      AI Lecture Notes Generator Initialized      =")
    print("======================================================")

    setup_directories()

    # Load the prompt from file
    prompt = load_prompt()

    lecture_numbers = get_lecture_numbers()
    if not lecture_numbers:
        print("\nNo lectures found. Exiting.")
        return

    # Initialize the client once
    client = genai.Client()

    for i, num in enumerate(lecture_numbers):
        # As per the request, skip lecture 1 and start from 2
        if int(num) < 2:
            continue

        process_lecture(num, client, prompt)

        # Add a delay to avoid hitting API rate limits, but not after the last item
        if i < len(lecture_numbers) - 1:
            print(f"\nWaiting for {API_CALL_DELAY} seconds before the next lecture...")
            time.sleep(API_CALL_DELAY)

    print("\n======================================================")
    print("=              Processing Complete               =")
    print("======================================================")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProcess interrupted by user. Exiting gracefully.")
        exit(0)
