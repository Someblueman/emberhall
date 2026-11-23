"""Decision for the 320-letter repeated-word tripod template.

Period 320, base lengths (427,267,211), literal prefixes (213,133,105).
Every coefficient row from coupled_word_completion.compile_shape is kept
unmodified; this module only decides whether a {-1,+1} assignment exists.
A positive result carries a word checked by verify_word and audit_word.
A negative result is a deterministic exact replay of a standard-library
integer search. The general tripod target stays undecided.

External exact solvers decide that no signing exists: CP-SAT proved the
full system infeasible and Z3 proved a CNF encoding of the 468-row core
below unsatisfiable (Vesper, preserved run 7e983be7; the core was also
rechecked infeasible under an independently written CP-SAT encoding).
That evidence is recorded, not counted as a house certificate: the core
certificate's standard-library replay reaches its 20,000-conflict cap
(resource_limit), so template_existence_decided stays False. See
TEMPLATE_320_DECISION.md.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import coupled_word_completion as coupled
import integer_template_decision as prior

FORMAT = "tripod-320-template-decision-v1"
CORE_FORMAT = "tripod-320-template-core-v1"
PERIOD = 320
BASE = (427, 267, 211)
CUTS = (213, 133, 105)
SHAPES = [[("literal", cut), ("repeat", PERIOD),
           ("literal", length - (arm < 2) - cut)]
          for arm, (length, cut) in enumerate(zip(BASE, CUTS))]

if SHAPES != prior.SHAPES or PERIOD != prior.PERIOD:
    raise AssertionError("320 shape drifted from integer_template_decision")
if BASE != prior.BASE or CUTS != prior.CUTS:
    raise AssertionError("320 lengths drifted from integer_template_decision")

# Filled from the recorded minimization run; indices into the row list of
# coupled.compile_shape(PERIOD, SHAPES) in its (sorted-degree) order.
CORE_ROWS = (
    0, 1, 2, 4, 5, 6, 50, 51, 52, 53, 54, 55,
    56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 67, 68,
    69, 70, 71, 73, 74, 75, 76, 77, 78, 79, 80, 82,
    84, 85, 86, 87, 88, 89, 91, 92, 94, 95, 96, 97,
    99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110,
    111, 112, 113, 114, 115, 116, 117, 119, 204, 205, 206, 207,
    208, 209, 210, 211, 212, 213, 215, 216, 217, 218, 219, 220,
    222, 312, 313, 314, 315, 316, 317, 319, 320, 321, 322, 323,
    324, 325, 326, 327, 328, 330, 332, 334, 336, 338, 340, 342,
    344, 346, 348, 352, 354, 356, 358, 360, 362, 366, 368, 372,
    374, 376, 378, 380, 382, 386, 388, 392, 394, 396, 402, 404,
    406, 408, 410, 412, 414, 416, 418, 419, 420, 421, 423, 424,
    425, 426, 427, 428, 429, 430, 431, 432, 433, 434, 435, 436,
    438, 440, 442, 444, 446, 448, 450, 452, 454, 456, 458, 460,
    462, 466, 468, 470, 472, 476, 478, 480, 482, 486, 488, 490,
    492, 494, 496, 502, 504, 506, 508, 510, 512, 516, 518, 520,
    522, 524, 526, 528, 529, 530, 531, 532, 533, 534, 536, 645,
    648, 651, 654, 657, 658, 659, 660, 661, 662, 663, 664, 666,
    667, 668, 669, 670, 673, 675, 676, 679, 681, 807, 810, 813,
    816, 819, 822, 823, 824, 826, 827, 829, 831, 832, 833, 834,
    837, 838, 839, 960, 963, 969, 970, 972, 973, 975, 976, 978,
    979, 980, 981, 982, 983, 984, 985, 986, 987, 988, 990, 994,
    995, 996, 997, 999, 1000, 1002, 1003, 1009, 1012, 1015, 1018, 1021,
    1024, 1027, 1030, 1033, 1036, 1039, 1042, 1045, 1051, 1057, 1060, 1063,
    1066, 1069, 1072, 1078, 1081, 1084, 1087, 1090, 1093, 1102, 1105, 1108,
    1111, 1114, 1117, 1120, 1123, 1126, 1128, 1129, 1131, 1134, 1135, 1138,
    1139, 1141, 1142, 1143, 1144, 1145, 1146, 1147, 1148, 1149, 1150, 1151,
    1152, 1153, 1154, 1155, 1157, 1159, 1248, 1249, 1250, 1251, 1252, 1253,
    1254, 1255, 1256, 1257, 1258, 1259, 1260, 1261, 1356, 1357, 1358, 1359,
    1360, 1361, 1362, 1363, 1364, 1365, 1366, 1367, 1368, 1370, 1371, 1461,
    1462, 1463, 1464, 1465, 1466, 1467, 1468, 1469, 1470, 1471, 1472, 1473,
    1474, 1475, 1476, 1477, 1478, 1479, 1566, 1567, 1568, 1569, 1570, 1571,
    1572, 1573, 1574, 1575, 1576, 1577, 1578, 1579, 1580, 1581, 1582, 1583,
    1584, 1586, 1588, 1665, 1667, 1676, 1677, 1678, 1679, 1680, 1681, 1682,
    1683, 1684, 1685, 1686, 1687, 1688, 1690, 1691, 1692, 1693, 1694, 1695,
    1780, 1781, 1783, 1784, 1785, 1786, 1787, 1788, 1789, 1790, 1791, 1792,
    1793, 1794, 1795, 1796, 1797, 1798, 1799, 1800, 1801, 1802, 1803, 1804,
    1867, 1868, 1869, 1870, 1871, 1872, 1874, 1875, 1920, 1921, 1922, 1923,
    1924, 1925, 1926, 1928, 1929, 1931, 1974, 1975, 1976, 1977, 1978, 1980,
)
REPLAY = {"max_conflicts": 20000, "conflicts": 20000, "decisions": 26635,
          "maximum_depth": 47, "integer_reasons": 554248}
ROWS_SHA256 = "9301c4b82acb6fd95c1e4c2027d26a176fd81372961f8daafdb9c1630ecf8a01"


def rows_for_template():
    """Recompile the 1,981 unmodified integer rows."""
    rows, variables, base, growth = coupled.compile_shape(PERIOD, SHAPES)
    if base != list(BASE) or growth != [1, 1, 1]:
        raise AssertionError("recompiled base changed")
    if len(rows) != 1981 or len(variables) != 1864:
        raise AssertionError("row or variable count changed")
    return rows, variables, base, growth


def compiled_rows():
    """Recompiled rows and variables only (core-certificate view)."""
    rows, variables, _base, _growth = rows_for_template()
    return rows, variables


def rows_sha256(rows):
    digest = hashlib.sha256()
    for degree, row in rows.items():
        digest.update(repr(degree).encode())
        for index in sorted(row):
            digest.update(f":{index}={row[index]}".encode())
        digest.update(b"\n")
    return digest.hexdigest()


def replay_core(rows, variables, core_rows, max_conflicts):
    keys = list(rows.keys())
    subset = {keys[j]: rows[keys[j]] for j in core_rows}
    engine = prior.IntegerSearch(subset, len(variables))
    exists = engine.solve(max_conflicts)
    stats = {"max_conflicts": max_conflicts, "conflicts": engine.conflicts,
             "decisions": engine.decisions,
             "maximum_depth": engine.maximum_depth,
             "integer_reasons": engine.integer_reasons}
    return exists, stats


def certificate():
    rows, variables = compiled_rows()
    core_vars = {i for j in CORE_ROWS for i in list(rows.values())[j]}
    return {"format": CORE_FORMAT, "period": PERIOD,
            "base_lengths": list(BASE), "prefix_lengths": list(CUTS),
            "rows_sha256": ROWS_SHA256, "coefficient_rows": len(rows),
            "sign_variables": len(variables), "core_rows": list(CORE_ROWS),
            "core_row_count": len(CORE_ROWS),
            "core_variables": len(core_vars), "replay": dict(REPLAY),
            "external_exact_decision": "no signing (CP-SAT full system "
            "INFEASIBLE; Z3 SAT on a CNF encoding UNSAT; core rechecked)",
            "template_existence_decided": False,
            "general_target_decided": False,
            "all_hole_supports_excluded": False,
            "method": "infeasible row core located by external CP-SAT; "
                      "stdlib IntegerSearch replay recorded to its cap "
                      "(resource_limit) as a deterministic anchor, not yet "
                      "a complete stdlib refutation"}


def verify_certificate(saved):
    if type(saved) is not dict or saved.get("format") != CORE_FORMAT:
        raise ValueError("expected a 320-template core certificate")
    rows, variables = compiled_rows()
    if rows_sha256(rows) != ROWS_SHA256:
        raise ValueError("recompiled rows differ from the certified rows")
    expected = certificate()
    for key, value in expected.items():
        if key == "replay":
            continue
        if saved.get(key) != value:
            raise ValueError(f"certificate field {key!r} altered")
    if set(saved) != set(expected):
        raise ValueError("certificate fields altered")
    core = saved["core_rows"]
    if (type(core) is not list or core != sorted(set(core))
            or any(type(j) is not int or not 0 <= j < len(rows) for j in core)):
        raise ValueError("invalid core row list")
    replay = saved.get("replay")
    if type(replay) is not dict or set(replay) != set(REPLAY):
        raise ValueError("invalid replay record")
    exists, stats = replay_core(rows, variables, core,
                                replay["max_conflicts"])
    if stats != replay or stats != REPLAY:
        raise ValueError("replay statistics differ from the certificate")
    # Honest status: the recorded stdlib replay reaches its conflict cap
    # (exists is None). It anchors the core deterministically but is not
    # yet a stdlib proof; see TEMPLATE_320_DECISION.md.
    return {"valid": True, "exists": exists,
            "status": "resource_limit" if exists is None else "exact",
            "template_existence_decided": exists is not None,
            "general_target_decided": False,
            "core_row_count": len(core), "conflicts": stats["conflicts"]}


def separating_repeat_count(rows):
    degrees = [z for z, _ in rows]
    return (max(degrees) - min(degrees)) // PERIOD + 1


def run_exact(engine, max_conflicts):
    """Drive an IntegerSearch to completion without the prior 1M cap."""
    if max_conflicts is not None and (
            type(max_conflicts) is not int or max_conflicts < 1):
        raise ValueError("max_conflicts must be a positive int or None")
    import heapq
    if engine.impossible_row:
        return False
    restart, next_restart = 100, 100
    while True:
        conflict = engine.propagate()
        if conflict is not None:
            engine.conflicts += 1
            if not engine.limits:
                return False
            if max_conflicts is not None and engine.conflicts >= max_conflicts:
                return None
            learned, back = engine.analyze(conflict)
            engine.backtrack(back)
            number = len(engine.clauses)
            engine.clauses.append(learned)
            if len(learned) > 1:
                engine.watches[learned[0]].append(number)
                engine.watches[learned[1]].append(number)
            engine.enqueue(learned[0], learned)
            engine.increment /= 0.95
            if engine.increment > 1e100:
                engine.activity = [a * 1e-100 for a in engine.activity]
                engine.increment *= 1e-100
                engine.retire_clauses()
            if engine.conflicts % 5000 == 0:
                engine.retire_clauses()
        else:
            if engine.conflicts >= next_restart:
                engine.backtrack(0)
                restart = int(restart * 1.5)
                next_restart = engine.conflicts + restart
            while engine.heap:
                activity, variable = heapq.heappop(engine.heap)
                if (not engine.values[variable]
                        and activity == -engine.activity[variable]):
                    break
            else:
                for row in engine.rows:
                    if sum(a * -engine.values[i + 1]
                           for i, a in row.items()):
                        raise AssertionError(
                            "candidate violates an original row")
                return True
            engine.decisions += 1
            engine.limits.append(len(engine.trail))
            engine.maximum_depth = max(engine.maximum_depth,
                                       len(engine.limits))
            engine.enqueue(variable * engine.phase[variable], None)


def solve_exact(max_conflicts=None):
    """Exact decision; None only when a finite max_conflicts is hit."""
    rows, variables, base, growth = rows_for_template()
    engine = prior.IntegerSearch(rows, len(variables))
    exists = run_exact(engine, max_conflicts)
    result = {"format": FORMAT, "period": PERIOD,
              "base_lengths": base, "prefix_lengths": list(CUTS),
              "growth": growth, "max_conflicts": max_conflicts,
              "sign_variables": len(variables),
              "coefficient_rows": len(rows),
              "conflicts": engine.conflicts,
              "decisions": engine.decisions,
              "maximum_depth": engine.maximum_depth,
              "integer_reasons": engine.integer_reasons,
              "status": ("resource_limit" if exists is None else "exact"),
              "template_existence_decided": exists is not None,
              "general_target_decided": False,
              "all_hole_supports_excluded": False}
    if exists is not None:
        result["exists"] = exists
    if exists:
        signs = {(a, s, k): "+" if engine.values[i + 1] < 0 else "-"
                 for i, (a, s, k) in enumerate(variables)}
        word = {"format": coupled.FORMAT, "centre": 1, "period": PERIOD,
                "arms": [[{kind: "".join(signs[a, s, k]
                                         for k in range(size))}
                          for s, (kind, size) in enumerate(arm)]
                         for a, arm in enumerate(SHAPES, 1)]}
        coupled.verify_word(word)
        result["word"] = word
    return result


def verify(saved):
    """Deterministically replay and reject any altered certificate."""
    if type(saved) is dict and saved.get("format") == CORE_FORMAT:
        return verify_certificate(saved)
    if type(saved) is not dict or saved.get("format") != FORMAT:
        raise ValueError("expected a 320 template decision receipt")
    if (saved.get("period") != PERIOD or saved.get("base_lengths") != list(BASE)
            or saved.get("prefix_lengths") != list(CUTS)
            or saved.get("general_target_decided") is not False
            or saved.get("all_hole_supports_excluded") is not False):
        raise ValueError("certificate scope changed")
    expected = solve_exact(saved.get("max_conflicts"))
    if json.dumps(saved, sort_keys=True) != json.dumps(
            expected, sort_keys=True):
        raise ValueError("receipt differs from exact deterministic replay")
    if expected.get("exists") is True:
        report = coupled.verify_word(expected["word"])
        cutoff = separating_repeat_count(rows_for_template()[0])
        for count in (0, 1, cutoff):
            audit = coupled.audit_word(expected["word"], count)
            if not audit["equal_distance_multisets"]:
                raise AssertionError("original-tree audit failed")
    return {"valid": True, "status": expected["status"],
            "template_existence_decided":
                expected["template_existence_decided"],
            "general_target_decided": False}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--solve", action="store_true")
    group.add_argument("--certificate", action="store_true")
    group.add_argument("--verify", type=Path)
    parser.add_argument("--max-conflicts", type=int, default=None)
    parser.add_argument("--write", type=Path)
    parser.add_argument("--audit-repeat", type=int, default=None)
    args = parser.parse_args(argv)
    try:
        saved = (json.loads(args.verify.read_text()) if args.verify
                 else certificate() if args.certificate
                 else solve_exact(args.max_conflicts))
        if args.verify:
            report = verify(saved)
            if args.audit_repeat is not None:
                if saved.get("exists") is not True:
                    raise ValueError("no word to audit")
                report["original_tree_audit"] = coupled.audit_word(
                    saved["word"], args.audit_repeat)
        else:
            report = {k: v for k, v in saved.items()
                      if k not in ("word", "core_rows")}
            if saved.get("exists") is True and args.audit_repeat is not None:
                report["original_tree_audit"] = coupled.audit_word(
                    saved["word"], args.audit_repeat)
        if args.write:
            args.write.write_text(json.dumps(saved, indent=2) + "\n")
        print(json.dumps(report, sort_keys=True))
        return 2 if saved.get("status") == "resource_limit" else 0
    except (ValueError, OSError, TypeError, AttributeError) as error:
        parser.exit(1, str(error) + "\n")


if __name__ == "__main__":
    raise SystemExit(main())
