#!/usr/bin/env python3
"""Checks for the arXiv HTML converter and the page mapper, on small fixtures.

    paperlib test   (or: python3 tests/test_conversion.py)

Each fixture is a fragment of LaTeXML output, run through the real
html-to-markdown.py (and so the Lua filter); no network is used. Prints one
line per check and exits non-zero if any fails.
"""

import hashlib
import importlib.util
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))


def load(name):
    spec = importlib.util.spec_from_file_location(name.replace("-", "_"), SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def convert(fragment, env=None):
    """Markdown for an article fragment, and the image files it wrote. Small pictures are
    not sent to a model unless `env` says so (PAPERLIB_ICONS)."""
    page = f'<html><body><div class="ltx_page_content">{fragment}</div></body></html>'
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        (tmp / "paper.html").write_text(page, encoding="utf-8")
        subprocess.run(
            [sys.executable, SCRIPTS / "html-to-markdown.py", tmp / "paper.html", tmp / "body.md",
             tmp / "images", "paper"],
            check=True, capture_output=True, timeout=120, env={**os.environ, "PAPERLIB_ICONS": "off", **(env or {})},
        )
        images = sorted(p.name for p in (tmp / "images").glob("*")) if (tmp / "images").exists() else []
        return (tmp / "body.md").read_text(encoding="utf-8"), images


def math(tex, display=False):
    return (f'<math display="{"block" if display else "inline"}"><semantics><mi>x</mi>'
            f'<annotation encoding="application/x-tex">{tex}</annotation></semantics></math>')


def eqn_row(*cells, number=None):
    tds = "".join(f'<td class="ltx_eqn_cell">{c}</td>' for c in cells)
    tag = f'<td class="ltx_eqn_cell ltx_eqn_eqno"><span class="ltx_tag">({number})</span></td>' if number else ""
    return f'<tr class="ltx_eqn_row">{tds}{tag}</tr>'


def td(text, classes=""):
    return f'<span class="ltx_td {classes}">{text}</span>'


SPAN_TABLE = (
    '<p class="ltx_p"><span class="ltx_inline-block ltx_transformed_outer">'
    '<span class="ltx_tabular">'
    '<span class="ltx_tr">' + td("Length", "ltx_border_t ltx_rowspan ltx_rowspan_2")
    + td("Qwen", "ltx_border_t ltx_colspan ltx_colspan_2") + "</span>"
    '<span class="ltx_tr">' + td("Vanilla", "ltx_border_t") + td("RAG", "ltx_border_t") + "</span>"
    '<span class="ltx_tr">' + td("100K", "ltx_border_t") + td("0.300", "ltx_border_t")
    + td("0.650", "ltx_border_t") + "</span>"
    "</span></span></p>"
)

BORDER_TABLE = (
    '<table class="ltx_tabular"><tbody>'
    '<tr class="ltx_tr"><td class="ltx_td ltx_border_tt">Model</td><td class="ltx_td ltx_border_tt">PPL</td></tr>'
    '<tr class="ltx_tr"><td class="ltx_td ltx_border_t">A</td><td class="ltx_td ltx_border_t">3.29</td></tr>'
    '<tr class="ltx_tr"><td class="ltx_td">B</td><td class="ltx_td">2.69</td></tr>'
    "</tbody></table>"
)


def picture(blocks, paths=2, height=160):
    fos = "".join(
        f'<foreignObject width="400" height="20"><span class="ltx_foreignobject_container">'
        f'<span class="ltx_foreignobject_content">{b}</span></span></foreignObject>'
        for b in blocks
    )
    shapes = '<path d="M0 0"></path>' * paths
    return f'<svg class="ltx_picture" height="{height}" viewBox="0 0 400 {height}">{shapes}<g>{fos}</g></svg>'


PROMPT = ('<span class="ltx_p">Please act as an impartial judge and evaluate the quality of the '
          'responses provided by two AI assistants.</span><span class="ltx_p">[[User Question]]</span>')
ITEMS = ('<span class="ltx_enumerate"><span class="ltx_item"><span class="ltx_tag">1.</span>'
         '<span class="ltx_para"><span class="ltx_p">Can we train a network to compress many LoRAs?</span>'
         '</span></span><span class="ltx_item"><span class="ltx_tag">2.</span><span class="ltx_para">'
         '<span class="ltx_p">Can we decode new adapters from instructions alone?</span></span></span></span>')


def checks():
    """(name, passed) for each check."""
    md, _ = convert(SPAN_TABLE)
    yield "scaled table becomes a table", "<table>" in md and "0.650" in md and "Length 0.300" not in md
    yield "scaled table keeps spans", 'rowspan="2"' in md and 'colspan="2"' in md
    yield "scaled table gets its header rows", "<thead>" in md and md.index("Vanilla") < md.index("</thead>")

    md, _ = convert('<p class="ltx_p"><span class="ltx_tabular">'
                    '<span class="ltx_tr">' + td("7B Models", "ltx_colspan ltx_colspan_2") + "</span>"
                    '<span class="ltx_tr">' + td("FLAN") + td("50%") + "</span>"
                    '<span class="ltx_tr">' + td("13B Models", "ltx_colspan ltx_colspan_2") + "</span>"
                    '<span class="ltx_tr">' + td("Vicuna") + td("64.1%") + "</span>"
                    "</span></p>")
    yield "scaled table with full-width group rows is a table", "<table>" in md and "FLAN 50%" not in md

    def lines(*texts):  # a multi-line cell: a one-column tabular nested in it
        return ('<span class="ltx_tabular">'
                + "".join(f'<span class="ltx_tr">{td(t)}</span>' for t in texts) + "</span>")

    md, _ = convert('<p class="ltx_p"><span class="ltx_tabular">'
                    '<span class="ltx_tr">' + td("Thinking") + td("Non-Thinking") + "</span>"
                    '<span class="ltx_tr">' + td(lines("&lt;user&gt;", "{query} /think", "&lt;think&gt;"))
                    + td(lines("&lt;user&gt;", "{query} /no_think", "&lt;think&gt;", "&lt;/think&gt;")) + "</span>"
                    "</span></p>")
    yield "scaled table with multi-line cells is a table", (
        "| Thinking | Non-Thinking |" in md and "| &lt;user&gt; {query} /think &lt;think&gt; |" in md.replace("\\<", "&lt;").replace("\\>", "&gt;"))

    md, _ = convert('<p class="ltx_p"><span class="ltx_tabular">'
                    '<span class="ltx_tr">' + td("") + td("Subjective") + td("Objective") + "</span>"
                    '<span class="ltx_tr">' + td("Video alignment", "ltx_rowspan ltx_rowspan_4") + td("Correctness")
                    + td("ImageBind", "ltx_rowspan ltx_rowspan_4") + "</span>"
                    '<span class="ltx_tr">' + td("Synchronization") + "</span>"
                    '<span class="ltx_tr">' + td("Mood") + "</span>"
                    '<span class="ltx_tr">' + td("Action") + "</span>"
                    "</span></p>")
    yield "scaled table whose rows sit under a \\multirow is a table", (
        "<table>" in md and '<td rowspan="4">ImageBind</td>' in md)

    md, _ = convert('<p class="ltx_p">A <span class="ltx_tabular">'
                    '<span class="ltx_tr">' + td("Num. of") + "</span>"
                    '<span class="ltx_tr">' + td("Samples") + "</span></span> cell.</p>")
    yield "a one-column span tabular in text stays text", "<table>" not in md and "|" not in md and "Num. of" in md

    def rotated(name):  # a column title turned on its side: a tabular of <th> around its lines
        return ('<span class="ltx_td ltx_th ltx_th_column"> <span class="ltx_tabular"><span class="ltx_tr">'
                '<span class="ltx_td ltx_th ltx_th_column"><span class="ltx_inline-block ltx_transformed_outer">'
                '<span class="ltx_transformed_inner" style="transform:rotate(-90deg)"><span class="ltx_p">'
                + lines(name, "4.2b") + "</span></span></span></span></span></span> </span>")

    md, _ = convert('<p class="ltx_p"><span class="ltx_tabular">'
                    '<span class="ltx_tr">' + td("") + rotated("Phi-3.5-Vision") + rotated("GPT-4O") + "</span>"
                    '<span class="ltx_tr">' + td("MMMU", "ltx_border_t ltx_rowspan ltx_rowspan_2") + td("43.0", "ltx_border_t")
                    + td("62.4", "ltx_border_t") + "</span>"
                    '<span class="ltx_tr">' + td("44.1") + td("63.0") + "</span>"
                    "</span></p>")
    yield "a rotated column title set as a tabular of <th> keeps its text", (
        "<th>Phi-3.5-Vision 4.2b</th>" in md and "<th>GPT-4O 4.2b</th>" in md)

    md, _ = convert(BORDER_TABLE)
    yield "header row above \\midrule becomes the header", md.lstrip().startswith("| Model | PPL")

    md, _ = convert("<h6>Abstract</h6><h6>Abstract</h6><p>Text.</p>")
    yield "repeated empty heading is dropped", md.count("Abstract") == 1

    md, _ = convert('<table class="ltx_tabular"><tr><td></td><td></td></tr></table><p>Text.</p>')
    yield "empty layout table is dropped", "|" not in md

    md, _ = convert('<table class="ltx_tabular"><tr><td><span class="ltx_listing ltx_lstlisting">'
                    '<span class="ltx_listingline"># Task</span><span class="ltx_listingline">Answer (A).</span>'
                    "</span></td></tr></table><p>Text.</p>")
    yield "table holding only a listing is kept", "Answer (A)." in md

    md, _ = convert('<table class="ltx_equation ltx_eqn_table"><tbody>'
                    + eqn_row(math(r"\displaystyle a=1,\hskip 9.24994ptb=2"), number=1) + "</tbody></table>")
    yield "\\hskip keeps its space, no pt residue", r"\hspace{9.24994pt}b=2" in md and " 9.24994ptb" not in md

    md, _ = convert('<table class="ltx_equationgroup ltx_eqn_table"><tbody>'
                    + eqn_row(math(r"\displaystyle\textbf{WA}"), math(r"\displaystyle:=x"), number=1)
                    + '</tbody><tbody><tr class="ltx_eqn_row"><td class="ltx_eqn_cell" colspan="3">where '
                    + math(r"\bot") + " denotes a missing source.</td></tr></tbody></table>")
    yield "aligned pair is one equation", r"\textbf{WA}\displaystyle:=x \tag{1}" in md
    yield "\\intertext prose is kept", "where $\\bot$ denotes a missing source." in md

    md, _ = convert('<table class="ltx_equation ltx_eqn_table"><tbody>'
                    + eqn_row('<span class="ltx_text ltx_markedasmath">output</span>', math(r"\displaystyle=y W"),
                              '<span class="ltx_text ltx_markedasmath"># gating</span>')
                    + "</tbody></table>")
    yield "text cells kept as \\text", r"\text{output}\displaystyle=y W \qquad \text{\# gating}" in md

    md, _ = convert('<table class="ltx_equation ltx_eqn_table"><tbody>'
                    + eqn_row(math(r"\displaystyle I"), math(r"\displaystyle=Kq,"), math(r"\displaystyle s"),
                              math(r"\displaystyle=\text{Softmax}(I)"), number=1)
                    + "</tbody></table>")
    yield "equations on one row are spaced apart", r"=Kq, \qquad \displaystyle s" in md

    md, _ = convert("<p>See " + math(r"\mathsection") + " 2 and " + math(r"\argmax_{x}f") + ".</p>")
    yield "\\mathsection and \\argmax", r"$\S$" in md and r"\operatorname*{arg\,max}_{x}f" in md

    md, _ = convert("<p>" + math(r"0.769\,142\,111\,540\,03\pm 0.162\,334\,188") + " of "
                    + math(r"10\,000") + " with " + math(r"x_{1\,2}") + ".</p>")
    yield "siunitx digit groups joined and rounded", r"$0.7691\pm 0.1623$ of $10000$" in md
    yield "a thin space between indices is kept", r"x_{1\,2}" in md

    md, _ = convert("<p>" + math(r"5\text{\times}{10}^{-4}") + " and "
                    + math(r"83.1_{\raisebox{-0.5pt}{\tiny\pm1.6}}") + " and "
                    + math(r"r\mathrel{\raisebox{-1.2pt}{\mathbin{\overset{\text{{def}}}{=}}}}s") + ".</p>")
    yield "a math command in a text argument is set as math", (
        r"5\text{\(\times\)}{10}^{-4}" in md and r"{\tiny\(\pm\)1.6}" in md
        and r"\raisebox{-1.2pt}{\(\mathbin{\overset{\text{{def}}}{=}}\)}}s" in md)

    md, _ = convert("<p>" + math(r"x\quad\text{\text[citep]{[\@@bibref{Number}{smith_2010}{}{}]}}") + " and "
                    + math(r"\textnormal{(by Eq \ref{eq:chain_rule})}") + " and "
                    + math(r"\centering{\bm{x}}\@add@centering") + ".</p>")
    yield "LaTeXML's citation internals keep the key", r"\text{\text{[smith\_2010]}}" in md and "bibref" not in md
    yield "an underscore in a text label is escaped", r"\text{eq:chain\_rule}" in md
    yield "\\centering is dropped", r"${\bm{x}}$" in md

    md, _ = convert("<p>" + math(r"\begin{split}a&amp;=b\end{split}") + " and "
                    + math(r"\begin{multlined}a\\ b\end{multlined}") + " and "
                    + math(r"\begin{array}{@{}rcl@{\qquad}l}x&amp;=&amp;f&amp;g\end{array}") + ".</p>"
                    + '<table class="ltx_equation ltx_eqn_table"><tbody>'
                    + eqn_row(math(r"\displaystyle\begin{split}a&amp;=b\end{split}"), number=1) + "</tbody></table>")
    yield "split becomes aligned", (
        r"$\begin{aligned}a&=b\end{aligned}$" in md and r"\begin{aligned}a&=b\end{aligned} \tag{1}" in md)
    yield "multlined becomes gathered", r"\begin{gathered}a\\ b\end{gathered}" in md
    yield "@{} is taken out of array columns", r"\begin{array}{rcll}x&=&f&g" in md

    md, _ = convert("<p>" + math(r"y=\sigma\mathopen{}\mathclose{{\left(\sum_{i}{w}_{i}+b}}\right)") + " and "
                    + math(r"\Tr{\A^\T}") + " and " + math(r"2\--3\times") + " and x " + math(r"\mod") + " y and "
                    + math("[\\begin{smallmatrix}U\\\\\nV\\end{smallmatrix}]") + ".</p>")
    yield "\\mleft ... \\mright wrapper is taken off", r"$y=\sigma\left(\sum_{i}{w}_{i}+b\right)$" in md
    yield "an unknown macro as a script is one group", r"\operatorname{A}^{\operatorname{T}}" in md
    yield "\\- is dropped, a bare \\mod is a name", r"$2-3\times$" in md and r"$\operatorname{mod}$" in md
    yield "inline math stays on one line", r"$[\begin{smallmatrix}U\\ V\end{smallmatrix}]$" in md

    md, _ = convert("<p>" + math(r"\raisebox{2pt}{\hbox{\(\hbox{{\kern-0.2pt\bigwedge}}\)}}") + " and "
                    + math(r"\text{bo$n$ \(\alpha\)}") + ".</p>")
    yield "a box inside math inside a box is text again", r"\hbox{\(\hbox{{\kern-0.2pt\(\bigwedge\)}}\)}" in md
    yield "math in a text argument is kept", r"\text{bo\(n\) \(\alpha\)}" in md

    md, _ = convert("<p>cost of " + math(r"\sim") + "$" + math("0.6") + ", the " + math(r"\$") + " value.</p>")
    yield "a currency sign between two formulas joins them", r"$\sim \$0.6$" in md and r"the \$ value" in md

    md, images = convert("<div>" + picture([PROMPT]) + "</div>")
    yield "prompt box becomes a quote", md.startswith("> Please act as an impartial judge") and not images
    yield "box paragraphs stay apart", "\n>\n> \\[\\[User Question\\]\\]" in md

    md, _ = convert("<div>" + picture(["Prompt Template for Judgment Annotation", PROMPT]) + "</div>")
    yield "box title in bold", md.startswith("> **Prompt Template for Judgment Annotation**")

    md, _ = convert("<div>" + picture([ITEMS]) + "</div>")
    yield "list items in a box stay apart", "1\\. Can we train" in md and "\n>\n> 2\\. Can we decode" in md

    md, images = convert('<table class="ltx_tabular"><tr><td class="ltx_td">'
                         + picture(['<span class="ltx_text">+ MaTTS</span>'], height=7.77)
                         + '</td><td class="ltx_td">51.2</td></tr></table>')
    yield "small badge becomes its text", "+ MaTTS" in md and not images

    rank = picture(['<span class="ltx_text">3</span>'], height=13.07)
    md, _ = convert('<table class="ltx_tabular"><tr><td class="ltx_td">MIRACL</td><td class="ltx_td">42.0'
                    f'<span class="ltx_inline-block">{rank}</span></td><td class="ltx_td">GPT '
                    f'<span class="ltx_inline-block">{rank}</span></td></tr></table>')
    yield "a badge on a value is set apart from it", "| 42.0 (3) |" in md and "| GPT 3 |" in md

    md, images = convert(picture(["0", "1", "2", "epochs"], paths=40))
    yield "plot stays an image", md.strip().startswith("![](images/") and len(images) == 1

    md, _ = convert('<p>As in <span id="x" class="ltx_ERROR undefined">\\Cref</span>'
                    '<span class="ltx_text">sec:what-memory, the</span></p>')
    yield "unresolved \\Cref keeps its label", "As in § what-memory, the" in md

    md, _ = convert('<p><span class="ltx_tabular ltx_markedasmath"><span class="ltx_tr">'
                    + td(math(r"\montraitd\fldr")) + '</span><span class="ltx_tr">' + td(math("n"))
                    + "</span></span> over N.</p>")
    yield "\\vv arrow becomes \\vec", r"$\vec{n}$ over N." in md

    h2m = load("html-to-markdown")
    tree = h2m.forest_nodes(r"""for tree={grow=east, draw=blue},
        [Memory, ver
            [Long Term, fill=x
                [Encoding [MyAgent \citep{a}{,} MemOS~\citep{b}, text width=20em]]
            ]
            [{KV Cache Eviction} [H$_2$O \cite{c}]]
        ]""")
    yield "forest tree parsed", tree is not None and tree[0] == "Memory" and [c[0] for c in tree[1]] == [
        "Long Term", "{KV Cache Eviction}"]
    lists = h2m.forest_html([tree], "")
    yield "forest node text cleaned", "MyAgent, MemOS" in lists[0] and "citep" not in lists[0]
    yield "forest math kept", "x-tex" in lists[0] and "_2" in lists[0]
    article = ('<section id="S4" class="ltx_section"><h2 class="ltx_title ltx_title_section">'
               '<span class="ltx_tag ltx_tag_section">4 </span>Foundational Components</h2>'
               '<section id="S4.SS2" class="ltx_subsection"><h3 class="ltx_title ltx_title_subsection">'
               '<span class="ltx_tag ltx_tag_subsection"><span class="ltx_text">IV-B</span> </span>'
               '<span class="ltx_text ltx_font_italic">Context &amp; Processing</span></h3></section>'
               '<section id="S4.SS2.SSS1" class="ltx_subsubsection"><h4 class="ltx_title ltx_title_subsubsection">'
               '<span class="ltx_tag ltx_tag_subsubsection">4.2.1 </span>Context Processing</h4></section></section>'
               '<section id="S9" class="ltx_paragraph"><h5 class="ltx_title ltx_title_paragraph">'
               'Foundational Components</h5></section>')
    tex = (r"\section{Foundational Components}" "\n" r"\label{sec:found}" "\n"
           r"\subsection{\textcolor{red}{Context \& Processing}}\vspace{-1mm}" "\n" r"\label{subsec:proc} text" "\n"
           r"\subsection{Lost in the HTML}\label{subsec:lost}")
    sections = h2m.section_numbers(article, tex)
    yield "section labels numbered by title and level", sections == {
        "sec:found": ("4", "S4"), "subsec:proc": ("IV-B", "S4.SS2")}
    tree = h2m.forest_nodes(r"""[\ \ Context Engineering\ \ \ , ver
        [\ \ \ Foundational \\ \ \ Components~(\S\ref{sec:found}),ver
            [\ \ \ Context \\ \ Processing~(\S\ref{subsec:proc}) [\eg ~Mamba~\citep{a}{,} YaRN~\citep{b}, leaf]]
            [\ Lost \ (\S\ref{subsec:lost})]]]""")
    twice = ('<section id="S2.SS2"><h3><span class="ltx_tag ltx_tag_subsection">2.2 </span>Reward Modeling</h3></section>'
             '<section id="A1.SS2"><h3><span class="ltx_tag ltx_tag_subsection">A.2 </span>Reward Modeling</h3></section>')
    yield "sections with one title paired in order", h2m.section_numbers(
        twice, r"\subsection{Reward Modeling}\label{rm} \subsection{Reward Modeling}") == {"rm": ("2.2", "S2.SS2")}
    yield "sections with one title left alone when the counts differ", h2m.section_numbers(
        twice, r"\subsection{Reward Modeling}\label{rm}") == {}
    lists = h2m.forest_html([tree], "", sections)
    yield "forest section references resolved", (
        '(<a href="#S4">§4</a>)' in lists[0] and '(<a href="#S4.SS2">§IV-B</a>)' in lists[0])
    yield "forest padding and empty references dropped", (
        "<li>Context Engineering<ul>" in lists[0] and "<li>Foundational Components" in lists[0]
        and "<li>Lost</li>" in lists[0] and "()" not in lists[0] and "Mamba, YaRN" in lists[0])

    md, _ = convert(
        '<div class="ltx_para ltx_noindent"><p class="ltx_p">marginparsep has been altered.\n<br class="ltx_break">'
        'topmargin has been altered.\n<br class="ltx_break"></p></div>'
        '<div class="ltx_para ltx_noindent"><p class="ltx_p">The page layout violates the ICML style.</p></div>'
        '<div class="ltx_para"><p class="ltx_p">Please do not change the page layout, or include packages like '
        'geometry, savetrees, or fullpage, which change it for you.\nWe&#8217;re not able to reliably undo arbitrary '
        'changes to the style. Please remove\nthe offending package(s), or layout-changing commands and try again.</p></div>'
        '<h1 class="ltx_title ltx_title_document">A Paper</h1>'
        '<div class="ltx_para"><p class="ltx_p">The learning rate has been altered. Please remove it.</p></div>')
    yield "style-file warnings dropped", (
        "violates" not in md and "marginparsep" not in md and "savetrees" not in md
        and "offending" not in md
        and "The learning rate has been altered. Please remove it." in md)
    yield "paper version from the margin stamp", h2m.paper_version("<div>arXiv:2505.00675v3 [cs.CL] 24 Dec 2025</div>") == "2505.00675v3"

    named = h2m.name_uncaptioned_images(
        '<img src="2512.06688v1/figures/yes_emoji.png" alt="[Uncaptioned image]">'
        '<img src="2512.06688v1/x12.png" alt="[Uncaptioned image]">')
    yield "an icon gets its file name as alt text", 'alt="yes_emoji"' in named
    yield "a generic file name stays a placeholder", named.count("[Uncaptioned image]") == 1

    labels, entries = h2m.citations_from_bibtex(["jiang2025know", "nokey"], """
        @article{jiang2025know, title={Know Me, Respond to Me}, year={2025},
                 author={Jiang, Bowen and Hao, Zhuoqun and Cho, Young-Min and Li, Bryan}}""")
    yield "citation label from the .bib", labels == {"jiang2025know": "Jiang et al. 2025"}
    yield "reference entry from the .bib", "Know Me, Respond to Me" in entries.get("jiang2025know", "")

    md, _ = convert(f'<p>{math("2true294")} problems, {math("1true558")} lines, {math("x=true0")}.</p>')
    yield "digit groups joined by \"true\" are one number", "$2294$" in md and "$1558$" in md and "true0" in md
    md, _ = convert(f'<p>{math("14.199802true398681true64")} and {math("-4.356true14")}</p>')
    yield "\"true\" between groups of any length is dropped, raw input rounded", "$14.1998$" in md and "$-4.35614$" in md

    md, _ = convert(f'<p>{math(r"{\tt KL\mathchar 45\relax UCB}")}, '
                    f'{math(r"\mathchar 28999\mathchar 12349\delimiter 67273472 x\delimiter 84054785")}, '
                    f'{math(r"\pi\mathrel{\mathop{\mathchar 58\relax}}X")}, {math(r"\mathchar 4944\displaylimits_{i}a")}, '
                    f'{math(r"\texttt{num\char 95\relax pixels}")}, {math(r"(\mathchar 28673\mathchar 28999)")}, {math(r"{a\over\mathchar 28999}")}</p>')
    yield "TeX character codes become the characters", (
        r"{\tt KL-UCB}" in md and "$G=(x)$" in md and r"\mathop{:}}X" in md and r"\sum _{i}a" in md
        and r"\texttt{num\_pixels}" in md and r"(\Delta G)" in md and r"{a\over G}" in md and "mathchar" not in md and "delimiter" not in md and "relax" not in md)

    md, _ = convert(f'<p>{math(r"(\pazocal{S},\mdmathbb{E},\mathscrsfs{E},\widebar{C},\mathbfcal{S}_{3})")} '
                    f'{math(r"\sumop\displaylimits_{m=1}^{N}e_{m}")}</p>')
    yield "fonts loaded under another name are the usual ones", (
        r"\mathcal{S},\mathbb{E},\mathscr{E},\overline{C},\boldsymbol{\mathcal{S}}_{3}" in md
        and r"\sum_{m=1}^{N}e_{m}" in md and "operatorname" not in md)

    md, _ = convert(f'<p>{math(r"k^{\cramped{{}^{\mathsf{T}}}}")} {math(r"\lambda_{1}\cdot\mspace{-26mu}r")} '
                    f'{math(r"\makebox[120.00018pt][l]{Transition:} s")} {math(r"\mathmakebox[1em]{Z}\leftarrow 0")} '
                    f'{math(r"z_{i}{\mathbin{\vbox{\hbox{{\(\textstyle\bullet\)}}}}}z_{j}")} '
                    f'{math(r"\left.\vbox{\vrule height=0.0pt,width=0.0pt}\text{a}\right.")} '
                    f'{math(r"\hbox{\pagecolor{cdelback}\vrule width=0.0pt,height=0.0pt,depth=0.0pt{b}}")} '
                    f'{math(r"\{-1,\scalebox{1}[1.0]{-}1\}")}</p>')
    yield "wrappers that only size, box or colour are dropped", (
        r"k^{{{}^{\mathsf{T}}}}" in md and r"\cdot r" in md and r"\text{Transition:} s" in md
        and r"{Z}\leftarrow 0" in md and r"\mathbin{{\hbox{" in md and r"\left.{}\text{a}\right." in md
        and r"\hbox{{b}}" in md and r"\{-1,{-}1\}" in md
        and not re.search(r"operatorname\{(cramped|mspace|makebox|mathmakebox|vbox|vrule)\}|pagecolor|\[1\.0\]", md))

    md, _ = convert(f'<p>{math(r"-\eta\quantity[\nabla L]")} {math(r"\bqty{\Sigma}+\pqty{a}+\bqty{B\bqty{X}}")} '
                    f'{math(r"\expectationvalue{\nabla S, w}")} {math(r"\expectationvalue{A}{\psi}")}</p>')
    yield "the physics package's brackets and expectation values", (
        r"-\eta[\nabla L]" in md and r"\left[\Sigma\right]+\left(a\right)+\left[B\left[X\right]\right]" in md
        and r"\left\langle \nabla S, w\right\rangle" in md
        and r"\left\langle \psi\middle|A\middle|\psi\right\rangle" in md and "operatorname" not in md)

    md, _ = convert(f'<p>{math(r"c_{\textsubscript{best}}")} {math(r"20\textsuperscript{th}")} '
                    f'{math(r"\mathrm{F\textsubscript{1}}")} {math(r"10\text{\sc{e}-3}")}</p>')
    yield "\\textsubscript in an equation is a subscript; \\sc is dropped", (
        r"c_{\text{best}}" in md and r"20^{\text{th}}" in md and r"\mathrm{F_{\text{1}}}" in md
        and r"10\text{{e}-3}" in md and "textsub" not in md and "textsuper" not in md and "{sc}" not in md)

    md, _ = convert(f'<p>{math(r"p(s_{t}\mids_{t-1})")} {math(r"\displaystyleh=1")} {math(r"\quadZ")} '
                    f'{math(r"\rank(A)+\supp(x)")}</p>')
    yield "a command run into the letter after it is split again; a paper's macro is not", (
        r"p(s_{t}\mid s_{t-1})" in md and r"\displaystyle h=1" in md and r"\quad Z" in md
        and r"\operatorname{rank}(A)" in md and r"\operatorname{supp}(x)" in md)

    md, _ = convert('<p>edits <span class="ltx_text ltx_lstlisting ltx_font_typewriter">'
                    '<span class="ltx_text ltx_lst_identifier">napoleon_use_param</span></span> first.</p>')
    yield "inline listing keeps its code", "`napoleon_use_param`" in md

    md, _ = convert(f'<p>5.4 {math("+0" + chr(92) + "%")}<span class="ltx_text ltx_phantom">'
                    '<span style="visibility:hidden">5</span></span> end</p>')
    yield "phantom text is dropped", "$5" not in md and "end" in md

    sim = r"\mathrel{\mathchoice{\vbox{\hbox{$\scriptstyle\sim$}}}{\vbox{\hbox{$\scriptstyle\sim$}}}" \
          r"{\vbox{\hbox{$\scriptscriptstyle\sim$}}}{\vbox{\hbox{$\scriptscriptstyle\sim$}}}}2000"
    md, _ = convert(f"<p>a pool of {math(sim)} problems</p>")
    yield "\\mathchoice keeps one rendering, unboxed", r"\scriptstyle\sim" in md and "mathchoice" not in md and "vbox" not in md

    md, _ = convert(f'<p>(0% {math(chr(92) + "rightarrow" + chr(92) + "penalty" + chr(92) + " ")}70%)</p>')
    yield "\\penalty with a control space leaves no escaped dollar", r"$\rightarrow$" in md and r"\$" not in md

    md, _ = convert(f'<p>{math(r"\text{pass\textasciicircum k}=1")}</p>')
    yield "\\textasciicircum is kept", r"\text{pass\textasciicircum k}" in md

    md, _ = convert('<p><span class="ltx_text">pass</span>\xa0' + math(r"\hat{}") + '\xa0<span class="ltx_text">1</span> '
                    'and 5\u03035% of failures</p>')
    yield "an empty accent between words is a caret", "pass^1" in md
    yield "a tilde set on a digit goes before the number", "~55%" in md

    md, _ = convert(f'<p>indented{chr(160) * 40}{math("y")} line</p>')
    yield "a run of non-breaking spaces before other math converts", "$y$" in md

    md, _ = convert('<table class="ltx_tabular"><tr class="ltx_tr"><td class="ltx_td ltx_border_tt">Name</td>'
                    '<td class="ltx_td ltx_border_tt">Access</td></tr><tr class="ltx_tr"><td class="ltx_td ltx_border_t">Battles</td>'
                    '<td class="ltx_td ltx_border_t"><span class="ltx_inline-block fas fa-lock" aria-hidden="true"> </span></td></tr>'
                    '<tr class="ltx_tr"><td class="ltx_td">Prompts</td><td class="ltx_td">'
                    '<span class="ltx_inline-block fas fa-globe" aria-hidden="true"> </span></td></tr></table>')
    yield "icon font glyphs are named", "lock" in md and "globe" in md

    md, _ = convert('<div class="ltx_listing"><div class="ltx_listingline">S <span class="ltx_text" style="float:right;">'
                    '<span class="ltx_inline-block ltx_parbox" style="width:0.0pt;"><span class="ltx_p">196.12387pt</span></span>'
                    'Calibrate thresholds</span></div></div>')
    yield "a box's width is not text", "196.12387pt" not in md and "Calibrate" in md

    def float_table(n):
        return ('<table class="ltx_tabular"><tr class="ltx_tr"><td class="ltx_td">Model</td><td class="ltx_td">Score</td></tr>'
                f'<tr class="ltx_tr"><td class="ltx_td">M{n}</td><td class="ltx_td">{n}0.5</td></tr></table>'
                f'<figcaption class="ltx_caption"><span class="ltx_tag ltx_tag_table">Table {n}: </span>Results {n}.</figcaption>')
    md, _ = convert(f'<figure class="ltx_table">{float_table(1)}{float_table(2)}</figure>')
    yield "each caption stays with its own table", md.index("Table 1: Results") < md.index("M2") < md.index("Table 2: Results")

    bibitem = ('<li id="bib.bibx{n}" class="ltx_bibitem"><span class="ltx_tag ltx_tag_bibitem">[2018]</span> '
               '<span class="ltx_bibblock">{authors}</span> <span class="ltx_bibblock">2018. A title.</span></li>')
    md, _ = convert('<p><cite class="ltx_cite">[<a href="#bib.bibx1" class="ltx_ref">2018</a>, '
                    '<a href="#bib.bibx2" class="ltx_ref">2018</a>]</cite></p><ul>'
                    + bibitem.format(n=1, authors="Mihaylov, T.; Clark, P.; and Khot, T.")
                    + bibitem.format(n=2, authors="L. Breiman.") + "</ul>")
    yield "a bare-year citation gets its first author", "[Mihaylov et al. 2018]" in md and "[Breiman 2018]" in md

    md, _ = convert('<h1 class="ltx_title ltx_title_document">Terminal-Bench:<br class="ltx_break">Benchmarking Agents</h1>'
                    "<p>Text.</p>")
    yield "a title broken over two lines is one heading", md.startswith("# Terminal-Bench: Benchmarking Agents\n")

    notes = ('<span class="ltx_author_notes"><span class="ltx_author_notes_content">Affiliation: '
             + ", ".join(f"<sup>{k}</sup>University {k}" for k in range(1, 9)) + "</span></span>")
    md, _ = convert('<div class="ltx_authors">' + "".join(
        f'<span class="ltx_creator ltx_role_author"><span class="ltx_personname">{name}</span>{notes}</span>'
        for name in ("Ada Lovelace", "Alan Turing", "Grace Hopper")) + "</div><p>Text.</p>")
    yield "a shared affiliation list is shown once", md.count("University 8") == 1 and "Grace Hopper" in md

    md, _ = convert('<div class="ltx_authors"><span class="ltx_creator ltx_role_author"><span class="ltx_personname">'
                    'name=Ada Lovelace </span></span> <span class="ltx_author_before"> </span>'
                    '<span class="ltx_creator ltx_role_author"><span class="ltx_personname">affiliation=1 </span></span>'
                    "</div><p>Text.</p>")
    yield "name= and affiliation= are one author", "Ada Lovelace<sup>1</sup>" in md and "name=" not in md

    md, _ = convert('<table class="ltx_equationgroup ltx_eqn_table"><tbody><tr class="ltx_eqn_row">'
                    f'<td class="ltx_eqn_cell" colspan="2">{math(r"\displaystyle\begin{split}q&=a\\ &+b\end{split}")}</td>'
                    '<td class="ltx_eqn_cell ltx_eqn_eqno"><span class="ltx_tag">(1)</span></td></tr></tbody></table>')
    yield "an equation across the columns is a display equation", md.strip().startswith("$$") and r"\tag{1}" in md

    def font(text, classes="ltx_font_bold"):
        return f'<span class="ltx_text {classes}">{text}</span>'

    note = ('<span class="ltx_note ltx_role_footnote"><sup class="ltx_note_mark">1</sup><span class="ltx_note_outer">'
            '<span class="ltx_note_content"><sup class="ltx_note_mark">1</sup> <span class="ltx_tag ltx_tag_note">1</span> '
            "Most samples are short.</span></span></span>")
    md, _ = convert(f'<h2>{font("2 Method")}</h2><p class="ltx_p">{font("Setup. ")}A {font("new", "ltx_font_italic")} '
                    f'dataset{note} of {font(font("pairs"))}.</p><p>After.</p>')
    yield "bold and italics are kept in running text", "**Setup.** A *new* dataset" in md and "**pairs**." in md
    yield "a bold heading is a plain heading", "## 2 Method\n" in md
    yield "a footnote follows its paragraph, its mark printed once", (
        "dataset<sup>1</sup> of" in md and "\n\n<sup>1</sup> Most samples are short.\n\nAfter." in md
        and md.count("<sup>1</sup>") == 2)

    shared = note.replace("Most samples are short.", "Scores from the leaderboard.")
    md, _ = convert('<table class="ltx_tabular"><tr><td class="ltx_td">Model</td><td class="ltx_td">MBPP</td></tr>'
                    f'<tr><td class="ltx_td">A</td><td class="ltx_td">82.3{shared}</td></tr>'
                    f'<tr><td class="ltx_td">B</td><td class="ltx_td">73.8{shared}</td></tr></table>')
    yield "a note marked in several cells is written once", (
        "82.3<sup>1</sup>" in md and "73.8<sup>1</sup>" in md and md.count("Scores from the leaderboard.") == 1)

    md, _ = convert('<figure class="ltx_table"><table class="ltx_tabular"><tr class="ltx_tr">'
                    '<td class="ltx_td ltx_rowspan ltx_rowspan_2" rowspan="2"><span class="ltx_inline-block">\n <span class="ltx_p">'
                    '<span class="ltx_text ltx_font_bold">Llama-3.3</span></span>\n <span class="ltx_p">70b</span>\n </span></td>'
                    '<td class="ltx_td">66.3</td></tr><tr class="ltx_tr"><td class="ltx_td">78.9</td></tr></table></figure>')
    yield "a cell written as HTML loses its padding", '<td rowspan="2"><b>Llama-3.3</b> 70b</td>' in md

    md, _ = convert(f'<p class="ltx_p">0.272<sup class="ltx_sup">{font("†", "ltx_font_italic")}</sup> and '
                    f'{font(" ±0.3 ")} hold.</p><table class="ltx_equation ltx_eqn_table"><tbody>'
                    + eqn_row(math(r"\displaystyle\geq q(U)"), "by Eq.\u00a06", number=1) + "</tbody></table>")
    yield "a dagger or a ± set in italics or bold stays whole", "<sup>*†*</sup>" in md and "**±0.3**" in md
    yield "a no-break space in an equation's text is a space", r"\text{by Eq. 6}" in md and "\ufffd" not in md

    md, _ = convert('<figure class="ltx_table"><table class="ltx_tabular"><tr class="ltx_tr">'
                    f'<td class="ltx_td ltx_border_tt">{font("Model")}</td><td class="ltx_td ltx_border_tt">NDCG</td></tr>'
                    f'<tr class="ltx_tr"><td class="ltx_td ltx_border_t">YetiRank{note}</td>'
                    f'<td class="ltx_td ltx_border_t">{font("50.75")}</td></tr><tr class="ltx_tr"><td class="ltx_td">LambdaMART</td>'
                    f'<td class="ltx_td">{font("50.11", "ltx_framed ltx_framed_underline")}</td></tr></table>'
                    f'<figcaption class="ltx_caption"><span class="ltx_tag ltx_tag_table">{font("Table")} {font("2")}: </span>Results.'
                    "</figcaption></figure>")
    yield "bold and underline mark a table's results", "**50.75**" in md and "<u>50.11</u>" in md
    yield "column titles and the caption's label are not bold", "| Model" in md and "\nTable 2: Results." in md
    yield "a footnote in a cell follows the table", (
        "YetiRank<sup>1</sup>" in md and md.index("Table 2: Results.") < md.index("<sup>1</sup> Most samples"))

    md, _ = convert('<table class="ltx_tabular"><tr class="ltx_tr"><td class="ltx_td ltx_border_tt">Run</td>'
                    '<td class="ltx_td ltx_border_tt"><span class="ltx_text ltx_font_italic" style="position:relative; bottom:-3.5pt;">'
                    '<span class="ltx_text">Pro</span><span class="ltx_text" style="position:relative; bottom:12.0pt;">Gemini 2.5'
                    '</span></span></td></tr><tr class="ltx_tr"><td class="ltx_td ltx_border_t">Kappa</td>'
                    f'<td class="ltx_td ltx_border_t">{math("0.34")}<span class="ltx_text" style="font-size:90%;">0.01</span></td></tr>'
                    '<tr class="ltx_tr"><td class="ltx_td">LiveBench</td><td class="ltx_td">70.9'
                    '<span class="ltx_text" style="--ltx-fg-color:#00E000;">+2.3</span></td></tr></table>')
    yield "a value and the deviation after it are set apart", "$0.34$ 0.01" in md and "70.9 +2.3" in md
    yield "a raised line of a column title is read first", "Gemini 2.5 Pro" in md

    md, _ = convert('<div class="ltx_para"><span class="ltx_ERROR undefined">\\DeclareCaptionType</span>'
                    '<p class="ltx_p">listing[Listing][List of Listings]</p></div>'
                    '<p class="ltx_p">Data: <span class="ltx_ERROR undefined">\\sans</span>(pretrain), ranked '
                    '<em class="ltx_emph">edited</em> ¿ <em class="ltx_emph">chosen</em>; ¿Qué tal?</p>')
    yield "an unknown macro's name is dropped", "sans" not in md and "(pretrain)" in md and "Listing" not in md
    yield "a lone ¿ is the > it was typed as", "*edited* \\> *chosen*" in md and "¿Qué" in md

    md, _ = convert('<section class="ltx_section"><h2 class="ltx_title ltx_title_section">7 Results</h2>'
                    '<p class="ltx_p">Before.</p><figure class="ltx_table"><figcaption class="ltx_caption">'
                    '<span class="ltx_tag ltx_tag_table">Table 7: </span>Query times.</figcaption><div class="ltx_block">'
                    '<table class="ltx_tabular"><tr class="ltx_tr"><td class="ltx_td">varint</td><td class="ltx_td">1.4</td></tr>'
                    '<tr class="ltx_tr"><td class="ltx_td">bitmap</td><td class="ltx_td">2.0</td></tr></table>'
                    '<section class="ltx_section"><h2 class="ltx_title ltx_title_section">8 Discussion</h2>'
                    '<p class="ltx_p">Last words.</p></section></div></figure></section>')
    yield "a float that swallowed the next section ends before it", (
        "| bitmap | 2.0 |" in md and md.index("Table 7: Query times.") < md.index("## 8 Discussion") < md.index("Last words."))

    def th(text, attrs=""):
        return f'<th class="ltx_td ltx_th ltx_th_column" {attrs}>{text}</th>'

    def cells(*texts):
        return "".join(f'<td class="ltx_td">{t}</td>' for t in texts)
    md, _ = convert('<figure class="ltx_table"><table class="ltx_tabular ltx_guessed_headers"><tbody class="ltx_tbody">'
                    f'<tr class="ltx_tr">{th("Method", 'rowspan="2"')}{th("Sentence", 'colspan="2"')}{th("Passage")}</tr>'
                    f'<tr class="ltx_tr">{cells("NoFac", "Fact", "Pear.")}</tr>'
                    f'<tr class="ltx_tr">{th("SelfCk-BERT")}{th("81.96")}{th("44.23")}{th("58.18")}</tr>'
                    f'<tr class="ltx_tr">{cells("SelfCk-QA", "84.26", "48.14", "61.07")}</tr></tbody></table>'
                    '<figcaption class="ltx_caption">Table 3: Detection.</figcaption></figure>')
    head = md[:md.index("</thead>")] if "</thead>" in md else ""
    yield "a header's second row stays under the cell that spans it", (
        '<th rowspan="2">Method</th>' in head and head.index("Sentence") < head.index("NoFac"))
    yield "a row of results marked as a header is a body row", "SelfCk-BERT" not in head and "<td>81.96</td>" in md

    def ruled_th(*texts):
        return "".join(f'<th class="ltx_td ltx_th ltx_th_column ltx_border_t">{t}</th>' for t in texts)
    md, _ = convert('<figure class="ltx_table"><table class="ltx_tabular ltx_guessed_headers"><tbody class="ltx_tbody">'
                    f'<tr class="ltx_tr">{th("Model", 'rowspan="2"')}{th("Empty", 'colspan="2"')}</tr>'
                    f'<tr class="ltx_tr">{cells("ASR", "ISR")}</tr>'
                    f'<tr class="ltx_tr">{ruled_th("GPT-4o-mini", "62%", "100%")}</tr>'
                    f'<tr class="ltx_tr">{cells("Llama-3.1", "52.94%", "100%")}</tr></tbody></table>'
                    '<figcaption class="ltx_caption">Table 1: Attack success.</figcaption></figure>')
    head = md[:md.index("</thead>")] if "</thead>" in md else ""
    yield "a ruled-off row of percentages marked as a header is a body row", (
        "ASR" in head and "GPT-4o-mini" not in head and "62%" in md)
    md, _ = convert('<figure class="ltx_table"><table class="ltx_tabular ltx_guessed_headers"><tbody class="ltx_tbody">'
                    f'<tr class="ltx_tr">{th("Method")}{th("Recall", 'colspan="2"')}</tr>'
                    f'<tr class="ltx_tr">{ruled_th("k", "10", "100")}</tr>'
                    f'<tr class="ltx_tr">{cells("BM25", "0.41", "0.68")}</tr>'
                    f'<tr class="ltx_tr">{cells("DPR", "0.52", "0.75")}</tr></tbody></table>'
                    '<figcaption class="ltx_caption">Table 2: Recall.</figcaption></figure>')
    head = md[:md.index("</thead>")] if "</thead>" in md else md[:md.index("BM25")]
    yield "ruled-off column titles that are whole numbers stay in the header", "100" in head and "0.41" not in head

    def ruled(*texts):
        return "".join(f'<td class="ltx_td ltx_border_t">{t}</td>' for t in texts)
    md, _ = convert('<figure class="ltx_table"><table class="ltx_tabular">'
                    f'<tr class="ltx_tr">{ruled("Benchmark", "Dataset", "Size")}</tr>'
                    f'<tr class="ltx_tr">{ruled("", "Task-specific", "30,000")}</tr>'
                    f'<tr class="ltx_tr">{cells("HaluEval", "General", "5,000")}</tr>'
                    f'<tr class="ltx_tr">{ruled("Med-HALT", "-", "4,916")}</tr></table>'
                    '<figcaption class="ltx_caption">Table 4: Benchmarks.</figcaption></figure>')
    yield "a group's label typed on its last row opens the group, in a pipe table without a span", (
        "rowspan" not in md and bool(re.search(r"\| HaluEval +\| Task-specific", md)) and md.count("HaluEval") == 1)

    def row(*cells):  # each cell: (tag, text[, classes[, attributes]])
        def cell(tag, text, classes="", attrs=""):
            return f'<{tag} class="ltx_td {classes}" {attrs}>{text}</{tag}>'
        return '<tr class="ltx_tr">' + "".join(cell(*c) for c in cells) + "</tr>"
    md, _ = convert('<figure class="ltx_table"><table class="ltx_tabular ltx_guessed_headers"><thead class="ltx_thead">'
                    + row(("th", "", "ltx_border_tt"), ("th", "BernNB", "ltx_border_tt", 'colspan="2"')) + '</thead><tbody class="ltx_tbody">'
                    + row(("th", "Section"), ("td", "TOP1"), ("td", "TOP5"))
                    + row(("th", "Abstract", "ltx_border_t"), ("td", "40.65", "ltx_border_t"), ("td", "63.92", "ltx_border_t"))
                    + row(("th", "Claims"), ("td", "39.37"), ("td", "65.42")) + "</tbody></table></figure>")
    head = md[:md.index("</thead>")] if "</thead>" in md else ""
    yield "a header's label raised over its second row takes that row into the head", (
        '<th rowspan="2">Section</th>' in head and "TOP5" in head and "Abstract" not in head)

    md, _ = convert('<figure class="ltx_table"><table class="ltx_tabular ltx_guessed_headers"><tbody class="ltx_tbody">'
                    + row(("th", "", "ltx_border_tt"), ("th", "Helium", "ltx_border_tt"), ("td", "Moshi", "ltx_border_tt", 'colspan="2"'))
                    + row(("th", "Hyper-parameter"), ("th", "pre"), ("td", "post"), ("td", "fine"))
                    + row(("th", "Temporal Transformer", "ltx_border_t", 'colspan="4"'))
                    + row(("th", "Model dimension", "ltx_border_t"), ("th", "4096", "ltx_border_t"), ("td", "same", "ltx_border_t", 'colspan="2"'))
                    + row(("th", "Heads"), ("th", "32"), ("td", "32"), ("td", "32")) + "</tbody></table></figure>")
    head = md[:md.index("</thead>")] if "</thead>" in md else ""
    yield "the head a raised label opens ends at its group", (
        '<th rowspan="2">Hyper-parameter</th>' in head and "fine" in head and "Temporal" not in head and "Temporal" in md)

    md, _ = convert('<figure class="ltx_table"><table class="ltx_tabular ltx_guessed_headers"><tbody class="ltx_tbody">'
                    + row(("th", "Dataset", "ltx_border_tt"), ("th", "Method", "ltx_border_tt"), ("th", "Error", "ltx_border_tt"))
                    + row(("th", "CIFAR-10", "ltx_border_t", 'rowspan="3"'), ("th", "BatchNorm", "ltx_border_t"), ("th", "6.61", "ltx_border_t"))
                    + row(("td", "Xavier", "ltx_border_t"), ("td", "7.78", "ltx_border_t"))
                    + row(("td", "Fixup"), ("td", "7.24")) + "</tbody></table></figure>")
    head = md[:md.index("</thead>")] if "</thead>" in md else ""
    yield "a guessed header row below the rule, spanning into the body, is a body row", (
        "Error" in head and "CIFAR" not in head and '<td rowspan="3">CIFAR-10</td>' in md and "<td>Xavier</td>\n<td>7.78</td>" in md)

    md, _ = convert('<figure class="ltx_table"><table class="ltx_tabular ltx_guessed_headers"><tbody class="ltx_tbody">'
                    + row(("th", "", "ltx_border_t"), ("td", "Architecture", "ltx_border_t"), ("td", "Err.", "ltx_border_t"))
                    + row(("th", "DNN", "ltx_border_tt"), ("td", "2000-2000 + dropout", "ltx_border_tt"), ("td", "57.8%", "ltx_border_tt"))
                    + row(("th", "SNN-30k", "ltx_border_t", 'rowspan="2"'), ("td", "128c-p-1200L", "ltx_border_t"),
                          ("td", "21.8%", "ltx_border_t", 'rowspan="2"'))
                    + row(("td", "+ dropout")) + "</tbody></table></figure>")
    head = md[:md.index("</thead>")] if "</thead>" in md else ""
    yield "a double rule under the header ends it", "Architecture" in head and "DNN" not in head

    def shaded_table(caption):
        gray = 'style="--ltx-bg-color:#E6E6E6;"'
        return ('<figure class="ltx_table"><table class="ltx_tabular"><tr class="ltx_tr">'
                '<td class="ltx_td ltx_border_tt">Method</td><td class="ltx_td ltx_border_tt">AUROC</td></tr>'
                '<tr class="ltx_tr"><td class="ltx_td ltx_border_t">Probe</td><td class="ltx_td ltx_border_t">0.940</td></tr>'
                f'<tr class="ltx_tr"><td class="ltx_td" {gray}>Prompt</td><td class="ltx_td" {gray}>0.929</td></tr>'
                '<tr class="ltx_tr"><td class="ltx_td">SAE</td><td class="ltx_td">0.695</td></tr></table>'
                f'<figcaption class="ltx_caption"><span class="ltx_tag ltx_tag_table">Table 1: </span>{caption}</figcaption></figure>')
    md, _ = convert(shaded_table("Mean AUROC. Gray indicates non-representation methods."))
    yield "shading the caption refers to is marked", "<mark>Prompt</mark>" in md and md.count("<mark>") == 1
    md, _ = convert(shaded_table("Mean AUROC compared across methods."))
    yield "other shading is dropped", "<mark>" not in md and "Prompt" in md

    def coloured_table(caption):
        def gray(text):
            return f'<span class="ltx_text" style="--ltx-fg-color:#808080;">{text}</span>'
        return ('<figure class="ltx_table"><table class="ltx_tabular"><tr class="ltx_tr">'
                '<td class="ltx_td ltx_border_tt">Topic</td><td class="ltx_td ltx_border_tt">Relevant</td>'
                '<td class="ltx_td ltx_border_tt">Judged</td></tr>'
                '<tr class="ltx_tr"><td class="ltx_td ltx_border_t">19335</td><td class="ltx_td ltx_border_t">53</td>'
                '<td class="ltx_td ltx_border_t">194</td></tr>'
                f'<tr class="ltx_tr"><td class="ltx_td">{gray("47923")}</td><td class="ltx_td">{gray("2")}</td>'
                f'<td class="ltx_td">{gray("148")}</td></tr>'
                '<tr class="ltx_tr"><td class="ltx_td">87181</td><td class="ltx_td">116</td><td class="ltx_td">158</td></tr></table>'
                f'<figcaption class="ltx_caption"><span class="ltx_tag ltx_tag_table">Table 5: </span>{caption}</figcaption></figure>')
    md, _ = convert(coloured_table('Judging statistics. Excluded topics are '
                                   '<span class="ltx_text" style="--ltx-fg-color:#808080;">in gray</span>.'))
    yield "text in a colour the caption refers to is marked", "<mark>47923</mark>" in md and md.count("<mark>") == 1
    md, _ = convert(coloured_table("Judging statistics for the two tasks."))
    yield "other coloured text is left plain", "<mark>" not in md and "47923" in md

    def colour_table(cells, caption, row=""):
        def text(colour, value):
            return f'<span class="ltx_text" style="--ltx-fg-color:{colour};">{value}</span>' if colour else value
        rows = "".join(f'<tr class="ltx_tr" {row if k == 0 else ""}><td class="ltx_td">M{k}</td>'
                       + "".join(f'<td class="ltx_td">{text(c, v)}</td>' for c, v in line) + "</tr>"
                       for k, line in enumerate(cells))
        return ('<figure class="ltx_table"><table class="ltx_tabular"><tr class="ltx_tr"><td class="ltx_td">Model</td>'
                '<td class="ltx_td">A</td><td class="ltx_td">B</td></tr>' + rows + '</table><figcaption class="ltx_caption">'
                f'<span class="ltx_tag ltx_tag_table">Table 2: </span>{caption}</figcaption></figure>')
    red, blue, gray = "#B22222", "#0000FF", "#A6A6A6"
    md, _ = convert(colour_table([[(red, "85.9"), (blue, "60.1")], [(blue, "80.6"), (red, "62.0")], [(None, "70.0"), (None, "50.0")]],
                                 "Results. The red denotes the highest result, and the blue the second highest."))
    yield "each colour a caption names is marked with its name", (
        '<mark class="red">85.9</mark>' in md and '<mark class="blue">80.6</mark>' in md and md.count("<mark") == 4)
    md, _ = convert(colour_table([[(None, "48.8"), (None, "50.1")], [(gray, "29.3"), (None, "43.4")], [(None, "70.0"), (gray, "50.0")]],
                                 "Results. Gray numbers indicate usage of closed-set training data.",
                                 row='style="--ltx-bg-color:#E6E6E6;"'))
    yield "a caption about gray numbers marks the numbers, not a gray row", (
        "<mark>29.3</mark>" in md and "<mark>50.0</mark>" in md and "M0</mark>" not in md and md.count("<mark") == 2)
    green = "#1B8E3E"
    md, _ = convert(colour_table([[(green, "✓"), (gray, "✓")], [(gray, "✓"), (None, "✗")], [(green, "✓"), (None, "✗")]],
                                 f'Marks: <span class="ltx_text" style="--ltx-fg-color:{green};">✓</span>: covered; '
                                 f'<span class="ltx_text" style="--ltx-fg-color:{gray};">✓</span>: partly covered; ✗: not covered.'))
    yield "a legend set in the table's colours marks both", (
        '<mark class="green">✓</mark>: covered' in md and '<mark class="gray">✓</mark>: partly' in md
        and md.count('<mark class="green">') == 3 and md.count('<mark class="gray">') == 3)

    def coloured(colour, text, layer="fg"):
        return f'<span class="ltx_text" style="--ltx-{layer}-color:{colour};">{text}</span>'

    def coloured_math(tex, tokens):
        """A formula whose symbols are (text, colour or None), as LaTeXML colours them."""
        mrow = "".join(f'<mn style="--ltx-fg-color:{c};" mathcolor="{c}">{t}</mn>' if c else f"<mn>{t}</mn>"
                       for t, c in tokens)
        return (f'<math class="ltx_Math" alttext="{tex}" display="inline"><semantics><mrow>{mrow}</mrow>'
                f'<annotation encoding="application/x-tex">{tex}</annotation></semantics></math>')

    md, _ = convert(colour_table([[(None, "Ron Weasley " + coloured(red, "is a President") + " of Hogwarts."), (None, "x")],
                                  [(None, "He " + coloured(blue, "plays chess") + "."), (None, "y")]],
                                 "Inconsistencies (in red); the parts of the input they contradict are in blue."))
    yield "coloured words inside a cell are marked", (
        '<mark class="red">is a President</mark> of Hogwarts' in md and '<mark class="blue">plays chess</mark>' in md)
    md, _ = convert(colour_table([[(None, "6.2 " + coloured_math("+15\\%", [("+", gray), ("15", gray), ("%", "#000000")])),
                                   (None, "5.4")],
                                  [(None, coloured_math("\\underline{72.3}", [("72.3", blue)])), (None, "70.1")]],
                                 "Accuracy. The gray text is the gain over the baseline; the best is in blue."))
    yield "a formula set in a colour the caption names is marked", (
        '6.2 <mark class="gray">$+15\\%$</mark>' in md and '<mark class="blue">$\\underline{72.3}$</mark>' in md)
    def shaded_row(colour, *cells):
        return '<tr class="ltx_tr">' + "".join(f'<td class="ltx_td" style="--ltx-bg-color:{colour};">{c}</td>' for c in cells) + "</tr>"
    md, _ = convert('<figure class="ltx_table"><table class="ltx_tabular"><tr class="ltx_tr"><td class="ltx_td">Step</td>'
                    '<td class="ltx_td">GQA</td><td class="ltx_td">MME</td></tr>'
                    + shaded_row("#D9F2FF", "+VQA-v2", "47.0", "1197") + shaded_row("#FFE6F2", "13B", "46.8", "1323")
                    + '<tr class="ltx_tr"><td class="ltx_td">final</td><td class="ltx_td">62.0</td><td class="ltx_td">1510</td></tr>'
                    '</table><figcaption class="ltx_caption"><span class="ltx_tag ltx_tag_table">Table 2: </span>'
                    f'Scaling results on {coloured("#D9F2FF", "◼")} data and {coloured("#FFE6F2", "◼")} model.</figcaption></figure>')
    yield "a legend box in a text colour marks the rows shaded in it", (
        '<mark class="blue">+VQA-v2</mark>' in md and '<mark class="pink">13B</mark>' in md and '<mark class="blue">◼</mark> data' in md)
    md, _ = convert('<figure class="ltx_table"><table class="ltx_tabular"><tr class="ltx_tr">'
                    '<td class="ltx_td ltx_colspan ltx_colspan_2" colspan="2" style="--ltx-bg-color:#FFE6CC;">Long-tail Knowledge</td></tr>'
                    '<tr class="ltx_tr"><td class="ltx_td">Jacobi</td><td class="ltx_td">68.9%</td></tr>'
                    '<tr class="ltx_tr"><td class="ltx_td ltx_colspan ltx_colspan_2" colspan="2" style="--ltx-bg-color:#CCFFFF;">'
                    'Semantic Coherence</td></tr><tr class="ltx_tr"><td class="ltx_td">the</td><td class="ltx_td">40.1%</td></tr>'
                    '</table><figcaption class="ltx_caption"><span class="ltx_tag ltx_tag_table">Table 5: </span>Probabilities. '
                    'Orange section: factual tokens. Cyan section: function words.</figcaption></figure>')
    yield "a header row in a colour the caption names is marked", (
        '<mark class="orange">Long-tail Knowledge</mark>' in md and '<mark class="cyan">Semantic Coherence</mark>' in md)
    purple, green = "#E069FF", "#BDFF3D"
    md, _ = convert('<figure class="ltx_float ltx_float_algorithm ltx_framed_top"><figcaption class="ltx_caption">'
                    '<span class="ltx_tag ltx_tag_float">Algorithm 1 </span>'
                    f'{coloured(purple, "SGD with L2 regularization", "bg")} and {coloured(green, "SGD with decoupled weight decay", "bg")}'
                    '</figcaption><div class="ltx_listing ltx_listing">'
                    f'<div class="ltx_listingline">6: g ← ∇f {coloured(purple, "+λθ", "bg")}</div>'
                    f'<div class="ltx_listingline">9: θ ← θ − m {coloured(green, "−ηλθ", "bg")}</div></div></figure>')
    yield "an algorithm's lines in the colours of its caption are marked", (
        '<mark class="purple">+λθ</mark>' in md and '<mark class="green">−ηλθ</mark>' in md
        and '<mark class="purple">SGD with L2 regularization</mark>' in md)

    md, _ = convert('<table class="ltx_tabular"><tr class="ltx_tr"><td class="ltx_td">Finding</td><td class="ltx_td">'
                    '<table class="ltx_tabular"><tr class="ltx_tr"><td class="ltx_td">' + math("\\bullet")
                    + ' Developers <span class="ltx_text ltx_font_bold">forecast</span> a speed-up</td></tr>'
                    '<tr class="ltx_tr"><td class="ltx_td">of <span class="ltx_text ltx_font_italic">24%</span></td></tr>'
                    '</table></td></tr><tr class="ltx_tr"><td class="ltx_td">Other</td><td class="ltx_td">plain</td></tr></table>')
    yield "a cell broken over lines keeps its formulas, bold and italics", (
        "$\\bullet$ Developers **forecast** a speed-up of *24%*" in md)

    md, _ = convert('<p class="ltx_p">The analytical ones in <span class="ltx_text ltx_font_bold">green<span class="ltx_text '
                    'ltx_font_medium"> are from (13). The empirical</span></span> ones.</p><p class="ltx_p">A '
                    '<span class="ltx_text ltx_ulem_uline ltx_font_bold">0.81</span>, <span class="ltx_text ltx_ulem_uline">0.7'
                    '</span>, <span class="ltx_text" style="text-decoration:line-through;;">93.2</span> and <span class="ltx_text '
                    'ltx_font_medium">plain</span>.</p>')
    yield "\\mdseries ends the bold around it", "**green** are from (13). The empirical ones." in md
    yield "ulem's underline and a struck-out value are kept", (
        "<u>**0.81**</u>" in md and "<u>0.7</u>" in md and "~~93.2~~" in md and " plain." in md)
    md, _ = convert('<table class="ltx_tabular"><tr class="ltx_tr"><td class="ltx_td">GPT-4</td><td class="ltx_td">'
                    '<span class="ltx_text ltx_ulem_uline">8</span>0.84</td><td class="ltx_td">87.6</td></tr></table>')
    yield "a number underlined from its first digit is underlined whole", "<u>80.84</u>" in md

    h2m = load("html-to-markdown")
    yield "links to the paper's own arXiv page stay in the paper", h2m.local_links(
        '<a href="https://arxiv.org/html/2302.07730v4#S1.SS1">1.1</a> <a href="https://arxiv.org/html/2302.07730#S2">2</a> '
        '<a href="https://arxiv.org/html/2401.00001v1#S2">other</a>', "2302.07730v4") == (
        '<a href="#S1.SS1">1.1</a> <a href="#S2">2</a> <a href="https://arxiv.org/html/2401.00001v1#S2">other</a>')

    cross = ('<svg id="S3.T2.pic1" class="ltx_picture" height="10.02" overflow="visible" version="1.1" viewBox="0 0 10.02 10.02" '
             'width="10.02"><g fill="#000000" stroke="#000000" transform="translate(0,10.02) matrix(1 0 0 -1 0 0)">'
             '<path style="fill:none" d="M 0 0 C 3.16 3.9 5.16 5.9 9.05 9.05"></path>'
             '<path style="fill:none" d="M 1.81 8.6 C 3.77 5.3 4.95 3.53 7.24 0.45"></path></g></svg>')
    empty = ('<svg id="alg1.l2.pic3" class="ltx_picture" height="1" overflow="visible" version="1.1" viewBox="0 0 1 1" width="1">'
             '<g transform="translate(0,1) matrix(1 0 0 -1 0 0)"></g></svg>')
    with tempfile.TemporaryDirectory() as cache:
        drawn = h2m.repair_svg(re.sub(r'\s(?:xml:)?id="[^"]*"', "", cross)).encode("utf-8")
        (Path(cache) / "icons").mkdir()
        (Path(cache) / "icons" / (hashlib.sha256(drawn).hexdigest() + ".txt")).write_text("✗", encoding="utf-8")
        md, images = convert('<table class="ltx_tabular"><tr class="ltx_tr"><td class="ltx_td">Repo</td><td class="ltx_td">Unbiased?</td>'
                             f'<td class="ltx_td">Yes</td></tr><tr class="ltx_tr"><td class="ltx_td">trl</td><td class="ltx_td">{cross}</td>'
                             '<td class="ltx_td"><object type="image/svg+xml" data="yes.svg" width="10" height="1"></object>'
                             f'</td></tr></table><p class="ltx_p">Step{empty} one.</p>',
                             env={"PAPERLIB_ICONS": "haiku", "PAPERS_CACHE": cache})
    yield "a small drawn symbol is read as text, by its cached reading", bool(re.search(r"\| trl +\| ✗ +\|", md))
    yield "a small <object> keeps its file's name, an empty picture goes", (
        "![yes](yes.svg)" in md and "Step one." in md and not images)

    def panel(rows, label):
        body = "".join('<tr class="ltx_tr">' + "".join(f'<td class="ltx_td">{c}</td>' for c in row) + "</tr>" for row in rows)
        return (f'<figure class="ltx_table ltx_figure_panel"><table class="ltx_tabular">{body}</table>'
                f'<figcaption class="ltx_caption"><span class="ltx_tag ltx_tag_table">({label}) </span>Panel.</figcaption></figure>')
    md, _ = convert('<figure class="ltx_table"><div class="ltx_flex_figure">'
                    + panel([["", "coding", "bits"], ["BP128", "1700", "17"], ["PFOR", "380", "16"], ["BP32", "790", "15"]], "a")
                    + panel([["coding", "bits"], ["1800", "7.0"], ["440", "6.8"], ["840", "5.8"]], "b")
                    + '</div><figcaption class="ltx_caption"><span class="ltx_tag ltx_tag_table">Table 4: </span>Speed.'
                    "</figcaption></figure>")
    yield "a panel without row labels gets its neighbour's", bool(
        __import__("re").search(r"\| PFOR +\| 440 +\| 6\.8", md)) and md.count("BP32") == 2

    md, _ = convert('<table class="ltx_tabular"><tr class="ltx_tr"><td class="ltx_td ltx_border_tt">Task</td>'
                    '<td class="ltx_td ltx_border_tt">Domain</td><td class="ltx_td ltx_border_tt">Size</td></tr>'
                    '<tr class="ltx_tr"><td class="ltx_td ltx_border_t" rowspan="2">Retrieval</td><td class="ltx_td ltx_border_t">Web</td>'
                    '<td class="ltx_td ltx_border_t">502</td></tr><tr class="ltx_tr"><td class="ltx_td">News</td><td class="ltx_td">57</td></tr>'
                    '<tr class="ltx_tr"><td class="ltx_td"></td><td class="ltx_td">Wiki</td><td class="ltx_td">176</td></tr>'
                    '<tr class="ltx_tr"><td class="ltx_td" rowspan="2">QA</td><td class="ltx_td">Web</td><td class="ltx_td">78</td></tr>'
                    '<tr class="ltx_tr"><td class="ltx_td">Books</td><td class="ltx_td">9</td></tr></table>')
    yield "a row label spanning a group takes the group's last row", (
        '<td rowspan="3">Retrieval</td>' in md and "<td></td>" not in md and "<td>Wiki</td>" in md)

    header = row(("td", "Set", "ltx_border_tt"), ("td", "Model", "ltx_border_tt"), ("td", "WER", "ltx_border_tt"))
    md, _ = convert('<table class="ltx_tabular">' + header
                    + row(("td", "YT", "ltx_border_t", 'rowspan="2"'), ("td", "De", "ltx_border_t"), ("td", "7.3", "ltx_border_t"))
                    + row(("td", "AVG"), ("td", "7.5"))
                    + row(("td", "", "ltx_border_t"), ("td", "De", "ltx_border_t"), ("td", "4.8", "ltx_border_t"))
                    + row(("td", ""), ("td", "En"), ("td", "5.9"))
                    + row(("td", "VB-Multi"), ("td", "AVG"), ("td", "5.0")) + "</table>")
    yield "a row label is not stretched over the next group, under a rule", (
        '<td rowspan="2">YT</td>' in md and '<td rowspan="3">VB-Multi</td>' in md)

    md, _ = convert('<table class="ltx_tabular">' + header
                    + row(("td", "YT", "ltx_border_t", 'rowspan="2"'), ("td", "De"), ("td", "7.3"))
                    + row(("td", "AVG"), ("td", "7.5"))
                    + row(("td", ""), ("td", "De"), ("td", "4.8"))
                    + row(("td", ""), ("td", "En"), ("td", "5.9"))
                    + row(("td", "VB-Multi"), ("td", "AVG"), ("td", "5.0")) + "</table>")
    yield "nor over the rows above a lone label, which are that label's", (
        '<td rowspan="2">YT</td>' in md and md.count("<td></td>") == 2)

    md, _ = convert('<table class="ltx_tabular">'
                    + row(("td", "Pointers", "ltx_border_tt"), ("td", "GRU", "ltx_border_tt"), ("td", "MOSE", "ltx_border_tt", 'colspan="2"'))
                    + row(("td", "", "ltx_border_t"), ("td", "", "ltx_border_t"), ("td", "73.1", "ltx_border_t"), ("td", "64.5", "ltx_border_t"))
                    + row(("td", ""), ("td", "✓"), ("td", "72.3"), ("td", "65.3"))
                    + row(("td", "✓"), ("td", ""), ("td", "73.0"), ("td", "68.3")) + "</table>")
    yield "a mark on a group's last row is that row's, not the group's label", (
        "rowspan" not in md and "<td>✓</td>\n<td></td>\n<td>73.0</td>" in md)

    header = row(("td", "Type", "ltx_border_tt"), ("td", "Model", "ltx_border_tt"), ("td", "Size", "ltx_border_tt"))
    md, _ = convert('<table class="ltx_tabular">' + header
                    + row(("td", "", "ltx_border_t"), ("td", "BERT", "ltx_border_t"), ("td", "110M", "ltx_border_t"))
                    + row(("td", "Encoder-Only"), ("td", "RoBERTa"), ("td", "355M"))
                    + row(("td", ""), ("td", "XLNet"), ("td", "340M"))
                    + row(("td", "", "ltx_border_t"), ("td", "GPT-1", "ltx_border_t"), ("td", "120M", "ltx_border_t"))
                    + row(("td", "Decoder-Only"), ("td", "GPT-2"), ("td", "1.5B")) + "</table>")
    yield "a group's label centred on its middle row by hand opens the group", (
        "rowspan" not in md and bool(re.search(r"\| Encoder-Only +\| BERT", md))
        and bool(re.search(r"\| Decoder-Only +\| GPT-1", md)) and md.count("Encoder-Only") == 1)

    md, _ = convert('<table class="ltx_tabular">'
                    + row(("td", "Architecture", "ltx_border_tt"), ("td", "Coupling", "ltx_border_tt"), ("td", "Flow", "ltx_border_tt"))
                    + row(("td", "Coupling", "ltx_border_t", 'rowspan="2"'), ("td", "Affine", "ltx_border_t"), ("td", "RealNVP", "ltx_border_t"))
                    + row(("td", "Splines", "ltx_border_t", 'rowspan="2"'), ("td", "cubic", "ltx_border_t"))
                    + row(("td", ""), ("td", ""), ("td", "RQ-NSF"))
                    + row(("td", ""), ("td", "Bijective", "ltx_border_t"), ("td", "RAD", "ltx_border_t"))
                    + row(("td", "Residual", "ltx_border_t"), ("td", "", "ltx_border_t"), ("td", "iResNet", "ltx_border_t")) + "</table>")
    yield "a label counted short spans its group to the next rule, nested in another", (
        '<td rowspan="4">Coupling</td>' in md and '<td rowspan="2">Splines</td>' in md and "<td></td>\n<td>RQ-NSF" not in md)

    md, _ = convert('<table class="ltx_tabular">'
                    + row(("td", "Data", "ltx_border_tt"), ("td", "Size", "ltx_border_tt"), ("td", "Prompt", "ltx_border_tt"))
                    + row(("td", "LLaVA", "ltx_border_t"), ("td", "158K", "ltx_border_t"), ("td", "–", "ltx_border_t"))
                    + row(("td", "VQAv2", "ltx_border_t"), ("td", "83K", "ltx_border_t"), ("td", "Answer briefly.", "ltx_border_t"))
                    + row(("td", "GQA"), ("td", "72K"), ("td", ""))
                    + row(("td", "TextCaps", "ltx_border_t"), ("td", "22K", "ltx_border_t"), ("td", "Caption it.", "ltx_border_t"))
                    + row(("td", "Total", "ltx_border_t"), ("td", "665K", "ltx_border_t"), ("td", "", "ltx_border_t")) + "</table>")
    yield "a group's one entry outside the first column, on its first row, is left as typed", (
        "rowspan" not in md and bool(re.search(r"\| GQA +\| 72K +\| +\|", md)) and md.count("Answer briefly") == 1)

    md, _ = convert('<table class="ltx_tabular">'
                    + row(("td", "Model", "ltx_border_tt"), ("td", "Data", "ltx_border_tt"), ("td", "Size", "ltx_border_tt"))
                    + row(("td", "LLaMA", "ltx_border_t"), ("td", "", "ltx_border_t"), ("td", "7B", "ltx_border_t"))
                    + row(("td", "Alpaca"), ("td", "Web"), ("td", "7B"))
                    + row(("td", "PaLM", "ltx_border_t"), ("td", "Books", "ltx_border_t"), ("td", "8B", "ltx_border_t"))
                    + row(("td", "Flan"), ("td", "Books"), ("td", "8B")) + "</table>")
    yield "a group's one entry outside the first column, below its first row, opens the group", (
        "rowspan" not in md and bool(re.search(r"\| LLaMA +\| Web +\| 7B", md)) and md.count("Web") == 1)

    md, _ = convert('<table class="ltx_tabular">'
                    + row(("td", "Model", "ltx_border_tt"), ("td", "Venue", "ltx_border_tt"), ("td", "F1", "ltx_border_tt"))
                    + row(("td", "A", "ltx_border_t"), ("td", "ICLR", "ltx_border_t"), ("td", "70.1", "ltx_border_t"))
                    + row(("td", "B"), ("td", ""), ("td", "71.0"))
                    + row(("td", "C", "ltx_border_t"), ("td", "NeurIPS", "ltx_border_t"), ("td", "72.3", "ltx_border_t"))
                    + row(("td", "D"), ("td", "ACL"), ("td", "73.0"))
                    + row(("td", "E"), ("td", ""), ("td", "73.4")) + "</table>")
    yield "a column whose groups leave some cells empty among filled ones keeps its blanks", (
        bool(re.search(r"\| B +\| +\| 71\.0", md)) and md.count("ICLR") == 1)

    md, _ = convert('<table class="ltx_tabular">'
                    + row(("th", "", "ltx_border_tt"), ("th", "", "ltx_border_tt"), ("th", "TPR", "ltx_border_tt", 'colspan="2"'))
                    + row(("th", "Dataset"), ("th", "Detector"), ("th", "@1%"), ("th", "@5%"))
                    + row(("th", "", "ltx_border_t"), ("th", "PPL", "ltx_border_t"), ("td", "0.94", "ltx_border_t"), ("td", "0.98", "ltx_border_t"))
                    + row(("th", "Writing"), ("th", "X-PPL"), ("td", "0.59"), ("td", "0.79"))
                    + row(("th", "Prompts"), ("th", "Ours"), ("td", "0.92"), ("td", "0.98"))
                    + row(("th", "Sampling", "ltx_border_tt", 'rowspan="2"'), ("th", "Random", "ltx_border_tt"),
                          ("td", "M1", "ltx_border_tt"), ("td", "M2", "ltx_border_tt"))
                    + row(("th", "Active"), ("td", "M3"), ("td", "M4")) + "</table>")
    head = md[:md.index("</thead>")] if "</thead>" in md else ""
    yield "a header's label is raised beside a body column it cannot fix", (
        '<th rowspan="2">Dataset</th>' in head and "Sampling" not in head and '<th rowspan="2">Sampling</th>' in md)

    md, _ = convert('<table class="ltx_tabular">'
                    + row(("th", "", "ltx_border_tt"), ("th", "", "ltx_border_tt"), ("td", "Data usage", "ltx_border_tt", 'colspan="2"'))
                    + row(("th", ""), ("th", ""), ("td", "GT", "ltx_border_t"), ("td", "LLM", "ltx_border_t"))
                    + row(("th", "Sampling", "", 'rowspan="2"'), ("th", "Random", "ltx_border_t"), ("td", "M1", "ltx_border_t"),
                          ("td", "M2", "ltx_border_t"))
                    + row(("th", "Active"), ("td", "M3"), ("td", "M4")) + "</table>")
    head = md[:md.index("</thead>")] if "</thead>" in md else ""
    yield "a label spanning rows under the header is not raised into it", "Sampling" not in head and "M1" not in head

    md, _ = convert('<table class="ltx_tabular">'
                    + row(("td", "Task", "ltx_border_tt"), ("td", "Size", "ltx_border_tt"), ("td", "LR", "ltx_border_tt"))
                    + row(("td", "", "ltx_border_t"), ("td", "336M", "ltx_border_t"), ("td", "", "ltx_border_t"))
                    + row(("td", "MNLI"), ("td", "1.3B"), ("td", "1e-5"))
                    + row(("td", "QQP", "ltx_border_t"), ("td", "336M", "ltx_border_t"), ("td", "5e-5", "ltx_border_t"))
                    + row(("td", ""), ("td", "1.3B"), ("td", "3e-5")) + "</table>")
    yield "a number alone in a group is not repeated over it", (
        md.count("1e-5") == 1 and bool(re.search(r"\| MNLI +\| 336M", md)))

    cite = '(<a href="#bib.bib30">Socher et al., 2013b</a>)'
    md, _ = convert('<table class="ltx_tabular">'
                    + row(("td", "Model", "ltx_border_tt"), ("td", "Error rate", "ltx_border_tt"), ("td", "Error rate", "ltx_border_tt"))
                    + row(("td", ""), ("td", "(Positive/"), ("td", "(Fine-"))
                    + row(("td", ""), ("td", "Negative)"), ("td", "grained)"))
                    + row(("td", "Naïve Bayes", "ltx_border_t"), ("td", "18.2 %", "ltx_border_t"), ("td", "59.0%", "ltx_border_t"))
                    + row(("td", cite), ("td", ""), ("td", ""))
                    + row(("td", "SVMs " + cite), ("td", "20.6%"), ("td", "59.3%"))
                    + row(("td", "Supervised"), ("td", ""), ("td", ""))
                    + row(("td", "Paragraph Vector"), ("td", "12.2%"), ("td", "51.3%")) + "</table>")
    yield "a citation or a column title continued on a row of its own joins its cell", (
        "Error rate (Positive/Negative)" in md and "Error rate (Fine-grained)" in md
        and bool(re.search(r"\| Naïve Bayes \(\[Socher et al\., 2013b\]\(#bib\.bib30\)\) +\| 18\.2 %", md))
        and bool(re.search(r"\| Supervised +\| +\| +\|", md)) and len(re.findall(r"^\|", md, re.M)) == 6)

    md, _ = convert('<table class="ltx_tabular">'
                    + row(("td", "Category", "ltx_border_tt"), ("td", "Phenomena", "ltx_border_tt"), ("td", "Size", "ltx_border_tt"))
                    + row(("td", "Lexical Semantics", "ltx_border_t", 'rowspan="2"'), ("td", "Entailment, Negation,", "ltx_border_t"),
                          ("td", "368", "ltx_border_t", 'rowspan="2"'))
                    + row(("td", "Symmetry, Redundancy"))
                    + row(("td", "Logic", "ltx_border_t"), ("td", "", "ltx_border_t"), ("td", "364", "ltx_border_t"))
                    + row(("td", "", "ltx_border_t"), ("td", "", "ltx_border_t"), ("td", "Pointwise, Pairwise,", "ltx_border_t"))
                    + row(("td", "CompassJudger"), ("td", "Various"), ("td", "&amp; Generative")) + "</table>")
    yield "a list going on under a row label joins its cell, a fragment above its row the row below", (
        "rowspan" not in md and "Entailment, Negation, Symmetry, Redundancy" in md
        and "Pointwise, Pairwise, & Generative" in md and len(re.findall(r"^\|", md, re.M)) == 5)

    md, _ = convert('<table class="ltx_tabular">'
                    + row(("td", "Scale", "ltx_border_tt"), ("td", "Im2GPS", "ltx_border_tt"), ("td", "PlaNet", "ltx_border_tt"))
                    + row(("td", ""), ("td", ""), ("td", "MobileNet"))
                    + row(("td", "Continent", "ltx_border_t"), ("td", "51.9%", "ltx_border_t"), ("td", "79.3%", "ltx_border_t"))
                    + row(("td", "Country"), ("td", "35.4%"), ("td", "60.3%")) + "</table>")
    yield "a column title's second line joins it", "| PlaNet MobileNet |" in md and len(re.findall(r"^\|", md, re.M)) == 4

    h2m = load("html-to-markdown")
    tex = (r"\begin{table}\begin{tabular}{@{}l|c|cc@{}}\toprule Prompt & Shots & \multicolumn{2}{c}{F1} \\ \midrule"
           "\n & 6 & 73.76 & 90.24 \\\\\n\\multirow{-2}{*}{Fewshot-related} & 10 & 76.56 & 90.80 \\\\\n"
           " & 6 & 77.86 & 89.44 \\\\\n\\multirow{-2}{*}{\\textbf{Fewshot-random}} & 10 & 80.51 & 89.05 \\\\\n"
           "Hand-written rules & 0 & 81.49 & 87.65 \\\\ \\bottomrule\\end{tabular}\\end{table}")
    files, h2m.source_files = h2m.source_files, lambda version: {"main.tex": "\\documentclass{article}" + tex}

    def unruled(head):
        return ('<table class="ltx_tabular">' + head
                + row(("th", ""), ("th", "6"), ("td", "73.76"), ("td", "90.24"))
                + row(("th", "Fewshot-related"), ("th", "10"), ("td", "76.56"), ("td", "90.80"))
                + row(("th", ""), ("th", "6"), ("td", "77.86"), ("td", "89.44"))
                + row(("th", '<span class="ltx_text ltx_font_bold">Fewshot-random</span>'), ("th", "10"), ("td", "80.51"), ("td", "89.05"))
                + row(("th", "Hand-written rules"), ("th", "0"), ("td", "81.49"), ("td", "87.65")) + "</table>")
    page = '<base href="/html/2310.11244v4/">'
    flat = h2m.source_row_spans(unruled(row(("th", "Prompt"), ("th", "Shots"), ("td", "F1"), ("td", ""))), page)
    spanned = h2m.source_row_spans(unruled(row(("th", "Prompt"), ("th", "Shots"), ("td", "F1", "", 'colspan="2"'))), page)
    h2m.source_files = files
    yield "a \\multirow{-2} LaTeXML dropped takes its rows from the source", (
        flat.index("Fewshot-related") < flat.index(">10<") and "rowspan" not in flat
        and re.search(r'rowspan="2"[^>]*>Fewshot-related<', spanned) and 'rowspan="2"' in spanned.split("90.80")[1]
        and spanned.count("<tr") == 6 and spanned.count("<th") == 10)

    cited = h2m.unknown_citations(
        "<p>introduced by Google researchers in 2017 ( ?). The encoder-decoder models ( ?) came first.</p>",
        r"introduced by Google researchers in 2017 \protect~\shortcite{vaswani2017attention}. Nothing else.",
        "@article{vaswani2017attention, author={Vaswani, Ashish and Shazeer, Noam and Parmar, Niki}, "
        "title={Attention is all you need}, year={2017}}")
    yield "a citation with no key left is found in the LaTeX source", (
        "(Vaswani et al. 2017)" in cited and "models ( ?)" in cited)

    tex = r"and 17 widely used \emph{agentic} benchmarks (Table \ref{tab:all}). As shown in Figure~\ref{fig:flow}, we then"
    files, h2m.source_files = h2m.source_files, lambda version: {
        "appendix.tex": "\\documentclass{article}\\begin{document}More.\\end{document}",
        "paper.tex": "\\documentclass{article}\\begin{document}\\input{intro} % \\ref{no}\n\\end{document}",
        "intro.tex": "The walk is shown in Figure \\ref{fig:toy}."}
    spliced = h2m.latex_source("1403.6652v2")
    h2m.source_files = files
    yield "the paper is the longest document of its source, its \\input files spliced in", (
        "Figure \\ref{fig:toy}" in spliced and "{no}" not in spliced and "More" not in spliced)
    table = "\\begin{{table}}\\caption{{Multi-label classification results in \\{0}}}\\label{{tbl:{0}}}\\end{{table}}"
    caption = '<figcaption class="ltx_caption"><span class="ltx_tag ltx_tag_table">Table {}: </span>Multi-label classification results in {}</figcaption>'
    samples = ("\\begin{figure}\\begin{subfigure}\\caption{Normal model, no trigger}\\end{subfigure}"
               "\\caption[]{Samples from our models}\\label{fig:samples}\\end{figure}")
    files, h2m.source_files = h2m.source_files, lambda version: {
        "paper.tex": "\\documentclass{article}" + table.format("blog") + table.format("flickr") + table.format("youtube") + samples
                     + "\\begin{equation}x\\label{eq:objective}\\end{equation}"}
    resolved = h2m.unresolved_citations(
        caption.format(2, "BlogCatalog") + caption.format(3, "Flickr") + caption.format(4, "YouTube")
        + '<figcaption class="ltx_caption"><span class="ltx_tag ltx_tag_figure">(a) </span>Normal model, no trigger</figcaption>'
        + '<figcaption class="ltx_caption"><span class="ltx_tag ltx_tag_figure">Figure 9: </span>Samples from our models</figcaption>'
        + '<p>See Table <span class="ltx_ref ltx_missing_label ltx_ref_self">LABEL:tbl:youtube</span> and '
        'Table <span class="ltx_ref ltx_missing_label ltx_ref_self">LABEL:tbl:blog</span> and '
        'Figure <span class="ltx_ref ltx_missing_label ltx_ref_self">LABEL:fig:samples</span>. '
        'Eq. <span class="ltx_ref ltx_missing_label ltx_ref_self">LABEL:eq:objective</span></p>',
        '<base href="/html/1403.6652v2/">')
    h2m.source_files = files
    yield "captions that open alike are numbered by their order in the source", "See Table 4 and Table 2 and" in resolved
    yield "a label takes the caption before it, not a sub-figure's", "and Figure 9." in resolved
    yield "a label outside a float does not take the float's number", "Eq. objective</p>" in resolved
    yield "an empty reference is found in the LaTeX source", (
        h2m.label_in_source("17 widely used <em>agentic</em> benchmarks (Table ", tex) == "tab:all"
        and h2m.label_in_source("held out. As shown in Figure ", tex) == "fig:flow"
        and h2m.label_in_source("something else entirely in Table ", tex) is None)

    captions = load("caption-numbers")
    pdf_caps = [("Table 6", captions.words("Agreement between two types of judges on Chatbot Arena.")),
                ("Figure 2", captions.words("Agreement and win rate difference. Each point")),
                ("Table 7", captions.words("Category-wise win rate of models."))]
    yield "caption numbers follow the PDF", (
        captions.pdf_label("Agreement and win rate difference. Each point corresponds", "Table 7", pdf_caps) == "Figure 2"
        and captions.pdf_label("Category-wise win rate of models.", "Table 8", pdf_caps) == "Table 7"
        and captions.pdf_label("Agreement between two types of judges on Chatbot Arena.", "Table 6", pdf_caps) == "Table 6"
        and captions.pdf_label("Something the PDF does not have at all", "Table 9", pdf_caps) is None)

    with tempfile.TemporaryDirectory() as tmp:
        import pymupdf
        pdf_file, md_file = Path(tmp) / "p.pdf", Path(tmp) / "p.md"
        doc = pymupdf.open()
        page = doc.new_page()
        page.insert_text((72, 100), "Figure 2: Agreement and win rate difference of judges.")
        page.insert_text((72, 300), "Table 7: Category-wise win rate of all models.")
        doc.save(pdf_file)
        md_file.write_text("See Table [8](#S4.T8 \"Table 8 ‣ 4 Results\") and [Figure\xa07](#S4.T7 \"In 4 Results\").\n\n"
                           "Table 7: Agreement and win rate difference of judges.\n\n"
                           "Table 8: Category-wise win rate of all models.\n", encoding="utf-8")
        subprocess.run([sys.executable, SCRIPTS / "caption-numbers.py", pdf_file, md_file], check=True, capture_output=True)
        out = md_file.read_text(encoding="utf-8")
    yield "captions and their links are renumbered from the PDF", (
        "Figure 2: Agreement" in out and "Table 7: Category-wise" in out
        and "Table [7](#S4.T8)" in out and "[Figure\xa07](#S4.T7)" in out)

    with tempfile.TemporaryDirectory() as tmp:
        pdf_file, md_file = Path(tmp) / "p.pdf", Path(tmp) / "p.md"
        doc = pymupdf.open()
        page = doc.new_page()
        page.insert_text((72, 100), "(b) LoTTE results.\nTable 5: Zero-shot evaluation results on both sets.")
        page.insert_text((72, 300), "Table 1: Main results of the progressive techniques.")
        doc.save(pdf_file)
        md_file.write_text("Algorithm 1 Sampling\n\nTable 1:\n\nTable 1: Main results of the progressive techniques.\n\n"
                           "Table 6: Zero-shot evaluation results on both sets.\n\nFigure 3:\n", encoding="utf-8")
        subprocess.run([sys.executable, SCRIPTS / "caption-numbers.py", pdf_file, md_file], check=True, capture_output=True)
        out = md_file.read_text(encoding="utf-8")
    yield "a bare label a captioned table carries too is dropped", out.count("Table 1:") == 1 and "Figure 3:" in out
    yield "a caption under a sub-table's label is found in the PDF", "Table 5: Zero-shot" in out

    with tempfile.TemporaryDirectory() as tmp:
        pdf_file, md_file = Path(tmp) / "p.pdf", Path(tmp) / "p.md"
        doc = pymupdf.open()
        page = doc.new_page()
        page.insert_text((72, 100), "Table 7: Zero-shot evaluation results on the dev sets of LoTTE.")
        doc.save(pdf_file)
        text = ("Table 5: Zero-shot evaluation results. Sub-table (a) reports BEIR.\n\n"
                "Table 7: Zero-shot evaluation results on the dev sets of LoTTE.\n")
        md_file.write_text(text, encoding="utf-8")
        subprocess.run([sys.executable, SCRIPTS / "caption-numbers.py", pdf_file, md_file], check=True, capture_output=True)
        out = md_file.read_text(encoding="utf-8")
    yield "a caption does not take the number another caption keeps", out == text

    with tempfile.TemporaryDirectory() as tmp:
        pdf_file, md_file = Path(tmp) / "p.pdf", Path(tmp) / "p.md"
        doc = pymupdf.open()
        for number, text in enumerate(("1 Introduction", "2 Method", "A Proofs"), 1):
            page = doc.new_page()
            page.insert_text((72, 100), text)
            if number == 3:
                page.insert_text((72, 300), "1. Basic properties")
        doc.set_toc([[1, "1 Introduction", 1], [1, "2 Method", 2], [1, "A Proofs", 3]])
        doc.save(pdf_file)
        md_file.write_text("## 1 Introduction\n\n## 2 Method\n\n## Appendix A Proofs\n\n#### 1. Basic properties\n",
                           encoding="utf-8")
        subprocess.run([sys.executable, SCRIPTS / "page-map.py", pdf_file, md_file], check=True, capture_output=True)
        out = md_file.read_text(encoding="utf-8")
    yield "a numbered step in an appendix is not section 1", (
        "## 2 Method (p. 2)" in out and "#### 1. Basic properties (p. 3)" in out)

    md, _ = convert('<p>See Table <a href="#S4.T8" title="Table&nbsp;8 ‣ 4.2 Results ‣ 4 Experiments ‣ A Paper">8</a> in Section '
                    '<a href="#S4" title="4 Experiments ‣ A Paper">4</a> (<a href="https://x.org" title="Home">site</a>).</p>')
    yield "a link's title keeps only the float it names", (
        '[8](#S4.T8 "Table 8")' in md and "[4](#S4)" in md and "Experiments" not in md and '"Home"' in md)

    md, _ = convert('<table class="ltx_tabular"><tr class="ltx_tr"><td class="ltx_td ltx_border_tt" rowspan="2">Model</td>'
                    f'<td class="ltx_td ltx_border_tt">Size {math(r"\times 10^{3}")}</td></tr>'
                    f'<tr class="ltx_tr"><td class="ltx_td">{math("a&lt;b")}</td></tr>'
                    f'<tr class="ltx_tr"><td class="ltx_td ltx_border_t">A</td><td class="ltx_td ltx_border_t">{math("18.65")}</td></tr>'
                    f'</table><p>Costs {math("x")}2 here.</p>')
    yield "mathematics in an HTML table is its TeX", (
        r"Size $\times 10^{3}$" in md and "<td>18.65</td>" in md and r"$a\lt b$" in md and "math inline" not in md)
    yield "a formula before a digit still closes", "$x$<!-- -->2" in md

    picture_tex = (r"\{\mathchoice" + r"{\hbox to46.43pt{\vbox to13.69pt{\pgfpicture\makeatletter\hbox{{stroke=#000000}}\endpgfpicture}}}" * 4
                   + r",\hbox to9pt{\vbox to5pt{\pgfpicture\endpgfpicture}}\}")
    drawn = ('<mtext><svg height="18" width="64"><g><path d="M 0 0 h 6"></path><foreignObject width="57" height="12">'
             '<span class="ltx_foreignobject_container">{}</span></foreignObject></g></svg></mtext>')
    md, _ = convert(f'<p>Tokens <math alttext="{picture_tex}" display="inline"><semantics><mrow>'
                    + drawn.format("Critique") + drawn.format(r'<math alttext="\displaystyle\mathstrut c_{t}" display="inline"><mi>c</mi></math>')
                    + f'</mrow><annotation encoding="application/x-tex">{picture_tex}</annotation></semantics></math> are added.</p>')
    yield "a picture in a formula is what it shows, not its drawing commands", (
        r"$\{\text{Critique},{c_{t}}\}$" in md and "pgfpicture" not in md and "images/" not in md)

    md, _ = convert('<table class="ltx_tabular"><tr class="ltx_tr"><td class="ltx_td" rowspan="2">Stage</td><td class="ltx_td">Early</td></tr>'
                    r'<tr class="ltx_tr"><td class="ltx_td"><math alttext="0.26\scalebox{0.7}{$\pm$}\text{\scriptsize 0.0020}" display="inline">'
                    '<semantics><mrow><mn>0.26</mn><mtext><div class="ltx_inline-block"><span class="ltx_p">±</span></div></mtext>'
                    '<mtext>0.0020</mtext></mrow></semantics></math></td></tr></table>')
    yield "a value and its scaled deviation stay one formula", r"0.26{\pm}\text{\scriptsize 0.0020}" in md

    md, _ = convert('<h2 class="ltx_title"><span class="ltx_tag ltx_tag_section">4 \\par</span>Experiments</h2>'
                    '<table class="ltx_tabular"><tr class="ltx_tr"><td class="ltx_td" rowspan="2">SST</td><td class="ltx_td">'
                    '<math alttext="\\par" display="inline"><semantics><mn>0.395\u2009443\u2009126\u2009241\u2009129\u20096</mn>'
                    '<annotation encoding="application/x-tex">\\par</annotation></semantics></math></td></tr>'
                    '<tr class="ltx_tr"><td class="ltx_td">0.59</td></tr></table>'
                    '<p>Embeddings [<a href="#bib.bibx2" class="ltx_ref">\\citeauthoryearBengio et al.2003</a>], circuits '
                    '\\cite[citep]{(\\@@bibref{AuthorsPhrase1Year}{olsson_2022}{\\@@citephrase{, }}{})}, and a cell '
                    '<span class="ltx_ERROR ltx_centering undefined">\\cellcolor</span>c3-item-bkg<span class="ltx_text">Score</span> '
                    'beside <span class="ltx_picture">\\diaghead(-3,1){pad}{{\\shortstack[l]{Method}}}{{\\shortstack[r]{Dataset}}}</span>.</p>')
    yield "a \\par set as text is dropped, and a number behind one is kept", (
        "## 4 Experiments" in md and "<td>0.3954</td>" in md and "par" not in md)
    yield "TeX set as text is read: a citation, a colour's name, a split header", (
        "[Bengio et al. 2003](#bib.bibx2)" in md and "(olsson_2022)" in md and "cell Score" in md
        and "Method / Dataset" in md and "\\" not in md.replace("\\[", "").replace("\\]", ""))

    rowcolor = '<span class="ltx_ERROR undefined">\\rowcolor</span><span class="ltx_text">gray!10{}</span>'
    md, _ = convert(f'<p>Rows {rowcolor.format("ANLI")} and {rowcolor.format("AIME 2025")} and {rowcolor.format("")}end.</p>')
    yield "a colour mix before a one-word cell goes alone", "Rows ANLI and AIME 2025 and end." in md

    unplaced = ('<span class="ltx_note ltx_role_footnotetext"><sup class="ltx_note_mark">†</sup><span class="ltx_note_outer">'
                '<span class="ltx_note_content"><sup class="ltx_note_mark">†</sup>{}</span></span></span>')
    md, _ = convert(f'<p>Abstract text.</p><p>{unplaced.format("Under review.")}{unplaced.format("Code at x.")}</p>')
    yield "a paragraph of note marks alone is dropped", (
        "<sup>†</sup><sup>†</sup>" not in md and "<sup>†</sup> Under review." in md and "<sup>†</sup> Code at x." in md)

    paperlib = load("paperlib")
    view = paperlib.read_view({"title": "T", "source": "html"}, "N = 10<sup>4</sup>, x<sub>i</sub>, a<sup>†‡</sup>\n")
    yield "the read view keeps superscripts apart", "10^4" in view and "x_i" in view and "a^{†‡}" in view
    view = paperlib.read_view({"title": "T", "source": "html"}, (
        "![](images/T-fig01.png)\n\n| A | ![check-mark](images/x2.png) |\n\n"
        '<td><img src="images/T-fig08.svg" /></td><td><img src="images/x3.png" alt="snowflake" /></td>\n'))
    yield "the read view names icons and drops image paths", (
        view.count("[figure]") == 2 and "[check-mark]" in view and "[snowflake]" in view and "images/" not in view)

    import io
    import random
    import zlib
    from PIL import Image
    noise = Image.frombytes("L", (64, 64), random.Random(0).randbytes(64 * 64))
    png = io.BytesIO()
    noise.save(png, "PNG")
    png = png.getvalue()
    text = b"tEXtmxGraphModel\0<diagram/>"  # draw.io rewrites its diagram, not the checksum
    bad_crc = png[:33] + len(text[4:]).to_bytes(4, "big") + text + (zlib.crc32(text) ^ 1).to_bytes(4, "big") + png[33:]
    with tempfile.TemporaryDirectory() as tmp:
        cache = Path(tmp)
        (cache / "cut.png").write_bytes(b"")
        served = {"cut.png": png[:len(png) // 2], "crc.png": bad_crc, "short.png": png[:len(png) // 2]}  # arXiv's HTML server
        source = {"missing.png": png, "cut.png": png}  # the paper's LaTeX source
        refetched = []

        def fetch(url, attempts=4, fresh=False):
            name = url.rpartition("/")[2]
            if fresh:
                refetched.append(name)
                return png if name == "cut.png" else served.get(name)
            return served.get(name)

        figures = load("paperlib")
        figures.fetch = fetch
        figures.cache_path = lambda url: cache / url.rpartition("/")[2]
        figures.source_images = lambda version: source if version == "2401.00001v1" else {}
        names = iter(range(1, 10))
        body = "".join(f"![](2401.00001v1/{n}.png)\n" for n in ("missing", "cut", "crc", "gone", "short"))
        body, failed = figures.localize_figures(body, lambda data, ext: f"images/f{next(names)}.{ext}", pause=0)
    yield "a figure arXiv lacks comes from the source; a cut-off cached one is downloaded again", (
        body.startswith("![](images/f1.webp)\n![](images/f2.webp)\n") and refetched == ["cut.png"])
    yield "a PNG loses a text chunk with a bad checksum; a figure found nowhere, or only cut off, keeps its arXiv link", (
        "![](images/f3.webp)" in body and "](https://arxiv.org/html/2401.00001v1/gone.png)" in body
        and "](https://arxiv.org/html/2401.00001v1/short.png)" in body and failed == 2)

    pdf = load("pdf-to-markdown")
    yield "PDF heading levels from numbering", [
        pdf.heading_level(t, False, 2) for t in ("3 Method", "3.1 Setup", "A.2 Proofs", "Abstract", "User Consent")
    ] == [2, 3, 3, 2, 3]
    yield "PDF heading levels in an IEEE paper", [
        pdf.heading_level(t, True, 2) for t in ("II. RELATED WORK", "A. Surveys", "1) Details")] == [2, 3, 4]
    yield "PDF numbers set in math mode are rejoined", pdf.tidy("BM25  32 . 3   41 . 2") == "BM25 32.3 41.2"

    yield "PDF text with lost symbols is sent to the model", (
        pdf.needs_reading("as a task _ ~ ( ), drawn from", False)
        and pdf.needs_reading("a support set ᵢˢᵘᵖᵖᵒʳᵗ", False)
        and not pdf.needs_reading("The learning rate α is small.", False)
        and pdf.needs_reading("where θ ∈ ℝ and α > 0", True)
        and pdf.needs_reading("Given a query q and keys K", True, math_font=True)
        and not pdf.needs_reading("Given a query q and keys K", False, math_font=True))
    yield "a model reading must keep the words and numbers", (
        pdf.trusted_reading("accuracy rises from 0.702 to 0.748 after _ steps",
                            "accuracy rises from 0.702 to 0.748 after $k$ steps")
        and not pdf.trusted_reading("accuracy rises from 0.702 to 0.748", "accuracy rises from 0.702 to 0.743")
        and not pdf.trusted_reading("a long paragraph about memory layers and retrieval quality", "a long"))
    yield "PDF text starting with # is not a heading", (
        pdf.reading_or_text(SimpleNamespace(text="# weights  learning rate"), None) == "\\# weights learning rate")
    yield "a table docling split in two is rejoined", pdf.join_split_tables(
        ["| Model | Hit |\n|---|---|\n| A | 0.4 |", "| B | 0.6 |\n|---|---|\n| C | 0.7 |"]
    ) == ["| Model | Hit |\n|---|---|\n| A | 0.4 |\n| B | 0.6 |\n| C | 0.7 |"]
    gpt1_eq5 = "L_3(\\mathcal{C}) = L_2(\\mathcal{C}) + \\lambda * L_1(\\mathcal{C}) \\quad (5)"
    yield "a PDF equation read as only its number is found", (
        all(pdf.number_only(t) for t in ("(5)", "\\tag{3}", "↑ (4)", "\\quad (2.1)", "(3)"))
        and not any(pdf.number_only(t) for t in (gpt1_eq5, "x = 1 \\quad (2)", "", "\\alpha"))
        and pdf.equation_number("\\begin{aligned} l_1 &= W_1 x \\end{aligned} \\tag{3}") == "3")
    yield "a number-only equation is re-read only into the same equation", (
        pdf.keeps_number(gpt1_eq5, "5")
        and not pdf.keeps_number("See the additional supplement for details of the remaining complex weights.", "5")
        and not pdf.keeps_number("(5)", "5")
        and not pdf.keeps_number("y = f(x) \\quad (6)", "5")
        and pdf.keeps_number("\\langle v_1/i_1, \\dots \\rangle.", "5", own_box=True)
        and not pdf.keeps_number("\\langle v_1/i_1, \\dots \\rangle.", "5")
        and not pdf.keeps_number("See the additional supplement for details.", "5", own_box=True))
    # DSSM, p. 3: docling's box for Eq. (3) holds only its number; the formula,
    # which has no text in the PDF's text layer, is in the band between the blocks.
    dssm = [[54, 364, 296, 404], [282, 432, 294, 440], [54, 462, 280, 480], [282, 493, 294, 500],
            [54, 513, 296, 531], [318, 405, 560, 557]]
    yield "a number-only equation is re-read from a wider crop, and the band of a narrow box", (
        pdf.retry_boxes([282, 432, 294, 440], dssm) == [[280, 430, 296, 442], [54, 405, 296, 461]]
        and pdf.retry_boxes([248, 689, 504, 699], [[108, 643, 504, 684], [108, 702, 504, 722]])
        == [[246, 687, 506, 701]])
    # Two number-only equations, each with one crop; the model reads both from them.
    items = [SimpleNamespace(orig="(5)", text=""), SimpleNamespace(orig="a = b (6)", text="")]
    boxes = [{"page": 1, "bbox": [100, 100, 400, 110], "kind": "equation"},
             {"page": 1, "bbox": [100, 200, 400, 210], "kind": "equation"}]
    readings = {0: ["(5)"], 1: ["(6)"]}
    real_read = pdf.read_blocks
    pdf.read_blocks = lambda path, crops: ["x = 1", "y = 2 \\quad (6)"][:len(crops)]
    try:
        pdf.reread_number_only("p.pdf", items, {0: "equation", 1: "equation"}, boxes, [0, 1], readings,
                               {1: [b["bbox"] for b in boxes]})
    finally:
        pdf.read_blocks = real_read
    yield "each number-only equation takes its own new reading", readings == {0: ["x = 1 \\quad (5)"], 1: ["y = 2 \\quad (6)"]}

    import pymupdf
    doc = pymupdf.open()
    page = doc.new_page()
    for x, text, font in ((100, "53.80", "Times-Bold"), (200, "52.10", "Times-Roman"), (300, "51.20", "Times-Italic"),
                          (400, "50.40", "Times-Roman")):
        page.insert_text((x, 100), text, fontname=font, fontsize=10)
    page.insert_text((100, 130), "0.71", fontname="Times-Bold", fontsize=10)
    page.draw_line((400, 101.5), (424, 101.5), width=0.5)  # under 50.40
    page.draw_line((80, 133), (480, 133), width=0.5)  # a table rule under the second row
    rules = pdf.page_rules(page)
    marks = [pdf.cell_marks(page, (x - 2, 90, x + 40, 104), rules) for x in (100, 200, 300, 400)]
    yield "bold, italic and underline in a PDF table cell come from its fonts and rules", (
        marks == [{"bold"}, set(), {"italic"}, {"underline"}]
        and pdf.cell_marks(page, (98, 120, 140, 134), rules) == {"bold"})
    box = lambda x0, y0, x1, y1: SimpleNamespace(coord_origin=SimpleNamespace(name="TOPLEFT"), l=x0, t=y0, r=x1, b=y1)
    cells = [SimpleNamespace(text=t, bbox=box(x - 2, 90, x + 40, 104), column_header=False)
             for x, t in ((100, "53.80"), (200, "52.10"), (400, "50.40"))]
    pdf.mark_table_cells(SimpleNamespace(data=SimpleNamespace(table_cells=cells)), page, 842)
    yield "a PDF table cell's marks are written into its text", (
        [c.text for c in cells] == ["**53.80**", "52.10", "<u>50.40</u>"])
    cells = [SimpleNamespace(text=t, bbox=box(x - 2, 90, x + 40, 104), column_header=False)
             for x, t in ((100, "53.80"), (98, "53.80"))]
    pdf.mark_table_cells(SimpleNamespace(data=SimpleNamespace(table_cells=cells)), page, 842)
    yield "a mark every body cell of a PDF table has is left out", [c.text for c in cells] == ["53.80", "53.80"]

    page_map = load("page-map")
    said = [" ".join(f"{topic}{chr(97 + i % 26)}{chr(97 + i // 26)}" for i in range(130))
            for topic in ("intro", "method", "proof", "ablation", "prompts")]
    doc = pymupdf.open()
    for text in said + ["Smith 2019. In Proceedings of the Conference. " * 14 + said[0]]:
        doc.new_page().insert_textbox(pymupdf.Rect(40, 40, 560, 800), text, fontsize=6)
    lacking, texty = page_map.missing_pages(doc, said[0] + "\n\n" + said[1])
    yield "pages of the PDF the markdown lacks are found, a page of references aside", (
        (lacking, texty) == ([3, 4, 5], 6) and page_map.page_ranges([3, 4, 5, 9]) == "3–5, 9")

    symptoms = load("conversion-symptoms")
    yield "a < in an equation is not a tag", symptoms.prose_words(
        "If $a<b$ then one two three and $c>d$ holds.\n\n$$x<y \\tag{1}$$\n\n<span>four</span> <!-- note -->") == 12
    yield "frontmatter is split from the body", symptoms.split_frontmatter(
        "---\ntitle: T\nauthors: [A, B]\n---\nBody text.\n") == ({"title": "T", "authors": ["A", "B"]}, "Body text.\n")

    page_map = load("page-map")
    yield "ICML heading number", page_map.heading_number("1 Introduction", True, False) == ("1", "Introduction", ["1"])
    yield "IEEE section", page_map.heading_number("IV Method", True, True) == ("4", "Method", ["iv"])
    yield "IEEE subsection", page_map.heading_number("II-A Surveys", False, True)[:2] == ("2.1", "Surveys")
    yield "IEEE subsubsection", page_map.heading_number("IV-B1 Details", False, True)[:2] == ("4.2.1", "Details")
    yield "appendix letter only at top level", (
        page_map.heading_number("B Proofs", True, False) is not None
        and page_map.heading_number("A Harmless Assistant", False, False) is None)


def main():
    failed = 0
    for name, passed in checks():
        print(f"{'ok  ' if passed else 'FAIL'} {name}")
        failed += not passed
    if failed:
        sys.exit(f"{failed} checks failed")


if __name__ == "__main__":
    main()
