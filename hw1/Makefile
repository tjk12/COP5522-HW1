# Makefile for Matrix-Vector Multiplication Assignment

# ---------------------------------
#      COMPILER CONFIGURATION
# ---------------------------------
# Use g++ as the C++ compiler
CXX = g++
# Common flags: C++17 standard, high optimization, show all warnings
COMMON_FLAGS = -std=c++17 -O3 -Wall
# Flags specific to the optimized version to enable AVX2, FMA, etc.
# -march=native enables all instruction sets supported by the local machine.
# -mavx2 and -mfma are added for explicit compatibility.
OPTIMIZED_FLAGS = -march=native -mavx2 -mfma

# ---------------------------------
#         FILE DEFINITIONS
# ---------------------------------
# Main executables
BASELINE_TARGET = Mv
OPTIMIZED_TARGET = hw1

# All executables
TARGETS = $(BASELINE_TARGET) $(OPTIMIZED_TARGET)

# Source files
SRC_BASELINE = Mv.cpp
SRC_OPTIMIZED = hw1.cpp

# ---------------------------------
#           BUILD RULES
# ---------------------------------
.PHONY: all clean test

# 'make all' or just 'make' will build both executables
all: $(TARGETS)

# Build baseline Mv executable
$(BASELINE_TARGET): $(SRC_BASELINE)
	$(CXX) $(COMMON_FLAGS) -o $@ $<
	@echo "Baseline executable built: ./$(BASELINE_TARGET) <matrix_size>"

# Build optimized hw1 executable with optimization flags
$(OPTIMIZED_TARGET): $(SRC_OPTIMIZED)
	$(CXX) $(COMMON_FLAGS) $(OPTIMIZED_FLAGS) -o $@ $<
	@echo "Optimized executable built: ./$(OPTIMIZED_TARGET) [opt_type] <matrix_size>"

# ---------------------------------
#            TESTING
# ---------------------------------
test: all
	@echo "========================================="
	@echo "Testing baseline implementation (Mv)..."
	@echo "========================================="
	./$(BASELINE_TARGET) 256
	@echo ""
	@echo "========================================="
	@echo "Testing optimized implementation (hw1 default)..."
	@echo "========================================="
	./$(OPTIMIZED_TARGET) 256
	@echo ""
	@echo "Comparison complete!"

# ---------------------------------
#            CLEANUP
# ---------------------------------
# 'make clean' removes all generated files
clean:
	@echo "Cleaning up generated files..."
	rm -f $(TARGETS) *.o

# ---------------------------------
#              HELP
# ---------------------------------
help:
	@echo "Available targets:"
	@echo "  all        - Build both Mv and hw1 executables"
	@echo "  test       - Run tests with n=256 for both executables"
	@echo "  clean      - Remove all generated files"
	@echo "  help       - Show this help message"
