#!/bin/bash

# Bash completion for single_file.py LaTeX compiler script
# This script provides autocompletion for .tex files when using single_file.py

_single_file_completion() {
  local cur prev opts
  COMPREPLY=()
  cur="${COMP_WORDS[COMP_CWORD]}"
  prev="${COMP_WORDS[COMP_CWORD - 1]}"

  # Available options
  opts="-i --interactive -c --clear -h --help"

  # If the previous word is one of the script names, complete with .tex files
  if [[ ${COMP_CWORD} -eq 1 ]] || [[ "${prev}" == "single_file.py" ]] || [[ "${prev}" == "python3" && "${COMP_WORDS[COMP_CWORD - 2]}" == *"single_file.py" ]]; then
    # Complete with .tex files in current directory and subdirectories
    COMPREPLY=($(compgen -f -X "!*.tex" -- ${cur}))
    return 0
  fi

  # Complete with options if current word starts with -
  if [[ ${cur} == -* ]]; then
    COMPREPLY=($(compgen -W "${opts}" -- ${cur}))
    return 0
  fi

  # If we're not completing the first argument and it's not an option,
  # complete with .tex files
  COMPREPLY=($(compgen -f -X "!*.tex" -- ${cur}))
}

# Register the completion function
complete -F _single_file_completion single_file.py
complete -F _single_file_completion python3\ single_file.py
complete -F _single_file_completion ./single_file.py

# Also register for common ways the script might be called
complete -F _single_file_completion python\ single_file.py
complete -F _single_file_completion python3\ ./single_file.py
