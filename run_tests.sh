#!/bin/bash

# number of times to run each test
RUNS=30
OUTPUT="results.csv"

# Matrix sizes bumped up so runtimes are long enough to produce
# meaningful signal (especially for C/Rust). 500x500 was finishing
# in low milliseconds, making MoE explode relative to mean.
MATRIX_SIZES="300 600 1000"

# Monte Carlo: low end raised slightly so C/Rust aren't done in <1ms
MONTE_SIZES="5000000 10000000 50000000"

# Merge sort sizes are well-spaced already; kept as-is
SORT_SIZES="100000 500000 1000000"

echo "language,algorithm,input_size,run,time_sec" > "$OUTPUT"

# ---------------------------------------------------------------------------
# run_test <lang> <algo> <cmd_prefix> <size>
#   Runs the command RUNS times, validates output, and appends to CSV.
#   Stderr is suppressed (pi sanity checks, etc.) but a missing or
#   non-numeric result triggers a warning so bad runs don't corrupt the CSV.
# ---------------------------------------------------------------------------
run_test() {
    local lang=$1
    local algo=$2
    local cmd=$3
    local size=$4
    local failed=0

    for i in $(seq 1 $RUNS); do
        result=$($cmd "$size" 2>/dev/null)

        # Guard: skip and warn if result is empty or not a number
        if [ -z "$result" ]; then
            echo "WARNING: empty result for $lang $algo size=$size run=$i" >&2
            failed=$((failed + 1))
            continue
        fi
        if ! echo "$result" | grep -qE '^[0-9]+(\.[0-9]+)?$'; then
            echo "WARNING: non-numeric result '$result' for $lang $algo size=$size run=$i" >&2
            failed=$((failed + 1))
            continue
        fi

        echo "$lang,$algo,$size,$i,$result" >> "$OUTPUT"
    done

    if [ "$failed" -gt 0 ]; then
        echo "  [$lang $algo size=$size] $failed/$RUNS runs failed or produced bad output" >&2
    fi
}

# ---------------------------------------------------------------------------
# C benchmarks
# ---------------------------------------------------------------------------
echo "running C benchmarks..."

for s in $MATRIX_SIZES; do
    echo "  matrix_mult size=$s"
    run_test "C" "matrix_mult" "./c/matrix_mult" "$s"
done

for s in $MONTE_SIZES; do
    echo "  monte_carlo pts=$s"
    run_test "C" "monte_carlo" "./c/monte_carlo" "$s"
done

for s in $SORT_SIZES; do
    echo "  merge_sort size=$s"
    run_test "C" "merge_sort" "./c/merge_sort" "$s"
done

# ---------------------------------------------------------------------------
# Python benchmarks (uses multiprocessing — separate processes, not threads;
# this is documented in the paper as a noted experimental difference vs C/Rust)
# ---------------------------------------------------------------------------
echo "running Python benchmarks..."

for s in $MATRIX_SIZES; do
    echo "  matrix_mult size=$s"
    run_test "Python" "matrix_mult" "python3 python/matrix_mult.py" "$s"
done

for s in $MONTE_SIZES; do
    echo "  monte_carlo pts=$s"
    run_test "Python" "monte_carlo" "python3 python/monte_carlo.py" "$s"
done

for s in $SORT_SIZES; do
    echo "  merge_sort size=$s"
    run_test "Python" "merge_sort" "python3 python/merge_sort.py" "$s"
done

# ---------------------------------------------------------------------------
# Rust benchmarks
# ---------------------------------------------------------------------------
echo "running Rust benchmarks..."

for s in $MATRIX_SIZES; do
    echo "  matrix_mult size=$s"
    run_test "Rust" "matrix_mult" "./rust/matrix_mult/target/release/matrix_mult" "$s"
done

for s in $MONTE_SIZES; do
    echo "  monte_carlo pts=$s"
    run_test "Rust" "monte_carlo" "./rust/monte_carlo/target/release/monte_carlo" "$s"
done

for s in $SORT_SIZES; do
    echo "  merge_sort size=$s"
    run_test "Rust" "merge_sort" "./rust/merge_sort/target/release/merge_sort" "$s"
done

echo ""
echo "done. results saved to $OUTPUT"

# Quick check: how many rows landed in the CSV (excluding header)
total_rows=$(tail -n +2 "$OUTPUT" | wc -l)
expected=$((RUNS * 3 * 3 * 3))   # 3 langs * 3 algos * 3 sizes
echo "rows written: $total_rows (expected ~$expected if no failures)"
