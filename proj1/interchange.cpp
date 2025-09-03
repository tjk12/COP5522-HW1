// interchange.cpp - "Optimized" with loop interchange to demonstrate cache effects
#include <iostream>
#include <vector>
#include <chrono>
#include <cstdlib>

void Mv_mult_interchanged(int n, const std::vector<double>& A, const std::vector<double>& b, std::vector<double>& c) {
    // Initialize c vector to zeros
    for (int i = 0; i < n; ++i) {
        c[i] = 0.0;
    }

    // Swapped loop order (k, then i)
    // This is expected to be SLOWER due to poor spatial locality on matrix A
    for (int k = 0; k < n; ++k) {
        for (int i = 0; i < n; ++i) {
            c[i] += A[i * n + k] * b[k];
        }
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
    Mv_mult_interchanged(n, A, b, c);
    auto end = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> diff = end - start;
    std::cout << "n = " << n << std::endl;
    std::cout << "Execution time: " << diff.count() << " seconds" << std::endl;
    double sum_c = 0.0;
    for(int i = 0; i < n; ++i) sum_c += c[i];
    std::cout << "Checksum (sum of c elements): " << sum_c << std::endl;
    return 0;
}
