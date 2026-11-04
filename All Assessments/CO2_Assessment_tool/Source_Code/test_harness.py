"""
test_harness.py
---------------
Test harness for the SentinelOps module.

Runs the SAME test-suite against
    * original_sentinelops   - expected to FAIL (proves the tests detect the defects)
    * corrected_sentinelops  - expected to PASS everything
    * optimised_sentinelops  - expected to PASS everything

Covers every function, the course test data, the boundary cases of part (b)
(empty blocklist, pattern at the very end of the log, pattern longer than the
log, equal severities, fewer than two login events) and a randomised
differential test of optimised vs corrected vs independent reference
implementations.

Usage:  python test_harness.py            (exit code 0 only if corrected + optimised pass)
"""
import itertools
import math
import random
import re
import sys

import original_sentinelops as orig
import corrected_sentinelops as corr
import optimised_sentinelops as opt

# ----------------------------------------------------------------- test data
ALERTS    = [("A1", 3), ("A2", 9), ("A3", 5), ("A4", 9), ("A5", 1)]
BLOCKLIST = ["10.0.0.5", "10.0.0.9", "172.16.4.2"]
QUERIES   = ["10.0.0.9", "10.0.0.5", "8.8.8.8"]
LOG, PATTERN = "FAILFAIXFAIL", "FAIL"
EVENTS    = [(2, 3), (12, 30), (40, 50), (5, 1), (12, 10), (3, 4)]


# -------------------------------------------------- independent references
def ref_sort(alerts):
    """Stable descending sort by severity, written independently."""
    return sorted(alerts, key=lambda a: -a[1])


def ref_signature(log, pattern):
    """All (overlapping) occurrences via a regex look-ahead."""
    if not pattern:
        return []
    return [mt.start() for mt in re.finditer("(?=" + re.escape(pattern) + ")", log)]


def ref_closest(events):
    """Closest pair via itertools.combinations; ties -> smallest (i, j)."""
    if len(events) < 2:
        return None, math.inf
    best = min(itertools.combinations(range(len(events)), 2),
               key=lambda p: (math.dist(events[p[0]], events[p[1]]), p))
    return best, math.dist(events[best[0]], events[best[1]])


# ------------------------------------------------------------ mini framework
class Runner:
    def __init__(self, label):
        self.label, self.passed, self.failed = label, 0, 0

    def check(self, name, got, expected, close=False):
        if close:
            ok = (got[0] == expected[0] and math.isclose(got[1], expected[1]))
        else:
            ok = got == expected
        self.passed += ok
        self.failed += (not ok)
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
        if not ok:
            print(f"         expected: {expected!r}")
            print(f"         actual  : {got!r}")

    def raises_nothing(self, name, fn, expected):
        """Run fn(); an exception counts as a failure."""
        try:
            got = fn()
        except Exception as exc:                       # noqa: BLE001
            got = f"{type(exc).__name__}: {exc}"
        self.check(name, got, expected)


def suite(label, m, fast_lookup):
    """Run every test against module `m`.  `fast_lookup` -> build a set index."""
    print(f"\n=== {label} " + "=" * (60 - len(label)))
    r = Runner(label)
    lookup = (lambda bl: m.build_blocklist_index(bl)) if fast_lookup else (lambda bl: bl)

    # ---------------------------------------------------------- sort_alerts
    print(" sort_alerts")
    exp = [("A2", 9), ("A4", 9), ("A3", 5), ("A1", 3), ("A5", 1)]
    r.raises_nothing("course data", lambda: m.sort_alerts(list(ALERTS)), exp)
    r.raises_nothing("no alert lost / duplicated (same multiset)",
                     lambda: sorted(m.sort_alerts(list(ALERTS))), sorted(ALERTS))
    r.raises_nothing("empty list", lambda: m.sort_alerts([]), [])
    r.raises_nothing("single alert", lambda: m.sort_alerts([("X", 4)]), [("X", 4)])
    eq = [("B1", 5), ("B2", 5), ("B3", 5), ("B4", 5)]
    r.raises_nothing("all equal severities keep arrival order",
                     lambda: m.sort_alerts(list(eq)), eq)
    r.raises_nothing("already sorted (highest first)",
                     lambda: m.sort_alerts([("a", 9), ("b", 5), ("c", 1)]),
                     [("a", 9), ("b", 5), ("c", 1)])
    r.raises_nothing("reverse order (lowest first)",
                     lambda: m.sort_alerts([("c", 1), ("b", 5), ("a", 9)]),
                     [("a", 9), ("b", 5), ("c", 1)])
    r.raises_nothing("maximum arrives last, must reach index 0",
                     lambda: m.sort_alerts([("a", 1), ("b", 2), ("c", 9)]),
                     [("c", 9), ("b", 2), ("a", 1)])
    r.raises_nothing("two elements, swap needed (j reaches -1)",
                     lambda: m.sort_alerts([("a", 1), ("b", 2)]), [("b", 2), ("a", 1)])
    r.raises_nothing("duplicates of max interleaved (stability)",
                     lambda: m.sort_alerts([("a", 2), ("b", 9), ("c", 2), ("d", 9), ("e", 2)]),
                     [("b", 9), ("d", 9), ("a", 2), ("c", 2), ("e", 2)])

    # ----------------------------------------------------------- is_blocked
    print(" is_blocked")
    r.raises_nothing("course queries (blocked, blocked, clean)",
                     lambda: [m.is_blocked(lookup(BLOCKLIST), q) for q in QUERIES],
                     [True, True, False])
    r.raises_nothing("empty blocklist -> False (not None)",
                     lambda: m.is_blocked(lookup([]), "1.1.1.1"), False)
    r.raises_nothing("match is the LAST element",
                     lambda: m.is_blocked(lookup(BLOCKLIST), "172.16.4.2"), True)
    r.raises_nothing("match is the middle element",
                     lambda: m.is_blocked(lookup(BLOCKLIST), "10.0.0.9"), True)
    r.raises_nothing("single-element list, match",
                     lambda: m.is_blocked(lookup(["9.9.9.9"]), "9.9.9.9"), True)
    r.raises_nothing("single-element list, no match",
                     lambda: m.is_blocked(lookup(["9.9.9.9"]), "9.9.9.8"), False)
    r.raises_nothing("near-miss IP is not blocked",
                     lambda: m.is_blocked(lookup(BLOCKLIST), "10.0.0.50"), False)
    r.raises_nothing("duplicate entries in blocklist",
                     lambda: m.is_blocked(lookup(["1.1.1.1", "1.1.1.1"]), "1.1.1.1"), True)
    r.raises_nothing("returns a real bool",
                     lambda: type(m.is_blocked(lookup(BLOCKLIST), "10.0.0.5")).__name__, "bool")

    # -------------------------------------------------------- find_signature
    print(" find_signature")
    r.raises_nothing("course data FAILFAIXFAIL / FAIL -> [0, 8]",
                     lambda: m.find_signature(LOG, PATTERN), [0, 8])
    r.raises_nothing("no false hit at 'FAIX' (index 4)",
                     lambda: 4 in m.find_signature(LOG, PATTERN), False)
    r.raises_nothing("pattern at the very end of the log",
                     lambda: m.find_signature("xxxxFAIL", "FAIL"), [4])
    r.raises_nothing("pattern at the very start only",
                     lambda: m.find_signature("FAILxxxx", "FAIL"), [0])
    r.raises_nothing("pattern longer than the log",
                     lambda: m.find_signature("FAI", "FAIL"), [])
    r.raises_nothing("pattern equals the log",
                     lambda: m.find_signature("FAIL", "FAIL"), [0])
    r.raises_nothing("empty log",
                     lambda: m.find_signature("", "FAIL"), [])
    r.raises_nothing("empty pattern -> no hits",
                     lambda: m.find_signature("FAIL", ""), [])
    r.raises_nothing("no occurrence",
                     lambda: m.find_signature("abcdefgh", "xyz"), [])
    r.raises_nothing("overlapping occurrences AAAAAA / AAAA",
                     lambda: m.find_signature("AAAAAA", "AAAA"), [0, 1, 2])
    r.raises_nothing("single-character pattern",
                     lambda: m.find_signature("abcabca", "a"), [0, 3, 6])
    r.raises_nothing("partial-match-then-mismatch at last char (AAAB in AAAC AAAB)",
                     lambda: m.find_signature("AAACAAAB", "AAAB"), [4])
    r.raises_nothing("case sensitive",
                     lambda: m.find_signature("fail FAIL", "FAIL"), [5])

    # -------------------------------------------------------- closest_logins
    print(" closest_logins")
    r.check("course data -> ((0, 5), sqrt 2)", m.closest_logins(EVENTS),
            ((0, 5), math.sqrt(2)), close=True)
    r.raises_nothing("empty events -> (None, inf)",
                     lambda: m.closest_logins([]), (None, math.inf))
    r.raises_nothing("one event -> (None, inf)",
                     lambda: m.closest_logins([(1, 1)]), (None, math.inf))
    r.check("two events", m.closest_logins([(0, 0), (3, 4)]), ((0, 1), 5.0), close=True)
    r.check("identical locations -> distance 0 (not a self pair)",
            m.closest_logins([(5, 5), (9, 9), (5, 5)]), ((0, 2), 0.0), close=True)
    r.check("tie -> lexicographically smallest pair",
            m.closest_logins([(0, 0), (1, 0), (10, 0), (11, 0)]), ((0, 1), 1.0), close=True)
    r.check("all points share one x (vertical line)",
            m.closest_logins([(7, 0), (7, 10), (7, 3), (7, 40)]), ((0, 2), 3.0), close=True)
    r.check("negative coordinates",
            m.closest_logins([(-5, -5), (-4, -5), (6, 6)]), ((0, 1), 1.0), close=True)
    r.check("float coordinates",
            m.closest_logins([(0.0, 0.0), (0.5, 0.5), (2.0, 2.0)]),
            ((0, 1), math.sqrt(0.5)), close=True)
    r.check("closest pair is not adjacent in input order",
            m.closest_logins([(0, 0), (50, 50), (100, 100), (1, 1)]),
            ((0, 3), math.sqrt(2)), close=True)

    print(f" -> {label}: {r.passed} passed, {r.failed} failed")
    return r


def differential_tests(trials=3000, seed=2026):
    """Random cross-check: optimised == corrected == independent reference."""
    print("\n=== Randomised differential test " + "=" * 30)
    rng = random.Random(seed)
    bad = 0
    for t in range(trials):
        # sort
        k = rng.randint(0, 25)
        alerts = [(f"A{i}", rng.randint(1, 5)) for i in range(k)]   # many ties
        a = ref_sort(alerts)
        if corr.sort_alerts(list(alerts)) != a or opt.sort_alerts(list(alerts)) != a:
            bad += 1; print("  sort mismatch", alerts)
        # blocklist
        bl = [f"10.0.0.{rng.randint(0, 20)}" for _ in range(rng.randint(0, 8))]
        ip = f"10.0.0.{rng.randint(0, 25)}"
        exp = ip in bl
        if (corr.is_blocked(bl, ip) != exp or opt.is_blocked(bl, ip) != exp
                or opt.is_blocked(opt.build_blocklist_index(bl), ip) != exp):
            bad += 1; print("  blocklist mismatch", bl, ip)
        # signature (tiny alphabet -> many overlaps / partial matches)
        log = "".join(rng.choice("ab") for _ in range(rng.randint(0, 30)))
        pat = "".join(rng.choice("ab") for _ in range(rng.randint(0, 5)))
        exp = ref_signature(log, pat)
        if (corr.find_signature(log, pat) != exp or opt.find_signature(log, pat) != exp
                or opt.find_signature_horspool(log, pat) != exp):
            bad += 1; print("  signature mismatch", log, pat)
        # closest pair (small integer grid -> many ties and duplicates)
        ev = [(rng.randint(0, 12), rng.randint(0, 12)) for _ in range(rng.randint(0, 25))]
        if rng.random() < 0.3:   # float coordinates too
            ev = [(round(rng.uniform(0, 50), 2), round(rng.uniform(0, 50), 2))
                  for _ in range(rng.randint(0, 25))]
        c1, c2, c3 = corr.closest_logins(ev), opt.closest_logins(ev), ref_closest(ev)
        if not (c1[0] == c2[0] == c3[0] and math.isclose(c1[1], c2[1], abs_tol=1e-12)
                and math.isclose(c1[1], c3[1], abs_tol=1e-12) or
                (c1[0] is None and c2[0] is None and c3[0] is None)):
            bad += 1; print("  closest mismatch", ev, c1, c2, c3)
    print(f"  {trials} random trials x 4 functions, mismatches: {bad}")
    return bad


if __name__ == "__main__":
    # The original has no build_blocklist_index; run it with list lookups.
    r_orig = suite("ORIGINAL (defects expected)", orig, fast_lookup=False)
    r_corr = suite("CORRECTED", corr, fast_lookup=False)
    r_opt = suite("OPTIMISED", opt, fast_lookup=True)
    r_opt_list = suite("OPTIMISED (is_blocked fed a plain list)", opt, fast_lookup=False)
    diff_bad = differential_tests()

    print("\n=== SUMMARY " + "=" * 51)
    print(f"  original : {r_orig.passed:3d} passed, {r_orig.failed:3d} failed   (failures are the defects)")
    print(f"  corrected: {r_corr.passed:3d} passed, {r_corr.failed:3d} failed")
    print(f"  optimised: {r_opt.passed:3d} passed, {r_opt.failed:3d} failed (set index)")
    print(f"  optimised: {r_opt_list.passed:3d} passed, {r_opt_list.failed:3d} failed (list input)")
    print(f"  differential mismatches: {diff_bad}")
    ok = (r_corr.failed == 0 and r_opt.failed == 0 and r_opt_list.failed == 0
          and diff_bad == 0 and r_orig.failed > 0)
    print("  RESULT:", "ALL CHECKS AS EXPECTED" if ok else "UNEXPECTED RESULT")
    sys.exit(0 if ok else 1)
