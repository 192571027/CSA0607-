"""
original_sentinelops.py
-----------------------
The junior developer's ORIGINAL SentinelOps SOC alert-triage module,
kept VERBATIM (nine defects included) so the failures can be reproduced.
Do NOT fix anything in this file - fixes live in corrected_sentinelops.py.
"""
import math

def sort_alerts(alerts):            # insertion sort by severity, highest first
    for i in range(1, len(alerts)):
        key = alerts[i]
        j = i - 1
        while j > 0 and alerts[j][1] < key[1]:
            alerts[j + 1] = alerts[j]
            j -= 1
        alerts[j] = key
    return alerts

def is_blocked(blocklist, ip):      # sequential search
    for i in range(len(blocklist)):
        if blocklist[i] == ip:
            return False
        else:
            return False

def find_signature(log, pattern):   # brute-force string matching, all occurrences
    n, m = len(log), len(pattern)
    hits = []
    for i in range(n - m):
        for j in range(m):
            if log[i + j] != pattern[j]:
                break
        if j == m - 1:
            hits.append(i)
    return hits

def closest_logins(events):         # brute-force closest pair of login locations
    min_dist = 0
    pair = None
    for i in range(len(events)):
        for j in range(len(events)):
            d = math.sqrt((events[i][0] - events[j][0]) ** 2 +
                          (events[i][1] - events[j][1]) ** 2)
            if d > min_dist:
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
