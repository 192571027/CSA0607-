"""Task B2 - Adversarial Search: Minimax vs Alpha-Beta (with move ordering) on Tic-Tac-Toe
and depth-limited Connect-4 (6x7)."""
import time

# ================= Tic-Tac-Toe =================
LINES = [(0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6)]


def winner(b):
    for a, c, d in LINES:
        if b[a] != '.' and b[a] == b[c] == b[d]:
            return b[a]
    return None


class Counter:
    n = 0


def ttt_minimax(b, player):             # X maximises, O minimises
    Counter.n += 1
    w = winner(b)
    if w:
        return 1 if w == 'X' else -1
    if '.' not in b:
        return 0
    vals = []
    for i in range(9):
        if b[i] == '.':
            b[i] = player
            vals.append(ttt_minimax(b, 'O' if player == 'X' else 'X'))
            b[i] = '.'
    return max(vals) if player == 'X' else min(vals)


ORDER = [4, 0, 2, 6, 8, 1, 3, 5, 7]     # centre, corners, edges


def ttt_alphabeta(b, player, alpha=-2, beta=2, ordered=True):
    Counter.n += 1
    w = winner(b)
    if w:
        return 1 if w == 'X' else -1
    if '.' not in b:
        return 0
    moves = [i for i in (ORDER if ordered else range(9)) if b[i] == '.']
    if player == 'X':
        best = -2
        for i in moves:
            b[i] = 'X'
            best = max(best, ttt_alphabeta(b, 'O', alpha, beta, ordered))
            b[i] = '.'
            alpha = max(alpha, best)
            if alpha >= beta:
                break                    # beta cut-off
        return best
    best = 2
    for i in moves:
        b[i] = 'O'
        best = min(best, ttt_alphabeta(b, 'X', alpha, beta, ordered))
        b[i] = '.'
        beta = min(beta, best)
        if alpha >= beta:
            break                        # alpha cut-off
    return best


def best_move(b, player):
    scores = {}
    for i in ORDER:
        if b[i] == '.':
            b[i] = player
            scores[i] = ttt_alphabeta(b, 'O' if player == 'X' else 'X', ordered=True)
            b[i] = '.'
    return (max if player == 'X' else min)(scores, key=scores.get)


def self_play():
    b = ['.'] * 9
    p = 'X'
    while not winner(b) and '.' in b:
        b[best_move(b, p)] = p
        p = 'O' if p == 'X' else 'X'
    return winner(b) or 'Draw'


# ================= Connect-4 (depth limited) =================
ROWS, COLS = 6, 7


def c4_moves(g):
    return [c for c in (3, 2, 4, 1, 5, 0, 6) if g[0][c] == '.']     # centre-first ordering


def c4_drop(g, c, p):
    for r in range(ROWS - 1, -1, -1):
        if g[r][c] == '.':
            g[r][c] = p
            return r


def c4_win(g, r, c, p):
    for dr, dc in ((0, 1), (1, 0), (1, 1), (1, -1)):
        k = 1
        for s in (1, -1):
            rr, cc = r + s * dr, c + s * dc
            while 0 <= rr < ROWS and 0 <= cc < COLS and g[rr][cc] == p:
                k += 1
                rr += s * dr
                cc += s * dc
        if k >= 4:
            return True
    return False


def c4_eval(g):                          # simple heuristic: centre-column control
    s = 0
    for r in range(ROWS):
        if g[r][3] == 'X':
            s += 3
        elif g[r][3] == 'O':
            s -= 3
    return s


def c4_search(g, depth, player, last, alpha, beta, use_ab):
    Counter.n += 1
    if last and c4_win(g, last[0], last[1], 'O' if player == 'X' else 'X'):
        return (-1000 - depth) if player == 'X' else (1000 + depth)
    mv = c4_moves(g)
    if depth == 0 or not mv:
        return c4_eval(g)
    maxing = player == 'X'
    best = -10 ** 9 if maxing else 10 ** 9
    for c in mv:
        r = c4_drop(g, c, player)
        v = c4_search(g, depth - 1, 'O' if maxing else 'X', (r, c), alpha, beta, use_ab)
        g[r][c] = '.'
        if maxing:
            best = max(best, v)
            alpha = max(alpha, best)
        else:
            best = min(best, v)
            beta = min(beta, best)
        if use_ab and alpha >= beta:
            break
    return best


if __name__ == "__main__":
    # --- Tic-Tac-Toe from empty board
    Counter.n = 0; t = time.time(); v1 = ttt_minimax(['.'] * 9, 'X'); n1 = Counter.n; t1 = time.time() - t
    Counter.n = 0; t = time.time(); v2 = ttt_alphabeta(['.'] * 9, 'X', ordered=False); n2 = Counter.n; t2 = time.time() - t
    Counter.n = 0; t = time.time(); v3 = ttt_alphabeta(['.'] * 9, 'X', ordered=True); n3 = Counter.n; t3 = time.time() - t
    assert v1 == v2 == v3 == 0
    print("Tic-Tac-Toe (empty board, value must be 0 = draw)")
    print(f"{'Algorithm':32}{'value':>6}{'nodes':>10}{'time s':>9}")
    print(f"{'Minimax':32}{v1:>6}{n1:>10}{t1:>9.3f}")
    print(f"{'Alpha-Beta (natural order)':32}{v2:>6}{n2:>10}{t2:>9.3f}")
    print(f"{'Alpha-Beta (centre-first order)':32}{v3:>6}{n3:>10}{t3:>9.3f}")
    print(f"Pruning: {100 * (1 - n2 / n1):.1f}% / {100 * (1 - n3 / n1):.1f}% fewer nodes than minimax")
    print("Perfect-play self-play result:", self_play())
    # Known test positions
    b = list("XX.OO....")
    assert ttt_alphabeta(b, 'X') == 1 and best_move(b, 'X') == 2     # X wins at square 2
    # O to move: square 5 wins immediately; best_move must pick a move whose value is a forced O win (-1)
    mv = best_move(b, 'O'); b[mv] = 'O'
    assert ttt_alphabeta(b, 'X') == -1; b[mv] = '.'
    # O threatens 0-1-2 and X has no win: X must block square 2 (every other move loses)
    b2 = list("OO..X...X")
    assert best_move(b2, 'X') == 2
    print("Positional tests passed (win / block).")
    # --- Connect-4
    print("\nConnect-4 6x7, empty board, X to move")
    print(f"{'Depth':>5}{'Minimax nodes':>16}{'AlphaBeta nodes':>17}{'Reduction':>11}{'Value MM':>10}{'Value AB':>10}")
    for d in range(1, 7):
        g = [['.'] * COLS for _ in range(ROWS)]
        Counter.n = 0; a = c4_search(g, d, 'X', None, -10 ** 9, 10 ** 9, False); nm = Counter.n
        Counter.n = 0; b_ = c4_search(g, d, 'X', None, -10 ** 9, 10 ** 9, True); na = Counter.n
        assert a == b_
        print(f"{d:>5}{nm:>16}{na:>17}{100 * (1 - na / nm):>10.1f}%{a:>10}{b_:>10}")
