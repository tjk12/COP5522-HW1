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
# Define benchmarks as "key:command_prefix". The matrix size will be appended.
BENCHMARKS=(
    "baseline_Mv:./Mv"
    "hw1_interchange:./hw1 interchange"
    "hw1_unroll:./hw1 unroll"
    "hw1_avx2:./hw1 avx2"
)
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
    
    for benchmark in "${BENCHMARKS[@]}"; do
        # Split the benchmark string into a key and the command to run
        IFS=':' read -r opt_key CMD_PREFIX <<< "$benchmark"
        
        # Construct the full command with the matrix size
        FULL_CMD="$CMD_PREFIX $n"
        
        echo -n "  - Benchmarking $opt_key ($FULL_CMD)..."
        
        BEST_TIME="99999" 
        
        for ((j=1; j<=RUNS; j++)); do
            # Capture both stdout and stderr to diagnose issues
            PROGRAM_OUTPUT=$(eval $FULL_CMD 2>&1)
            
            CURRENT_TIME=""

            TIME_US=$(echo "$PROGRAM_OUTPUT" | grep "Time =" | awk '{print $3}')

            if [[ "$TIME_US" =~ ^[0-9]*\.?[0-9]+$ ]]; then
                # Convert microseconds to seconds using bc for floating point math
                CURRENT_TIME=$(echo "scale=10; $TIME_US / 1000000" | bc -l)
            else
                CURRENT_TIME="" # Ensure CURRENT_TIME is empty on failure
            fi

            # Check if we successfully parsed a valid time
            if [[ "$CURRENT_TIME" =~ ^[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?$ ]]; then
                if (( $(echo "$CURRENT_TIME < $BEST_TIME" | bc -l) )); then
                    BEST_TIME=$CURRENT_TIME
                fi
            else
                # If a run fails, print the captured error message
                ERROR_MSG=$(echo "$PROGRAM_OUTPUT" | tr -d '\n')
                echo -n " (fail: $ERROR_MSG)"
            fi
        done
        
        # --- FIX: Ensure BEST_TIME has a leading zero for valid JSON ---
        if [[ $BEST_TIME == .* ]]; then
            BEST_TIME="0$BEST_TIME"
        fi

        echo " best: ${BEST_TIME}s"
        RESULT_ROW="${RESULT_ROW}, \"${opt_key}_time\": ${BEST_TIME}"
    done
    
    RESULT_ROW="${RESULT_ROW}}"

    # Build the JSON array content in a variable
    if [ -z "$JSON_CONTENT" ]; then
        JSON_CONTENT="$RESULT_ROW"
    else
        JSON_CONTENT="$JSON_CONTENT, $RESULT_ROW"
    fi
done

# Write the complete JSON content to the file
echo "[$JSON_CONTENT]" > $RESULTS_FILE

# 3. Clean up executables
echo -e "\n--- Cleaning up executables ---"
make clean
if [ $? -ne 0 ]; then
    echo "Warning: 'make clean' failed."
fi

echo -e "\nBenchmark process complete. Results saved to $RESULTS_FILE"