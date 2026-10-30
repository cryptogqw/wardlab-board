"""wardlab.io 停更检查（GitHub Actions 每小时运行一次）。

读取公开看板页面里的两个时间：本版生成时间（发布是否停了）和报价截至时间（采集是否停了）。
任一超过 2 小时就让这次运行失败，GitHub 会通知仓库维护者；持续停更时每 6 小时再失败一次，不每小时都发。
只读取公开页面，不需要任何凭据。
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.request
from datetime import datetime, timezone

URL = "https://wardlab.io/board/"
LIMIT_H = 2.0      # 超过这么多小时没有更新就提醒
REPEAT_H = 6.0     # 持续停更时，每隔这么多小时再提醒一次


def decide(gen_h: float, quote_h: float, limit: float = LIMIT_H, repeat: float = REPEAT_H) -> tuple[bool, str]:
    """(是否提醒, 说明)。gen_h / quote_h：距本版生成、距报价截至的小时数。
    第一次超过阈值的那一小时提醒；之后每满 repeat 小时的那一小时再提醒。"""
    worst = max(gen_h, quote_h)
    which = "发布" if gen_h >= quote_h else "报价采集"
    if worst < limit:
        return False, f"正常：本版生成于 {gen_h:.1f} 小时前，报价截至 {quote_h:.1f} 小时前"
    over = worst - limit
    if over < 1 or (over % repeat) < 1:
        return True, f"wardlab.io 已 {worst:.1f} 小时没有更新（{which}停了；阈值 {limit:g} 小时）"
    nxt = limit + repeat * (int(over // repeat) + 1)
    return False, f"仍未更新（{worst:.1f} 小时，{which}停了），本次不重复提醒；满 {nxt:g} 小时时再提醒"


def fetch(url: str = URL, tries: int = 3) -> str:
    last: Exception | None = None
    for i in range(tries):
        try:
            req = urllib.request.Request(f"{url}?t={int(time.time())}", headers={"User-Agent": "wardlab-stale-check", "Cache-Control": "no-cache"})
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read().decode("utf-8")
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(20)
    raise SystemExit(f"打不开 {url}：{last}")


def main() -> None:
    html = fetch()
    m = re.search(r'<script id="wl-data-public" type="application/json">(.*?)</script>', html, re.S)
    if not m:
        raise SystemExit("页面里找不到公开数据")
    meta = json.loads(m.group(1))["meta"]
    now = datetime.now(timezone.utc)
    hours = lambda k: (now - datetime.fromisoformat(meta[k].replace("Z", "+00:00"))).total_seconds() / 3600
    print(f"本版生成于 {meta['generated_at']}，报价截至 {meta['as_of']}（UTC）")
    if os.environ.get("TEST_ALERT") == "true":
        raise SystemExit("试发提醒：这次运行按要求失败，用来确认能收到 GitHub 的失败通知")
    alert, msg = decide(hours("generated_at"), hours("as_of"))
    if alert:
        raise SystemExit(msg)
    print(msg)


if __name__ == "__main__":
    main()
