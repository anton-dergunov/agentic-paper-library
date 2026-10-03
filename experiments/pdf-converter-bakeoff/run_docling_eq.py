import sys, time
from pathlib import Path
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
B = Path(__file__).parent
formula = sys.argv[1] == 'formula'
opts = PdfPipelineOptions()
opts.do_ocr = False
opts.do_formula_enrichment = formula
conv = DocumentConverter(format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=opts)})
out = B / ('docling-formula' if formula else 'docling'); out.mkdir(exist_ok=True)
for pdf in sorted((B / 'pdf-eq').glob('*.pdf')):
    t = time.time()
    try:
        doc = conv.convert(pdf).document
        (out / f'{pdf.stem}.md').write_text(doc.export_to_markdown())
        print(f'{out.name}\t{pdf.stem}\t{time.time() - t:.0f}s', flush=True)
    except Exception as e:
        print(f'{out.name}\t{pdf.stem}\tFAILED {e!r}', flush=True)
