# Task 2 · Contrast curve

Points are uniform in the unit cube [0,1]^d. Each run samples 20,000 random pairs (unless noted) and measures their
Euclidean distances. Raw numbers: `curse.json`.

## A7 · Machine

| | |
|---|---|
| CPU | AMD Ryzen 5 7430U (6 cores / 12 threads), `AMD64 Family 25 Model 80` |
| RAM | 13.8 GB |
| OS / Python | Windows 11 (10.0.26200), Python 3.14.6 |
| Also running | the Claude desktop app and normal background apps |
| Largest run | d = 1000, 2,000 points, 20,000 pairs: **6.2 s** (the 200,000-pair run at d = 20 took 1.8 s) |

## A2 · Contrast against dimension

| d | points | mean | min | max | contrast (max−min)/min | relative sd | mean / √(d/6) |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 2 | 1,000 | 0.521 | 0.003 | 1.326 | 488.6 | 0.476 | 0.902 |
| 5 | 1,000 | 0.884 | 0.111 | 1.687 | 14.26 | 0.282 | 0.968 |
| 10 | 1,000 | 1.274 | 0.438 | 2.159 | 3.93 | 0.193 | 0.987 |
| 20 | 1,000 | 1.815 | 0.821 | 2.670 | 2.25 | 0.135 | 0.994 |
| 50 | 1,000 | 2.867 | 1.909 | 3.785 | **0.98** | 0.083 | 0.993 |
| 100 | 1,000 | 4.068 | 3.206 | 4.954 | 0.55 | 0.060 | 0.997 |
| 200 | 1,000 | 5.776 | 4.871 | 6.682 | **0.37** | 0.041 | 1.000 |
| 500 | 2,000 | 9.126 | 8.099 | 10.176 | 0.26 | 0.026 | 1.000 |
| 1000 | 2,000 | 12.909 | 11.970 | 13.806 | 0.15 | 0.019 | 1.000 |

## A3 · What contrast does

Contrast collapses fast and then keeps sliding: from 489 at d = 2 to 14 at d = 5, 2.3 at d = 20, and it goes
**below 1 at d ≈ 50** (0.98). It goes **below 0.5 between d = 100 (0.55) and d = 200 (0.37)**, and is 0.15 at d = 1000.
Below 1 means the furthest pair in the sample is less than twice as far as the closest pair; at d = 1000 the closest
and furthest pairs differ by only 15%.

## A4 · How the mean grows

The mean grows like **√d, not linearly**: the last column divides by √(d/6) — the root of the expected *squared*
distance, d · E[(x−y)²] = d/6 — and it is 0.99–1.00 from d = 10 up. Doubling d from 100 to 200 multiplied the mean
by 1.42 ≈ √2, not 2. At small d the ratio is below 1 (0.90 at d = 2) because the mean of a square root is smaller
than the square root of the mean (Jensen), and that gap matters only while the spread is large compared to the mean.

## A5 · Relative standard deviation

Relative sd falls from 0.476 to 0.019, roughly as **0.6 / √d** (d · rel.sd² stays at 0.34–0.36 from d = 20 to 1000).
I think relative sd captures "distance stopped meaning anything" better than contrast: it describes the whole
distribution, not two extreme pairs, and it is stable — at d = 20 it was 0.134–0.135 for every point count I tried,
while contrast moved between 1.73 and 2.67 (A6). Contrast is still the number a nearest-neighbour query feels, but
it is a noisy estimate of it.

## A6 · Does n matter?

| d | points | pairs sampled | contrast | relative sd |
|---:|---:|---:|---:|---:|
| 20 | 100 | 19,803 (only 4,950 distinct) | 1.73 | 0.134 |
| 20 | 1,000 | 19,981 | 2.25 | 0.135 |
| 20 | 2,000 | 19,989 | 2.45 | 0.134 |
| 20 | 10,000 | 19,999 | 1.90 | 0.135 |
| 20 | 10,000 | 199,983 | 2.67 | 0.135 |
| 100 | 100 | 19,812 | 0.52 | 0.060 |
| 100 | 10,000 | 19,999 | 0.68 | 0.060 |
| 2 | 1,000 / 10,000 | ~20,000 | 489 / 301 | 0.476 / 0.478 |

**Yes, contrast depends on how many distances you look at, not only on d.** min and max are extremes, so the more
distinct pairs you see, the closer the closest pair and the further the furthest: at d = 20, going from 4,950
distinct pairs (n = 100) to ~200,000 pairs (n = 10,000) raised contrast from 1.73 to 2.67. With only 20,000 sampled pairs
it is also noisy (n = 2,000 gave 2.45 but n = 10,000 gave 1.90). Relative sd does not move with n at all.
So "contrast drops below 1 at d ≈ 50" is a statement about *this* sample size; a larger data set pushes that dimension
up somewhat, but only slowly, because the extremes grow slowly with the number of pairs while the concentration with
d is steady.

## A8 · Does this threaten week 3's LSH on Jaccard?

**Not directly, in my view.** The curse measured here is for points spread *uniformly* in every dimension, where
each coordinate adds an independent bit of noise to every distance. Shingle sets are nothing like that: they are
extremely sparse, and documents that are near-duplicates share most of their shingles, so their Jaccard similarity
stays high (0.8+) while random pairs sit near 0 — the gap does not shrink as the shingle vocabulary grows.
MinHash also does not "see" the dimension: P(minhash agrees) = Jaccard similarity exactly, whatever the number of
possible shingles. Where it *would* bite is a collection of unrelated documents with no near-duplicates — then all
similarities bunch together near 0 and "the most similar pair" carries no meaning, which is the same lesson as this
task: the curse is about whether the data has structure, not about the algorithm.
