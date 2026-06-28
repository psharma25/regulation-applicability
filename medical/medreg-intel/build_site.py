"""Inline docs/{styles.css,data.js,app.js} into a single standalone root index.html.
Also embeds the example PDFs as data URIs so the root HTML is fully self-contained (one file)."""
import os, base64, glob, json
ROOT = os.path.dirname(os.path.abspath(__file__))
docs = os.path.join(ROOT, "docs")

html = open(os.path.join(docs, "index.html")).read()
css = open(os.path.join(docs, "styles.css")).read()
data = open(os.path.join(docs, "data.js")).read()
app = open(os.path.join(docs, "app.js")).read()

# build embedded PDF map {filename: data-uri}
pdfs = {}
for p in sorted(glob.glob(os.path.join(ROOT, "examples", "*.pdf"))):
    with open(p, "rb") as f:
        pdfs[os.path.basename(p)] = "data:application/pdf;base64," + base64.b64encode(f.read()).decode()
pdf_script = "window.MEDREG_PDFS = " + json.dumps(pdfs) + ";"

# build embedded XLSX map
xlsxs = {}
XMIME = "data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,"
for p in sorted(glob.glob(os.path.join(ROOT, "examples", "*.xlsx"))):
    with open(p, "rb") as f:
        xlsxs[os.path.basename(p)] = XMIME + base64.b64encode(f.read()).decode()
pdf_script += "\nwindow.MEDREG_XLSX = " + json.dumps(xlsxs) + ";"

html = html.replace('<link rel="stylesheet" href="styles.css" />', f"<style>\n{css}\n</style>")
html = html.replace('<script src="data.js"></script>\n<script src="app.js"></script>',
                    f"<script>\n{data}\n</script>\n<script>\n{pdf_script}\n</script>\n<script>\n{app}\n</script>")
html = html.replace("(static)", "(standalone)")

out = os.path.join(ROOT, "index.html")
open(out, "w").write(html)
print("wrote", out, "·", len(html), "bytes ·", len(pdfs), "PDFs ·", len(xlsxs), "XLSX embedded")
assert "window.MEDREG" in html and "runTracker" in html and "MEDREG_PDFS" in html and "MEDREG_XLSX" in html
