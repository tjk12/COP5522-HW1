#include <iostream>
#include <vector>
#include <chrono>
#include <cstdlib>
#include <string>
#include <cstring>
#include <immintrin.h> // Required for AVX2

using namespace std;

// --- Helper Functions (copied from Mv.cpp for identical output) ---
double microtime() {
    auto now = chrono::high_resolution_clock::now();
    auto duration = now.time_since_epoch();
    return chrono::duration_cast<chrono::microseconds>(duration).count();
}

double get_microtime_resolution() {
    return 1.0; // 1 microsecond resolution for chrono::microseconds
}

void print_usage(const char* prog_name) {
    cerr << "Usage: " << prog_name << " [optimization_type] <matrix_size_n>" << endl;
    cerr << "  <optimization_type> is optional and defaults to 'avx2'." << endl;
    cerr << "Optimization types:" << endl;
    cerr << "  baseline    - Standard i-k loop implementation" << endl;
    cerr << "  avx2        - AVX2 SIMD optimization" << endl;
    cerr << "  unroll      - Loop unrolling optimization" << endl;
    cerr << "  interchange - Loop interchange (demonstrates cache effects)" << endl;
}

// --- Optimization Implementations (all use float for consistency with Mv.cpp) ---



// 1. Loop Interchange (k-i loop order)
void Mv_mult_interchanged(int n, const vector<float>& A, const vector<float>& B, vector<float>& C) {
    fill(C.begin(), C.end(), 0.0f);
    for (int k = 0; k < n; ++k) {
        for (int i = 0; i < n; ++i) {
            C[i] += A[i * n + k] * B[k];
        }
    }
}

// 2. Loop Unrolling (unroll factor of 4)
void Mv_mult_unrolled(int n, const vector<float>& A, const vector<float>& B, vector<float>& C) {
    for (int i = 0; i < n; ++i) {
        float sum = 0.0f;
        int k = 0;
        for (; k <= n - 4; k += 4) {
            sum += A[i * n + k] * B[k];
            sum += A[i * n + k + 1] * B[k + 1];
            sum += A[i * n + k + 2] * B[k + 2];
            sum += A[i * n + k + 3] * B[k + 3];
        }
        // Handle remainder
        for (; k < n; ++k) {
            sum += A[i * n + k] * B[k];
        }
        C[i] = sum;
    }
}

// 3. AVX2 SIMD Optimization
void Mv_mult_avx2(int n, const vector<float>& A, const vector<float>& B, vector<float>& C) {
    for (int i = 0; i < n; ++i) {
        __m256 c_vec = _mm256_setzero_ps();
        int k = 0;
        for (; k <= n - 8; k += 8) {
            __m256 a_vec = _mm256_loadu_ps(&A[i * n + k]);
            __m256 b_vec = _mm256_loadu_ps(&B[k]);
            c_vec = _mm256_fmadd_ps(a_vec, b_vec, c_vec);
        }
        float c_sum_array[8];
        _mm256_storeu_ps(c_sum_array, c_vec);
        float sum = c_sum_array[0] + c_sum_array[1] + c_sum_array[2] + c_sum_array[3] +
                    c_sum_array[4] + c_sum_array[5] + c_sum_array[6] + c_sum_array[7];
        for (; k < n; ++k) {
            sum += A[i * n + k] * B[k];
        }
        C[i] = sum;
    }
}

// --- Main Function ---
int main(int argc, char **argv)
{
    string opt_type;
    int n;

    if (argc == 2) {
        // Default to avx2 if only matrix size is provided
        opt_type = "avx2";
        n = atoi(argv[1]);
    } else if (argc == 3) {
        // User specifies optimization type and matrix size
        opt_type = argv[1];
        n = atoi(argv[2]);
    } else {
        // Incorrect number of arguments
        print_usage(argv[0]);
        return 1;
    }
    
    vector<float> A(n * n), B(n), C(n);

    // Initialize matrices (using Mv.cpp logic for consistency)
    for (int i = 0; i < n; ++i) {
        B[i] = 1.0f / (i + 2.0f); // j is always 0 for a vector
        for (int j = 0; j < n; ++j) {
            A[i * n + j] = 1.0f / (i + j + 2.0f);
        }
    }

    double time1 = microtime();
    
    if (opt_type == "avx2") {
        Mv_mult_avx2(n, A, B, C);
    } else if (opt_type == "unroll") {
        Mv_mult_unrolled(n, A, B, C);
    } else if (opt_type == "interchange") {
        Mv_mult_interchanged(n, A, B, C);
    } else {
        cerr << "Error: Unknown optimization type '" << opt_type << "'" << endl;
        print_usage(argv[0]);
        return 1;
    }
    
    double time2 = microtime();
    double t = time2 - time1;

    // Output in the exact same format as Mv.cpp
    cout << "\nTime = " << t << " us\tTimer Resolution = " << get_microtime_resolution() 
         << " us\tPerformance = " << 2.0 * n * n * 1e-3 / t << " Gflop/s" << endl;
    cout << "C[N/2] = " << static_cast<double>(C[n/2]) << "\n" << endl;

    return 0;
}