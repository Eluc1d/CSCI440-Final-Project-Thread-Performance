#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <time.h>

#define NUM_THREADS 4

int size;
double **A, **B, **C;

typedef struct {
    int start_row;
    int end_row;
} ThreadArgs;

void* multiply(void *arg) {
    ThreadArgs *t = (ThreadArgs *)arg;
    for (int i = t->start_row; i < t->end_row; i++) {
        for (int j = 0; j < size; j++) {
            C[i][j] = 0.0;
            for (int k = 0; k < size; k++)
                C[i][j] += A[i][k] * B[k][j];
        }
    }
    return NULL;
}

double** allocMatrix(int n) {
    double **mat = malloc(n * sizeof(double *));
    for (int i = 0; i < n; i++)
        mat[i] = malloc(n * sizeof(double));
    return mat;
}

void freeMatrix(double **mat, int n) {
    for (int i = 0; i < n; i++)
        free(mat[i]);
    free(mat);
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Usage: %s <matrix_size>\n", argv[0]);
        return 1;
    }

    size = atoi(argv[1]);

    A = allocMatrix(size);
    B = allocMatrix(size);
    C = allocMatrix(size);

    for (int i = 0; i < size; i++) {
        for (int j = 0; j < size; j++) {
            A[i][j] = (double)(i + j + 1);
            B[i][j] = (double)(i - j + 1);
        }
    }

    pthread_t threads[NUM_THREADS];
    ThreadArgs args[NUM_THREADS];
    int rows_per_thread = size / NUM_THREADS;

    struct timespec start, end;
    clock_gettime(CLOCK_MONOTONIC, &start);

    for (int t = 0; t < NUM_THREADS; t++) {
        args[t].start_row = t * rows_per_thread;
        // last thread picks up any leftover rows
        args[t].end_row = (t == NUM_THREADS - 1) ? size : args[t].start_row + rows_per_thread;
        pthread_create(&threads[t], NULL, multiply, &args[t]);
    }

    for (int t = 0; t < NUM_THREADS; t++)
        pthread_join(threads[t], NULL);

    clock_gettime(CLOCK_MONOTONIC, &end);

    double elapsed = (end.tv_sec - start.tv_sec) + (end.tv_nsec - start.tv_nsec) / 1e9;
    printf("%.6f\n", elapsed);

    freeMatrix(A, size);
    freeMatrix(B, size);
    freeMatrix(C, size);
    return 0;
}
