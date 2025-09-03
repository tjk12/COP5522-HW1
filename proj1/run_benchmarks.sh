#!/bin/bash

# This script compiles and runs C++ benchmarks with a self-contained configuration
# and outputs the results to results.json.

# --- Dependency Check ---
# 'jq' is no longer needed. We only check for 'bc' for floating point math.
if ! command -v bc &> /dev/null; then
    echo "Error: 'bc' (a command-line calculator) is not installed." >&2
    echo "Please install it to continue. It is typically installed by default." >&2
    exit 1
fi

# --- Internal Configuration ---
# All settings previously in config.json are now defined here.
MATRIX_SIZES=(256 512 1024 2048 4096)
RUNS=3

# Define optimizers using parallel arrays.
# The keys (names) must correspond to the executables.
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

# Initialize JSON output
echo "[]" > $RESULTS_FILE

# 2. Run benchmarks
echo -e "\n--- Running Benchmarks (best of $RUNS runs) ---"

for n in "${MATRIX_SIZES[@]}"; do
    echo "Testing size n = $n..."
    # Start building the JSON object for this row as a string
    RESULT_ROW="{\"n\": $n"
    
    # Iterate through the optimizers using their indices
    for i in "${!OPTIMIZER_KEYS[@]}"; do
        opt_key="${OPTIMIZER_KEYS[$i]}"
        EXE_NAME="${OPTIMIZER_EXES[$i]}"
        
        echo -n "  - Benchmarking $opt_key..."
        
        BEST_TIME="1e9" # Start with a very large number
        
        for ((j=1; j<=RUNS; j++)); do
            # Extract time from C++ program output
            CURRENT_TIME=$(./$EXE_NAME $n | grep "Execution time:" | awk '{print $3}')
            
            # Bash floating point comparison using bc
            if (( $(echo "$CURRENT_TIME < $BEST_TIME" | bc -l) )); then
                BEST_TIME=$CURRENT_TIME
            fi
        done
        
        echo " best: ${BEST_TIME}s"
        # Append the key-value pair to our JSON string
        RESULT_ROW="${RESULT_ROW}, \"${opt_key}_time\": ${BEST_TIME}"
    done
    
    # Close the JSON object
    RESULT_ROW="${RESULT_ROW}}"

    # To avoid needing jq to merge JSON, we'll build the file string manually.
    # This is less robust than jq but removes the dependency.
    if [ $(wc -c <"$RESULTS_FILE") -le 3 ]; then # If file is empty or just "[]"
        sed -i '' "s/\[\]/\[$RESULT_ROW\]/" "$RESULTS_FILE"
    else # Append to the existing array
        sed -i '' "s/\]/, $RESULT_ROW\]/" "$RESULTS_FILE"
    fi
done

# 3. Clean up executables
echo -e "\n--- Cleaning up executables ---"
make clean
if [ $? -ne 0 ]; then
    echo "Warning: 'make clean' failed."
fi

echo -e "\nBenchmark process complete. Results saved to $RESULTS_FILE"

