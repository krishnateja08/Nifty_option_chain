"""
patch_table_fix.py
==================
Run this script in the same folder as your main Nifty script.
Usage: python patch_table_fix.py nifty_script.py

It applies targeted find-and-replace fixes to make the Intraday OI Trend
table fit on screen without horizontal scrolling.
"""

import sys
import re
import shutil
from datetime import datetime

# ── All replacements as (exact_old, exact_new) tuples ──────────────────────
PATCHES = [

    # 1. Widen the outer container  (1200px → 1600px)
    (
        ".container{max-width:1200px;",
        ".container{max-width:1600px;"
    ),

    # 2. Reduce table min-width  (1080px → 860px)
    (
        ".oi-table{width:100%;min-width:1080px;border-collapse:collapse;font-family:'JetBrains Mono',monospace;}",
        ".oi-table{width:100%;min-width:860px;border-collapse:collapse;font-family:'JetBrains Mono',monospace;table-layout:fixed;}"
    ),

    # 3. Tighten thead th padding & font
    (
        ".oi-table thead th{padding:11px 14px;font-size:9px;letter-spacing:2px;color:rgba(128,222,234,0.45);text-transform:uppercase;font-weight:700;text-align:right;border-bottom:1px solid rgba(79,195,247,0.15);background:rgba(79,195,247,0.05);white-space:nowrap;}",
        ".oi-table thead th{padding:7px 6px;font-size:8px;letter-spacing:1px;color:rgba(128,222,234,0.45);text-transform:uppercase;font-weight:700;text-align:right;border-bottom:1px solid rgba(79,195,247,0.15);background:rgba(79,195,247,0.05);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}"
    ),

    # 4. Tighten tbody td padding & font
    (
        ".oi-table tbody td{padding:10px 14px;font-size:clamp(11px,1.4vw,13px);text-align:right;color:#b0bec5;white-space:nowrap;}",
        ".oi-table tbody td{padding:7px 6px;font-size:clamp(10px,1.1vw,12px);text-align:right;color:#b0bec5;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}"
    ),

    # 5. Compact signal badges (all 5 variants — do them individually)
    (
        ".oi-signal-ssell{display:inline-block;padding:3px 10px;border-radius:6px;font-size:10px;font-weight:700;letter-spacing:1px;background:rgba(220,38,38,0.2);color:#fca5a5;border:1px solid rgba(220,38,38,0.4);}",
        ".oi-signal-ssell{display:inline-block;padding:2px 6px;border-radius:5px;font-size:9px;font-weight:700;letter-spacing:0.5px;background:rgba(220,38,38,0.2);color:#fca5a5;border:1px solid rgba(220,38,38,0.4);}"
    ),
    (
        ".oi-signal-sell{display:inline-block;padding:3px 10px;border-radius:6px;font-size:10px;font-weight:700;letter-spacing:1px;background:rgba(239,68,68,0.15);color:#f87171;border:1px solid rgba(239,68,68,0.3);}",
        ".oi-signal-sell{display:inline-block;padding:2px 6px;border-radius:5px;font-size:9px;font-weight:700;letter-spacing:0.5px;background:rgba(239,68,68,0.15);color:#f87171;border:1px solid rgba(239,68,68,0.3);}"
    ),
    (
        ".oi-signal-sbuy{display:inline-block;padding:3px 10px;border-radius:6px;font-size:10px;font-weight:700;letter-spacing:1px;background:rgba(5,150,105,0.2);color:#a7f3d0;border:1px solid rgba(5,150,105,0.4);}",
        ".oi-signal-sbuy{display:inline-block;padding:2px 6px;border-radius:5px;font-size:9px;font-weight:700;letter-spacing:0.5px;background:rgba(5,150,105,0.2);color:#a7f3d0;border:1px solid rgba(5,150,105,0.4);}"
    ),
    (
        ".oi-signal-buy{display:inline-block;padding:3px 10px;border-radius:6px;font-size:10px;font-weight:700;letter-spacing:1px;background:rgba(16,185,129,0.15);color:#6ee7b7;border:1px solid rgba(16,185,129,0.3);}",
        ".oi-signal-buy{display:inline-block;padding:2px 6px;border-radius:5px;font-size:9px;font-weight:700;letter-spacing:0.5px;background:rgba(16,185,129,0.15);color:#6ee7b7;border:1px solid rgba(16,185,129,0.3);}"
    ),
    (
        ".oi-signal-neutral{display:inline-block;padding:3px 10px;border-radius:6px;font-size:10px;font-weight:700;letter-spacing:1px;background:rgba(245,158,11,0.12);color:#fde68a;border:1px solid rgba(245,158,11,0.25);}",
        ".oi-signal-neutral{display:inline-block;padding:2px 6px;border-radius:5px;font-size:9px;font-weight:700;letter-spacing:0.5px;background:rgba(245,158,11,0.12);color:#fde68a;border:1px solid rgba(245,158,11,0.25);}"
    ),

    # 6. Compact VWAP bias badges
    (
        ".oi-vwap-bias{display:inline-flex;align-items:center;gap:5px;padding:4px 11px;border-radius:20px;font-size:10px;font-weight:700;letter-spacing:0.8px;white-space:nowrap;}",
        ".oi-vwap-bias{display:inline-flex;align-items:center;gap:3px;padding:2px 7px;border-radius:12px;font-size:9px;font-weight:700;letter-spacing:0.5px;white-space:nowrap;}"
    ),

    # 7. Compact nearest level badge
    (
        ".oi-nlevel-badge{display:inline-block;padding:3px 10px;border-radius:6px;font-size:10px;font-weight:700;letter-spacing:0.5px;white-space:nowrap;}",
        ".oi-nlevel-badge{display:inline-block;padding:2px 6px;border-radius:5px;font-size:9px;font-weight:700;letter-spacing:0.3px;white-space:nowrap;}"
    ),

    # 8. Compact distance value
    (
        ".oi-dist-val{display:inline-block;padding:3px 10px;border-radius:6px;font-size:11px;font-weight:700;font-family:'JetBrains Mono',monospace;}",
        ".oi-dist-val{display:inline-block;padding:2px 6px;border-radius:5px;font-size:9px;font-weight:700;font-family:'JetBrains Mono',monospace;}"
    ),

    # 9. Compact streak widget
    (
        ".oi-streak{display:inline-flex;align-items:center;gap:6px;}",
        ".oi-streak{display:inline-flex;align-items:center;gap:3px;}"
    ),
    (
        ".oi-streak-num{font-family:'Oxanium',sans-serif;font-size:15px;font-weight:800;line-height:1;}",
        ".oi-streak-num{font-family:'Oxanium',sans-serif;font-size:12px;font-weight:800;line-height:1;}"
    ),
    (
        ".oi-streak-lbl{font-size:8px;letter-spacing:0.8px;color:rgba(176,190,197,0.35);text-transform:uppercase;line-height:1.4;}",
        ".oi-streak-lbl{font-size:7px;letter-spacing:0.5px;color:rgba(176,190,197,0.35);text-transform:uppercase;line-height:1.3;}"
    ),

    # 10. Pip dots slightly smaller
    (
        ".oi-pip{width:5px;height:5px;border-radius:50%;flex-shrink:0;}",
        ".oi-pip{width:4px;height:4px;border-radius:50%;flex-shrink:0;}"
    ),

    # 11. Compact Spot Δ badges
    (
        ".oi-sdelta{display:inline-flex;align-items:center;gap:4px;padding:3px 9px;border-radius:6px;font-size:11px;font-weight:700;font-family:'JetBrains Mono',monospace;white-space:nowrap;}",
        ".oi-sdelta{display:inline-flex;align-items:center;gap:2px;padding:2px 6px;border-radius:5px;font-size:9px;font-weight:700;font-family:'JetBrains Mono',monospace;white-space:nowrap;}"
    ),

    # 12. Mobile media query — also keep table font tiny
    (
        ".oi-table thead th,.oi-table tbody td{padding:6px 6px;font-size:9px;}",
        ".oi-table thead th,.oi-table tbody td{padding:4px 4px;font-size:8px;}"
    ),

    # 13. Remove scroll hint on desktop (only show on truly narrow mobile)
    (
        ".oi-table-scroll-hint{display:none;align-items:center;gap:6px;",
        ".oi-table-scroll-hint{display:none;align-items:center;gap:4px;"
    ),

]


def apply_patches(filepath: str) -> None:
    # ── Read source ──────────────────────────────────────────────────
    with open(filepath, "r", encoding="utf-8") as f:
        source = f.read()

    # ── Backup ───────────────────────────────────────────────────────
    ts     = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = f"{filepath}.backup_{ts}"
    shutil.copy2(filepath, backup)
    print(f"✅ Backup saved → {backup}")

    applied = 0
    skipped = 0

    for old, new in PATCHES:
        if old in source:
            source = source.replace(old, new, 1)   # replace only first occurrence
            applied += 1
            print(f"  ✔ Patched: {old[:60].strip()}...")
        else:
            skipped += 1
            print(f"  ⚠ NOT FOUND (already patched or different version): {old[:60].strip()}...")

    # ── Write back ───────────────────────────────────────────────────
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(source)

    print(f"\n{'='*60}")
    print(f"  Applied : {applied} / {len(PATCHES)} patches")
    print(f"  Skipped : {skipped} (not found — may already be patched)")
    print(f"  File    : {filepath}")
    print(f"{'='*60}")
    print("\n✅ Done! Run your Nifty script normally — the next index.html")
    print("   will have a wider container and compact OI table columns.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python patch_table_fix.py <your_nifty_script.py>")
        print("Example: python patch_table_fix.py nifty_report.py")
        sys.exit(1)
    apply_patches(sys.argv[1])
