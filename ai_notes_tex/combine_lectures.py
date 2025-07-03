#!/usr/bin/env python3

import os
import re


def load_preamble(preamble_file="preamble.tex"):
    """Loads the common preamble from a LaTeX file."""
    try:
        with open(preamble_file, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: Preamble file '{preamble_file}' not found.")
        print("Make sure the preamble.tex file exists in the current directory.")
        return None
    except Exception as e:
        print(f"Error reading preamble file '{preamble_file}': {e}")
        return None


def extract_content(filepath):
    """Extracts the title and main body from a LaTeX file."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # Extract title (handles multi-line titles)
        title_match = re.search(r"\\title\{(.*?)\}", content, re.DOTALL)
        title = (
            title_match.group(1).strip()
            if title_match
            else f"Lezione Sconosciuta ({os.path.basename(filepath)})"
        )

        # Clean up title for chapter heading (remove LaTeX commands)
        title = re.sub(r"\\(\\|Large|large|huge|Huge|Large)\s*", " ", title)
        title = re.sub(r"[{}]", "", title)  # Remove all braces
        title = title.replace("\n", " ").strip()
        title = re.sub(r"\s+", " ", title)  # Consolidate multiple spaces

        # Remove the "Lezione di Informatica Teorica" prefix with various formats
        # Handle: "Lezione di Informatica Teorica: Topic" or "Lezione di Informatica Teorica Topic"
        title = re.sub(
            r"^Lezione\s+di\s+Informatica\s+Teorica\s*:?\s*",
            "",
            title,
            flags=re.IGNORECASE,
        )

        # Handle: "Lezione sulle ... in Informatica Teorica"
        title = re.sub(
            r"^Lezione\s+sulle?\s+.*?\s+in\s+Informatica\s+Teorica\s*",
            "",
            title,
            flags=re.IGNORECASE,
        )

        # Handle any remaining "Lezione" prefix
        title = re.sub(r"^Lezione\s+", "", title, flags=re.IGNORECASE)

        # Clean up any leftover "di Informatica Teorica" at the beginning
        title = re.sub(
            r"^di\s+Informatica\s+Teorica\s*:?\s*", "", title, flags=re.IGNORECASE
        )

        # Extract content between \begin{document} and \end{document}
        body_match = re.search(
            r"\\begin\{document\}(.*?)\\end\{document\}", content, re.DOTALL
        )
        body = body_match.group(1).strip() if body_match else ""

        # Remove the original \maketitle and \tableofcontents from the body
        body = re.sub(r"\\maketitle", "", body)
        body = re.sub(r"\\tableofcontents", "", body)

        # Remove \newpage commands to avoid unwanted page breaks
        body = re.sub(r"\\newpage\s*", "", body)

        return title, body

    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return None, None


def detect_compiler_needed(preamble_content):
    """Detects if the preamble requires LuaTeX or can use pdfLaTeX."""
    if "graphdrawing" in preamble_content:
        return "lualatex", "TikZ graph drawing library requires LuaTeX"
    elif "luacode" in preamble_content or "luatex" in preamble_content.lower():
        return "lualatex", "LuaTeX-specific packages detected"
    else:
        return "pdflatex", "Standard LaTeX packages"


def create_master_document(
    source_dir=".",
    output_file="all_lectures.tex",
    preamble_file="preamble.tex",
):
    """
    Finds all lecture-*.tex files, combines them into a single master document.
    """
    print(f"Scanning for lecture files in '{source_dir}'...")

    # Load the common preamble
    common_preamble = load_preamble(preamble_file)
    if common_preamble is None:
        return

    # Detect which compiler is needed
    compiler, reason = detect_compiler_needed(common_preamble)
    print(f"Detected compiler requirement: {compiler} ({reason})")

    # Find all lecture files
    try:
        all_files = os.listdir(source_dir)
    except FileNotFoundError:
        print(f"Error: Directory '{source_dir}' not found.")
        return

    lecture_files = [f for f in all_files if re.match(r"lecture-\d+\.tex", f)]

    if not lecture_files:
        print("No 'lecture-*.tex' files found. Aborting.")
        return

    # Sort files numerically based on the lecture number
    lecture_files.sort(key=lambda f: int(re.search(r"(\d+)", f).group(1)))

    print(f"Found {len(lecture_files)} lecture files to combine.")

    with open(output_file, "w", encoding="utf-8") as master_doc:
        # 1. Write the common preamble
        master_doc.write(common_preamble)

        # 2. Write the main document structure
        master_doc.write("\n\\title{Appunti Completi di Informatica Teorica}\n")
        master_doc.write("\\author{Consolidato da Script Python}\n")
        master_doc.write("\\date{\\today}\n\n")

        master_doc.write("\\begin{document}\n")
        master_doc.write("\\frontmatter\n")  # for things like title page and ToC
        master_doc.write("\\maketitle\n")
        master_doc.write("\\tableofcontents\n")
        master_doc.write("\\mainmatter\n")  # for the main content (chapters)

        # 3. Loop through each lecture file and append its content
        for i, filename in enumerate(lecture_files):
            print(f"Processing '{filename}'...")
            filepath = os.path.join(source_dir, filename)

            title, body = extract_content(filepath)

            if title and body:
                # Get the lecture number for the chapter title
                lecture_num = re.search(r"(\d+)", filename).group(1)

                master_doc.write(
                    "\n% =====================================================\n"
                )
                master_doc.write(f"% --- START LECTURE {lecture_num} ---\n")
                master_doc.write(
                    "% =====================================================\n\n"
                )

                # Each lecture becomes a chapter
                master_doc.write(f"\\chapter{{{title}}}\n\n")
                master_doc.write(body)
                master_doc.write("\n\n")
            else:
                print(f"Warning: Skipping '{filename}' due to extraction error.")

        # 4. End the document
        master_doc.write("\\end{document}\n")

    print(f"\nSuccessfully created master file: '{output_file}'")
    print("To compile with table of contents, run these commands:")
    print(f"  {compiler} --shell-escape {output_file}")
    print(f"  {compiler} --shell-escape {output_file}")
    print(f"  {compiler} --shell-escape {output_file}")
    print(f"Note: Using {compiler} because: {reason}")
    print(
        "Note: Running three times is needed to properly generate the table of contents and fix page numbers."
    )

    # Ask user if they want to auto-compile
    response = (
        input("\nWould you like to compile the document now? (y/N): ").strip().lower()
    )

    if response in ["y", "yes"]:
        print("\nCompiling the document...")
        import subprocess

        try:
            print("Running first compilation...")
            result1 = subprocess.run(
                [compiler, "--shell-escape", output_file],
                capture_output=False,
                text=True,
                cwd=".",
            )
            if result1.returncode == 0:
                print("✓ First compilation successful!")
                print("Running second compilation for TOC...")
                result2 = subprocess.run(
                    [compiler, "--shell-escape", output_file],
                    capture_output=True,
                    text=True,
                    cwd=".",
                )
                if result2.returncode == 0:
                    print("✓ Second compilation successful!")
                    print("Running third compilation to fix page numbers in TOC...")
                    result3 = subprocess.run(
                        [compiler, "--shell-escape", output_file],
                        capture_output=True,
                        text=True,
                        cwd=".",
                    )
                    if result3.returncode == 0:
                        print("✓ Compilation complete! PDF generated successfully.")
                        pdf_file = output_file.replace(".tex", ".pdf")
                        print(f"📄 Output: {pdf_file}")

                        # Clean up cache files
                        print("Cleaning up cache files...")
                        try:
                            cache_result = subprocess.run(
                                ["./rm_cache.sh"],
                                capture_output=True,
                                text=True,
                                cwd=".",
                            )
                            if cache_result.returncode == 0:
                                print("✓ Cache cleanup successful!")
                            else:
                                print(
                                    "⚠ Cache cleanup failed, but PDF was generated successfully."
                                )
                                if cache_result.stderr:
                                    print(f"Cache cleanup error: {cache_result.stderr}")
                        except FileNotFoundError:
                            print("⚠ rm_cache.sh not found. Skipping cache cleanup.")
                        except Exception as e:
                            print(f"⚠ Cache cleanup error: {e}")
                    else:
                        print("✗ Third compilation failed.")
                        if result3.stderr:
                            print("Error output:")
                            print(
                                result3.stderr[:500] + "..."
                                if len(result3.stderr) > 500
                                else result3.stderr
                            )
                else:
                    print("✗ Second compilation failed.")
                    if result2.stderr:
                        print("Error output:")
                        print(
                            result2.stderr[:500] + "..."
                            if len(result2.stderr) > 500
                            else result2.stderr
                        )
            else:
                print("✗ First compilation failed.")
                if result1.stderr:
                    print("Error output:")
                    print(
                        result1.stderr[:500] + "..."
                        if len(result1.stderr) > 500
                        else result1.stderr
                    )
        except FileNotFoundError:
            print(
                f"✗ Error: {compiler} not found. Please install LaTeX or check your PATH."
            )
        except Exception as e:
            print(f"✗ Compilation error: {e}")
    else:
        print("Compilation skipped. You can compile manually using the commands above.")


if __name__ == "__main__":
    # Assuming the script is in the same directory as the .tex files
    create_master_document()
