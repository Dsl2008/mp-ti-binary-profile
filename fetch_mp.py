# -*- coding: utf-8 -*-
"""
第 6 周项目 · 第 1 步：从 Materials Project 拉数据。

准备：
  1. 把 API key 存到 week06/api_key.txt（只有一行，不要引号空格）
  2. cd week06
  3. python fetch_mp.py

输出：data/mp_ti_binary.csv
"""

import os
import sys
import time
from pathlib import Path

import pandas as pd
import requests

HERE = Path(__file__).resolve().parent
KEY_FILE = HERE / "api_key.txt"
OUT = HERE / "data" / "mp_ti_binary.csv"

API_URL = "https://api.materialsproject.org/materials/summary/"

# 只拉需要的列，响应会小很多
FIELDS = [
    "material_id", "formula_pretty", "chemsys", "elements", "nelements",
    "nsites", "volume", "density", "symmetry",
    "band_gap", "is_metal",
    "formation_energy_per_atom", "energy_above_hull", "is_stable",
    "total_magnetization",
]

# 查询条件：含 Ti、二元化合物、未废弃
QUERY = {
    "elements": "Ti",
    "nelements_max": 2,
    "deprecated": "false",
}

PAGE = 1000          # API 单次最多 1000 条
MAX_DOCS = 3000      # 防止一次拉太多；不够就把这个数调大

COLUMNS = [
    "material_id", "formula_pretty", "chemsys", "nelements", "nsites",
    "volume", "density", "crystal_system", "spacegroup", "band_gap",
    "is_metal", "formation_energy_per_atom", "energy_above_hull",
    "is_stable", "total_magnetization",
]


def read_key():
    """环境变量优先，其次读 api_key.txt。"""
    key = os.environ.get("MP_API_KEY", "").strip()
    if key:
        return key
    if not KEY_FILE.exists():
        sys.exit(
            "没找到 api_key.txt。\n"
            "请把 Materials Project 的 API key 存到：\n  %s\n"
            "整行只放 key，不要引号。也可以设置环境变量 MP_API_KEY。" % KEY_FILE
        )
    key = KEY_FILE.read_text(encoding="utf-8-sig").strip().strip("'\"")
    if not key:
        sys.exit("api_key.txt 是空的，里面要放 key 本身。")
    return key


def flatten(doc):
    """把一条 MP 文档压成一行 CSV。symmetry 是个嵌套字典，要拆开。"""
    sym = doc.get("symmetry") or {}
    return {
        "material_id": doc.get("material_id"),
        "formula_pretty": doc.get("formula_pretty"),
        "chemsys": doc.get("chemsys"),
        "nelements": doc.get("nelements"),
        "nsites": doc.get("nsites"),
        "volume": doc.get("volume"),
        "density": doc.get("density"),
        "crystal_system": sym.get("crystal_system"),
        "spacegroup": sym.get("symbol"),
        "band_gap": doc.get("band_gap"),
        "is_metal": doc.get("is_metal"),
        "formation_energy_per_atom": doc.get("formation_energy_per_atom"),
        "energy_above_hull": doc.get("energy_above_hull"),
        "is_stable": doc.get("is_stable"),
        "total_magnetization": doc.get("total_magnetization"),
    }


def fetch_page(session, skip):
    params = {"_fields": ",".join(FIELDS), "_limit": PAGE, "_skip": skip}
    params.update(QUERY)
    for attempt in range(3):
        r = session.get(API_URL, params=params, timeout=60)
        if r.status_code == 401:
            sys.exit(
                "API key 被拒绝（401）。检查 api_key.txt 里是不是完整的 key，\n"
                "有没有多复制了空格或换行。刚注册的账号 key 可能还没生效，等 1–2 分钟再试。"
            )
        if r.status_code == 429:
            wait = 10 * (attempt + 1)
            print("  请求太频繁（429），等 %d 秒重试..." % wait)
            time.sleep(wait)
            continue
        if r.status_code >= 400:
            sys.exit("请求失败：HTTP %s\n%s" % (r.status_code, r.text[:500]))
        return r.json()
    sys.exit("连续 3 次被限流，过几分钟再跑。")


def main():
    session = requests.Session()
    session.headers.update({
        "X-API-KEY": read_key(),
        "Accept": "application/json",
        "User-Agent": "python-learning-week06",
    })

    rows = []
    seen = set()
    skip = 0
    total = None

    while True:
        payload = fetch_page(session, skip)
        docs = payload.get("data", [])
        meta = payload.get("meta", {}) or {}
        if total is None:
            total = meta.get("total_doc", len(docs))
            print("命中总数：%s 条（本次最多取 %d 条）" % (total, MAX_DOCS))
        if not docs:
            break

        for doc in docs:
            mid = doc.get("material_id")
            if mid in seen:
                continue
            seen.add(mid)
            rows.append(flatten(doc))

        print("  已取 %d / %d" % (len(rows), min(total or MAX_DOCS, MAX_DOCS)))
        skip += PAGE
        if len(rows) >= MAX_DOCS or skip >= (total or 0):
            break
        time.sleep(1)          # 对服务器客气一点

    if not rows:
        sys.exit("一条数据都没拿到。检查查询条件，或者稍后再试。")

    df = pd.DataFrame(rows, columns=COLUMNS)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False, encoding="utf-8")

    print()
    print("保存到：%s" % OUT)
    print("形状：%s" % (df.shape,))
    print("化学体系数：%d" % df["chemsys"].nunique())
    print("缺失值统计（前几列）：")
    print(df.isna().sum().head(8).to_string())
    print()
    print("前 3 行：")
    print(df.head(3).to_string(index=False))


if __name__ == "__main__":
    main()
