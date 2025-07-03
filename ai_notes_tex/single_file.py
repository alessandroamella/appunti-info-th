#!/usr/bin/env python3

import argparse
import os
import subprocess
import sys


def detect_compiler_needed(tex_file):
    """Detects if the tex file requires LuaTeX or can use pdfLaTeX."""
    try:
        with open(tex_file, "r", encoding="utf-8") as f:
            content = f.read()

        if "graphdrawing" in content:
            return "lualatex", "TikZ graph drawing library requires LuaTeX"
        elif "luacode" in content or "luatex" in content.lower():
            return "lualatex", "LuaTeX-specific packages detected"
        else:
            return "pdflatex", "Standard LaTeX packages"
    except Exception as e:
        print(f"Warning: Could not analyze file content: {e}")
        return "pdflatex", "Default choice"


def compile_tex_file(tex_file, interactive=False, clear_cache=False):
    """Compiles a single .tex file with the appropriate compiler."""

    # Check if file exists
    if not os.path.exists(tex_file):
        print(f"Error: File '{tex_file}' not found.")
        return False

    # Detect which compiler is needed
    compiler, reason = detect_compiler_needed(tex_file)
    print(f"Detected compiler requirement: {compiler} ({reason})")

    print("To compile this document, run these commands:")
    print(f"  {compiler} --shell-escape {tex_file}")
    print(f"  {compiler} --shell-escape {tex_file}")
    print(f"  {compiler} --shell-escape {tex_file}")
    print(
        "Note: Running three times is needed to properly generate references, table of contents, and fix page numbers."
    )

    # Ask user if they want to compile (only if interactive mode is enabled)
    if interactive:
        response = (
            input("\nWould you like to compile the document now? (y/N): ")
            .strip()
            .lower()
        )
        if response not in ["y", "yes"]:
            print(
                "Compilation skipped. You can compile manually using the commands above."
            )
            return False

    print("\nCompiling the document...")

    try:
        print("Running first compilation...")
        result1 = subprocess.run(
            [compiler, "--shell-escape", tex_file],
            capture_output=False,
            text=True,
            cwd=".",
        )
        if result1.returncode == 0:
            print("✓ First compilation successful!")
            print("Running second compilation for references/TOC...")
            result2 = subprocess.run(
                [compiler, "--shell-escape", tex_file],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                cwd=".",
            )
            if result2.returncode == 0:
                print("✓ Second compilation successful!")
                print("Running third compilation to fix page numbers...")
                result3 = subprocess.run(
                    [compiler, "--shell-escape", tex_file],
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    cwd=".",
                )
                if result3.returncode == 0:
                    print("✓ Compilation complete! PDF generated successfully.")
                    pdf_file = tex_file.replace(".tex", ".pdf")
                    print(f"📄 Output: {pdf_file}")

                    # Clean up cache files only if clear_cache is True and rm_cache.sh exists
                    if clear_cache and os.path.exists("./rm_cache.sh"):
                        print("Cleaning up cache files...")
                        try:
                            cache_result = subprocess.run(
                                ["./rm_cache.sh"],
                                capture_output=True,
                                text=True,
                                encoding="utf-8",
                                errors="replace",
                                cwd=".",
                            )
                            if cache_result.returncode == 0:
                                print("✓ Cache cleanup successful!")
                            else:
                                print(
                                    "⚠ Cache cleanup failed, but PDF was generated successfully."
                                )
                        except Exception as e:
                            print(f"⚠ Cache cleanup error: {e}")

                    return True
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
            # Note: result1 has capture_output=False, so stderr might not be available
            print("Check the terminal output above for error details.")

    except FileNotFoundError:
        print(
            f"✗ Error: {compiler} not found. Please install LaTeX or check your PATH."
        )
    except Exception as e:
        print(f"✗ Compilation error: {e}")

    return False


def main():
    """Main function to handle command line arguments."""
    parser = argparse.ArgumentParser(
        description="Compile LaTeX files with automatic compiler detection",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 compile_tex.py lecture-01.tex
  python3 compile_tex.py all_lectures.tex --interactive
  python3 compile_tex.py lecture-02.tex --clear
  python3 compile_tex.py all_lectures.tex -i -c
        """,
    )

    parser.add_argument("tex_file", help="The LaTeX file to compile")

    parser.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        help="Ask for confirmation before compiling (default: False)",
    )

    parser.add_argument(
        "-c",
        "--clear",
        action="store_true",
        help="Clear cache files after compilation (default: False)",
    )

    args = parser.parse_args()

    print(f"Compiling LaTeX file: {args.tex_file}")
    success = compile_tex_file(args.tex_file, args.interactive, args.clear)

    if success:
        print("\n🎉 Compilation completed successfully!")
    else:
        print("\n❌ Compilation failed or was cancelled.")
        sys.exit(1)


if __name__ == "__main__":
    main()
