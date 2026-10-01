#!/usr/bin/env python3
"""Checks for the arXiv HTML converter and the page mapper, on small fixtures.

    ./scripts/test_conversion.py

Each fixture is a fragment of LaTeXML output, run through the real
html-to-markdown.py (and so the Lua filter); no network is used. Prints one
line per check and exits non-zero if any fails.
"""

import importlib.util
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
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
            check=True, capture_output=True,
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

    md, _ = convert(BORDER_TABLE)
    yield "header row above \\midrule becomes the header", md.lstrip().startswith("| Model | PPL")

    md, _ = convert("<h6>Abstract</h6><h6>Abstract</h6><p>Text.</p>")
    yield "repeated empty heading is dropped", md.count("Abstract") == 1

    md, _ = convert('<table class="ltx_tabular"><tr><td></td><td></td></tr></table><p>Text.</p>')
    yield "empty layout table is dropped", "|" not in md

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
    yield "paper version from the margin stamp", h2m.paper_version("<div>arXiv:2505.00675v3 [cs.CL] 24 Dec 2025</div>") == "2505.00675v3"

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
