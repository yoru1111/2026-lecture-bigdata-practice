# Observations

## Task 1
In the broken version, dead-end rank disappears because there are no outgoing contributions; I instead redistribute it uniformly across all nodes.
Uniform dead-end redistribution preserves mass, and teleportation supplies escape probability from traps, so the repaired random-surfer model handles both failures.
Beta is the probability of following a link; with probability 1-beta the surfer chooses a uniformly random node.

## Task 2
At 1,200 nodes, increasing beta from 0.5 to 0.99 raised iterations from 14 to 24 because weaker teleportation slows mixing.
At beta 0.85, increasing size 5x raised iterations only 20 to 22 but time about 6.03x: work per iteration grows with nodes and edges, while convergence depends on graph structure.
The first sampled top-10 order change was at beta 0.7 (positions 7 and 8 swapped); membership stayed fixed, so published rankings should still disclose beta. Measurements are from a ChatGPT server, not my laptop.

## Task 3
I store integer adjacency lists and two rank vectors, using O(n+E) overall storage and at most 2n+16 float slots (2,416 for n=1,200, including a conservative scalar allowance), instead of n² matrix entries. The float metric excludes integer and Python-object overhead, so it is not a RAM ratio.
Teleportation and redistributed dead-end mass form one scalar base added to each rank in O(n); no n-by-n matrix is needed, and each iteration is O(n+E).
The unmodified harness measured 77.5x speedup and 596.0x fewer float slots, with worst per-node error 1.17e-15; this tiny difference comes from floating-point accumulation order. Times may vary across runs.
