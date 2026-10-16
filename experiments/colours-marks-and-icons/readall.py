"""Read every sampled icon (icons/sample, from collect.py) with one model: read-<model>.json."""
import sys, os
from pathlib import Path
model = sys.argv[1]
os.environ["PAPERLIB_ICONS"] = model
os.environ["PAPERS_CACHE"] = f"{Path(__file__).resolve().parent}/cache-{model}"
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from concurrent.futures import ThreadPoolExecutor
import paperlib, json
files = sorted(Path("icons/sample").iterdir())
with ThreadPoolExecutor(8) as ex:
    res = list(ex.map(lambda f: paperlib.read_icon(f.read_bytes()), files))
json.dump({f.name: r for f, r in zip(files, res)}, open(f"read-{model}.json", "w"), ensure_ascii=False, indent=0)
print(sum(r is None for r in res), "unread of", len(res))
