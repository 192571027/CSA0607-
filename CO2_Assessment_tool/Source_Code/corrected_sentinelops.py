"""
corrected_sentinelops.py
------------------------
SentinelOps SOC alert-triage module - CORRECTED version.

This is the original module debugged IN PLACE (same four functions, same
brute-force structure, same signatures).  Only the faulty lines were changed;
each change is tagged D1..D9 (the nine reported defects) or H1 (a latent
boundary defect found while testing).  Nothing has been optimised yet -
see optimised_sentinelops.py for that.

Defect map
    D1  sort_alerts      while j > 0                -> while j >= 0
    D2  sort_alerts      alerts[j] = key            -> alerts[j + 1] = key
    D3  is_blocked       return False on a match    -> return True
    D4  is_blocked       else: return False (exits after 1st item, and no
                         terminal return)           -> removed; return False after loop
    D5  find_signature   range(n - m)               -> range(n - m + 1)
    D6  find_signature   if j == m - 1 (false hit)  -> for ... else
    D7  closest_logins   min_dist = 0               -> math.inf
    D8  closest_logins   if d > min_dist            -> if d < min_dist
    D9  closest_logins   inner loop over all j      -> range(i + 1, n)
    H1  find_signature   empty pattern              -> return []
"""
import math


def sort_alerts(alerts):
    """Sort alerts by severity, highest first; equal severities keep arrival order.

    Insertion sort (stable because elements are shifted only while STRICTLY
    smaller than the key).  Sorts the list in place and also returns it.

    Args:
        alerts: list of (alert_id, severity) tuples.
    Returns:
        The same list, ordered by severity descending.
    """
    for i in range(1, len(alerts)):
        key = alerts[i]
        j = i - 1
        while j >= 0 and alerts[j][1] < key[1]:      # D1: was  j > 0
            alerts[j + 1] = alerts[j]
            j -= 1
        alerts[j + 1] = key                          # D2: was  alerts[j] = key
    return alerts


def is_blocked(blocklist, ip):
    """Sequential search: is `ip` on the blocklist?

    Args:
        blocklist: list of IP strings.
        ip: IP string to look up.
    Returns:
        True if `ip` is in `blocklist`, otherwise False (also for an empty list).
    """
    for i in range(len(blocklist)):
        if blocklist[i] == ip:
            return True                              # D3: was  return False
        # D4: the  else: return False  branch is removed - it ended the search
        #     after the first element.
    return False                                     # D4: terminal return added


def find_signature(log, pattern):
    """Brute-force string matching: every start index of `pattern` in `log`.

    Overlapping occurrences are reported.  An empty pattern matches nothing.

    Args:
        log: the log line (str).
        pattern: the attack signature (str).
    Returns:
        List of 0-based start indices in increasing order.
    """
    n, m = len(log), len(pattern)
    hits = []
    if m == 0:                                       # H1: empty pattern guard
        return hits
    for i in range(n - m + 1):                       # D5: was  range(n - m)
        for j in range(m):
            if log[i + j] != pattern[j]:
                break
        else:                                        # D6: was  if j == m - 1
            hits.append(i)                           #     (inner loop never broke => full match)
    return hits


def closest_logins(events):
    """Brute-force closest pair of login locations.

    Args:
        events: list of (x, y) coordinates in km.
    Returns:
        ((i, j), distance) with i < j, the indices of the closest pair and their
        Euclidean distance.  Ties go to the lexicographically smallest (i, j).
        With fewer than two events: (None, math.inf).
    """
    min_dist = math.inf                              # D7: was  0
    pair = None
    for i in range(len(events)):
        for j in range(i + 1, len(events)):          # D9: was  range(len(events))
            d = math.sqrt((events[i][0] - events[j][0]) ** 2 +
                          (events[i][1] - events[j][1]) ** 2)
            if d < min_dist:                         # D8: was  d > min_dist
                min_dist = d
                pair = (i, j)
    return pair, min_dist


# ---------------------------------------------------------------- test data
ALERTS    = [("A1", 3), ("A2", 9), ("A3", 5), ("A4", 9), ("A5", 1)]
BLOCKLIST = ["10.0.0.5", "10.0.0.9", "172.16.4.2"]
QUERIES   = ["10.0.0.9", "10.0.0.5", "8.8.8.8"]
LOG, PATTERN = "FAILFAIXFAIL", "FAIL"
EVENTS    = [(2, 3), (12, 30), (40, 50), (5, 1), (12, 10), (3, 4)]   # (x, y) km


if __name__ == "__main__":
    print("sort_alerts    :", sort_alerts(list(ALERTS)))
    print("is_blocked     :", [(q, is_blocked(BLOCKLIST, q)) for q in QUERIES])
    print("find_signature :", find_signature(LOG, PATTERN))
    print("closest_logins :", closest_logins(EVENTS))
