# Task 2 - Identify the Basic Operation (2 marks)

The basic operation is the operation executed most often in the innermost part of the algorithm, whose count grows with n and therefore dominates the running time. Every other statement (index arithmetic, assignments, function-call overhead) is executed at most a constant number of times per basic operation, so counting basic operations measures the algorithm's growth rate independently of hardware.

**Table 2.1 - Basic operations**

| Algorithm | Basic operation | Where it occurs | Why it is appropriate | How its count changes with n |
|---|---|---|---|---|
| A - Linear search | Comparison A[i] = key | Body of the single for-loop; once per examined record | It is the only work inside the loop; loop control is proportional to it. Each execution examines exactly one record. | Between 1 and n. It grows in direct proportion to n for failed searches (always n) and on average for successful ones ((n+1)/2). |
| B - Binary search | Three-way comparison of key with A[mid] | Once per recursive call (once per level of the recursion) | Each call performs exactly one such comparison and then discards half of the range, so the number of calls equals the number of comparisons. | Equals the number of times n can be halved: at most floor(log2 n)+1. Multiplying n by 1,000 adds only about 10 comparisons. |
| B - Preprocessing (merge sort) | Comparison of two elements in Merge | Inner while-loop of Merge | Each comparison moves one element to the output, so total work is proportional to comparisons. | About n log2 n - n comparisons for random input. |
| C - Hash table | Comparison A[idx] = key inside the chain (the hash computation is one O(1) step per search) | For-loop over the chain of bucket h(key) | Hashing costs the same for every n, so the part that can vary is the chain scan; its length is the only n-dependent cost. | Expected chain length is alpha = n/m (about 0.75 here), independent of n if m grows with n. So it stays about 1-2 comparisons for any n. |
| C - Preprocessing (build) | Hash computation + append, once per record | Loop of BuildHash | Exactly n executions, each O(1). | Exactly n. |

**Relation to behaviour.** In A the operation count is governed by *where the key is*, in B by *how many times the range can be halved* (a property of n only), in C by *how crowded the key's bucket is* (a property of the load factor, not of n). These three different dependencies are exactly what produce the linear, logarithmic and constant growth derived in Task 3 and confirmed by counters in Task 9.
