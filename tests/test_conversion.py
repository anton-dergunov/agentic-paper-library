#!/usr/bin/env python3
"""Checks for the arXiv HTML converter and the page mapper, on small fixtures.

    paperlib test   (or: python3 tests/test_conversion.py)

Each fixture is a fragment of LaTeXML output, run through the real
html-to-markdown.py (and so the Lua filter); no network is used. Prints one
line per check and exits non-zero if any fails.
"""

import importlib.util
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


def convert(fragment):
    """Markdown for an article fragment, and the image files it wrote."""
    page = f'<html><body><div class="ltx_page_content">{fragment}</div></body></html>'
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        (tmp / "paper.html").write_text(page, encoding="utf-8")
        subprocess.run(
            [sys.executable, SCRIPTS / "html-to-markdown.py", tmp / "paper.html", tmp / "body.md",
             tmp / "images", "paper"],
            check=True, capture_output=True, timeout=120,
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

    h2m = load("html-to-markdown")
    cited = h2m.unknown_citations(
        "<p>introduced by Google researchers in 2017 ( ?). The encoder-decoder models ( ?) came first.</p>",
        r"introduced by Google researchers in 2017 \protect~\shortcite{vaswani2017attention}. Nothing else.",
        "@article{vaswani2017attention, author={Vaswani, Ashish and Shazeer, Noam and Parmar, Niki}, "
        "title={Attention is all you need}, year={2017}}")
    yield "a citation with no key left is found in the LaTeX source", (
        "(Vaswani et al. 2017)" in cited and "models ( ?)" in cited)

    tex = r"and 17 widely used \emph{agentic} benchmarks (Table \ref{tab:all}). As shown in Figure~\ref{fig:flow}, we then"
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
        and 'Table [7](#S4.T8 "Table 7 ‣ 4 Results")' in out and "[Figure\xa07]" in out)

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

    paperlib = load("paperlib")
    view = paperlib.read_view({"title": "T", "source": "html"}, "N = 10<sup>4</sup>, x<sub>i</sub>, a<sup>†‡</sup>\n")
    yield "the read view keeps superscripts apart", "10^4" in view and "x_i" in view and "a^{†‡}" in view

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
