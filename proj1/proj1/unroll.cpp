// unroll.cpp - Optimized with manual loop unrolling
#include <iostream>
#include <vector>
#include <chrono>
#include <cstdlib>

void Mv_mult_unrolled(int n, const std::vector<double>& A, const std::vector<double>& b, std::vector<double>& c) {
    for (int i = 0; i < n; ++i) {
        double sum = 0.0;
        int k = 0;
        
        // Unroll the loop by a factor of 8
        for (; k <= n - 8; k += 8) {
            sum += A[i * n + k]     * b[k]     +
                   A[i * n + k + 1] * b[k + 1] +
                   A[i * n + k + 2] * b[k + 2] +
                   A[i * n + k + 3] * b[k + 3] +
                   A[i * n + k + 4] * b[k + 4] +
                   A[i * n + k + 5] * b[k + 5] +
                   A[i * n + k + 6] * b[k + 6] +
                   A[i * n + k + 7] * b[k + 7];
        }

        // Handle the remainder
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
    for (int i = 0; i < n; ++i) {
        b[i] = 1.0 / (i + 1.0);
        for (int j = 0; j < n; ++j) {
            A[i * n + j] = 1.0 / (i + j + 2.0);
        }
    }
    auto start = std::chrono::high_resolution_clock::now();
    Mv_mult_unrolled(n, A, b, c);
    auto end = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> diff = end - start;
    std::cout << "n = " << n << std::endl;
    std::cout << "Execution time: " << diff.count() << " seconds" << std::endl;
    double sum_c = 0.0;
    for(int i = 0; i < n; ++i) sum_c += c[i];
    std::cout << "Checksum (sum of c elements): " << sum_c << std::endl;
    return 0;
}
