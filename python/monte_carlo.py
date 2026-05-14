import sys
import time
import random
from multiprocessing import Pool

NUM_PROCESSES = 4

def count_inside(n):
    inside = 0
    for _ in range(n):
        x = random.random()
        y = random.random()
        if x*x + y*y <= 1.0:
            inside += 1
    return inside

def main():
    if len(sys.argv) < 2:
        print("Usage: python monte_carlo.py <num_points>")
        sys.exit(1)

    total = int(sys.argv[1])
    per_proc = total // NUM_PROCESSES

    t_start = time.perf_counter()

    with Pool(NUM_PROCESSES) as pool:
        results = pool.map(count_inside, [per_proc] * NUM_PROCESSES)

    t_end = time.perf_counter()

    inside = sum(results)
    pi = 4.0 * inside / total
    # sanity check
    print(f"pi ~ {pi:.5f}", file=sys.stderr)
    print(f"{t_end - t_start:.6f}")

if __name__ == "__main__":
    main()
