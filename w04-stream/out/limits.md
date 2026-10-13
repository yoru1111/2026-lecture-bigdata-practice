# Task 2 — Memory Limits

## Measurement environment
These measurements were performed in GitHub Codespaces, not on my local laptop.
Recorded platform: Linux-6.8.0-1064-azure-x86_64-with-glibc2.39.
Python: 3.12.3. Recorded architecture: x86_64.
CPU model, allocated RAM, and other running applications have not yet been documented.

## Results
Memory is the peak Python allocation measured by tracemalloc, not total process RAM.
MB uses 1,000,000 bytes.

| Stream size | True distinct | Exact time (s) | Exact peak (MB) | FM time (s) | FM peak (bytes) | FM / truth |
|---:|---:|---:|---:|---:|---:|---:|
| 100,000 | 36,702 | 0.369 | 3.926 | 62.338 | 4,393 | 1.320 |
| 200,000 | 73,410 | 0.943 | 5.761 | 123.364 | 4,393 | 1.267 |
| 400,000 | 146,970 | 1.637 | 11.591 | 247.323 | 4,395 | 1.438 |
| 1,600,000 | 587,625 | 5.843 | 46.648 | 984.008 | 4,395 | 1.319 |

## Memory growth
The stream size increased 16-fold, while exact-set peak memory increased approximately 11.9-fold.
Exact storage grows approximately linearly with the distinct count, which grows with n in this experiment: O(n). Set resizing causes nonuniform increases.
FM peak memory changed only from 4,393 to 4,395 bytes. With 64 hashes fixed, its storage is O(1) with respect to stream length.

## Accuracy
FM ratios ranged from 1.267 to 1.438, and all four estimates were above the truth.
Accuracy did not consistently improve or worsen as the stream grew.

## Where exact became impractical
The exact method did not become impractical within the tested range.
At the largest tested size, 1,600,000 items, it took 5.843 seconds and approximately 46.648 MB of tracked peak memory.
Therefore, these measurements do not establish a time or memory limit for the exact method. Requirement A2 still needs further measurement.
The long FM runtime is not evidence of an exact-method limit.
