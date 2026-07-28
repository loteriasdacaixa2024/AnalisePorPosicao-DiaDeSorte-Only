import json, glob, os
from datetime import datetime

src_dir = r"D:\Loterias\AnalisePorPosicao-DiaDeSorte-Only\conferencias-boloes\capturas-api"
files = sorted(glob.glob(src_dir + r"\*.json"))

for fn in files:
    name = fn.split(chr(92))[-1]
    try:
        ts_str = name.split("_")[-1].replace(".json","")
        ts = int(ts_str)
        # epoch in ms?
        if ts > 2000000000:  # > 2033-05-18 as seconds
            dt = datetime.fromtimestamp(ts)
        else:
            dt = datetime.fromtimestamp(ts)
    except:
        dt = None
    if dt is None:
        continue
    # Only show today 2026-06-26
    if dt.strftime("%Y-%m-%d") != "2026-06-26":
        continue
    try:
        with open(fn, encoding="utf-8") as f:
            data = json.load(f)
    except:
        print(f"ERR {dt} {name}")
        continue
    mods = set()
    for item in data:
        p = item.get("data",{}).get("payload",{})
        if isinstance(p,dict) and p.get("modalidade"):
            mods.add(p["modalidade"])
    # Only show se tem MAIS_MILIONARIA
    print(f"{dt.strftime('%Y-%m-%d %H:%M:%S')} | {name[:55]} | {mods}")
