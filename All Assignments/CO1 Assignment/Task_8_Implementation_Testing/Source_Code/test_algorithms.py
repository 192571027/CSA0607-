"""Unit tests (python test_algorithms.py  or  python -m unittest -v)."""
import random
import unittest
from algorithms import (linear_search, binary_search_recursive, merge_sort, merge_sorted,
                        HashIndex, linear_search_counted, binary_search_counted)
from data_gen import make_dataset, make_queries


class TestSearch(unittest.TestCase):
    def setUp(self):
        self.data = [905, 120, 777, 431, 654, 999, 101, 310]
        self.sorted, _ = merge_sort(self.data)
        self.h = HashIndex(list(self.data))

    # --- boundary / special cases --------------------------------------
    def test_empty(self):
        self.assertEqual(linear_search([], 5), -1)
        self.assertEqual(binary_search_recursive([], 5), -1)
        self.assertEqual(HashIndex([]).search(5), -1)

    def test_single_element(self):
        self.assertEqual(linear_search([7], 7), 0)
        self.assertEqual(binary_search_recursive([7], 7), 0)
        self.assertEqual(HashIndex([7]).search(7), 0)
        self.assertEqual(binary_search_recursive([7], 8), -1)

    def test_first_and_last(self):
        self.assertEqual(linear_search(self.data, 905), 0)
        self.assertEqual(linear_search(self.data, 310), 7)
        self.assertEqual(self.sorted[binary_search_recursive(self.sorted, 101)], 101)
        self.assertEqual(self.sorted[binary_search_recursive(self.sorted, 999)], 999)

    def test_absent_below_between_above(self):
        for k in (1, 500, 5000):
            self.assertEqual(linear_search(self.data, k), -1)
            self.assertEqual(binary_search_recursive(self.sorted, k), -1)
            self.assertEqual(self.h.search(k), -1)

    def test_all_present_keys(self):
        for k in self.data:
            self.assertEqual(self.data[linear_search(self.data, k)], k)
            self.assertEqual(self.sorted[binary_search_recursive(self.sorted, k)], k)
            self.assertEqual(self.h.records[self.h.search(k)], k)

    # --- sorting ---------------------------------------------------------
    def test_merge_sort_matches_builtin(self):
        for n in (0, 1, 2, 3, 10, 257, 5000):
            d = make_dataset(n) if n else []
            s, _ = merge_sort(d)
            self.assertEqual(s, sorted(d))

    def test_merge_sorted(self):
        a, b = sorted(random.sample(range(10000), 50)), sorted(random.sample(range(10000), 20))
        self.assertEqual(merge_sorted(a, b), sorted(a + b))

    # --- counted versions agree with plain versions ------------------------
    def test_counted_agree(self):
        d = make_dataset(1000)
        s, _ = merge_sort(d)
        h = HashIndex(list(d))
        hits, misses = make_queries(d, 100)
        for k in hits + misses:
            self.assertEqual(linear_search_counted(d, k)[0], linear_search(d, k))
            self.assertEqual(binary_search_counted(s, k)[0], binary_search_recursive(s, k))
            self.assertEqual(h.search_counted(k)[0], h.search(k))

    # --- worst-case operation counts match theory ---------------------------
    def test_linear_counts(self):
        d = make_dataset(1000)
        self.assertEqual(linear_search_counted(d, d[0])[1], 1)           # best
        self.assertEqual(linear_search_counted(d, d[-1])[1], 1000)       # worst (last)
        self.assertEqual(linear_search_counted(d, -1)[1], 1000)          # worst (absent)

    def test_binary_worst_case_bound(self):
        import math
        for n in (1, 2, 7, 8, 1000, 4096):
            s = list(range(0, 2 * n, 2))
            bound = math.floor(math.log2(n)) + 1
            worst = max(binary_search_counted(s, k)[1] for k in range(-1, 2 * n + 1))
            self.assertLessEqual(worst, bound)
            self.assertEqual(worst, bound)

    # --- cross-check on a large random dataset -----------------------------
    def test_large_random_agreement(self):
        d = make_dataset(20000)
        s, _ = merge_sort(d)
        h = HashIndex(list(d))
        hits, misses = make_queries(d, 500)
        for k in hits:
            self.assertGreaterEqual(linear_search(d, k), 0)
            self.assertGreaterEqual(binary_search_recursive(s, k), 0)
            self.assertGreaterEqual(h.search(k), 0)
        for k in misses:
            self.assertEqual(linear_search(d, k), -1)
            self.assertEqual(binary_search_recursive(s, k), -1)
            self.assertEqual(h.search(k), -1)

    # --- hash insert (daily update) -----------------------------------------
    def test_hash_insert(self):
        h = HashIndex([1, 2, 3])
        h.insert(42)
        self.assertEqual(h.records[h.search(42)], 42)
        self.assertEqual(len(h.records), 4)


if __name__ == "__main__":
    unittest.main(verbosity=2)
