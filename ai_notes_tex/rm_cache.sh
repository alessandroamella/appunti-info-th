#!/bin/bash

/bin/rm -rf __pycache__ *.pyg *.dot .*.swp *.log *.out *.aux *.toc *.synctex* *.bbl *.blg *.fls *.fdb_latexmk *.run.xml _minted-* 2>/dev/null

echo "✅ Cache eliminata"
