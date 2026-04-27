#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <stdint.h>

int main() {
    // Initialize random seed
    srand(time(NULL));
    
    // Generate two large 64-bit random numbers
    uint64_t a = ((uint64_t)rand() << 32) | rand();
    uint64_t b = ((uint64_t)rand() << 32) | rand();
    
    struct timespec start, end;
    
    // Start high-precision internal timer
    clock_gettime(CLOCK_MONOTONIC, &start);
    
    // Task 1: Multiplication of large numbers
    uint64_t result = a * b;
    
    // Stop internal timer
    clock_gettime(CLOCK_MONOTONIC, &end);
    
    // Calculate elapsed time in strictly nanoseconds (ns) using long long to avoid overflow
    long long time_spent_ns = (long long)(end.tv_sec - start.tv_sec) * 1000000000LL + (end.tv_nsec - start.tv_nsec);
    
    // Print result so the compiler doesn't optimize away the calculation
    printf("Result : %llu\n", (unsigned long long)result);
    
    // Print formatted time for Python to extract (in ns)
    printf("C_TIME_NS:%lld\n", time_spent_ns);

    return 0;
}