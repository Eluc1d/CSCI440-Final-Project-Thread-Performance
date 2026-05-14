import sys
import time
import random
from multiprocessing import Pool

NUM_PROCESSES = 4

def merge(left, right):
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result

def merge_sort(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    return merge(merge_sort(arr[:mid]), merge_sort(arr[mid:]))

def main():
    if len(sys.argv) < 2:
        print("Usage: python merge_sort.py <array_size>")
        sys.exit(1)

    n = int(sys.argv[1])
    random.seed(42)
    arr = [random.randint(0, 1000000) for _ in range(n)]

    chunk = n // NUM_PROCESSES
    chunks = []
    for t in range(NUM_PROCESSES):
        start = t * chunk
        end = n if t == NUM_PROCESSES - 1 else start + chunk
        chunks.append(arr[start:end])

    t_start = time.perf_counter()

    with Pool(NUM_PROCESSES) as pool:
        sorted_chunks = pool.map(merge_sort, chunks)

    # merge sorted chunks back down to one list
    while len(sorted_chunks) > 1:
        merged = []
        for i in range(0, len(sorted_chunks), 2):
            if i + 1 < len(sorted_chunks):
                merged.append(merge(sorted_chunks[i], sorted_chunks[i+1]))
            else:
                merged.append(sorted_chunks[i])
        sorted_chunks = merged

    t_end = time.perf_counter()
    print(f"{t_end - t_start:.6f}")

if __name__ == "__main__":
    main()
