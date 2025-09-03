// hw1.cpp - Optimized with AVX2 Intrinsics
#include <iostream>
#include <vector>
#include <chrono>
#include <cstdlib>
#include <immintrin.h> // Required for AVX2

// Optimized function using AVX2
void Mv_mult_optimized(int n, const std::vector<double>& A, const std::vector<double>& b, std::vector<double>& c) {
    for (int i = 0; i < n; ++i) {
        __m256d c_vec = _mm256_setzero_pd(); // Vector register to hold 4 partial sums, initialized to 0.0
        int k = 0;

        // Process 4 elements at a time using AVX2
        // We use loadu (unaligned) as it's more flexible than aligned loads and often just as fast on modern CPUs.
        for (; k <= n - 4; k += 4) {
            __m256d a_vec = _mm256_loadu_pd(&A[i * n + k]); // Load 4 doubles from A
            __m256d b_vec = _mm256_loadu_pd(&b[k]);      // Load 4 doubles from b
            c_vec = _mm256_fmadd_pd(a_vec, b_vec, c_vec); // Fused Multiply-Add: c_vec = (a_vec * b_vec) + c_vec
        }

        // Horizontal sum of the vector register c_vec
        // This collapses the 4 partial sums into a single scalar sum
        double c_sum_array[4];
        _mm256_storeu_pd(c_sum_array, c_vec);
        double sum = c_sum_array[0] + c_sum_array[1] + c_sum_array[2] + c_sum_array[3];

        // Handle the "tail" or remainder for n not divisible by 4
        for (; k < n; ++k) {
            sum += A[i * n + k] * b[k];
        }
        c[i] = sum;
    }
}


int main(int argc, char* argv[]) {
    if (argc != 2) {
        std::cerr << "Usage: " << argv[0] << " <matrix_size_n>" << std::endl;
        return 1;
    }
    int n = std::atoi(argv[1]);
    if (n <= 0) {
        std::cerr << "Matrix size must be a positive integer." << std::endl;
        return 1;
    }

    std::vector<double> A(n * n);
    std::vector<double> b(n);
    std::vector<double> c(n);

    // Initialization (same as baseline)
    for (int i = 0; i < n; ++i) {
        b[i] = 1.0 / (i + 1.0);
        for (int j = 0; j < n; ++j) {
            A[i * n + j] = 1.0 / (i + j + 2.0);
        }
    }

    auto start = std::chrono::high_resolution_clock::now();
    Mv_mult_optimized(n, A, b, c); // Call the optimized function
    auto end = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> diff = end - start;

    std::cout << "n = " << n << std::endl;
    std::cout << "Execution time: " << diff.count() << " seconds" << std::endl;
    double sum_c = 0.0;
    for(int i = 0; i < n; ++i) sum_c += c[i];
    std::cout << "Checksum (sum of c elements): " << sum_c << std::endl;

    return 0;
}
