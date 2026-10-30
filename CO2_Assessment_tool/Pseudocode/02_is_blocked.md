# Pseudocode 2 - `is_blocked` (blocklist membership)

**Input:** `B[0..b-1]` list of IP strings, query `ip`  
**Output:** `TRUE` if `ip` is in `B`, otherwise `FALSE` (also `FALSE` when `b = 0`)

## 2A. Corrected algorithm (sequential search)

```
ALGORITHM IsBlockedCorrected(B[0..b-1], ip)
    for i <- 0 to b-1 do
        if B[i] = ip then
            return TRUE                                       // D3: match must return TRUE
        end if
        // D4: no 'else return FALSE' here - keep scanning
    end for
    return FALSE                                              // D4: terminal return after the loop
```

* Comparisons: best 1, worst `b` (miss or last element), average about `b/2` for a hit.  `O(b)` per query.
* `q` queries cost `O(q*b)`.

## 2B. Optimised algorithm (hash index built once, O(1) lookups)

```
ALGORITHM BuildBlocklistIndex(B[0..b-1])
    S <- empty hash set
    for i <- 0 to b-1 do
        insert B[i] into S                                    // expected O(1) each
    end for
    return S                                                  // O(b) once

ALGORITHM IsBlockedOptimised(S, ip)
    return (ip in S)                                          // expected O(1): hash(ip), probe one bucket
```

* `q` queries cost `O(b + q)` expected instead of `O(q*b)`.
* Worst case of hashing `O(b)` per probe is only reached with adversarial collisions; Python salts string hashes.
* Space `O(b)`.  The index must be rebuilt (or updated with `add` / `discard`) when the blocklist changes.
