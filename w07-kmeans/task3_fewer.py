#!/usr/bin/env python3
"""Week 7 · Task 3 — The same clustering, with far fewer distances.

Textbook §7.3, and §7.1.3 for why distance is the expensive part.

`NaiveKMeans` does what the definition says: every iteration, compare every
point with every centroid. That is n x k distance computations per pass, and on
a real dataset the distance computation is almost the entire cost.

Most of that work is wasted. After the first couple of iterations, most points
do not change cluster, and most centroids barely move. The triangle inequality
lets you prove a point cannot have changed cluster **without measuring it**.

    python3 bench.py
    python3 bench.py --yours

Correctness first: your final SSE must match the baseline's. Fewer distances
with a worse clustering is not an improvement, it is a different algorithm.
"""


class NaiveKMeans:
    """Every point against every centroid, every iteration."""

    def __init__(self, k, max_iter=50):
        self.k, self.max_iter = k, max_iter

    def run(self, points, initial_centroids, distance):
        centroids = list(initial_centroids)
        labels = [None] * len(points)
        for self.iterations in range(1, self.max_iter + 1):
            changed = False
            for i, p in enumerate(points):
                best, bi = None, 0
                for j, c in enumerate(centroids):
                    d = distance(p, c)
                    if best is None or d < best - 1e-12:
                        best, bi = d, j
                if labels[i] != bi:
                    labels[i] = bi
                    changed = True
            centroids = _means(points, labels, self.k, centroids)
            if not changed:
                break
        return labels, centroids


def _means(points, labels, k, previous):
    out = []
    for j in range(k):
        group = [p for p, l in zip(points, labels) if l == j]
        if group:
            out.append(tuple(sum(v) / len(group) for v in zip(*group)))
        else:
            out.append(previous[j])
    return out


class YourKMeans:
    """Your k-means.

        __init__(k, max_iter=50)
        run(points, initial_centroids, distance) -> (labels, centroids)

    Same starting centroids, same `distance` function - which is counted. That
    counter is your score.

    The idea, from §7.3 and the triangle inequality:

        if a point is much closer to its current centroid than that centroid
        moved, and than any other centroid could have come, then it cannot have
        changed cluster, and you do not have to measure anything

    Keeping enough bookkeeping to make that test cheap, without keeping so much
    that the bookkeeping costs more than the distances, is the task.

    You may call `distance` on two centroids, and those calls are counted too -
    which is the correct accounting, since that is real work. There are k of
    them and n points, and k is much smaller than n. That asymmetry is the
    whole opening.

    Hamerly's version: per point, one upper bound `upper[i]` on the distance to
    its own centroid and one lower bound `lower[i]` on the distance to every
    other centroid. Two extra floats per point, plus k numbers per iteration.
    """

    def __init__(self, k, max_iter=50):
        self.k, self.max_iter = k, max_iter

    def _nearest_two(self, p, centroids, distance):
        """Full scan, same tie rule as NaiveKMeans. Returns (label, d1, d2)."""
        best, bi, second = None, 0, float("inf")
        for j, c in enumerate(centroids):
            d = distance(p, c)
            if best is None or d < best - 1e-12:
                if best is not None:
                    second = min(second, best)
                best, bi = d, j
            else:
                second = min(second, d)
        return bi, best, second

    def run(self, points, initial_centroids, distance):
        k = self.k
        centroids = list(initial_centroids)
        labels = [None] * len(points)
        upper = [0.0] * len(points)
        lower = [0.0] * len(points)

        for self.iterations in range(1, self.max_iter + 1):
            changed = False
            if self.iterations == 1:
                # nothing to prune with yet: one full scan sets both bounds
                for i, p in enumerate(points):
                    labels[i], upper[i], lower[i] = self._nearest_two(p, centroids, distance)
                changed = True
            else:
                # half the distance to the nearest other centroid: a point closer
                # than this to its own centroid cannot be closer to any other
                half = [float("inf")] * k
                for a in range(k):
                    for b in range(a + 1, k):
                        d = distance(centroids[a], centroids[b]) / 2
                        half[a] = min(half[a], d)
                        half[b] = min(half[b], d)
                for i, p in enumerate(points):
                    a = labels[i]
                    bound = max(half[a], lower[i])
                    if upper[i] <= bound:
                        continue
                    upper[i] = distance(p, centroids[a])  # tighten, then test again
                    if upper[i] <= bound:
                        continue
                    new, upper[i], lower[i] = self._nearest_two(p, centroids, distance)
                    if new != a:
                        labels[i] = new
                        changed = True

            moved = _means(points, labels, k, centroids)
            if not changed:
                centroids = moved
                break
            # each centroid's own move: k distances, used to loosen the bounds
            shift = [distance(c, m) for c, m in zip(centroids, moved)]
            centroids = moved
            top = max(range(k), key=shift.__getitem__)
            runner_up = max((shift[j] for j in range(k) if j != top), default=0.0)
            for i in range(len(points)):
                a = labels[i]
                upper[i] += shift[a]
                lower[i] -= runner_up if a == top else shift[top]
        return labels, centroids
