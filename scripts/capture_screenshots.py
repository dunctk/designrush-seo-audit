"""Capture website screenshots via Spider Cloud API.

Usage examples:
- Default (uses latest artifacts/<date>/screenshots or today):
    uv run python scripts/capture_screenshots.py

- With explicit targets YAML and out dir:
    uv run python scripts/capture_screenshots.py \
        --targets scripts/screenshots.yml \
        --out-dir artifacts/2025-09-13/screenshots

Requirements:
- Set SPIDER_API_KEY in your environment or in a .env file at repo root.
- Define targets in YAML (see scripts/screenshots.yml for schema).
"""
from __future__ import annotations

import argparse
import base64
import json
import os
from pathlib import Path
from typing import Any, Iterable

import requests
import yaml
from dotenv import load_dotenv
from datetime import date


DEFAULT_TARGETS = [
    {"name": "01-homepage", "url": "https://www.designrush.com/", "devices": ["desktop", "mobile"]},
    {"name": "02-category-web-design", "url": "https://www.designrush.com/agency/web-design", "devices": ["desktop", "mobile"]},
    {"name": "03-category-seo", "url": "https://www.designrush.com/agency/seo", "devices": ["desktop", "mobile"]},
    {"name": "04-directory-root", "url": "https://www.designrush.com/agency", "devices": ["desktop", "mobile"]},
    {"name": "05-geo-new-york-web-design", "url": "https://www.designrush.com/agency/web-design/new-york", "devices": ["desktop", "mobile"]},
    {"name": "06-trends", "url": "https://www.designrush.com/trends", "devices": ["desktop"]},
    {"name": "07-404", "url": "https://www.designrush.com/404", "devices": ["desktop", "mobile"]},
    # SERP examples (uncomment if permitted)
    # {"name": "08-serp-web-design-agency", "url": "https://www.google.com/search?q=web+design+agency", "devices": ["desktop"]},
]


def _latest_artifacts_dir() -> Path:
    arts = Path("artifacts")
    if not arts.exists():
        return arts / date.today().strftime("%Y-%m-%d")
    dirs = [d for d in arts.iterdir() if d.is_dir()]
    if not dirs:
        return arts / date.today().strftime("%Y-%m-%d")
    # Dates sort lexicographically
    return sorted(dirs)[-1]


def _resolve_out_dir(user_out: str | Path | None) -> Path:
    if user_out:
        p = Path(user_out)
        (p).mkdir(parents=True, exist_ok=True)
        return p
    base = _latest_artifacts_dir()
    # Place screenshots under artifacts/<date>/screenshots
    out = base / "screenshots"
    out.mkdir(parents=True, exist_ok=True)
    return out


def _load_targets(path: str | Path | None) -> list[dict[str, Any]]:
    if path is None:
        return DEFAULT_TARGETS
    p = Path(path)
    if not p.exists():
        raise SystemExit(f"Targets YAML not found: {p}")
    with p.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or []
    if not isinstance(data, list):
        raise SystemExit("Targets YAML must be a list of entries")
    return data  # type: ignore[return-value]


def _b64_from_data_uri_or_raw(content: str) -> bytes | None:
    try:
        if content.startswith("data:image"):
            b64 = content.split(",", 1)[1]
            return base64.b64decode(b64)
        # heuristic: if it's base64-looking (no spaces, len multiple of 4)
        if " " not in content and len(content) % 4 == 0:
            return base64.b64decode(content)
    except Exception:
        return None
    return None


def _guess_ext_from_headers(headers: dict[str, str] | None) -> str:
    ct = (headers or {}).get("Content-Type", "").lower()
    if "png" in ct:
        return ".png"
    if "jpeg" in ct or "jpg" in ct:
        return ".jpg"
    if "webp" in ct:
        return ".webp"
    return ".png"


def _write_image_bytes(path: Path, content: bytes) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    return path


def spider_screenshot(
    url: str,
    device: str = "desktop",
    delay_ms: int = 1500,
    full_page: bool = False,
) -> tuple[bytes | None, str | None, dict[str, Any]]:
    """Call Spider screenshot endpoint. Returns (image_bytes, download_url, raw_json)."""
    api_key = os.getenv("SPIDER_API_KEY")
    if not api_key:
        raise SystemExit("SPIDER_API_KEY is not set (in env or .env)")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "url": url,
        "device": device,
        "full_page": full_page,
        "delay": delay_ms,
        # Add more options if needed:
        # "wait_until": "networkidle",
        # "viewport": {"width": 1440, "height": 900} for desktop
    }
    resp = requests.post(
        "https://api.spider.cloud/screenshot",
        headers=headers,
        json=payload,
        timeout=120,
    )
    resp.raise_for_status()
    raw = resp.json()
    item = raw[0] if isinstance(raw, list) else raw
    content = item.get("content")

    # Try decode inline content
    if isinstance(content, str):
        b = _b64_from_data_uri_or_raw(content)
        if b is not None:
            return b, None, item
        # If looks like a URL, return as download url
        if content.startswith("http://") or content.startswith("https://"):
            return None, content, item

    # Some APIs return file/url fields
    file_info = item.get("file") if isinstance(item, dict) else None
    if isinstance(file_info, dict):
        url2 = file_info.get("url")
        if isinstance(url2, str):
            return None, url2, item

    # Fallback: return raw item only
    return None, None, item


def download_binary(url: str, headers: dict[str, str] | None = None) -> tuple[bytes, str | None]:
    r = requests.get(url, headers=headers, timeout=120)
    r.raise_for_status()
    return r.content, r.headers.get("Content-Type")


def sanitize_slug(text: str) -> str:
    s = "".join(ch if ch.isalnum() or ch in ("-", "_") else "-" for ch in text.lower())
    while "--" in s:
        s = s.replace("--", "-")
    return s.strip("-") or "shot"


def ensure_iter_devices(dev: str | Iterable[str] | None) -> list[str]:
    if dev is None:
        return ["desktop"]
    if isinstance(dev, str):
        return [dev]
    return list(dev)


def main() -> None:
    load_dotenv()  # load .env if present

    ap = argparse.ArgumentParser(description="Capture screenshots using Spider Cloud")
    ap.add_argument("--targets", default="scripts/screenshots.yml", help="Path to targets YAML")
    ap.add_argument("--out-dir", default=None, help="Output directory (defaults to artifacts/<date>/screenshots)")
    ap.add_argument("--delay", type=int, default=None, help="Override delay in ms for all captures")
    ap.add_argument("--full-page", action="store_true", help="Capture full page height if supported")
    args = ap.parse_args()

    out_dir = _resolve_out_dir(args.out_dir)
    targets = _load_targets(args.targets if args.targets else None)

    print(f"Saving screenshots to: {out_dir}")
    ok = 0
    fail = 0

    for t in targets:
        name = sanitize_slug(t.get("name") or t.get("slug") or t.get("url") or "shot")
        url = t.get("url")
        if not url:
            print(f"! Skipping target without url: {t}")
            continue
        devices = ensure_iter_devices(t.get("devices") or t.get("device"))
        delay_ms = args.delay if args.delay is not None else int(t.get("delay_ms", 1500))
        full_page = bool(args.full_page or t.get("full_page", False))

        for dev in devices:
            try:
                img_bytes, dl_url, raw = spider_screenshot(url, device=dev, delay_ms=delay_ms, full_page=full_page)
                base = out_dir / f"{name}__{dev}"
                if img_bytes is not None:
                    path = _write_image_bytes(base.with_suffix(".png"), img_bytes)
                    print(f"✔ {url} [{dev}] → {path.name}")
                    ok += 1
                    # sidecar json
                    base.with_suffix(".json").write_text(json.dumps(raw, indent=2), encoding="utf-8")
                elif dl_url is not None:
                    # Try to download the file URL
                    try:
                        content, ctype = download_binary(dl_url)
                        ext = ".png" if ctype is None else _guess_ext_from_headers({"Content-Type": ctype})
                        path = _write_image_bytes(base.with_suffix(ext), content)
                        print(f"✔ {url} [{dev}] → {path.name} (downloaded)")
                        ok += 1
                    except Exception as e:
                        print(f"! Download failed for {url} [{dev}] from {dl_url}: {e}")
                        base.with_suffix(".json").write_text(json.dumps(raw, indent=2), encoding="utf-8")
                        fail += 1
                else:
                    # No image, save JSON for inspection
                    base.with_suffix(".json").write_text(json.dumps(raw, indent=2), encoding="utf-8")
                    print(f"! No image content for {url} [{dev}] → saved JSON")
                    fail += 1
            except Exception as e:
                print(f"! Error capturing {url} [{dev}]: {e}")
                fail += 1

    print(f"Done. Success: {ok}, Failed: {fail}")


if __name__ == "__main__":
    main()
