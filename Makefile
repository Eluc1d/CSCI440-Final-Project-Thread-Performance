CC = gcc
CFLAGS = -O2 -pthread

all: c rust

c:
	$(CC) $(CFLAGS) -o c/matrix_mult c/matrix_mult.c
	$(CC) $(CFLAGS) -o c/monte_carlo c/monte_carlo.c
	$(CC) $(CFLAGS) -o c/merge_sort c/merge_sort.c

rust:
	cd rust/matrix_mult && cargo build --release
	cd rust/monte_carlo && cargo build --release
	cd rust/merge_sort && cargo build --release

clean:
	rm -f c/matrix_mult c/monte_carlo c/merge_sort
	cd rust/matrix_mult && cargo clean
	cd rust/monte_carlo && cargo clean
	cd rust/merge_sort && cargo clean
