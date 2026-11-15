"""Smooth a noisy daily series with a trailing moving average.

Used as a sample document for token counting: a mix of code,
docstrings, comments, and indentation.
"""

from collections import deque


def moving_average(values, window=7):
    """Return the trailing mean of `values` over `window` points.

    The first `window - 1` outputs average over fewer points, so the
    result has the same length as the input.
    """
    if window < 1:
        raise ValueError("window must be at least 1")

    buffer = deque(maxlen=window)
    total = 0.0
    smoothed = []
    for x in values:
        # Drop the oldest value from the running total once the buffer is full.
        if len(buffer) == window:
            total -= buffer[0]
        buffer.append(x)
        total += x
        smoothed.append(total / len(buffer))
    return smoothed


if __name__ == "__main__":
    daily_sales = [120, 135, 98, 160, 142, 155, 171, 133, 149, 188]
    for day, (raw, avg) in enumerate(zip(daily_sales, moving_average(daily_sales)), 1):
        print(f"day {day:2d}: raw={raw:4d}  7-day avg={avg:7.2f}")
