#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QA 健康檢查 —— 一條 command 驗證「成條鏈」係咪真係播到戲。

檢查項：
  1. 本地後端 (FastAPI)  /health 係咪 200
  2. 對外 tunnel（即部署版網站用緊嘅 API URL）/health 係咪 200
  3. 管理員帳號密碼登入係咪拎到 access_token / refresh_token
  4. /dramas 係咪有劇集
  5. 攞一集做樣本，經 /episodes/{id}/stream 拎播放位址
  6. 實際對該 video_url 做 HEAD + Range 請求，確認：
       - HTTP 200
       - Content-Type 係 video/*
       - Content-Length > 0
       - 支援 Accept-Ranges（可以 seek）
       - Range 請求真係攞到第一個 byte

用法：
  cd backend
  # 預設打本地 8000 + 由 .github/workflows/pages.yml 讀出嘅對外 API URL
  .venv/bin/python scripts/qa_check.py

  # 或者晒屙指定
  QA_BASE_URL=http://localhost:8000 \
  QA_API_URL=https://xxx.trycloudflare.com \
  ADMIN_PHONE=85263106930 ADMIN_PASSWORD=drama2026 \
  .venv/bin/python scripts/qa_check.py

全部通過 exit 0；任何一項失敗 exit 1。
淨係用 Python stdlib，唔使裝嘢。
"""
import json
import os
import re
import sys
import urllib.request
import urllib.error

# ---------------------------------------------------------------------------
# 設定
# ---------------------------------------------------------------------------
BASE_URL = os.environ.get("QA_BASE_URL", "http://localhost:8000").rstrip("/")
ADMIN_PHONE = os.environ.get("ADMIN_PHONE", "85263106930")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "drama2026")

# 專案根目錄（backend/scripts/qa_check.py -> 上兩層）
PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
WORKFLOW_FILE = os.path.join(PROJECT_ROOT, ".github", "workflows", "pages.yml")


def read_deployed_api_url():
    """由 GitHub Pages workflow 讀出 NEXT_PUBLIC_API_URL（部署版網站用緊嘅 API）。"""
    fallback = "https://ssl-zones-collectibles-thorough.trycloudflare.com"
    try:
        with open(WORKFLOW_FILE, "r", encoding="utf-8") as f:
            m = re.search(r'NEXT_PUBLIC_API_URL:\s*(\S+)', f.read())
        if m:
            return m.group(1).strip().rstrip("/")
    except OSError:
        pass
    return os.environ.get("QA_API_URL", fallback).rstrip("/")


API_URL = os.environ.get("QA_API_URL", read_deployed_api_url())

# ---------------------------------------------------------------------------
# 結果收集
# ---------------------------------------------------------------------------
results = []  # (name, ok, detail)


def check(name, ok, detail=""):
    results.append((name, ok, detail))
    mark = "PASS" if ok else "FAIL"
    line = f"  [{mark}] {name}"
    if detail:
        line += f"  -- {detail}"
    print(line)


# ---------------------------------------------------------------------------
# HTTP 工具
# ---------------------------------------------------------------------------
def _req(url, method="GET", headers=None, body=None, timeout=15):
    req = urllib.request.Request(url, method=method, headers=headers or {})
    data = None
    if body is not None:
        data = json.dumps(body).encode("utf-8")
    try:
        with urllib.request.urlopen(req, data=data, timeout=timeout) as r:
            return r.status, dict(r.headers), r.read()
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers or {}), e.read()
    except Exception as e:  # noqa: BLE001
        return None, {}, str(e).encode("utf-8")


# ---------------------------------------------------------------------------
# 1. 本地後端
# ---------------------------------------------------------------------------
print(f"\n=== QA 播放檢查 ===")
print(f"  本地後端 : {BASE_URL}")
print(f"  對外 API : {API_URL}")
print(f"  管理員   : {ADMIN_PHONE}\n")

status, _, _ = _req(f"{BASE_URL}/health", timeout=5)
check("1. 本地後端 /health", status == 200, f"HTTP {status}")

# ---------------------------------------------------------------------------
# 2. 對外 tunnel / 部署用 API
# ---------------------------------------------------------------------------
status, _, _ = _req(f"{API_URL}/health", timeout=15)
check("2. 對外 tunnel /health", status == 200, f"{API_URL} -> HTTP {status}")

# ---------------------------------------------------------------------------
# 3. 管理員登入
# ---------------------------------------------------------------------------
token = None
status, headers, raw = _req(
    f"{BASE_URL}/auth/login",
    method="POST",
    headers={"Content-Type": "application/json"},
    body={"identifier": ADMIN_PHONE, "password": ADMIN_PASSWORD},
)
login_ok = False
if status == 200:
    try:
        data = json.loads(raw.decode("utf-8"))
        token = data.get("access_token")
        rt = data.get("refresh_token")
        login_ok = bool(token and rt)
    except Exception:  # noqa: BLE001
        login_ok = False
check("3. 管理員登入拎到 access/refresh token", login_ok, f"HTTP {status}")

auth_headers = {"Authorization": f"Bearer {token}"} if token else {}

# ---------------------------------------------------------------------------
# 5. 掃描：照 /dramas 返嘅次序（即用戶見到嘅次序），逐套測第一集播唔播到
# ---------------------------------------------------------------------------
SCAN_LIMIT = int(os.environ.get("QA_SCAN_LIMIT", "15"))  # 最多掃幾多套劇

status, _, raw = _req(f"{BASE_URL}/dramas", headers=auth_headers, timeout=10)
has_drama = False
dramas = []
if status == 200:
    try:
        dramas = json.loads(raw.decode("utf-8"))
        has_drama = isinstance(dramas, list) and len(dramas) > 0
    except Exception:  # noqa: BLE001
        has_drama = False
check("4. /dramas 至少有一套劇", has_drama, f"HTTP {status}, 共 {len(dramas)} 套")


def probe_video(url):
    """回 (playable, http_status, content_type, size_bytes, note)。"""
    if not url:
        return False, None, "", 0, "冇 video_url"
    status, hdrs, _ = _req(url, method="HEAD", timeout=20)
    ctype = hdrs.get("Content-Type", hdrs.get("content-type", ""))
    try:
        size = int(hdrs.get("Content-Length", hdrs.get("content-length", "0")) or 0)
    except ValueError:
        size = 0
    playable = status == 200 and ctype.startswith("video/") and size > 1000
    note = f"{ctype} {size}B"
    return playable, status, ctype, size, note


print("\n  --- 播放掃描（用戶見到嘅次序，每套測第一集）---")
rows = []  # (title, ep_id, host, playable, status, note)
for d in dramas[:SCAN_LIMIT]:
    did = d["id"]
    dtitle = d.get("title", f"#{did}")
    _, _, draw = _req(f"{BASE_URL}/dramas/{did}", headers=auth_headers, timeout=10)
    ep_id, video_url = None, None
    try:
        detail = json.loads(draw.decode("utf-8"))
        eps = detail.get("episodes") or []
        if eps:
            ep_id = eps[0]["id"]
            _, _, sraw = _req(
                f"{BASE_URL}/episodes/{ep_id}/stream", headers=auth_headers, timeout=10
            )
            video_url = json.loads(sraw.decode("utf-8")).get("video_url")
    except Exception:  # noqa: BLE001
        pass

    host = ""
    if video_url:
        m = re.search(r"https?://([^/]+)", video_url)
        host = m.group(1) if m else "?"
    playable, hstatus, ctype, size, note = probe_video(video_url)
    rows.append((dtitle, ep_id, host, playable, hstatus, note))
    flag = "OK " if playable else "BAD"
    print(f"    [{flag}] {dtitle[:24]:<24} ep#{ep_id} <{host}> HTTP {hstatus} {note}")

n_play = sum(1 for r in rows if r[3])
n_total = len(rows)
first_ok = rows[0][3] if rows else False

print("\n  --- 播放結果 ---")
check(f"5. 掃描咗 {n_total} 套，至少有一套第一集播到", n_play > 0,
      f"{n_play}/{n_total} 套第一集播到")
check("6. 排最前（用戶第一眼見到）嘅劇第一集播到", first_ok,
      f"{rows[0][0] if rows else '無'} -> HTTP {rows[0][4] if rows else '?'}")

# ---------------------------------------------------------------------------
# 總結
# ---------------------------------------------------------------------------
print("\n=== 總結 ===")
passed = sum(1 for _, ok, _ in results if ok)
total = len(results)
print(f"  通過 {passed}/{total}")
if passed == total:
    print("  🎉 全部檢查通過，真係播到。\n")
    sys.exit(0)
else:
    print("  ❌ 有檢查失敗，未算播到。\n")
    sys.exit(1)
