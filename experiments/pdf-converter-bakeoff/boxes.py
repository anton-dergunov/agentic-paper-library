"""Write docling's equation boxes for a PDF as JSON, the input of pdf-equations.py.

    python3 boxes.py <pdf-dir> metalearn larimar     # -> <name>-boxes.json here

As run inline in the session; boxes are in PDF points from the page's top-left corner.
"""
import json, sys
from pathlib import Path
from docling.document_converter import DocumentConverter
from docling_core.types.doc import DocItemLabel as Label
B = Path(__file__).parent
for s in sys.argv[2:]:
    doc = DocumentConverter().convert(Path(sys.argv[1]) / f'{s}.pdf').document
    boxes = []
    for item, _ in doc.iterate_items():
        if item.label == Label.FORMULA and item.prov:
            prov = item.prov[0]
            b = prov.bbox.to_top_left_origin(page_height=doc.pages[prov.page_no].size.height)
            boxes.append({'page': prov.page_no, 'bbox': [b.l, b.t, b.r, b.b]})
    json.dump(boxes, open(B / f'{s}-boxes.json', 'w')); print(s, len(boxes), boxes[:1])
