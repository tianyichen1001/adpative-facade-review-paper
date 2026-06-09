#!/usr/bin/env python3
"""Merge all slice_*.json into abstracts_all.json and produce missing records.
Run once the Linux VM is back:  python3 merge_and_records.py
Self-locates the 04_abstracts dir via the manifest."""
import json, os, csv, glob
from collections import defaultdict

cands = glob.glob('/sessions/*/mnt/outputs/04_abstracts/manifest.json')
if not cands:
    cands = glob.glob('/**/04_abstracts/manifest.json', recursive=True)
BASE = os.path.dirname(cands[0])
man = json.load(open(os.path.join(BASE, 'manifest.json')))

merged = {}; missing_rows = []; shard_rows = []; empty = []
for m in man:
    pub, shard = m['pub'], m['shard']
    inp = os.path.join(BASE, 'scrape_inputs', f"{pub}_shard{shard}.csv")
    sp  = os.path.join(BASE, f"slice_{pub}_{shard}.json")
    indois = []
    if os.path.exists(inp):
        with open(inp, newline='', encoding='utf-8') as f:
            for row in csv.DictReader(f):
                indois.append((row['doi'].strip(), row.get('doi_url', '').strip()))
    got = {}
    if os.path.exists(sp):
        try: got = json.load(open(sp, encoding='utf-8'))
        except Exception: got = {}
    for d, a in got.items():
        if d and isinstance(a, str) and a.strip(): merged[d] = a
    gs = set(got.keys())
    miss = [(d, u) for d, u in indois if d not in gs]
    for d, u in miss: missing_rows.append((pub, shard, d, u))
    st = "ok" if not miss else ("empty" if not got else "partial")
    shard_rows.append((pub, shard, len(indois), len(got), len(miss), st))
    if not got: empty.append(f"{pub}_{shard}")

json.dump(merged, open(os.path.join(BASE, 'abstracts_all.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
with open(os.path.join(BASE, 'missing_dois.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f); w.writerow(['publisher', 'shard', 'doi', 'doi_url'])
    for r in missing_rows: w.writerow(r)
with open(os.path.join(BASE, 'missing_shards.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f); w.writerow(['publisher', 'shard', 'input_n', 'got_n', 'missing_n', 'status'])
    for r in shard_rows: w.writerow(r)

pin = defaultdict(int); pgot = defaultdict(int); pmiss = defaultdict(int)
for pub, shard, inn, gotn, missn, st in shard_rows:
    pin[pub] += inn; pgot[pub] += gotn; pmiss[pub] += missn
order = ['elsevier','mdpi','springer','wiley','ieee','iop','taylor_francis','asce','sage','other','acm','asme','wit','frontiers','edp','transtech','nature']
L = ["# Abstract scraping summary", "",
     f"Total input DOIs (sum of shards): {sum(pin.values())}",
     f"Unique abstracts collected: {len(merged)}",
     f"Missing DOI rows: {len(missing_rows)}", "",
     "| publisher | input | collected | missing | coverage |", "|---|---|---|---|---|"]
for p in order:
    if pin[p]: L.append(f"| {p} | {pin[p]} | {pgot[p]} | {pmiss[p]} | {round(100*pgot[p]/pin[p])}% |")
L += ["", f"Fully-blocked/empty shards: {', '.join(empty) if empty else 'none'}"]
open(os.path.join(BASE, 'SUMMARY.md'), 'w', encoding='utf-8').write("\n".join(L))

print("BASE:", BASE)
print("UNIQUE_ABSTRACTS:", len(merged))
print("MISSING_ROWS:", len(missing_rows))
print("EMPTY_SHARDS:", empty)
for p in order:
    if pin[p]: print(f"{p}: {pgot[p]}/{pin[p]} (missing {pmiss[p]})")
