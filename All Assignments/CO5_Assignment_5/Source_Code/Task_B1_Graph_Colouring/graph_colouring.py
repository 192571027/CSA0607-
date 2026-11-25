"""Task B1 - Graph (m-)Colouring by Backtracking with Pruning.

Solvers
  1. plain_backtracking      : fixed vertex order, check conflicts on assignment
  2. smart_backtracking      : MRV + degree tie-break + forward checking (domain pruning)
                               + symmetry breaking on colour labels
  3. greedy_welsh_powell     : polynomial heuristic (upper bound on chromatic number)
Metric: number of search nodes (recursive calls) and wall time.
"""
import random, time, itertools


# ---------- graph helpers ----------
def make_graph(n, edges):
    adj = {i: set() for i in range(n)}
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    return adj


def valid_colouring(adj, col):
    return (all(c is not None for c in col.values())
            and all(col[u] != col[v] for u in adj for v in adj[u]))


# ---------- 1. plain backtracking ----------
def plain_backtracking(adj, m):
    n = len(adj)
    col = {v: None for v in adj}
    nodes = [0]

    def rec(v):
        nodes[0] += 1
        if v == n:
            return True
        for c in range(m):
            if all(col[u] != c for u in adj[v]):      # safe check
                col[v] = c
                if rec(v + 1):
                    return True
                col[v] = None
        return False

    ok = rec(0)
    return (dict(col) if ok else None), nodes[0]


# ---------- 2. MRV + forward checking ----------
def smart_backtracking(adj, m):
    col = {v: None for v in adj}
    dom = {v: set(range(m)) for v in adj}
    nodes = [0]

    def rec(assigned, max_used):
        nodes[0] += 1
        if assigned == len(adj):
            return True
        # MRV: smallest remaining domain; tie-break on highest degree
        v = min((x for x in adj if col[x] is None),
                key=lambda x: (len(dom[x]), -len(adj[x])))
        for c in sorted(dom[v]):
            if c > max_used + 1:        # symmetry breaking: colours are interchangeable
                break
            col[v] = c
            pruned, fail = [], False
            for u in adj[v]:            # forward checking
                if col[u] is None and c in dom[u]:
                    dom[u].discard(c)
                    pruned.append(u)
                    if not dom[u]:
                        fail = True
                        break
            if not fail and rec(assigned + 1, max(max_used, c)):
                return True
            for u in pruned:            # undo
                dom[u].add(c)
            col[v] = None
        return False

    ok = rec(0, -1)
    return (dict(col) if ok else None), nodes[0]


# ---------- 3. greedy (Welsh-Powell) ----------
def greedy_welsh_powell(adj):
    order = sorted(adj, key=lambda v: -len(adj[v]))
    col = {}
    for v in order:
        taken = {col[u] for u in adj[v] if u in col}
        c = 0
        while c in taken:
            c += 1
        col[v] = c
    return col, len(set(col.values()))


def chromatic_number(adj, solver):
    total_nodes = 0
    for m in range(1, len(adj) + 1):
        sol, nodes = solver(adj, m)
        total_nodes += nodes
        if sol:
            return m, sol, total_nodes


# ---------- test graphs ----------
def petersen():
    e = ([(i, (i + 1) % 5) for i in range(5)] + [(i, i + 5) for i in range(5)]
         + [(5 + i, 5 + (i + 2) % 5) for i in range(5)])
    return make_graph(10, e)


def complete(n):
    return make_graph(n, itertools.combinations(range(n), 2))


def cycle(n):
    return make_graph(n, [(i, (i + 1) % n) for i in range(n)])


def australia():
    # 0 WA, 1 NT, 2 SA, 3 Q, 4 NSW, 5 V, 6 T
    e = [(0, 1), (0, 2), (1, 2), (1, 3), (2, 3), (2, 4), (2, 5), (3, 4), (4, 5)]
    return make_graph(7, e)


def random_graph(n, p, seed):
    r = random.Random(seed)
    return make_graph(n, [(i, j) for i in range(n) for j in range(i + 1, n) if r.random() < p])


if __name__ == "__main__":
    tests = {"K5": complete(5), "C5 (odd cycle)": cycle(5), "C6 (even cycle)": cycle(6),
             "Petersen": petersen(), "Australia map": australia(),
             "Random n=20 p=.3": random_graph(20, .3, 1),
             "Random n=30 p=.2": random_graph(30, .2, 2),
             "Random n=40 p=.15": random_graph(40, .15, 3)}
    print(f"{'Graph':20}{'n':>4}{'chi':>5}{'greedy':>8}{'plain nodes':>14}{'smart nodes':>13}{'plain s':>9}{'smart s':>9}")
    for name, g in tests.items():
        t = time.time(); chi, sol, smart_n = chromatic_number(g, smart_backtracking); ts = time.time() - t
        assert valid_colouring(g, sol)
        t = time.time(); chi2, sol2, plain_n = chromatic_number(g, plain_backtracking); tp = time.time() - t
        assert chi == chi2 and valid_colouring(g, sol2)
        _, gr = greedy_welsh_powell(g)
        print(f"{name:20}{len(g):>4}{chi:>5}{gr:>8}{plain_n:>14}{smart_n:>13}{tp:>9.3f}{ts:>9.3f}")
    # infeasibility tests
    assert plain_backtracking(complete(4), 3)[0] is None
    assert smart_backtracking(complete(4), 3)[0] is None
    assert plain_backtracking(cycle(5), 2)[0] is None
    print("All colourings validated; K4 with 3 colours and C5 with 2 colours correctly infeasible.")
