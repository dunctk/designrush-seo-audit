from __future__ import annotations

from pathlib import Path
from typing import Dict

import polars as pl
import json
import zlib
from zlib import crc32


def _try_import_mpl():
    try:
        import matplotlib

        matplotlib.use("Agg")  # headless
        import matplotlib.pyplot as plt

        return plt
    except Exception:
        return None


def _save_chart_data(df: pl.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.write_csv(path)


def _fmt_value(v: float) -> str:
    # Human-friendly value formatting
    try:
        if abs(v) >= 1_000_000:
            s = f"{v/1_000_000:.1f}M"
            return s.replace(".0M", "M")
        if abs(v) >= 1_000:
            s = f"{v/1_000:.1f}k"
            return s.replace(".0k", "k")
        if float(v).is_integer():
            return f"{int(v):,}"
        return f"{v:,.1f}"
    except Exception:
        return str(v)


def _plot_bar(df: pl.DataFrame, x: str, y: str, title: str, path: Path) -> None:
    plt = _try_import_mpl()
    if plt is None:
        # Fallback: draw a simple PNG bar chart with stdlib
        _simple_bar_png(
            labels=[str(v) for v in df[x].to_list()],
            values=[float(v) for v in df[y].to_list()],
            path=path,
            color=(59, 130, 246),
            with_labels=True,
        )
        _save_chart_data(df, path.with_suffix(".csv"))
        return

    path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 4.5))
    xs = df[x].to_list()
    ys = [float(v) for v in df[y].to_list()]
    bars = ax.bar(xs, ys, color="#3B82F6")
    ax.set_title(title)
    ax.set_xlabel(x)
    ax.set_ylabel(y)
    # Ensure headroom for labels
    if ys:
        ymax = max(ys)
        ax.set_ylim(0, ymax * 1.15)
    for label in ax.get_xticklabels():
        label.set_rotation(30)
        label.set_ha("right")
    # Add value labels
    for rect, v in zip(bars, ys):
        height = rect.get_height()
        ax.annotate(
            _fmt_value(v),
            xy=(rect.get_x() + rect.get_width() / 2, height),
            xytext=(0, 3),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=9,
            color="#111827",
        )
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def generate_all_charts(
    base_dir: Path,
    by_bucket: pl.DataFrame,
    intent: pl.DataFrame,
    categories: pl.DataFrame,
    services: pl.DataFrame,
) -> Dict[str, Path]:
    charts_dir = Path(base_dir) / "charts"
    charts_dir.mkdir(parents=True, exist_ok=True)

    # Position buckets
    buckets_df = by_bucket.select(["pos_bucket", "keywords"]).rename({"pos_bucket": "bucket"})
    buckets_png = charts_dir / "position_buckets.png"
    _plot_bar(buckets_df, "bucket", "keywords", "Keyword Distribution by Position", buckets_png)

    # Intent mix
    intent_df = intent.select(["Keyword Intents", "keywords"]).rename({"Keyword Intents": "intent"})
    intent_png = charts_dir / "intent_mix.png"
    _plot_bar(intent_df, "intent", "keywords", "Intent Mix (by keywords)", intent_png)

    # Categories (coarse)
    cats_df = categories.select(["url_category", "traffic"]).rename({"url_category": "category"})
    cats_png = charts_dir / "categories.png"
    _plot_bar(cats_df, "category", "traffic", "Traffic by Category", cats_png)

    # Services (fine)
    svc_top = services.sort("traffic", descending=True).head(12)
    svc_df = svc_top.select(["service", "traffic"])
    svc_png = charts_dir / "services.png"
    _plot_bar(svc_df, "service", "traffic", "Traffic by Service (Top 12)", svc_png)

    return {
        "position_buckets": buckets_png,
        "intent_mix": intent_png,
        "categories": cats_png,
        "services": svc_png,
    }


def generate_vega_specs(
    base_dir: Path,
    by_bucket: pl.DataFrame,
    intent: pl.DataFrame,
    categories: pl.DataFrame,
    services: pl.DataFrame,
) -> Dict[str, Path]:
    vega_dir = Path(base_dir) / "charts" / "vega"
    vega_dir.mkdir(parents=True, exist_ok=True)

    def write_spec(name: str, data: pl.DataFrame, x: str, y: str, title: str) -> Path:
        # Layer bars + value labels
        spec = {
            "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
            "description": title,
            "data": {"values": data.select([x, y]).to_dicts()},
            "layer": [
                {
                    "mark": {"type": "bar", "tooltip": True},
                    "encoding": {
                        "x": {
                            "field": x,
                            "type": "nominal",
                            "sort": None,
                            "axis": {"labelAngle": -30},
                        },
                        "y": {"field": y, "type": "quantitative"},
                    },
                },
                {
                    "mark": {"type": "text", "dy": -4, "align": "center", "baseline": "bottom"},
                    "encoding": {
                        "x": {"field": x, "type": "nominal", "sort": None},
                        "y": {"field": y, "type": "quantitative"},
                        "text": {"field": y, "type": "quantitative", "format": ",.0f"},
                    },
                },
            ],
            "title": title,
        }
        path = vega_dir / f"{name}.json"
        path.write_text(json.dumps(spec, indent=2), encoding="utf-8")
        return path

    out: Dict[str, Path] = {}
    out["position_buckets"] = write_spec(
        "position_buckets",
        by_bucket.rename({"pos_bucket": "bucket"}),
        "bucket",
        "keywords",
        "Keyword Distribution by Position",
    )
    out["intent_mix"] = write_spec(
        "intent_mix",
        intent.rename({"Keyword Intents": "intent"}),
        "intent",
        "keywords",
        "Intent Mix (by keywords)",
    )
    out["categories"] = write_spec(
        "categories",
        categories.rename({"url_category": "category"}),
        "category",
        "traffic",
        "Traffic by Category",
    )
    out["services"] = write_spec(
        "services",
        services.sort("traffic", descending=True).head(12),
        "service",
        "traffic",
        "Traffic by Service (Top 12)",
    )
    return out


# ---------------- Simple PNG renderer (no external deps) ---------------- #

def _simple_bar_png(labels: list[str], values: list[float], path: Path, color=(59, 130, 246), with_labels: bool = False) -> None:
    width, height = 800, 450
    margin_left, margin_right, margin_top, margin_bottom = 70, 20, 40, 50
    chart_w = width - margin_left - margin_right
    chart_h = height - margin_top - margin_bottom

    img = _new_img(width, height, (255, 255, 255))
    # Axes
    _draw_rect(img, margin_left, height - margin_bottom, width - margin_right, height - margin_bottom + 1, (0, 0, 0))
    _draw_rect(img, margin_left - 1, margin_top, margin_left, height - margin_bottom, (0, 0, 0))

    n = max(1, len(values))
    vmax = max(1.0, max(values) if values else 1.0)
    bar_space = chart_w / n
    bar_w = max(1, int(bar_space * 0.6))

    for i, v in enumerate(values):
        h = int((v / vmax) * (chart_h - 2))
        x_center = int(margin_left + i * bar_space + bar_space / 2)
        x0 = x_center - bar_w // 2
        x1 = x_center + bar_w // 2
        y1 = height - margin_bottom - 1
        y0 = y1 - h
        _draw_rect(img, x0, y0, x1, y1, color)
        if with_labels:
            text = _fmt_short(v)
            tx_w = _text_width(text, scale=2)
            tx_h = 7 * 2
            tx = x_center - tx_w // 2
            ty_above = y0 - 6 - tx_h
            ty_inside = y0 + 4
            if ty_above > margin_top:
                _draw_text(img, tx, ty_above, text, color=(17, 24, 39), scale=2)
            else:
                # draw inside bar near top in white for contrast
                _draw_text(img, tx, ty_inside, text, color=(255, 255, 255), scale=2)

    _write_png(path, img)


# --- Tiny 5x7 bitmap font for fallback labels --- #
_FONT_5x7: Dict[str, list[str]] = {
    "0": [
        " ### ",
        "#   #",
        "#  ##",
        "# # #",
        "##  #",
        "#   #",
        " ### ",
    ],
    "1": [
        "  #  ",
        " ##  ",
        "  #  ",
        "  #  ",
        "  #  ",
        "  #  ",
        " ### ",
    ],
    "2": [
        " ### ",
        "#   #",
        "    #",
        "   # ",
        "  #  ",
        " #   ",
        "#####",
    ],
    "3": [
        " ### ",
        "#   #",
        "    #",
        " ### ",
        "    #",
        "#   #",
        " ### ",
    ],
    "4": [
        "   # ",
        "  ## ",
        " # # ",
        "#  # ",
        "#####",
        "   # ",
        "   # ",
    ],
    "5": [
        "#####",
        "#    ",
        "#### ",
        "    #",
        "    #",
        "#   #",
        " ### ",
    ],
    "6": [
        " ### ",
        "#   ",
        "#    ",
        "#### ",
        "#   #",
        "#   #",
        " ### ",
    ],
    "7": [
        "#####",
        "    #",
        "   # ",
        "  #  ",
        "  #  ",
        "  #  ",
        "  #  ",
    ],
    "8": [
        " ### ",
        "#   #",
        "#   #",
        " ### ",
        "#   #",
        "#   #",
        " ### ",
    ],
    "9": [
        " ### ",
        "#   #",
        "#   #",
        " ####",
        "    #",
        "   # ",
        " ### ",
    ],
    ".": [
        "     ",
        "     ",
        "     ",
        "     ",
        "     ",
        " ### ",
        " ### ",
    ],
    "k": [
        "     ",
        "#   #",
        "#  # ",
        "###  ",
        "#  # ",
        "#   #",
        "     ",
    ],
    "M": [
        "#   #",
        "## ##",
        "# # #",
        "#   #",
        "#   #",
        "#   #",
        "#   #",
    ],
}


def _fmt_short(v: float) -> str:
    s = _fmt_value(v)
    # Replace thousand separators to avoid unsupported chars in tiny font
    return s.replace(",", "")


def _text_width(text: str, scale: int = 1, spacing: int = 1) -> int:
    w = 0
    for ch in text:
        glyph = _FONT_5x7.get(ch)
        if glyph is None:
            glyph_w = 3  # unknown char spacing
        else:
            glyph_w = len(glyph[0])
        w += glyph_w * scale + spacing * scale
    return max(0, w - spacing * scale)


def _draw_text(img: list[bytearray], x: int, y: int, text: str, color=(0, 0, 0), scale: int = 1, spacing: int = 1) -> None:
    cx = x
    for ch in text:
        glyph = _FONT_5x7.get(ch)
        if glyph is None:
            cx += (3 + spacing) * scale
            continue
        gw = len(glyph[0])
        gh = len(glyph)
        for gy in range(gh):
            row = glyph[gy]
            for gx in range(gw):
                if row[gx] != " ":
                    _draw_rect(img, cx + gx * scale, y + gy * scale, cx + (gx + 1) * scale, y + (gy + 1) * scale, color)
        cx += (gw + spacing) * scale


def _new_img(w: int, h: int, color=(255, 255, 255)) -> list[bytearray]:
    r, g, b = color
    row = bytearray([r, g, b] * w)
    return [bytearray(row)[:] for _ in range(h)]


def _draw_rect(img: list[bytearray], x0: int, y0: int, x1: int, y1: int, color=(0, 0, 0)) -> None:
    h = len(img)
    w = len(img[0]) // 3
    r, g, b = color
    x0 = max(0, min(w, x0))
    x1 = max(0, min(w, x1))
    y0 = max(0, min(h, y0))
    y1 = max(0, min(h, y1))
    if x0 > x1:
        x0, x1 = x1, x0
    if y0 > y1:
        y0, y1 = y1, y0
    for y in range(y0, y1):
        row = img[y]
        for x in range(x0, x1):
            idx = x * 3
            row[idx] = r
            row[idx + 1] = g
            row[idx + 2] = b


def _write_png(path: Path, img: list[bytearray]) -> None:
    h = len(img)
    if h == 0:
        return
    w = len(img[0]) // 3
    # Prepare scanlines: each row prefixed with filter byte 0
    raw = b"".join(b"\x00" + bytes(row) for row in img)
    comp = zlib.compress(raw, 9)

    def chunk(tag: bytes, data: bytes) -> bytes:
        return (
            len(data).to_bytes(4, "big")
            + tag
            + data
            + crc32(tag + data).to_bytes(4, "big")
        )

    ihdr = (
        w.to_bytes(4, "big")
        + h.to_bytes(4, "big")
        + b"\x08"  # bit depth 8
        + b"\x02"  # color type RGB
        + b"\x00\x00\x00"  # compression, filter, interlace
    )
    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", comp) + chunk(b"IEND", b"")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(png)
