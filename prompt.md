# Prompt per Generazione Appunti LaTeX

Prendi la trascrizione automatica della lezione del professor Enrico Malizia di Informatica Teorica e genera degli appunti completi in **formato LaTeX** pronti per la compilazione. La trascrizione potrebbe contenere errori di trascrizione, parole distorte o frasi incomplete - interpreta il contesto per ricostruire accuratamente i concetti.

## Struttura degli Appunti

Organizza il contenuto con:
- **Sezioni e sottosezioni** (`\section{}`, `\subsection{}`, `\subsubsection{}`)
- **Definizioni formali** con ambiente `definition` 
- **Teoremi e proprietà** con ambiente `theorem`
- **Esempi pratici** con ambiente `example` (includi tutti gli esempi che fa il professore)
- **Dimostrazioni** quando menzionate
- **Tabelle comparative** in formato LaTeX quando appropriato
- **Pseudocodice** con `minted` o `algorithmic`
- **Formule matematiche** correttamente formattate (`$...$` inline, `\[...\]` display)

## Requisiti di Formattazione

- Usa **LaTeX nativo** (non markdown): `\textbf{}`, `\textit{}`, `\emph{}`
- Simboli matematici corretti: `\alpha`, `\beta`, `\epsilon`, `\emptyset`, etc.
- Tabelle con `tabular` environment
- Codice con `minted` environment
- Automati e diagrammi con `tikz` se necessario

## Template di Partenza

```latex
\documentclass[a4paper]{article}
\usepackage{amsmath, amssymb, amsfonts}
\usepackage[italian]{babel}
\usepackage[utf8]{inputenc}
\usepackage{graphicx}
\usepackage{hyperref}
\usepackage[a4paper, total={6in, 8in}]{geometry}
\usepackage{minted}
\usepackage{mathpazo}
\usepackage{fancyhdr}
\usepackage{amsthm}
\usepackage{tikz}
\usetikzlibrary{automata,positioning}

% Definizione degli ambienti
\newtheorem{theorem}{Teorema}
\newtheorem{definition}{Definizione}
\newtheorem{example}{Esempio}
\newtheorem{lemma}{Lemma}
\newtheorem{proposition}{Proposizione}

\hypersetup{
    pdftitle={Lezione di Informatica Teorica},
    pdfauthor={Appunti da Trascrizione AI}
}

\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\textit{Lezione di Informatica Teorica}}
\fancyfoot[C]{\thepage}

\title{Lezione di Informatica Teorica}
\author{Appunti da Trascrizione Automatica}
\date{\today}

\begin{document}
\maketitle
\tableofcontents
\newpage

% INSERISCI QUI IL CONTENUTO DEGLI APPUNTI

\end{document}
```

## Obiettivo

Crea appunti **completi e autocontenuti** che uno studente possa usare per studiare l'argomento senza altre fonti. Includi:
- Tutte le definizioni e concetti teorici
- Ogni esempio pratico menzionato dal professore
- Controesempi quando rilevanti
- Formule e dimostrazioni complete
- Note esplicative per chiarire passaggi complessi

Fornisci l'output come **codice LaTeX completo e compilabile**.
