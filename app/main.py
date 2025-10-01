import os
import math
import time
from datetime import datetime, timezone

"""
A simple Cloud Run Jobs example that demonstrates:
  - Reading environment variables set on the Job
  - Using Cloud Run Jobs task sharding via CLOUD_RUN_TASK_INDEX and CLOUD_RUN_TASK_COUNT
  - Doing a small compute task (count primes in a range shard)
  - Printing structured logs students can verify in Cloud Logging
"""
def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    r = int(math.isqrt(n))
    for f in range(3, r + 1, 2):
        if n % f == 0:
            return False
    return True

def count_primes(lo: int, hi: int) -> int:
    return sum(1 for x in range(lo, hi + 1) if is_prime(x))

def main():
    # --- Read lab-specific env vars (with defaults) ---
    max_n = int(os.getenv("RANGE_MAX", "10000"))         # inclusive upper bound
    pause = float(os.getenv("PAUSE_SEC", "0"))            # optional artificial delay

    # --- Cloud Run Jobs sharding envs ---
    task_index = int(os.getenv("CLOUD_RUN_TASK_INDEX", "0"))
    task_count = int(os.getenv("CLOUD_RUN_TASK_COUNT", "1"))

    # Compute shard [lo, hi] for this task
    # Split 1..max_n as evenly as possible across task_count shards.
    total = max_n
    base = total // task_count
    rem = total % task_count

    # First 'rem' shards get one extra item
    shard_size = base + (1 if task_index < rem else 0)

    # Start index (1-based range)
    start = task_index * base + min(task_index, rem) + 1
    end = start + shard_size - 1

    t0 = time.time()
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Do the small compute
    prime_cnt = count_primes(start, end)

    if pause > 0:
        time.sleep(pause)

    elapsed = time.time() - t0

    # Print a single-line JSON log, easy to filter in Logs Explorer
    log = {
        "ts": ts,
        "task_index": task_index,
        "task_count": task_count,
        "range_start": start,
        "range_end": end,
        "range_max": max_n,
        "prime_count": prime_cnt,
        "elapsed_sec": round(elapsed, 3),
        "note": "Cloud Run Jobs student lab: shard-wise prime counting",
    }
    print(log, flush=True)

if __name__ == "__main__":
    main()
