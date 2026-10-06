#!/usr/bin/env python3
"""Task 2: run on your own machine. bench.py remains unmodified.

Example:
python3 task2_crossover.py --sizes 250,500,1000,2000,4000 \
    --cpu "your CPU" --ram-gb 16 --background "browser open"
Peak memory measures traced Python allocations, not total process RAM.
"""
import argparse
import json
import math
import os
import platform
import random
import time
import tracemalloc
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'out')


def build_docs(n, seed=246, shingle_count=60, vocab=5000):
    """Exactly n documents, approximately the harness's clone proportion.

    This is a separate Task 2 dataset generator, not a change to bench.py.
    A single seed is used for reproducibility at each size; datasets are not
    guaranteed to be nested across sizes.
    """
    rng = random.Random(seed)
    planted = min(n - 1, int(n * 120 / 2120))
    base_count = n - planted
    docs = [set(rng.sample(range(vocab), shingle_count))
            for _ in range(base_count)]
    for _ in range(planted):
        clone = set(docs[rng.randrange(base_count)])
        for _ in range(rng.randint(4, 14)):
            clone.discard(rng.choice(list(clone)))
            clone.add(rng.randrange(vocab))
        docs.append(clone)
    rng.shuffle(docs)
    assert len(docs) == n
    return docs


def machine(args):
    # Collect these details only on the user's computer when they run this file.
    return {
        'platform': platform.platform(),
        'processor': args.cpu or platform.processor() or platform.machine(),
        'python': platform.python_version(),
        'ram_gb': args.ram_gb,
        'background': args.background,
    }


def timed(fn, *args):
    tracemalloc.start()
    try:
        t0 = time.perf_counter()
        result = fn(*args)
        elapsed = time.perf_counter() - t0
        _, peak = tracemalloc.get_traced_memory()
        return result, elapsed, peak
    finally:
        tracemalloc.stop()


def save(path, data):
    temp = path + '.tmp'
    with open(temp, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(temp, path)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--sizes', default='250,500,1000,2000,4000')
    p.add_argument('--threshold', type=float, default=0.6)
    p.add_argument('--seed', type=int, default=246)
    p.add_argument('--cpu', default='', help='CPU model, recorded as supplied')
    p.add_argument('--ram-gb', type=float, help='Installed RAM in GB')
    p.add_argument('--background', default='not recorded',
                   help='Other programs running during measurement')
    a = p.parse_args()
    try:
        sizes = [int(x.strip()) for x in a.sizes.split(',')]
    except ValueError:
        p.error('--sizes must contain comma-separated positive integers')
    if not sizes or any(n <= 0 for n in sizes):
        p.error('all sizes must be positive')
    if not math.isfinite(a.threshold) or not 0 <= a.threshold <= 1:
        p.error('--threshold must be between 0 and 1')
    if a.ram_gb is not None and (not math.isfinite(a.ram_gb) or a.ram_gb <= 0):
        p.error('--ram-gb must be positive')

    import bench
    from task3_scale import BruteForce, YourFinder
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, 'crossover.json')
    if os.path.exists(path):
        with open(path, encoding='utf-8') as f:
            prior = json.load(f)
        old_runs = prior.get('runs', [])
        if old_runs and prior.get('generator') != 'task2_exact_n_v1':
            p.error('Existing crossover.json uses an older/unknown generator. '
                    'Move it to a backup filename before starting this series.')
    else:
        prior = {'runs': []}
    info = machine(a)
    prior['machine'] = info
    prior['generator'] = 'task2_exact_n_v1'
    prior['memory_note'] = 'tracemalloc peak; input documents generated before tracing'
    if not a.cpu or a.ram_gb is None or a.background == 'not recorded':
        print('Note: supply --cpu, --ram-gb and --background for requirement A6.', flush=True)

    for n in sizes:
        print(f'\nStarting n={n:,}; brute force first...', flush=True)
        docs = build_docs(n, a.seed)
        sim = bench.Counter()
        found, t_brute, m_brute = timed(BruteForce(a.threshold).find, docs, sim)
        brute_count = len(found)
        del found
        row = {
            'n': len(docs), 'seed': a.seed, 'threshold': a.threshold,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'machine': info,
            'brute_s': t_brute, 'brute_calls': sim.calls,
            'brute_peak_bytes': m_brute, 'brute_pairs': brute_count,
        }
        # Save the brute result before LSH: completed work survives interruption.
        prior['runs'].append(row)
        save(path, prior)
        print(f'  brute {t_brute:.2f}s  {sim.calls:,} comparisons', flush=True)
        sim2 = bench.Counter()
        found, t_lsh, m_lsh = timed(YourFinder(a.threshold).find, docs, sim2)
        row.update({'lsh_s': t_lsh, 'lsh_calls': sim2.calls,
                    'lsh_peak_bytes': m_lsh, 'lsh_pairs': len(found)})
        del found
        save(path, prior)
        print(f'  lsh   {t_lsh:.2f}s  {sim2.calls:,} comparisons', flush=True)
        print(f'  peak traced memory: brute {m_brute / 2**20:.2f} MiB; '
              f'lsh {m_lsh / 2**20:.2f} MiB', flush=True)
        if max(t_brute, t_lsh) >= 60:
            print('  At least one method exceeded a minute. Record this size and experience.',
                  flush=True)
        del docs
    print(f'\nSaved {len(prior["runs"])} measurement(s) to {path}')
    print('Next: write out/curve.md and fill Task 2 in observation.md.')
    print('Keep increasing sizes if measurements are still comfortable.')


if __name__ == '__main__':
    main()
