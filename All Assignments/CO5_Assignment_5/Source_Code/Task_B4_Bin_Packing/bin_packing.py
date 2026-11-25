"""Task B4 - Bin Packing: online/offline approximations vs exact branch-and-bound.
  NF, FF, BF (online);  FFD, BFD (offline, sort decreasing)
  exact : backtracking with L1 lower bound ceil(sum/C), symmetry and incumbent pruning
Known bounds: FF, BF <= 1.7 OPT + 1 ; FFD, BFD <= 11/9 OPT + 6/9 ; NF <= 2 OPT.
"""
import math, random, time


def next_fit(items, C):
    bins = [0]
    for x in items:
        if bins[-1] + x <= C:
            bins[-1] += x
        else:
            bins.append(x)
    return len(bins)


def first_fit(items, C):
    bins = []
    for x in items:
        for i in range(len(bins)):
            if bins[i] + x <= C:
                bins[i] += x
                break
        else:
            bins.append(x)
    return len(bins)


def best_fit(items, C):
    bins = []
    for x in items:
        j, rem = -1, C + 1
        for i, b in enumerate(bins):
            if b + x <= C and C - b - x < rem:
                rem = C - b - x
                j = i
        if j < 0:
            bins.append(x)
        else:
            bins[j] += x
    return len(bins)


def ffd(items, C):
    return first_fit(sorted(items, reverse=True), C)


def bfd(items, C):
    return best_fit(sorted(items, reverse=True), C)


def lower_bound(items, C):
    return math.ceil(sum(items) / C)


def exact(items, C, limit=2_000_000):
    """Returns (best bins found, nodes explored, proven_optimal)."""
    items = sorted(items, reverse=True)
    best = [ffd(items, C)]
    lb = lower_bound(items, C)
    nodes = [0]
    if best[0] == lb:
        return best[0], 1, True
    bins = []

    def rec(i):
        nodes[0] += 1
        if nodes[0] > limit or best[0] == lb:
            return
        if i == len(items):
            best[0] = min(best[0], len(bins))
            return
        x = items[i]
        seen = set()
        for j in range(len(bins)):
            if bins[j] + x <= C and bins[j] not in seen:    # equal-load bins are symmetric
                seen.add(bins[j])
                bins[j] += x
                rec(i + 1)
                bins[j] -= x
        if len(bins) + 1 < best[0]:                          # new bin must improve incumbent
            bins.append(x)
            rec(i + 1)
            bins.pop()

    rec(0)
    return best[0], nodes[0], nodes[0] <= limit


def instance(n, C, seed):
    r = random.Random(seed)
    return [r.randint(max(1, C // 10), C // 2) for _ in range(n)]


if __name__ == "__main__":
    C = 100
    assert first_fit([50, 50, 50, 50], 100) == 2 and next_fit([60, 50, 40, 50], 100) == 3
    assert ffd([4, 8, 1, 4, 2, 1], 10) == 2 and exact([4, 8, 1, 4, 2, 1], 10)[0] == 2
    assert lower_bound([50] * 5, 100) == 3
    print("Unit tests passed.\n")
    algs = [("NF", next_fit), ("FF", first_fit), ("BF", best_fit), ("FFD", ffd), ("BFD", bfd)]
    print(f"Random instances, capacity {C}, item sizes in [10,50]; ratio = bins/OPT")
    print(f"{'n':>4}{'seed':>5}{'LB':>5}{'OPT':>5}" + "".join(f"{a:>6}" for a, _ in algs) + f"{'B&B nodes':>11}{'exact s':>9}")
    tot = {a: 0 for a, _ in algs}
    mx = {a: 0 for a, _ in algs}
    cnt = 0
    for n in [10, 15, 20, 25, 30, 40]:
        for seed in range(3):
            it = instance(n, C, seed * 100 + n)
            t = time.time(); opt, nodes, done = exact(it, C); te = time.time() - t
            res = {a: f(it, C) for a, f in algs}
            for a in res:
                assert res[a] >= opt >= lower_bound(it, C)
                tot[a] += res[a] / opt
                mx[a] = max(mx[a], res[a] / opt)
            cnt += 1
            optstr = f"{opt}" if done else f"{opt}*"      # * = node limit hit, not proven optimal
            print(f"{n:>4}{seed:>5}{lower_bound(it, C):>5}{optstr:>5}" + "".join(f"{res[a]:>6}" for a, _ in algs) + f"{nodes:>11}{te:>9.3f}")
    print("(* = exact search hit the node limit; value is best found, an upper bound on OPT)")
    print("\nMean ratio : " + "  ".join(f"{a}={tot[a] / cnt:.3f}" for a, _ in algs))
    print("Worst ratio: " + "  ".join(f"{a}={mx[a]:.3f}" for a, _ in algs))
    print("\nLarge instances vs lower bound (n=1000)")
    it = instance(1000, C, 7)
    lb = lower_bound(it, C)
    for a, f in algs:
        t = time.time(); b = f(it, C)
        print(f"{a:>4}: {b} bins  (LB {lb}, ratio<= {b / lb:.3f}, {time.time() - t:.4f}s)")
    wc = [6] * 6 + [10] * 6 + [16] * 6 + [34] * 6 + [51] * 6
    C2 = 101
    print(f"\nClassic hard instance (C=101): FF={first_fit(wc, C2)}, FFD={ffd(wc, C2)}, LB={lower_bound(wc, C2)}, OPT={exact(wc, C2)[0]}")
