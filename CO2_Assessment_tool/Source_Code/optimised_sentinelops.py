"""
optimised_sentinelops.py
------------------------
SentinelOps SOC alert-triage module - OPTIMISED version.

Every function returns EXACTLY the same output as its counterpart in
corrected_sentinelops.py (verified by test_harness.py, including a
randomised differential test), but is built for the production load of
~50,000 alerts and ~8,000 login events per batch.

Optimisation summary
    sort_alerts     insertion sort O(n^2) worst  ->  Timsort (adaptive, stable)
                    O(n) on nearly sorted input, O(n log n) worst case.
    is_blocked      O(b) scan per query          ->  hash-set index, O(1) per
                    query after a one-off O(b) build.
    find_signature  brute force with early exit per window, no out-of-range
                    windows, first-character skip, O(1) guards.  An optional
                    Horspool scan (find_signature_horspool) skips alignments.
    closest_logins  n(n-1)/2 sqrt computations   ->  one sqrt in total,
                    squared distances, sort-by-x sweep that prunes pairs that
                    cannot be closest (same pair, same tie-break).
"""
import math
from operator import itemgetter


# --------------------------------------------------------------------------
# 1. Sorting alerts
# --------------------------------------------------------------------------
def sort_alerts(alerts):
    """Sort alerts by severity, highest first; equal severities keep arrival order.

    Uses Python's Timsort: it detects already-ordered runs, so nearly sorted
    alert streams cost about n comparisons, while the worst case stays
    O(n log n) (insertion sort is O(n^2)).  `reverse=True` preserves the
    original order of equal keys, so the sort is stable exactly as required.
    Sorts in place and also returns the list, like the corrected version.

    Args:
        alerts: list of (alert_id, severity) tuples.
    Returns:
        The same list, ordered by severity descending.
    """
    alerts.sort(key=itemgetter(1), reverse=True)
    return alerts


# --------------------------------------------------------------------------
# 2. Blocklist lookups
# --------------------------------------------------------------------------
def build_blocklist_index(blocklist):
    """Build a hash index of the blocklist once (O(b)) for O(1) lookups.

    Args:
        blocklist: iterable of IP strings.
    Returns:
        A frozenset of the blocked IPs.
    """
    return frozenset(blocklist)


def is_blocked(blocklist, ip):
    """Is `ip` on the blocklist?

    Pass the frozenset from build_blocklist_index() for repeated lookups
    (expected O(1) each).  A plain list still works (sequential search, O(b)),
    so the function is a drop-in replacement for the corrected version.

    Args:
        blocklist: list of IP strings, or a set/frozenset index of them.
        ip: IP string to look up.
    Returns:
        True if blocked, else False (also for an empty blocklist).
    """
    return ip in blocklist


# --------------------------------------------------------------------------
# 3. Signature scan
# --------------------------------------------------------------------------
def find_signature(log, pattern):
    """Brute-force string matching with no redundant comparisons.

    Compared with the corrected version:
      * O(1) guards: an empty pattern or a pattern longer than the log
        returns immediately without entering the scan;
      * only the n - m + 1 windows that can hold the pattern are tried;
      * the first character is tested once and a window that fails it is
        abandoned immediately (no inner-loop set-up);
      * a window is abandoned at its FIRST mismatch and no matched prefix is
        ever re-compared inside that window.
    Overlapping occurrences are reported.

    Args:
        log: the log line (str).
        pattern: the attack signature (str).
    Returns:
        List of 0-based start indices in increasing order.
    """
    n, m = len(log), len(pattern)
    if m == 0 or m > n:
        return []
    hits = []
    first = pattern[0]
    for i in range(n - m + 1):
        if log[i] != first:
            continue
        j = 1
        while j < m and log[i + j] == pattern[j]:
            j += 1
        if j == m:
            hits.append(i)
    return hits


def find_signature_horspool(log, pattern):
    """Optional extension: Horspool scan - skips alignments using a
    bad-character table.  Same output as find_signature (all, overlapping
    occurrences); average-case ~ n/m comparisons, worst case O(n*m).

    Args / Returns: as find_signature.
    """
    n, m = len(log), len(pattern)
    if m == 0 or m > n:
        return []
    shift = {pattern[k]: m - 1 - k for k in range(m - 1)}   # distance to last char
    hits = []
    i = 0
    last_start = n - m
    while i <= last_start:
        j = m - 1
        while j >= 0 and log[i + j] == pattern[j]:
            j -= 1
        if j < 0:
            hits.append(i)
        i += shift.get(log[i + m - 1], m)
    return hits


# --------------------------------------------------------------------------
# 4. Closest pair of logins
# --------------------------------------------------------------------------
def closest_logins(events):
    """Closest pair of login locations - pruned brute force.

    Optimisations over the corrected version (output is identical):
      * pairs are generated once (i < j) - no self / repeated pairs;
      * squared distances are compared, so math.sqrt is called ONCE at the end
        instead of once per pair;
      * the events are sorted by x; for each point the scan to the right stops
        as soon as (dx)^2 exceeds the best squared distance found so far,
        because every later point is even further away in x and therefore
        cannot be closer (strict '>' keeps pairs that tie, so the same
        tie-break as brute force is preserved).

    Args:
        events: list of (x, y) coordinates in km.
    Returns:
        ((i, j), distance) with i < j (indices into `events`); ties go to the
        lexicographically smallest (i, j).  With fewer than two events:
        (None, math.inf).
    """
    n = len(events)
    if n < 2:
        return None, math.inf
    order = sorted(range(n), key=lambda k: events[k][0])       # indices by x
    xs = [events[k][0] for k in order]
    ys = [events[k][1] for k in order]

    best = math.inf              # best SQUARED distance so far
    best_pair = None
    for a in range(n - 1):
        xa, ya, ia = xs[a], ys[a], order[a]
        for b in range(a + 1, n):
            dx = xs[b] - xa
            dx2 = dx * dx
            if dx2 > best:       # prune: this and all later points are too far in x
                break
            dy = ys[b] - ya
            d2 = dx2 + dy * dy
            if d2 <= best:
                ib = order[b]
                cand = (ia, ib) if ia < ib else (ib, ia)
                if d2 < best or (best_pair is not None and cand < best_pair):  # tie -> smaller (i, j)
                    best = d2
                    best_pair = cand
    return best_pair, math.sqrt(best)


# ---------------------------------------------------------------- test data
ALERTS    = [("A1", 3), ("A2", 9), ("A3", 5), ("A4", 9), ("A5", 1)]
BLOCKLIST = ["10.0.0.5", "10.0.0.9", "172.16.4.2"]
QUERIES   = ["10.0.0.9", "10.0.0.5", "8.8.8.8"]
LOG, PATTERN = "FAILFAIXFAIL", "FAIL"
EVENTS    = [(2, 3), (12, 30), (40, 50), (5, 1), (12, 10), (3, 4)]   # (x, y) km


if __name__ == "__main__":
    index = build_blocklist_index(BLOCKLIST)
    print("sort_alerts    :", sort_alerts(list(ALERTS)))
    print("is_blocked     :", [(q, is_blocked(index, q)) for q in QUERIES])
    print("find_signature :", find_signature(LOG, PATTERN))
    print("horspool       :", find_signature_horspool(LOG, PATTERN))
    print("closest_logins :", closest_logins(EVENTS))
