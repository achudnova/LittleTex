<!-- # <img src="pics/littletex.png" alt="Logo" width="80" align="middle" /> LittleTex -->

<h1 align="left">
  <img src="pics/littletex.png" alt="Logo" width="84" height="84" align="middle" />
  LittleTex
</h1>

### MVP

Goal: take a simple Markdown file as input and produce a basic, compilable LaTeX file as output.

It should support:
- headings (# Title, ## Section)
- paragraphs (plain text lines)
- basic LaTeX document structure (e.g \documentclass, \begin{document})

Run: `littletex examples/test_input.md output/test_output.tex` or `littletex examples/test_input.md output/test_output.tex --pdf`

Optional: `python main.py input.md output.tex` // `python main.py input.tex output.pdf`

## Abbreviation:

- Author => `@author:`
- Title => `@title:`
- Indentation => `>>`
- Heading 1 => `#`
- Heading 2 => `##`
- Heading 3 => `###`
- Custom Date Format => `@date: June 1, 2025`
- Today's Date => `@datetoday`
- Bold Text => `**text**`
- Italic Text => `*text*`
- Inline Code => `code` with ``
  
## Basic Text Formatting
- bold text: `**text**` -> `\textbf{text}`
- italic text: `*text*` -> `\textit{text}`
- inline code: `code` -> `\texttt{code}`

## Links
- `[Link text](https://example.com)` → `\href{https://example.com}{Link text}`

## Horizontal Rule (Divider)
