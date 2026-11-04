"""
trace_demo.py - step-by-step traces used in the report (part b):
  * insertion trace of the alerts list, ORIGINAL vs CORRECTED
  * alignment table of the log line 'FAILFAIXFAIL' / 'FAIL', ORIGINAL vs CORRECTED
  * closest_logins: pair table (n(n-1)/2 = 15 pairs) with the original's decisions
"""
import math

ALERTS = [("A1", 3), ("A2", 9), ("A3", 5), ("A4", 9), ("A5", 1)]
LOG, PAT = "FAILFAIXFAIL", "FAIL"
EVENTS = [(2, 3), (12, 30), (40, 50), (5, 1), (12, 10), (3, 4)]


def show(lst):
    return "[" + ", ".join(f"{a}:{s}" for a, s in lst) + "]"


def trace_insertion(alerts, buggy):
    alerts = list(alerts)
    print(f"  start            {show(alerts)}")
    for i in range(1, len(alerts)):
        key, j = alerts[i], i - 1
        moves = 0
        while (j > 0 if buggy else j >= 0) and alerts[j][1] < key[1]:
            alerts[j + 1] = alerts[j]; j -= 1; moves += 1
        alerts[j if buggy else j + 1] = key
        print(f"  i={i} key={key[0]}:{key[1]} shifts={moves} j_end={j:>2} "
              f"-> write at index {j if buggy else j + 1}  {show(alerts)}")
    return alerts


print("INSERTION TRACE - ORIGINAL (j > 0 ; alerts[j] = key)")
trace_insertion(ALERTS, True)
print("\nINSERTION TRACE - CORRECTED (j >= 0 ; alerts[j+1] = key)")
trace_insertion(ALERTS, False)

print("\nALIGNMENT TABLE  log='FAILFAIXFAIL' (n=12) pattern='FAIL' (m=4)")
print("  i  window  char compares (log vs pattern)       original(range(8))  corrected(range(9))")
for i in range(len(LOG) - len(PAT) + 1):
    window = LOG[i:i + 4]
    cmp_s, j = [], 0
    while j < 4:
        ok = LOG[i + j] == PAT[j]
        cmp_s.append(f"{LOG[i + j]}{'=' if ok else '!'}{PAT[j]}")
        if not ok:
            break
        j += 1
    full = (j == 4)
    j_end = min(j, 3)                         # loop variable value after the inner loop
    orig_hit = (i < len(LOG) - len(PAT)) and (j_end == 3)      # 'j == m-1' test, only i<=7
    orig_txt = ("not scanned" if i >= len(LOG) - len(PAT) else ("HIT" if orig_hit else "no hit"))
    corr_txt = "HIT" if full else "no hit"
    flag = "  <-- FALSE HIT" if orig_hit and not full else ("  <-- MISSED" if full and not orig_hit else "")
    print(f"  {i}  {window}    {' '.join(cmp_s):<34} {orig_txt:<19} {corr_txt}{flag}")

print("\nCLOSEST_LOGINS pair table (d in km)")
print("  pair  points                      d")
best = None
for i in range(len(EVENTS)):
    for j in range(i + 1, len(EVENTS)):
        d = math.dist(EVENTS[i], EVENTS[j])
        mark = ""
        if best is None or d < best[0]:
            best, mark = (d, (i, j)), "  <- new minimum"
        print(f"  ({i},{j})  {str(EVENTS[i]):>8} {str(EVENTS[j]):>8}   {d:8.4f}{mark}")
print(f"  closest pair = {best[1]}, d = {best[0]:.4f} km")
far = max(((math.dist(EVENTS[i], EVENTS[j]), (i, j)) for i in range(6) for j in range(i + 1, 6)))
print(f"  farthest pair (what the ORIGINAL returned) = {far[1]}, d = {far[0]:.4f} km")
