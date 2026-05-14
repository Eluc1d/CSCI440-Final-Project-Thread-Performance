import sys
import time
from multiprocessing import Pool

NUM_PROCESSES = 4

def multiply_rows(args):
    A, B, start, end, size = args
    result = []
    for i in range(start, end):
        row = []
        for j in range(size):
            total = sum(A[i][k] * B[k][j] for k in range(size))
            row.append(total)
        result.append((i, row))
    return result

def main():
    if len(sys.argv) < 2:
        print("Usage: python matrix_mult.py <matrix_size>")
        sys.exit(1)

    size = int(sys.argv[1])

    A = [[float(i + j + 1) for j in range(size)] for i in range(size)]
    B = [[float(i - j + 1) for j in range(size)] for i in range(size)]
    C = [[0.0] * size for _ in range(size)]

    chunk = size // NUM_PROCESSES
    work = []
    for t in range(NUM_PROCESSES):
        start = t * chunk
        end = size if t == NUM_PROCESSES - 1 else start + chunk
        work.append((A, B, start, end, size))

    t_start = time.perf_counter()

    with Pool(NUM_PROCESSES) as pool:
        results = pool.map(multiply_rows, work)

    t_end = time.perf_counter()

    for chunk_result in results:
        for i, row in chunk_result:
            C[i] = row

    print(f"{t_end - t_start:.6f}")

if __name__ == "__main__":
    main()
