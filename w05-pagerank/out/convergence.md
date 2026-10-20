# PageRank convergence measurements

Measurements were taken on the ChatGPT execution server, not the student's personal computer. Timings are single runs and can fluctuate.

## A1–A3: beta and convergence

| Nodes | Beta | L1 tolerance | Iterations | Seconds |
|---:|---:|---:|---:|---:|
| 1200 | 0.5 | 1e-10 | 14 | 0.008528 |
| 1200 | 0.7 | 1e-10 | 17 | 0.009610 |
| 1200 | 0.85 | 1e-10 | 20 | 0.010957 |
| 1200 | 0.95 | 1e-10 | 23 | 0.014174 |
| 1200 | 0.99 | 1e-10 | 24 | 0.014098 |
| 6000 | 0.5 | 1e-10 | 14 | 0.045765 |
| 6000 | 0.7 | 1e-10 | 18 | 0.054732 |
| 6000 | 0.85 | 1e-10 | 22 | 0.066026 |
| 6000 | 0.95 | 1e-10 | 24 | 0.074985 |
| 6000 | 0.99 | 1e-10 | 25 | 0.075384 |
| 1200 | 0.85 | 1e-04 | 9 | 0.005590 |
| 1200 | 0.85 | 1e-06 | 12 | 0.006376 |
| 1200 | 0.85 | 1e-03 | 7 | 0.004050 |

At 1,200 nodes and tolerance 1e-10, iterations increase from 14 to 24 as beta rises from 0.5 to 0.99. Less teleportation weakens mixing; the L1 contraction bound is beta, so the worst-case bound becomes slower near 1. This particular graph mixes faster than that bound predicts; the measured curve does not imply divergence.

## A4: size versus iterations and time

Before running, I predicted higher wall time for larger graphs but no proportional growth in iterations (see prediction.md). The graphs have 1,200 and 6,000 nodes, exactly 5x apart. At beta 0.85, iterations rise only from 20 to 22, while time rises from 0.010957 to 0.066026 seconds (6.03x). Each iteration scans nodes and edges, O(n + E); the iteration count depends on mixing and the stopping tolerance. The generated graphs also differ structurally, so size alone is not isolated by this experiment.

## A5: tolerance

At beta 0.85 and 1,200 nodes, tolerances 1e-4, 1e-6 and 1e-10 take 9, 12 and 20 iterations: 1.5 extra iterations per digit for the first two digits, then 2 per digit for the next four. The six-digit average is 11/6 = 1.83 extra iterations per digit. The additional 1e-3 run makes the absolute tolerance separation exceed 1e-4 as well. All runs stopped before the 500-iteration cap. These costs are empirical, not a universal constant.

## A6: top-10 ranking

For both sizes, the first observed order change is at beta 0.7 compared with 0.5: p00000 and p00004 swap positions 7 and 8. Membership of the top 10 stays the same for all five tested betas; order stays unchanged from 0.7 through 0.99. The exact transition lies somewhere in (0.5, 0.7], which this grid does not resolve. A published ranking should report beta: stable membership does not guarantee stable order.

## A7: machine and concurrent activity

- cpu: AMD EPYC 9V74 80-Core Processor
- logical_cpus: 9
- host_ram_gib: 9.73
- environment: ChatGPT execution server; not the student's laptop
- other_work: No other benchmark intentionally started; shared-host activity unknown
- platform: Linux-6.18.55-x86_64-with-glibc2.39
- processor: x86_64
- python: 3.12.14

RAM is the amount visible through /proc/meminfo; it is not a measurement of algorithm memory. Other shared-host workloads are unknown.
