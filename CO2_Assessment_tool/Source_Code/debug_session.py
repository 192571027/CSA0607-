"""
debug_session.py
----------------
Systematic, one-defect-at-a-time debugging of the ORIGINAL module.

The original source text is read from original_sentinelops.py and the nine
defect fixes (D1..D9) plus one latent boundary fix (H1) are applied as exact
text substitutions, CUMULATIVELY and one at a time.  After every single
substitution the module is re-executed and the probes for the affected
function are re-run, so the effect of each fix (and the remaining wrong
behaviour) is visible - the module is never rewritten from scratch.

Finally the fully patched source is compared with corrected_sentinelops.py.
"""
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = open(os.path.join(HERE, "original_sentinelops.py"), encoding="utf-8").read()
SRC = SRC.split("# ---------------------------------------------------------------- test data")[0]

# (id, function, why, old text, new text)
FIXES = [
    ("D1", "sort_alerts",
     "inner loop stops at j == 1, so alerts[0] is never compared or shifted",
     "while j > 0 and alerts[j][1] < key[1]:",
     "while j >= 0 and alerts[j][1] < key[1]:"),
    ("D2", "sort_alerts",
     "after the shift loop j points one slot BEFORE the gap; the key must go to j + 1",
     "        alerts[j] = key\n",
     "        alerts[j + 1] = key\n"),
    ("D3", "is_blocked",
     "a match returned False, so a blocked IP looked clean",
     "        if blocklist[i] == ip:\n            return False\n",
     "        if blocklist[i] == ip:\n            return True\n"),
    ("D4", "is_blocked",
     "the else branch returned on the FIRST element (only blocklist[0] was ever tested) "
     "and the function had no terminal return",
     "        else:\n            return False\n",
     "    return False\n"),
    ("D5", "find_signature",
     "range(n - m) omits the last window i = n - m, so a signature at the end is missed",
     "for i in range(n - m):",
     "for i in range(n - m + 1):"),
    ("D6", "find_signature",
     "'j == m - 1' is also true when the LAST character mismatches (break at j = m-1), "
     "giving false hits; use for/else so a hit means the inner loop never broke",
     "        for j in range(m):\n            if log[i + j] != pattern[j]:\n                break\n"
     "        if j == m - 1:\n            hits.append(i)\n",
     "        for j in range(m):\n            if log[i + j] != pattern[j]:\n                break\n"
     "        else:\n            hits.append(i)\n"),
    ("H1", "find_signature",
     "(latent, found by boundary tests) empty pattern: for/else would report every index",
     "    hits = []\n    for i in range(n - m + 1):",
     "    hits = []\n    if m == 0:\n        return hits\n    for i in range(n - m + 1):"),
    ("D7", "closest_logins",
     "min_dist starts at 0, so no distance can be < min_dist; it must start at +infinity",
     "    min_dist = 0\n",
     "    min_dist = math.inf\n"),
    ("D8", "closest_logins",
     "'d > min_dist' keeps the FARTHEST pair; the closest pair needs 'd < min_dist'",
     "if d > min_dist:",
     "if d < min_dist:"),
    ("D9", "closest_logins",
     "j ranged over all events, so (i, i) self pairs (d = 0) and mirrored pairs were compared; "
     "j must start at i + 1",
     "        for j in range(len(events)):\n",
     "        for j in range(i + 1, len(events)):\n"),
]

COURSE = dict(
    alerts=[("A1", 3), ("A2", 9), ("A3", 5), ("A4", 9), ("A5", 1)],
    blocklist=["10.0.0.5", "10.0.0.9", "172.16.4.2"],
    queries=["10.0.0.9", "10.0.0.5", "8.8.8.8"],
    log="FAILFAIXFAIL", pattern="FAIL",
    events=[(2, 3), (12, 30), (40, 50), (5, 1), (12, 10), (3, 4)],
)

# probes: function -> list of (label, lambda ns -> actual, expected)
PROBES = {
    "sort_alerts": [
        ("course alerts", lambda ns: ns["sort_alerts"](list(COURSE["alerts"])),
         [("A2", 9), ("A4", 9), ("A3", 5), ("A1", 3), ("A5", 1)]),
        ("max arrives last", lambda ns: ns["sort_alerts"]([("a", 1), ("b", 2), ("c", 9)]),
         [("c", 9), ("b", 2), ("a", 1)]),
        ("equal severities", lambda ns: ns["sort_alerts"]([("B1", 5), ("B2", 5), ("B3", 5)]),
         [("B1", 5), ("B2", 5), ("B3", 5)]),
    ],
    "is_blocked": [
        ("course queries", lambda ns: [ns["is_blocked"](COURSE["blocklist"], q) for q in COURSE["queries"]],
         [True, True, False]),
        ("match is last element", lambda ns: ns["is_blocked"](COURSE["blocklist"], "172.16.4.2"), True),
        ("empty blocklist", lambda ns: ns["is_blocked"]([], "1.1.1.1"), False),
    ],
    "find_signature": [
        ("course log", lambda ns: ns["find_signature"](COURSE["log"], COURSE["pattern"]), [0, 8]),
        ("pattern at very end", lambda ns: ns["find_signature"]("xxxxFAIL", "FAIL"), [4]),
        ("pattern longer than log", lambda ns: ns["find_signature"]("FAI", "FAIL"), []),
        ("empty pattern", lambda ns: ns["find_signature"]("FAIL", ""), []),
    ],
    "closest_logins": [
        ("course events", lambda ns: ns["closest_logins"](COURSE["events"]),
         ((0, 5), math.sqrt(2))),
        ("one event", lambda ns: ns["closest_logins"]([(1, 1)]), (None, math.inf)),
        ("identical points", lambda ns: ns["closest_logins"]([(5, 5), (9, 9), (5, 5)]), ((0, 2), 0.0)),
    ],
}


def load(src):
    ns = {}
    exec(compile(src, "<patched>", "exec"), ns)
    return ns


def same(a, b):
    if isinstance(a, tuple) and len(a) == 2 and isinstance(a[1], float):
        return a[0] == b[0] and math.isclose(a[1], b[1])
    return a == b


def run_probes(ns, func):
    all_ok = True
    for label, fn, expected in PROBES[func]:
        try:
            actual = fn(ns)
        except Exception as exc:                       # noqa: BLE001
            actual = f"{type(exc).__name__}: {exc}"
        ok = same(actual, expected)
        all_ok &= ok
        print(f"      [{'PASS' if ok else 'FAIL'}] {label:<26} actual={actual!r}")
        if not ok:
            print(f"             {'':<26} expect={expected!r}")
    return all_ok


if __name__ == "__main__":
    src = SRC
    print("STEP 0  original module (no fixes applied)")
    ns = load(src)
    for func in PROBES:
        print(f"    {func}")
        run_probes(ns, func)

    for step, (fid, func, why, old, new) in enumerate(FIXES, 1):
        assert src.count(old) == 1, f"{fid}: pattern must occur exactly once"
        src = src.replace(old, new)
        ns = load(src)
        print(f"\nSTEP {step}  fix {fid} in {func}")
        print(f"    why : {why}")
        print("    old :", old.strip().replace("\n", "\n          "))
        print("    new :", new.strip().replace("\n", "\n          "))
        print(f"    re-test {func}:")
        ok = run_probes(ns, func)
        print(f"    -> {func} {'ALL PROBES PASS' if ok else 'still has failing probes (later fixes pending)'}")

    # ----- final confirmation: patched source == corrected module (behaviourally)
    import corrected_sentinelops as corr
    ns = load(src)
    checks = [
        ns["sort_alerts"](list(COURSE["alerts"])) == corr.sort_alerts(list(COURSE["alerts"])),
        [ns["is_blocked"](COURSE["blocklist"], q) for q in COURSE["queries"]] ==
        [corr.is_blocked(COURSE["blocklist"], q) for q in COURSE["queries"]],
        ns["find_signature"](COURSE["log"], COURSE["pattern"]) ==
        corr.find_signature(COURSE["log"], COURSE["pattern"]),
        ns["closest_logins"](COURSE["events"]) == corr.closest_logins(COURSE["events"]),
    ]
    print("\nFINAL  patched original vs corrected_sentinelops.py on course data:",
          "IDENTICAL" if all(checks) else "DIFFERENT")
    print("FINAL  all probes on fully patched module:",
          "PASS" if all(run_probes(ns, f) for f in PROBES) else "FAIL")
