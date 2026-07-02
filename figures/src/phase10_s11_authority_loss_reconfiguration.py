#!/usr/bin/env python3
"""Render-plan source for the S11 authority-loss reconfiguration schematic fixture.

This fixture intentionally uses only deterministic schematic geometry. It does
not encode empirical measurements, mock performance data, final export status,
or manuscript/PDF readiness. S16 remains responsible for final human-facing PDF
export checks.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "generated"
SVG = GENERATED / "phase10_s11_authority_loss_reconfiguration.svg"
PDF = GENERATED / "phase10_s11_authority_loss_reconfiguration.pdf"

SVG_TEXT = """<svg xmlns="http://www.w3.org/2000/svg" width="720" height="360" viewBox="0 0 720 360" role="img" aria-labelledby="title desc">
  <title id="title">Authority-loss reconfiguration schematic</title>
  <desc id="desc">A two-panel schematic showing authority-path degradation and bounded reconfiguration response.</desc>
  <rect width="720" height="360" fill="#f7f7f2"/>
  <text x="36" y="42" font-family="Arial, sans-serif" font-size="18" font-weight="700" fill="#1f2933">A. Authority path degrades</text>
  <text x="390" y="42" font-family="Arial, sans-serif" font-size="18" font-weight="700" fill="#1f2933">B. Bounded reconfiguration</text>
  <rect x="40" y="82" width="92" height="54" rx="10" fill="#d9e8f5" stroke="#355c7d"/>
  <rect x="230" y="82" width="92" height="54" rx="10" fill="#f5d9d9" stroke="#7d3535"/>
  <line x1="132" y1="109" x2="230" y2="109" stroke="#7d3535" stroke-width="4" stroke-dasharray="8 8" marker-end="url(#arrow)"/>
  <text x="58" y="115" font-family="Arial, sans-serif" font-size="13">authority</text>
  <text x="250" y="115" font-family="Arial, sans-serif" font-size="13">loss</text>
  <rect x="398" y="82" width="92" height="54" rx="10" fill="#d9e8f5" stroke="#355c7d"/>
  <rect x="570" y="82" width="92" height="54" rx="10" fill="#ddf0df" stroke="#3b7d35"/>
  <line x1="490" y1="109" x2="570" y2="109" stroke="#3b7d35" stroke-width="4" marker-end="url(#arrow)"/>
  <text x="410" y="115" font-family="Arial, sans-serif" font-size="13">bounded</text>
  <text x="584" y="115" font-family="Arial, sans-serif" font-size="13">response</text>
  <text x="40" y="220" font-family="Arial, sans-serif" font-size="14" fill="#3a3a3a">Explanatory only: the schematic does not claim empirical performance evidence.</text>
  <text x="40" y="248" font-family="Arial, sans-serif" font-size="14" fill="#3a3a3a">Claim strength and caveats are inherited from S04/S08 controls.</text>
  <defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L0,6 L9,3 z" fill="#3a3a3a"/></marker></defs>
</svg>
"""

PDF_PLACEHOLDER = b"%PDF-1.4\n% S11 candidate placeholder. Run downstream export tooling before human-facing PDF delivery.\n"


def main() -> int:
    GENERATED.mkdir(parents=True, exist_ok=True)
    SVG.write_text(SVG_TEXT, encoding="utf-8")
    PDF.write_bytes(PDF_PLACEHOLDER)
    print(f"wrote {SVG}")
    print(f"wrote {PDF}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
