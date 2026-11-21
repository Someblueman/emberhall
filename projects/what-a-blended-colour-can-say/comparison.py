"""Frozen M3 held-out comparison pack, baseline distribution views, and scorer."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from fractions import Fraction as F
from html import escape
import json
from pathlib import Path
import re
from typing import Mapping, Sequence

import blended_colour as bc
import display_colour as dc
import quantized_bounds as qb
import render_legend as rl
from verify_atlas import verify_atlas

PROJECT_DIR = Path(__file__).resolve().parent
DEFAULT_OUT_DIR = PROJECT_DIR / "comparison"

_CASE_ORDER_MAP = {
    "dist_a_then_atlas_b": ("A", "B"),
    "atlas_a_then_dist_b": ("B", "A"),
}


@dataclass(frozen=True)
class ComparisonCase:
    """One held-out comparison item paired across Set A and Set B."""

    case: rl.Case
    set_name: str
    regime: str
    query_mode: str
    probe_op: str
    probe_threshold: F
    dist_order: tuple[str, str]

    def probe_question(self) -> str:
        pct = _exact_pct_label(self.probe_threshold)
        scope = (
            "exact linear-light model"
            if self.query_mode == "exact"
            else f"{self.query_mode} conservative observation model"
        )
        verb = f"exceed {pct}" if self.probe_op == "gt" else f"be below {pct}"
        return f"Under the {scope}, could {self.case.event_label} {verb}? (YES / NO)"


def _exact_pct_label(value: F) -> str:
    scaled = value * 100
    if scaled.denominator == 1:
        return f"{scaled.numerator}%"
    return f"{float(scaled):.2f}%"


def _round_pct_2(value: F) -> str:
    """Nearest 0.01% (half-up) using integer arithmetic only."""
    scaled = value * 10000 + F(1, 2)
    n = scaled.numerator // scaled.denominator
    return f"{n // 100}.{n % 100:02d}%"


def _outward_pct_range(p_min: F, p_max: F) -> tuple[str, str]:
    lo_x = p_min * 10000
    hi_x = p_max * 10000
    lo_n = lo_x.numerator // lo_x.denominator
    hi_n = -(-hi_x.numerator // hi_x.denominator)
    return f"{lo_n // 100}.{lo_n % 100:02d}%", f"{hi_n // 100}.{hi_n % 100:02d}%"


def heldout_palettes() -> dict[str, bc.Palette]:
    """Three held-out palettes distinct from M1/M2 built-in and example palettes."""
    c0 = (F(1, 20), F(3, 20), F(3, 5))
    c1 = (F(1, 10), F(3, 5), F(1, 2))
    c3 = (F(4, 5), F(7, 20), F(1, 20))
    c4 = (F(3, 4), F(1, 20), F(2, 5))
    c2 = tuple(
        F(1, 4) * a + F(1, 4) * b + F(1, 5) * d + F(3, 10) * e
        for a, b, d, e in zip(c0, c1, c3, c4)
    )
    pa = bc.Palette(
        "citrus_slate_3d",
        ("T1 Minimal", "T2 Low", "T3 Moderate", "T4 High", "T5 Severe"),
        tuple(F(i + 1) for i in range(5)),
        (c0, c1, c2, c3, c4),
        "Held-out 3D 5-stop palette A with interior stop T3 inside conv(T1, T2, T4, T5).",
    )

    d0 = (F(1, 10), F(1, 10), F(7, 10))
    d1 = (F(1, 5), F(13, 20), F(1, 5))
    d3 = (F(17, 20), F(1, 5), F(1, 10))
    d4 = (F(3, 5), F(1, 10), F(11, 20))
    d2 = tuple(
        F(3, 10) * a + F(1, 5) * b + F(1, 4) * d + F(1, 4) * e
        for a, b, d, e in zip(d0, d1, d3, d4)
    )
    pb = bc.Palette(
        "ochre_indigo_3d",
        ("G1 Safe", "G2 Guarded", "G3 Moderate", "G4 Elevated", "G5 Critical"),
        tuple(F(i + 1) for i in range(5)),
        (d0, d1, d2, d3, d4),
        "Held-out 3D 5-stop palette B with interior stop G3 inside conv(G1, G2, G4, G5).",
    )

    r0 = (F(1, 10), F(1, 5), F(7, 10))
    r4 = (F(9, 10), F(2, 5), F(1, 10))
    ramp_colours = tuple(
        tuple((1 - F(k, 4)) * a + F(k, 4) * b for a, b in zip(r0, r4))
        for k in range(5)
    )
    pr = bc.Palette(
        "amber_navy_ramp",
        ("R1", "R2", "R3", "R4", "R5"),
        tuple(F(i + 1) for i in range(5)),
        ramp_colours,
        "Held-out 1D collinear 5-stop ramp for non-stop unidentifiable blend.",
    )
    return {pa.name: pa, pb.name: pb, pr.name: pr}


def heldout_specs() -> tuple[ComparisonCase, ...]:
    """Matched Set A and Set B held-out cases spanning all five required regimes."""
    return (
        ComparisonCase(
            rl.Case("H1A", "Held-out outer face A", "citrus_slate_3d",
                    (F(3, 10), F(3, 10), F(0), F(2, 5), F(0)), (3, 4), "P(Tier >= 4)", True),
            "A", "EXACT", "exact", "gt", F(9, 20), ("min", "max"),
        ),
        ComparisonCase(
            rl.Case("H2A", "Held-out interior blend A", "citrus_slate_3d",
                    (F(0), F(1, 5), F(2, 5), F(1, 5), F(1, 5)), (3, 4), "P(Tier >= 4)", True),
            "A", "BOUNDED", "exact", "gt", F(11, 20), ("max", "min"),
        ),
        ComparisonCase(
            rl.Case("H3A", "Held-out stop T3 (Mid)", "citrus_slate_3d",
                    (F(0), F(0), F(1), F(0), F(0)), (2,), "P(Tier 3)", True),
            "A", "UNIDENTIFIABLE", "exact", "gt", F(4, 5), ("min", "max"),
        ),
        ComparisonCase(
            rl.Case("H4A", "Held-out sRGB8 blend A", "citrus_slate_3d",
                    (F(1, 4), F(1, 4), F(0), F(0), F(1, 2)), (3, 4), "P(Tier >= 4)", True),
            "A", "ROUNDED_SRGB8", "srgb8", "lt", F(12, 25), ("max", "min"),
        ),
        ComparisonCase(
            rl.Case("H5A", "Held-out linear8 blend A", "citrus_slate_3d",
                    (F(1, 10), F(2, 5), F(0), F(3, 10), F(1, 5)), (3, 4), "P(Tier >= 4)", True),
            "A", "ROUNDED_LINEAR8", "linear8", "gt", F(11, 20), ("min", "max"),
        ),
        ComparisonCase(
            rl.Case("H1B", "Held-out outer face B", "ochre_indigo_3d",
                    (F(1, 8), F(1, 4), F(0), F(0), F(5, 8)), (3, 4), "P(Grade >= 4)", True),
            "B", "EXACT", "exact", "gt", F(11, 20), ("min", "max"),
        ),
        ComparisonCase(
            rl.Case("H2B", "Held-out interior blend B", "ochre_indigo_3d",
                    (F(0), F(1, 4), F(1, 4), F(1, 4), F(1, 4)), (3, 4), "P(Grade >= 4)", True),
            "B", "BOUNDED", "exact", "lt", F(9, 20), ("max", "min"),
        ),
        ComparisonCase(
            rl.Case("H3B", "Held-out ramp mix B", "amber_navy_ramp",
                    (F(1, 4), F(0), F(3, 4), F(0), F(0)), (1, 3), "P(R2 or R4)", True),
            "B", "UNIDENTIFIABLE", "exact", "lt", F(3, 20), ("min", "max"),
        ),
        ComparisonCase(
            rl.Case("H4B", "Held-out sRGB8 blend B", "ochre_indigo_3d",
                    (F(3, 10), F(1, 10), F(0), F(3, 5), F(0)), (3, 4), "P(Grade >= 4)", True),
            "B", "ROUNDED_SRGB8", "srgb8", "gt", F(13, 20), ("max", "min"),
        ),
        ComparisonCase(
            rl.Case("H5B", "Held-out linear8 blend B", "ochre_indigo_3d",
                    (F(1, 5), F(1, 5), F(0), F(2, 5), F(1, 5)), (3, 4), "P(Grade >= 4)", True),
            "B", "ROUNDED_LINEAR8", "linear8", "lt", F(13, 50), ("min", "max"),
        ),
    )


def _evaluate_spec(spec: ComparisonCase, palettes: Mapping[str, bc.Palette]) -> dict:
    pal = palettes[spec.case.palette]
    rgb = bc.blend_colour(pal, spec.case.weights)
    exact_cert = bc.solve_event_bounds(pal, rgb, spec.case.event_indices)
    bc.verify_certificate(pal, rgb, spec.case.event_indices, exact_cert)

    obs_certs: dict[str, dict] = {}
    for mode in dc.MODES:
        rgb8 = dc.encode_rgb(rgb, mode)
        box_cert = qb.solve_observation(pal, rgb8, spec.case.event_indices, mode)
        qb.verify_observation(pal, rgb8, spec.case.event_indices, box_cert, mode)
        obs_certs[mode] = {
            "mode": mode,
            "rgb8": list(rgb8),
            "hex": dc.hex_rgb(rgb8),
            "cert": box_cert,
        }

    if spec.query_mode == "exact":
        p_min, p_max = exact_cert.p_min, exact_cert.p_max
        status = exact_cert.status
        w_min, w_max = exact_cert.witness_min, exact_cert.witness_max
        p_min_pct, p_max_pct = _round_pct_2(p_min), _round_pct_2(p_max)
    else:
        chosen = obs_certs[spec.query_mode]["cert"]
        p_min, p_max = chosen.p_min, chosen.p_max
        status = (
            "EXACT"
            if p_min == p_max
            else "UNIDENTIFIABLE"
            if p_min == 0 and p_max == 1
            else "BOUNDED"
        )
        w_min, w_max = chosen.witness_min, chosen.witness_max
        p_min_pct, p_max_pct = _outward_pct_range(p_min, p_max)

    q4_bool = p_max > spec.probe_threshold if spec.probe_op == "gt" else p_min < spec.probe_threshold
    return {
        "spec": spec,
        "rgb": rgb,
        "displayed_hex": bc.rgb_to_hex(rgb),
        "exact_cert": exact_cert,
        "obs_certs": obs_certs,
        "queried_p_min": p_min,
        "queried_p_max": p_max,
        "queried_p_min_pct": p_min_pct,
        "queried_p_max_pct": p_max_pct,
        "queried_status": status,
        "queried_witness_min": w_min,
        "queried_witness_max": w_max,
        "q4_answer": "YES" if q4_bool else "NO",
    }


def build_distribution_html(
    evaluated: Sequence[dict],
    palettes: Mapping[str, bc.Palette],
    title: str,
) -> str:
    """Build the equal-information explicit-distribution baseline HTML view.

    Deliberately omits precomputed event intervals, status labels, and keys.
    """
    cards = []
    options = "".join(
        f'<option value="{i}">{escape(item["spec"].case.id + " / " + item["spec"].case.title)}</option>'
        for i, item in enumerate(evaluated)
    )
    for i, item in enumerate(evaluated):
        spec: ComparisonCase = item["spec"]
        case = spec.case
        pal = palettes[case.palette]

        stop_rows = []
        for idx, (label, colour) in enumerate(zip(pal.labels, pal.colours)):
            mark = " (in target event)" if idx in case.event_indices else ""
            stop_rows.append(
                f'<li><span class="chip" style="background:{bc.rgb_to_hex(colour)}" '
                f'aria-hidden="true"></span><code>{escape(label)}</code>{escape(mark)}</li>'
            )

        if spec.query_mode == "exact":
            scope_line = "Model scope: exact linear-light blend"
        else:
            obs = item["obs_certs"][spec.query_mode]
            rgb8_str = ", ".join(str(v) for v in obs["rgb8"])
            scope_line = f"Model scope: {spec.query_mode} observation {obs['hex']} (bytes {rgb8_str})"

        dist_blocks = []
        weights_by_key = {
            "min": item["queried_witness_min"],
            "max": item["queried_witness_max"],
        }
        for pos, which in enumerate(spec.dist_order, start=1):
            weights = weights_by_key[which]
            bars = "".join(
                f'<span style="flex:{float(w):.12g};background:{bc.rgb_to_hex(pal.colours[k])}"></span>'
                for k, w in enumerate(weights)
                if w
            )
            if spec.query_mode == "exact":
                labels = "; ".join(
                    f"{pal.labels[k]}: {bc._frac_str(w)}"
                    for k, w in enumerate(weights)
                    if w
                )
            else:
                labels = "; ".join(
                    f"{pal.labels[k]}: {_round_pct_2(w)}"
                    for k, w in enumerate(weights)
                    if w
                )
            dist_blocks.append(
                f"<p><b>Compatible distribution {pos}</b></p>"
                f'<div class="bar" aria-hidden="true">{bars}</div>'
                f'<p class="numbers">{escape(labels)}</p>'
            )

        target_names = ", ".join(pal.labels[idx] for idx in case.event_indices)
        cards.append(
            f'<article data-case="{i}"><h2>{escape(case.id + " / " + case.title)}</h2>'
            f'<div class="columns"><section>'
            f'<div class="swatch" style="background:{item["displayed_hex"]}" role="img" '
            f'aria-label="Displayed sRGB colour {item["displayed_hex"]}"></div>'
            f'<p><code>{item["displayed_hex"]}</code> · displayed sRGB8</p>'
            f"<p><b>Target event</b>: {escape(case.event_label)} "
            f"({escape(target_names)})</p>"
            f"<p>{escape(scope_line)}</p>"
            f'<ul class="stops">{"".join(stop_rows)}</ul>'
            f'</section><section aria-label="Compatible explicit distributions">'
            f'{"".join(dist_blocks)}</section></div></article>'
        )

    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(title)}</title><style>
*{{box-sizing:border-box}}body{{margin:0;background:#f3f1e9;color:#172c3c;font:17px/1.5 system-ui,sans-serif}}main{{max-width:1080px;margin:auto;padding:24px}}h1{{font:36px Georgia,serif}}h2{{font-size:22px}}article{{background:white;border:1px solid #d6d9d8;border-radius:12px;margin:24px 0;padding:22px}}.columns{{display:grid;grid-template-columns:1fr 1fr;gap:32px}}.bar{{height:28px;display:flex;border:1px solid #526776}}.numbers{{overflow-wrap:anywhere;font-size:15px}}.swatch{{width:140px;height:95px;border:1px solid #526776}}code{{font-size:15px}}.stops{{list-style:none;padding:0;margin:12px 0 0;font-size:15px}}.stops li{{display:flex;align-items:center;gap:8px;margin:4px 0}}.chip{{display:inline-block;width:16px;height:16px;border:1px solid #526776;flex:0 0 auto}}[hidden]{{display:none!important}}.tools{{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin:16px 0}}select{{font:inherit;padding:8px;max-width:100%}}:focus-visible{{outline:3px solid #14547a;outline-offset:3px}}@media(max-width:650px){{main{{padding:14px}}h1{{font-size:29px}}.columns{{grid-template-columns:1fr;gap:8px}}article{{padding:16px}}}}
</style></head><body><main><h1>{escape(title)}</h1>
<p>Explicit-distribution baseline view. Each card shows the displayed sRGB8 swatch, palette stops for the queried event, and two extremal compatible stop distributions for the stated scope.</p>
<div class="tools" id="view-tools" hidden>
<label for="case-choice">Case</label><select id="case-choice"><option value="all">All cases</option>{options}</select></div>
<div id="card-view">{"".join(cards)}</div>
<footer>Supported: declared rational linear-light sRGB palettes, exact colours, sRGB8 and linear8 observations, half-up rounding.</footer></main><script>
const choice = document.getElementById('case-choice');
function showCase() {{
  const index = choice.value;
  document.querySelectorAll('article[data-case]').forEach(card => {{
    card.hidden = index !== 'all' && card.dataset.case !== index;
  }});
}}
choice.addEventListener('change', showCase);
document.getElementById('view-tools').hidden = false;
</script></body></html>"""


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def generate_comparison_pack(out_dir: Path | None = None) -> dict[str, object]:
    """Deterministically generate all frozen inputs, views, certificates, and keys."""
    target = out_dir if out_dir is not None else DEFAULT_OUT_DIR
    target.mkdir(parents=True, exist_ok=True)

    palettes = heldout_palettes()
    specs = heldout_specs()
    evaluated = [_evaluate_spec(spec, palettes) for spec in specs]

    prompts_cases = []
    input_cases = []
    key_cases = {}

    for item in evaluated:
        spec: ComparisonCase = item["spec"]
        case = spec.case
        prompts_cases.append(
            {
                "id": case.id,
                "set": spec.set_name,
                "title": case.title,
                "palette": case.palette,
                "event_label": case.event_label,
                "query_mode": spec.query_mode,
                "q1": "Minimum compatible probability p_min for the target event (fraction or %)",
                "q2": "Maximum compatible probability p_max for the target event (fraction or %)",
                "q3": "Identifiability status (EXACT / BOUNDED / UNIDENTIFIABLE)",
                "q4": spec.probe_question(),
                "q5": "Clarity rating (1 to 5 integer) and brief note",
            }
        )
        input_cases.append(
            {
                "id": case.id,
                "set": spec.set_name,
                "regime": spec.regime,
                "title": case.title,
                "palette": case.palette,
                "weights": [bc._frac_str(w) for w in case.weights],
                "event_indices": list(case.event_indices),
                "event_label": case.event_label,
                "query_mode": spec.query_mode,
                "probe_op": spec.probe_op,
                "probe_threshold": bc._frac_str(spec.probe_threshold),
                "dist_order": list(spec.dist_order),
            }
        )
        key_cases[case.id] = {
            "id": case.id,
            "set": spec.set_name,
            "regime": spec.regime,
            "query_mode": spec.query_mode,
            "displayed_hex": item["displayed_hex"],
            "p_min": bc._frac_str(item["queried_p_min"]),
            "p_max": bc._frac_str(item["queried_p_max"]),
            "p_min_pct": item["queried_p_min_pct"],
            "p_max_pct": item["queried_p_max_pct"],
            "status": item["queried_status"],
            "q4_answer": item["q4_answer"],
            "probe_op": spec.probe_op,
            "probe_threshold": bc._frac_str(spec.probe_threshold),
            "exact_p_min": bc._frac_str(item["exact_cert"].p_min),
            "exact_p_max": bc._frac_str(item["exact_cert"].p_max),
            "srgb8_hex": item["obs_certs"]["srgb8"]["hex"],
            "linear8_hex": item["obs_certs"]["linear8"]["hex"],
        }

    palette_payload = {
        name: {
            "labels": list(pal.labels),
            "values": [bc._frac_str(v) for v in pal.values],
            "colours": [[bc._frac_str(ch) for ch in col] for col in pal.colours],
            "description": pal.description,
        }
        for name, pal in palettes.items()
    }

    _write_json(
        target / "prompts.json",
        {
            "schema": "blended-colour-m3-prompts-v1",
            "orders": {
                "dist_a_then_atlas_b": {
                    "first": "dist_a/index.html",
                    "second": "atlas_b/first_legend.html",
                    "default_for_first_non_author": True,
                },
                "atlas_a_then_dist_b": {
                    "first": "atlas_a/first_legend.html",
                    "second": "dist_b/index.html",
                    "default_for_first_non_author": False,
                },
            },
            "cases": prompts_cases,
        },
    )
    _write_json(
        target / "inputs" / "heldout_spec.json",
        {
            "schema": "blended-colour-m3-heldout-spec-v1",
            "palettes": palette_payload,
            "cases": input_cases,
        },
    )
    _write_json(
        target / "keys" / "answer_keys.json",
        {
            "schema": "blended-colour-m3-keys-v1",
            "tolerance": "1/200",
            "cases": key_cases,
        },
    )

    for set_letter, set_name in (("a", "A"), ("b", "B")):
        subset_specs = [s for s in specs if s.set_name == set_name]
        subset_eval = [item for item in evaluated if item["spec"].set_name == set_name]
        subset_palettes = {
            s.case.palette: palettes[s.case.palette] for s in subset_specs
        }
        atlas_out = rl.render_atlas(
            subset_palettes,
            [s.case for s in subset_specs],
            modes=dc.MODES,
            title=f"Held-Out Comparison Set {set_name}: Probability-Interval Atlas",
        )
        atlas_dir = target / f"atlas_{set_letter}"
        atlas_dir.mkdir(parents=True, exist_ok=True)
        (atlas_dir / "first_legend.svg").write_text(atlas_out["svg"], encoding="utf-8")
        (atlas_dir / "first_legend.html").write_text(atlas_out["html"], encoding="utf-8")
        (atlas_dir / "witnesses.json").write_text(atlas_out["witnesses"], encoding="utf-8")

        cert_path = target / "certificates" / f"set_{set_letter}_certificates.json"
        cert_path.parent.mkdir(parents=True, exist_ok=True)
        cert_path.write_text(atlas_out["witnesses"], encoding="utf-8")

        dist_html = build_distribution_html(
            subset_eval,
            subset_palettes,
            f"Held-Out Comparison Set {set_name}: Explicit Distributions",
        )
        dist_dir = target / f"dist_{set_letter}"
        dist_dir.mkdir(parents=True, exist_ok=True)
        (dist_dir / "index.html").write_text(dist_html, encoding="utf-8")

    return {"cases": len(specs), "sets": 2, "out_dir": str(target)}


def verify_comparison_pack(comp_dir: Path | None = None) -> tuple[int, int]:
    """Verify frozen certificates, keys, and baseline HTML non-leakage without optimization."""
    target = comp_dir if comp_dir is not None else DEFAULT_OUT_DIR
    total_cases = 0
    total_obs = 0
    cert_by_id: dict[str, dict] = {}

    for set_letter in ("a", "b"):
        cert_data = json.loads(
            (target / "certificates" / f"set_{set_letter}_certificates.json").read_text(encoding="utf-8")
        )
        atlas_witnesses = json.loads(
            (target / f"atlas_{set_letter}" / "witnesses.json").read_text(encoding="utf-8")
        )
        if cert_data != atlas_witnesses:
            raise ValueError(f"Certificate bundle and atlas witnesses differ for set {set_letter}")
        c_count, o_count = verify_atlas(cert_data)
        total_cases += c_count
        total_obs += o_count
        for swatch in cert_data["swatches"]:
            cert_by_id[swatch["id"]] = swatch

        dist_html = (target / f"dist_{set_letter}" / "index.html").read_text(encoding="utf-8")
        for forbidden in ("EXACT", "BOUNDED", "UNIDENTIFIABLE", "conservative", "witnesses.json", "answer_keys"):
            if forbidden in dist_html:
                raise ValueError(f"Baseline view dist_{set_letter} leaks forbidden token {forbidden!r}")

    keys_data = json.loads((target / "keys" / "answer_keys.json").read_text(encoding="utf-8"))
    specs = {s.case.id: s for s in heldout_specs()}
    if set(keys_data["cases"]) != set(specs) or set(cert_by_id) != set(specs):
        raise ValueError("Case ID mismatch across specs, keys, and certificates")

    for cid, key in keys_data["cases"].items():
        swatch = cert_by_id[cid]
        if key["query_mode"] == "exact":
            cert_dict = swatch["certificate"]
        else:
            obs = next(o for o in swatch["observations"] if o["mode"] == key["query_mode"])
            cert_dict = obs["certificate"]
        if (key["p_min"], key["p_max"]) != (cert_dict["p_min"], cert_dict["p_max"]):
            raise ValueError(f"Answer key bounds disagree with verified certificate for {cid}")

    return total_cases, total_obs


def _parse_probability(raw: object) -> F:
    if isinstance(raw, (int, float)) and not isinstance(raw, bool):
        val = F(str(raw))
    elif isinstance(raw, str):
        text = raw.strip()
        if text.endswith("%"):
            val = F(text[:-1].strip()) / 100
        elif re.fullmatch(r"[+-]?\d+(?:/\d+)?", text) or re.fullmatch(r"[+-]?\d+(?:\.\d+)?", text):
            val = F(text)
        else:
            raise ValueError(f"Unrecognized probability format: {raw!r}")
    else:
        raise ValueError(f"Unsupported probability value: {raw!r}")
    if not F(0) <= val <= F(1):
        raise ValueError(f"Probability {val} out of [0, 1]")
    return val


def _score_view(view_answers: dict, keys_cases: dict, expected_set: str) -> dict:
    expected_ids = {cid for cid, k in keys_cases.items() if k["set"] == expected_set}
    if set(view_answers) != expected_ids:
        raise ValueError(f"Expected case IDs {sorted(expected_ids)} for set {expected_set}, got {sorted(view_answers)}")

    tol = F(1, 200)
    total_points = 0
    all_status_ok = True
    unidentifiable_ok = True
    clarities = []
    per_case = {}

    for cid in sorted(expected_ids):
        ans = view_answers[cid]
        key = keys_cases[cid]
        p_min_ans = _parse_probability(ans["q1_p_min"])
        p_max_ans = _parse_probability(ans["q2_p_max"])
        q1_ok = abs(p_min_ans - F(key["p_min"])) <= tol
        q2_ok = abs(p_max_ans - F(key["p_max"])) <= tol
        q3_ok = str(ans["q3_status"]).strip().upper() == key["status"]
        q4_ok = str(ans["q4_probe"]).strip().upper() == key["q4_answer"]
        clarity = int(ans["q5_clarity"])
        if not 1 <= clarity <= 5:
            raise ValueError(f"Clarity rating must be in 1..5 for {cid}")

        pts = int(q1_ok) + int(q2_ok) + int(q3_ok) + int(q4_ok)
        total_points += pts
        if not q3_ok:
            all_status_ok = False
            if key["status"] == "UNIDENTIFIABLE":
                unidentifiable_ok = False
        clarities.append(clarity)
        per_case[cid] = {
            "points": pts,
            "q1_ok": q1_ok,
            "q2_ok": q2_ok,
            "q3_ok": q3_ok,
            "q4_ok": q4_ok,
            "clarity": clarity,
        }

    return {
        "score": total_points,
        "max_score": 20,
        "all_status_ok": all_status_ok,
        "unidentifiable_ok": unidentifiable_ok,
        "clarity_mean": sum(clarities) / len(clarities),
        "per_case": per_case,
    }


def score_responses(responses: dict, keys: dict) -> dict:
    """Apply the pre-registered M3 scoring and PASS/INCONCLUSIVE/FAIL decision rules."""
    order = responses.get("order")
    if order not in _CASE_ORDER_MAP:
        raise ValueError(f"Unsupported presentation order {order!r}")
    dist_set, atlas_set = _CASE_ORDER_MAP[order]
    keys_cases = keys["cases"]

    atlas_res = _score_view(responses["atlas_view"], keys_cases, atlas_set)
    dist_res = _score_view(responses["dist_view"], keys_cases, dist_set)
    phone_desktop_ok = bool(responses.get("phone_desktop_ok", False))

    acc_diff = atlas_res["score"] - dist_res["score"]
    clarity_diff = atlas_res["clarity_mean"] - dist_res["clarity_mean"]

    fail_reasons = []
    if not phone_desktop_ok:
        fail_reasons.append("phone/desktop viewer check did not pass")
    if atlas_res["score"] < 17:
        fail_reasons.append(f"atlas score {atlas_res['score']}/20 < 17/20")
    if not atlas_res["unidentifiable_ok"]:
        fail_reasons.append("atlas misclassified an UNIDENTIFIABLE case")
    if not atlas_res["all_status_ok"]:
        fail_reasons.append("atlas missed one or more Q3 status classifications")
    if atlas_res["clarity_mean"] < 4.0:
        fail_reasons.append(f"atlas mean clarity {atlas_res['clarity_mean']:.2f} < 4.0")
    if acc_diff < 0:
        fail_reasons.append(f"baseline outperformed atlas ({dist_res['score']} vs {atlas_res['score']})")

    if fail_reasons:
        outcome = "FAIL"
        reason = "; ".join(fail_reasons)
    elif acc_diff >= 2 or (atlas_res["score"] >= 18 and dist_res["score"] >= 18 and clarity_diff >= 1.0):
        outcome = "PASS"
        reason = (
            f"atlas meets accuracy ({atlas_res['score']}/20, 5/5 status) and clarity "
            f"({atlas_res['clarity_mean']:.2f}/5) thresholds and improves over baseline "
            f"(accuracy +{acc_diff}, clarity {clarity_diff:+.2f})"
        )
    else:
        outcome = "INCONCLUSIVE"
        reason = (
            f"atlas accurate ({atlas_res['score']}/20) and clear ({atlas_res['clarity_mean']:.2f}/5) "
            f"but does not clear improvement margin over baseline "
            f"(accuracy {acc_diff:+d}, clarity {clarity_diff:+.2f})"
        )

    return {
        "outcome": outcome,
        "reason": reason,
        "order": order,
        "atlas_set": atlas_set,
        "dist_set": dist_set,
        "atlas_score": atlas_res["score"],
        "dist_score": dist_res["score"],
        "atlas_clarity_mean": atlas_res["clarity_mean"],
        "dist_clarity_mean": dist_res["clarity_mean"],
        "atlas_detail": atlas_res,
        "dist_detail": dist_res,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command")

    gen_p = sub.add_parser("generate", help="Regenerate the frozen comparison pack.")
    gen_p.add_argument("--out", type=Path, default=DEFAULT_OUT_DIR)

    ver_p = sub.add_parser("verify", help="Verify committed certificates, keys, and views.")
    ver_p.add_argument("--dir", type=Path, default=DEFAULT_OUT_DIR)

    score_p = sub.add_parser("score", help="Score a sealed reader response JSON file.")
    score_p.add_argument("responses", type=Path)
    score_p.add_argument("--keys", type=Path, default=DEFAULT_OUT_DIR / "keys" / "answer_keys.json")

    args = parser.parse_args(argv)
    if args.command in (None, "generate"):
        out_dir = getattr(args, "out", DEFAULT_OUT_DIR)
        summary = generate_comparison_pack(out_dir)
        cases, obs = verify_comparison_pack(out_dir)
        print(f"GENERATED: {summary['cases']} held-out cases across {summary['sets']} sets; verified {cases} exact and {obs} byte-box certificates.")
        return 0
    if args.command == "verify":
        cases, obs = verify_comparison_pack(args.dir)
        print(f"VERIFIED: {cases} held-out cases; {obs} byte-box certificates; baseline views uncorrupted.")
        return 0
    if args.command == "score":
        responses = json.loads(args.responses.read_text(encoding="utf-8"))
        keys = json.loads(args.keys.read_text(encoding="utf-8"))
        result = score_responses(responses, keys)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
