"""Task B3 - Exact vs Approximation: Minimum Vertex Cover (NP-hard).
  exact_bruteforce   : try all subsets by increasing size            O(2^n * m)
  exact_branch_bound : branch on an uncovered edge (take u OR v), prune with incumbent
                       and a maximal-matching lower bound
  approx_2           : maximal matching, take both endpoints; |C| <= 2*OPT
  approx_greedy      : repeatedly take max-degree vertex (ln n-approx; no constant bound)
"""
import itertools, random, time


def edges_of(n, p, seed):
    r = random.Random(seed)
    return [(i, j) for i in range(n) for j in range(i + 1, n) if r.random() < p]


def is_cover(edges, C):
    return all(u in C or v in C for u, v in edges)


def exact_bruteforce(n, edges):
    for k in range(n + 1):
        for C in itertools.combinations(range(n), k):
            s = set(C)
            if is_cover(edges, s):
                return s


def exact_branch_bound(n, edges):
    best = [set(range(n))]
    nodes = [0]

    def rec(E, C):
        nodes[0] += 1
        if len(C) >= len(best[0]):
            return                                           # prune: cannot beat incumbent
        if not E:
            best[0] = set(C)
            return
        used, lb = set(), 0                                  # lower bound = matching size
        for u, v in E:
            if u not in used and v not in used:
                used |= {u, v}
                lb += 1
        if len(C) + lb >= len(best[0]):
            return                                           # prune by matching bound
        u, v = E[0]
        rec([e for e in E if u not in e], C | {u})           # branch 1: take u
        rec([e for e in E if v not in e], C | {v})           # branch 2: take v

    rec(list(edges), set())
    return best[0], nodes[0]


def approx_2(edges):
    C = set()
    for u, v in edges:
        if u not in C and v not in C:
            C |= {u, v}
    return C


def approx_greedy(n, edges):
    E = set(edges)
    C = set()
    while E:
        deg = {}
        for u, v in E:
            deg[u] = deg.get(u, 0) + 1
            deg[v] = deg.get(v, 0) + 1
        x = max(deg, key=deg.get)
        C.add(x)
        E = {e for e in E if x not in e}
    return C


if __name__ == "__main__":
    print("Correctness/ratio on random graphs (p=0.25)")
    print(f"{'n':>4}{'|E|':>6}{'OPT':>5}{'2-apx':>7}{'ratio':>7}{'greedy':>8}{'ratio':>7}{'BF s':>10}{'B&B s':>10}{'B&B nodes':>11}{'apx s':>10}")
    worst = 0
    for n in [8, 12, 16, 20, 24]:
        E = edges_of(n, .25, n)
        t = time.time(); bf = exact_bruteforce(n, E) if n <= 20 else None
        tbf = time.time() - t if bf is not None else float('nan')
        t = time.time(); bb, nodes = exact_branch_bound(n, E); tbb = time.time() - t
        t = time.time(); a2 = approx_2(E); ta = time.time() - t
        gr = approx_greedy(n, E)
        assert is_cover(E, bb) and is_cover(E, a2) and is_cover(E, gr)
        if bf is not None:
            assert len(bf) == len(bb)
        opt = len(bb)
        worst = max(worst, len(a2) / opt)
        assert len(a2) <= 2 * opt
        print(f"{n:>4}{len(E):>6}{opt:>5}{len(a2):>7}{len(a2) / opt:>7.2f}{len(gr):>8}{len(gr) / opt:>7.2f}{tbf:>10.4f}{tbb:>10.4f}{nodes:>11}{ta:>10.6f}")
    print(f"Worst observed 2-approx ratio = {worst:.2f} (theoretical bound 2.00)")

    # Tight instance: K_{k,k}, matching edges processed first -> 2k vs OPT = k
    k = 6
    E = [(i, k + j) for i in range(k) for j in range(k)]
    E.sort(key=lambda e: (e[1] - e[0] != k, e))
    a2 = approx_2(E)
    opt, _ = exact_branch_bound(2 * k, E)
    assert is_cover(E, a2)
    print(f"Tight instance K_{{{k},{k}}}: 2-approx = {len(a2)}, OPT = {len(opt)}, ratio = {len(a2) / len(opt):.2f}")

    print("\nScaling (p=0.15)")
    print(f"{'n':>4}{'B&B s':>10}{'B&B size':>10}{'2-apx size':>12}{'2-apx s':>10}")
    for n in [30, 40, 50]:
        E = edges_of(n, .15, n)
        t = time.time(); bb, _ = exact_branch_bound(n, E); tb = time.time() - t
        t = time.time(); a2 = approx_2(E); ta = time.time() - t
        print(f"{n:>4}{tb:>10.3f}{len(bb):>10}{len(a2):>12}{ta:>10.6f}")

    print("\nLarge graphs (exact infeasible; approximation only, p=0.01)")
    print(f"{'n':>6}{'|E|':>9}{'2-apx size':>12}{'greedy size':>13}{'2-apx s':>10}{'greedy s':>10}")
    for n in [200, 500, 1000]:
        E = edges_of(n, .01, n)
        t = time.time(); a2 = approx_2(E); ta = time.time() - t
        t = time.time(); gr = approx_greedy(n, E); tg = time.time() - t
        assert is_cover(E, a2) and is_cover(E, gr)
        print(f"{n:>6}{len(E):>9}{len(a2):>12}{len(gr):>13}{ta:>10.5f}{tg:>10.4f}")
