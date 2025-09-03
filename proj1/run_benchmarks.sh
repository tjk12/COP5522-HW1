#!/bin/bash

# This script compiles and runs C++ benchmarks with a self-contained configuration
# and outputs the results to results.json. It is designed for Linux compatibility.

# --- Dependency Check ---
if ! command -v bc &> /dev/null; then
    echo "Error: 'bc' (a command-line calculator) is not installed." >&2
    echo "Please install it to continue. It is typically installed by default." >&2
    exit 1
fi

# --- Internal Configuration ---
MATRIX_SIZES=(256 512 1024 2048 4048)
RUNS=3
OPTIMIZER_KEYS=("baseline" "avx2" "unroll" "interchange")
OPTIMIZER_EXES=("baseline" "avx2" "unroll" "interchange")
RESULTS_FILE="results.json"

# --- Main Script ---

echo "--- Starting Benchmark Process ---"

# 1. Compile all C++ code using the makefile
echo "Compiling C++ executables via make..."
make all
if [ $? -ne 0 ]; then
    echo "!!! Compilation Failed. Aborting. !!!"
    exit 1
fi
echo "Compilation successful."

# Initialize JSON construction
JSON_CONTENT=""

# 2. Run benchmarks
echo -e "\n--- Running Benchmarks (best of $RUNS runs) ---"

for n in "${MATRIX_SIZES[@]}"; do
    echo "Testing size n = $n..."
    RESULT_ROW="{\"n\": $n"
    
    for i in "${!OPTIMIZER_KEYS[@]}"; do
        opt_key="${OPTIMIZER_KEYS[$i]}"
        EXE_NAME="${OPTIMIZER_EXES[$i]}"
        
        echo -n "  - Benchmarking $opt_key..."
        
        BEST_TIME="99999" 
        
        for ((j=1; j<=RUNS; j++)); do
            # Capture both stdout and stderr to diagnose C++ execution issues.
            PROGRAM_OUTPUT=$(./$EXE_NAME $n 2>&1)
            CURRENT_TIME=$(echo "$PROGRAM_OUTPUT" | grep "Execution time:" | awk '{print $3}')
            
            # *** MODIFIED PART ***
            # The regex now correctly parses both decimal and scientific notation (e.g., 1.23e-05)
            if [[ "$CURRENT_TIME" =~ ^[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?$ ]]; then
                if (( $(echo "$CURRENT_TIME < $BEST_TIME" | bc -l) )); then
                    BEST_TIME=$CURRENT_TIME
                fi
            else
                # If a run fails, print the captured error message from the C++ program.
                # This helps diagnose issues like "Illegal instruction".
                # We remove newlines to keep the output clean.
                ERROR_MSG=$(echo "$PROGRAM_OUTPUT" | tr -d '\n')
                echo -n " (fail: $ERROR_MSG)"
            fi
        done
        
        echo " best: ${BEST_TIME}s"
        RESULT_ROW="${RESULT_ROW}, \"${opt_key}_time\": ${BEST_TIME}"
    done
    
    RESULT_ROW="${RESULT_ROW}}"

    # Build the JSON array content in a variable for robustness
    if [ -z "$JSON_CONTENT" ]; then
        JSON_CONTENT="$RESULT_ROW"
    else
        JSON_CONTENT="$JSON_CONTENT, $RESULT_ROW"
    fi
done

# Write the complete JSON content to the file in one go. This is safer than sed.
echo "[$JSON_CONTENT]" > $RESULTS_FILE

# 3. Clean up executables
echo -e "\n--- Cleaning up executables ---"
make clean
if [ $? -ne 0 ]; then
    echo "Warning: 'make clean' failed."
fi

echo -e "\nBenchmark process complete. Results saved to $RESULTS_FILE"

