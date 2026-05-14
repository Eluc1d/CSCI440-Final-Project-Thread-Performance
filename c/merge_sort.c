#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <time.h>

#define NUM_THREADS 4

typedef struct {
    int *arr;
    int left;
    int right;
} ThreadArgs;

void merge(int *arr, int l, int m, int r) {
    int n1 = m - l + 1;
    int n2 = r - m;

    int *L = malloc(n1 * sizeof(int));
    int *R = malloc(n2 * sizeof(int));

    for (int i = 0; i < n1; i++) L[i] = arr[l + i];
    for (int i = 0; i < n2; i++) R[i] = arr[m + 1 + i];

    int i = 0, j = 0, k = l;
    while (i < n1 && j < n2)
        arr[k++] = (L[i] <= R[j]) ? L[i++] : R[j++];
    while (i < n1) arr[k++] = L[i++];
    while (j < n2) arr[k++] = R[j++];

    free(L);
    free(R);
}

void mergeSort(int *arr, int l, int r) {
    if (l < r) {
        int m = l + (r - l) / 2;
        mergeSort(arr, l, m);
        mergeSort(arr, m + 1, r);
        merge(arr, l, m, r);
    }
}

void* sortChunk(void *arg) {
    ThreadArgs *a = (ThreadArgs *)arg;
    mergeSort(a->arr, a->left, a->right);
    return NULL;
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Usage: %s <array_size>\n", argv[0]);
        return 1;
    }

    int n = atoi(argv[1]);
    int *arr = malloc(n * sizeof(int));

    srand(42);
    for (int i = 0; i < n; i++)
        arr[i] = rand() % 1000000;

    pthread_t threads[NUM_THREADS];
    ThreadArgs args[NUM_THREADS];
    int chunk = n / NUM_THREADS;

    struct timespec start, end;
    clock_gettime(CLOCK_MONOTONIC, &start);

    for (int t = 0; t < NUM_THREADS; t++) {
        args[t].arr = arr;
        args[t].left = t * chunk;
        args[t].right = (t == NUM_THREADS - 1) ? n - 1 : args[t].left + chunk - 1;
        pthread_create(&threads[t], NULL, sortChunk, &args[t]);
    }
    for (int t = 0; t < NUM_THREADS; t++)
        pthread_join(threads[t], NULL);

    // merge the sorted chunks sequentially
    int step = chunk;
    while (step < n) {
        for (int i = 0; i < n; i += step * 2) {
            int l = i;
            int m = i + step - 1;
            int r = (i + step * 2 - 1 < n - 1) ? i + step * 2 - 1 : n - 1;
            if (m < r)
                merge(arr, l, m, r);
        }
        step *= 2;
    }

    clock_gettime(CLOCK_MONOTONIC, &end);

    double elapsed = (end.tv_sec - start.tv_sec) + (end.tv_nsec - start.tv_nsec) / 1e9;
    printf("%.6f\n", elapsed);

    free(arr);
    return 0;
}
