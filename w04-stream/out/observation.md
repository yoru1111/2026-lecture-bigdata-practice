# Week 4 Observations

## Task 1
Bloom filters cannot produce false negatives because insertion sets every bit checked by membership queries, and those bits are never cleared; the predicted false-positive rate was 0.860%, versus 0.870% measured, with the small difference consistent with finite-sample variation.
My FM implementation averages trailing-zero maxima within groups and takes the median of group estimates; it estimated 24,219 versus 19,953 true distinct items (1.21×). Alternative combining rules have not yet been measured.
Reservoir sampling uses rng.randrange(count) and replaces an entry only when slot < k, giving each arriving item admission probability k/count without knowing the final stream length; the retained sample contains at most k items.

## Task 2
The exact method remained practical through 1,600,000 items (5.843 seconds, 46.648 MB), so I have not yet established the size where time or memory becomes unbearable; these results were measured in Codespaces, not on my laptop.
Across a 16× increase in stream size, exact peak memory rose approximately 11.9×, consistent with O(n) storage, while FM remained at 4,393–4,395 bytes, consistent with O(1) storage for a fixed hash count.
Factor-of-two accuracy may be acceptable for a rough capacity estimate with a large safety margin, but not for billing or precise daily-user reporting; my measured ratios ranged from 1.267× to 1.438× without a monotonic trend.

## Task 3
Minimizing p(k) ≈ (1 − exp(−kn/m))^k gives k* = (m/n) ln 2 ≈ 6.93 at 10 bits/item, so I changed the hash count from 1 to 7.
The ideal Bloom-filter minimum is exp(−10(ln 2)^2) ≈ 0.819%; I measured 0.891%, with zero false negatives and 79,304 bits of retained storage. Reserving overhead leaves 77,952 actual filter bits; false positives decreased by 90.6% relative to baseline.
For unknown n, I would monitor occupancy and use a scalable Bloom filter if additional memory were allowed: underestimating n raises false positives, while overestimating n wastes memory; a fixed budget cannot maintain the same low error rate indefinitely.
