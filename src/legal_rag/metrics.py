"""Measure source-span coverage without double-counting overlapping retrievals."""


def evidence_coverage(gold: tuple[int, int], spans: list[tuple[int, int]]) -> float:
    """Return the fraction of a nonempty gold span covered by retrieved spans."""
    start, end = gold
    if start < 0 or end <= start:
        raise ValueError("Gold span must have nonnegative start and positive length.")
    clipped = []
    for left, right in spans:
        if left < 0 or right < left:
            raise ValueError("Retrieved spans must have valid nonnegative boundaries.")
        left, right = max(left, start), min(right, end)
        if left < right:
            clipped.append((left, right))
    covered = 0
    last_end = start
    for left, right in sorted(clipped):
        covered += max(0, right - max(left, last_end))
        last_end = max(last_end, right)
    return covered / (end - start)
