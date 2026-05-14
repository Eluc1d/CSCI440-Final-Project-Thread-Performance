#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <time.h>

#define NUM_THREADS 4

long long pts_per_thread;
long long counts[NUM_THREADS];

void* run(void *arg) {
    int id = *(int *)arg;
    unsigned int seed = time(NULL) ^ (id * 1234567);
    long long inside = 0;

    for (long long i = 0; i < pts_per_thread; i++) {
        double x = (double)rand_r(&seed) / RAND_MAX;
        double y = (double)rand_r(&seed) / RAND_MAX;
        if (x*x + y*y <= 1.0)
            inside++;
    }

    counts[id] = inside;
    return NULL;
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Usage: %s <num_points>\n", argv[0]);
        return 1;
    }

    long long total = atoll(argv[1]);
    pts_per_thread = total / NUM_THREADS;

    pthread_t threads[NUM_THREADS];
    int ids[NUM_THREADS];

    struct timespec start, end;
    clock_gettime(CLOCK_MONOTONIC, &start);

    for (int t = 0; t < NUM_THREADS; t++) {
        ids[t] = t;
        pthread_create(&threads[t], NULL, run, &ids[t]);
    }
    for (int t = 0; t < NUM_THREADS; t++)
        pthread_join(threads[t], NULL);

    clock_gettime(CLOCK_MONOTONIC, &end);

    long long inside = 0;
    for (int t = 0; t < NUM_THREADS; t++)
        inside += counts[t];

    // just to sanity check the estimate looks right
    fprintf(stderr, "pi ~ %.5f\n", 4.0 * inside / total);

    double elapsed = (end.tv_sec - start.tv_sec) + (end.tv_nsec - start.tv_nsec) / 1e9;
    printf("%.6f\n", elapsed);
    return 0;
}
