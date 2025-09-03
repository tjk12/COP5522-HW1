# Makefile for HW1 Optimization Assignment

# ---------------------------------
#      COMPILER CONFIGURATION
# ---------------------------------
# Use g++ as the C++ compiler
CXX = g++
# Common flags: C++17 standard, high optimization, show all warnings
COMMON_FLAGS = -std=c++17 -O3 -Wall
# Flags specific to the optimized version to enable AVX2, etc.
OPTIMIZED_FLAGS = -march=native

# ---------------------------------
#         FILE DEFINITIONS
# ---------------------------------
# Required final executable
HW1_TARGET = hw1

# All executables for benchmarking
TARGETS = baseline avx2 unroll interchange

# Source files
SRC_avx2 = avx2.cpp
SRC_baseline = Mv.cpp
SRC_unroll = unroll.cpp
SRC_interchange = interchange.cpp

# ---------------------------------
#           BUILD RULES
# ---------------------------------
.PHONY: all clean

# 'make all' or just 'make' will build all executables and the final 'hw1'
all: $(HW1_TARGET) $(TARGETS)

# Rule to build the final 'hw1' executable from the best optimization (avx2)
$(HW1_TARGET): $(SRC_avx2)
	$(CXX) $(COMMON_FLAGS) $(OPTIMIZED_FLAGS) -o $(HW1_TARGET) $(SRC_avx2)

# Generic rule to build each benchmark executable from its source
baseline: $(SRC_baseline)
	$(CXX) $(COMMON_FLAGS) -o $@ $<

avx2: $(SRC_avx2)
	$(CXX) $(COMMON_FLAGS) $(OPTIMIZED_FLAGS) -o $@ $<

unroll: $(SRC_unroll)
	$(CXX) $(COMMON_FLAGS) $(OPTIMIZED_FLAGS) -o $@ $<

interchange: $(SRC_interchange)
	$(CXX) $(COMMON_FLAGS) -o $@ $<


# ---------------------------------
#            CLEANUP
# ---------------------------------
# 'make clean' removes all generated files
clean:
	@echo "Cleaning up generated files..."
	rm -f $(HW1_TARGET) $(TARGETS) *.o

