#!/bin/bash

# number of times to run each test
RUNS=30
OUTPUT="results.csv"

# test sizes for each algorithm
MATRIX_SIZES="100 300 500"
MONTE_SIZES="1000000 5000000 10000000"
SORT_SIZES="100000 500000 1000000"

echo "language,algorithm,input_size,run,time_sec" > $OUTPUT

run_test() {
    local lang=$1
    local algo=$2
    local cmd=$3
    local size=$4

    for i in $(seq 1 $RUNS); do
        result=$($cmd $size 2>/dev/null)
        echo "$lang,$algo,$size,$i,$result" >> $OUTPUT
    done
}

echo "running C benchmarks..."

for s in $MATRIX_SIZES; do
    run_test "C" "matrix_mult" "./c/matrix_mult" $s
done

for s in $MONTE_SIZES; do
    run_test "C" "monte_carlo" "./c/monte_carlo" $s
done

for s in $SORT_SIZES; do
    run_test "C" "merge_sort" "./c/merge_sort" $s
done

echo "running Python benchmarks..."

for s in $MATRIX_SIZES; do
    run_test "Python" "matrix_mult" "python3 python/matrix_mult.py" $s
done

for s in $MONTE_SIZES; do
    run_test "Python" "monte_carlo" "python3 python/monte_carlo.py" $s
done

for s in $SORT_SIZES; do
    run_test "Python" "merge_sort" "python3 python/merge_sort.py" $s
done

echo "running Rust benchmarks..."

for s in $MATRIX_SIZES; do
    run_test "Rust" "matrix_mult" "./rust/matrix_mult/target/release/matrix_mult" $s
done

for s in $MONTE_SIZES; do
    run_test "Rust" "monte_carlo" "./rust/monte_carlo/target/release/monte_carlo" $s
done

for s in $SORT_SIZES; do
    run_test "Rust" "merge_sort" "./rust/merge_sort/target/release/merge_sort" $s
done

echo "done. results saved to $OUTPUT"
