import subprocess
import os
import matplotlib.pyplot as plt
from fpdf import FPDF
import pandas as pd

# --- Configuration ---
RESULTS_FILENAME = "results.json"
PDF_FILENAME = "hw1.pdf"
LOG_FILENAME = "LOG.txt"
CHART_FILENAME = "performance_chart.png"

# This dictionary helps structure the report. The keys should match the internal column names.
OPTIMIZERS = {
    "baseline": {},
    "avx2": {},
    "unroll": {},
    "interchange": {}
}


def create_submission_archive():
    """Creates a tar file for submission with all required source and report files."""
    print("\n--- Creating Submission Archive ---")
    try:
        dir_name = os.path.basename(os.getcwd())
        archive_name = f"{dir_name}.tar"

        # Updated list of files to include in the tar file
        files_to_archive = [
            "Mv.cpp",
            "hw1.cpp",
            "Makefile",
            "run_benchmarks.sh",
            "hw1.pdf",
            "LOG.txt",
        ]
        
        existing_files = [f for f in files_to_archive if os.path.exists(f)]
        print(f"Archiving the following files: {existing_files}")
        
        command = ["tar", "cvf", archive_name] + existing_files
        subprocess.run(command, check=True, capture_output=True, text=True)
        print(f"Successfully created submission archive: {archive_name}")

    except FileNotFoundError:
        print("Error: 'tar' command not found. Cannot create archive.")
    except subprocess.CalledProcessError as e:
        print(f"!!! Archiving Failed !!!\nError message:\n{e.stderr}")
    except Exception as e:
        print(f"An unexpected error occurred during archiving: {e}")


def generate_performance_chart(df):
    """Creates and saves a performance comparison chart from the DataFrame."""
    plt.style.use('seaborn-v0_8-whitegrid')
    plt.figure(figsize=(12, 7))
    
    for opt_name in OPTIMIZERS.keys():
        if f'{opt_name}_time' in df.columns:
            plt.plot(df['n'], df[f'{opt_name}_time'], 'o-', label=opt_name, lw=2.5, ms=8)
    
    plt.title('Performance Comparison of Optimization Techniques', fontsize=16, fontweight='bold')
    plt.xlabel('Matrix Size (n)', fontsize=12)
    plt.ylabel('Execution Time (seconds, log scale)', fontsize=12)
    plt.xscale('log', base=2); plt.yscale('log')
    plt.legend(fontsize=11)
    plt.xticks(df['n'].astype(int), labels=[str(s) for s in df['n']])
    plt.tick_params(axis='both', which='major', labelsize=10)
    plt.tight_layout()
    plt.savefig(CHART_FILENAME, dpi=150)
    print(f"Chart saved to {CHART_FILENAME}")


class PDF(FPDF):
    """Custom PDF class to handle header and footer."""
    def header(self):
        self.set_font('Arial', 'B', 14); self.cell(0, 10, 'HW1 Performance Report', 0, 1, 'C'); self.ln(5)
    def footer(self):
        self.set_y(-15); self.set_font('Arial', 'I', 8); self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')
    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12); self.cell(0, 10, title, 0, 1, 'L'); self.ln(2)
    def chapter_body(self, text):
        self.set_font('Arial', '', 11); self.multi_cell(0, 5.5, text); self.ln()


def generate_pdf_report(df):
    """Assembles the final PDF report with comprehensive performance analysis."""
    # Calculate analysis data
    analysis_df = calculate_speedups(df)
    
    pdf = PDF()
    pdf.add_page()
    
    pdf.chapter_title('1. Optimization Techniques')
    intro_text = (
        "This report compares several optimization techniques for matrix-vector multiplication against a baseline compiled with g++ -O3. "
        "It is important to note that all optimized versions (interchange, unroll, and AVX2) are contained within the 'hw1' executable, "
        "which is compiled with AVX2 and FMA support (`-march=native -mavx2 -mfma`). This enables the AVX2-specific code to function and may "
        "allow the compiler to perform additional optimizations on the other versions.\n\n"
        "The optimized techniques tested are:\n"
        "1.  AVX2 SIMD: Leverages data parallelism by explicitly using AVX2 intrinsics to process 8 single-precision floats simultaneously.\n"
        "2.  Loop Unrolling: Reduces loop overhead by manually processing 4 elements per inner-loop iteration.\n"
        "3.  Loop Interchange: Swaps the inner and outer loops to demonstrate the negative impact of poor memory access patterns (cache performance)."
    )
    pdf.chapter_body(intro_text)

    pdf.chapter_title('2. Performance Chart')
    pdf.image(CHART_FILENAME, x=pdf.l_margin, w=(pdf.w - 2 * pdf.l_margin))
    pdf.ln(5)

    # Add performance analysis tables
    pdf.chapter_title('3. Performance Analysis')
    
    # Execution Times Table
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(0, 7, 'Execution Times (seconds)', 0, 1, 'L')
    pdf.set_font('Courier', '', 8)
    
    # Table header
    pdf.cell(20, 5, 'n', 1, 0, 'C')
    pdf.cell(25, 5, 'Baseline', 1, 0, 'C')
    pdf.cell(25, 5, 'AVX2', 1, 0, 'C')
    pdf.cell(25, 5, 'Unroll', 1, 0, 'C')
    pdf.cell(25, 5, 'Interchange', 1, 1, 'C')
    
    # Table data
    for _, row in analysis_df.iterrows():
        pdf.cell(20, 5, str(int(row['n'])), 1, 0, 'C')
        pdf.cell(25, 5, f"{row['baseline_time']:.6f}", 1, 0, 'C')
        pdf.cell(25, 5, f"{row['avx2_time']:.6f}", 1, 0, 'C')
        pdf.cell(25, 5, f"{row['unroll_time']:.6f}", 1, 0, 'C')
        pdf.cell(25, 5, f"{row['interchange_time']:.6f}", 1, 1, 'C')
    
    pdf.ln(5)
    
    # Speedup Factors Table
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(0, 7, 'Speedup Factors (relative to baseline)', 0, 1, 'L')
    pdf.set_font('Courier', '', 8)
    
    # Table header
    pdf.cell(20, 5, 'n', 1, 0, 'C')
    pdf.cell(30, 5, 'AVX2', 1, 0, 'C')
    pdf.cell(30, 5, 'Unroll', 1, 0, 'C')
    pdf.cell(30, 5, 'Interchange', 1, 1, 'C')
    
    # Table data
    for _, row in analysis_df.iterrows():
        pdf.cell(20, 5, str(int(row['n'])), 1, 0, 'C')
        pdf.cell(30, 5, f"{row['avx2_speedup']:.2f}x", 1, 0, 'C')
        pdf.cell(30, 5, f"{row['unroll_speedup']:.2f}x", 1, 0, 'C')
        pdf.cell(30, 5, f"{row['interchange_speedup']:.2f}x", 1, 1, 'C')
    
    pdf.ln(5)
    
    # Performance Improvements Table
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(0, 7, 'Performance Improvements (% relative to baseline)', 0, 1, 'L')
    pdf.set_font('Courier', '', 8)
    
    # Table header
    pdf.cell(20, 5, 'n', 1, 0, 'C')
    pdf.cell(30, 5, 'AVX2', 1, 0, 'C')
    pdf.cell(30, 5, 'Unroll', 1, 0, 'C')
    pdf.cell(30, 5, 'Interchange', 1, 1, 'C')
    
    # Table data
    for _, row in analysis_df.iterrows():
        pdf.cell(20, 5, str(int(row['n'])), 1, 0, 'C')
        pdf.cell(30, 5, f"{row['avx2_improvement']:+.1f}%", 1, 0, 'C')
        pdf.cell(30, 5, f"{row['unroll_improvement']:+.1f}%", 1, 0, 'C')
        pdf.cell(30, 5, f"{row['interchange_improvement']:+.1f}%", 1, 1, 'C')
    
    pdf.ln(10)

    # Add narrative analysis
    pdf.chapter_title('4. Detailed Performance Analysis')
    
    # Executive Summary
    avg_avx2_speedup = analysis_df['avx2_speedup'].mean()
    avg_unroll_speedup = analysis_df['unroll_speedup'].mean()
    avg_interchange_speedup = analysis_df['interchange_speedup'].mean()
    
    executive_summary = (
        f"Across all problem sizes (n=256 to n=4048), the AVX2 optimization demonstrates "
        f"the most consistent performance gains with an average speedup of {avg_avx2_speedup:.1f}x "
        f"over the baseline implementation. The unroll optimization shows moderate improvements "
        f"with an average speedup of {avg_unroll_speedup:.1f}x, while the interchange optimization "
        f"actually degrades performance with an average speedup of {avg_interchange_speedup:.1f}x.\n\n"
    )
    pdf.chapter_body(executive_summary)
    
    # AVX2 Analysis
    min_avx2 = analysis_df.loc[analysis_df['avx2_speedup'].idxmin()]
    max_avx2 = analysis_df.loc[analysis_df['avx2_speedup'].idxmax()]
    
    avx2_analysis = (
        f"AVX2 OPTIMIZATION: The AVX2 optimization consistently outperforms the baseline across all problem sizes. "
        f"Performance improvements range from {min_avx2['avx2_improvement']:.1f}% (n={int(min_avx2['n'])}) "
        f"to {max_avx2['avx2_improvement']:.1f}% (n={int(max_avx2['n'])}). "
        f"The best speedup of {max_avx2['avx2_speedup']:.1f}x occurs at n={int(max_avx2['n'])}, "
        f"while the lowest speedup of {min_avx2['avx2_speedup']:.1f}x occurs at n={int(min_avx2['n'])}.\n\n"
    )
    pdf.chapter_body(avx2_analysis)
    
    # Unroll Analysis
    min_unroll = analysis_df.loc[analysis_df['unroll_speedup'].idxmin()]
    max_unroll = analysis_df.loc[analysis_df['unroll_speedup'].idxmax()]
    
    unroll_analysis = (
        f"UNROLL OPTIMIZATION: The unroll optimization shows moderate but consistent improvements over the baseline. "
        f"Performance improvements range from {min_unroll['unroll_improvement']:.1f}% (n={int(min_unroll['n'])}) "
        f"to {max_unroll['unroll_improvement']:.1f}% (n={int(max_unroll['n'])}). "
        f"The optimization is most effective at n={int(max_unroll['n'])} with a {max_unroll['unroll_speedup']:.1f}x speedup.\n\n"
    )
    pdf.chapter_body(unroll_analysis)
    
    # Interchange Analysis
    min_interchange = analysis_df.loc[analysis_df['interchange_speedup'].idxmin()]
    max_interchange = analysis_df.loc[analysis_df['interchange_speedup'].idxmax()]
    
    interchange_analysis = (
        f"INTERCHANGE OPTIMIZATION: The interchange optimization shows poor performance across all problem sizes. "
        f"This optimization actually slows down execution by {abs(max_interchange['interchange_improvement']):.1f}% "
        f"to {abs(min_interchange['interchange_improvement']):.1f}% depending on problem size. "
        f"The worst performance occurs at n={int(min_interchange['n'])} where it is "
        f"{min_interchange['interchange_speedup']:.1f}x slower than baseline.\n\n"
    )
    pdf.chapter_body(interchange_analysis)
    
    # Scaling Behavior
    first_row = analysis_df.iloc[0]
    last_row = analysis_df.iloc[-1]
    
    scaling_analysis = (
        f"SCALING BEHAVIOR: As problem size increases from n=256 to n=4048:\n"
        f"- AVX2: Speedup changes from {first_row['avx2_speedup']:.1f}x to {last_row['avx2_speedup']:.1f}x\n"
        f"- Unroll: Speedup changes from {first_row['unroll_speedup']:.1f}x to {last_row['unroll_speedup']:.1f}x\n"
        f"- Interchange: Speedup changes from {first_row['interchange_speedup']:.1f}x to {last_row['interchange_speedup']:.1f}x\n\n"
    )
    pdf.chapter_body(scaling_analysis)
    
    pdf.chapter_title('5. AI Usage Log')
    ai_log_text = (
        "AI Tool Used: Google Gemini\n\n"
        "How I used the AI as a programming tool:\n"
        "1.  Code Scaffolding: I prompted the AI to generate initial boilerplate for the C++ programs (argument parsing, timing), which I then reviewed and adapted for the project's specific needs.\n"
        "2.  Syntax and Concept Lookup: I used the AI to look up the specific syntax for AVX2 intrinsics (`_mm256_fmadd_ps`, etc.) and to get a template for the horizontal sum logic, which I then integrated and validated within my `hw1.cpp` implementation.\n"
        "3.  Makefile Structure: I requested a `Makefile` structure for handling multiple C++ targets, which I then customized with the specific compiler flags (`-march=native`, `-mavx2`, `-mfma`) and targets required for this assignment.\n"
        "4.  Automation Scripting: The AI significantly accelerated the creation of the report generator. I had it generate individual functions for running benchmarks, creating plots, and building tables. I then assembled these components, debugged the integration, and refined the final report layout.\n\n"
        "Where the AI tool was useful:\n"
        "The tool excelled at accelerating development by handling repetitive or syntactically complex tasks. It was invaluable for quickly generating templates and looking up function calls, which allowed me to focus more on the high-level optimization strategy and the analysis of the results.\n\n"
        "Where the AI tool fell short:\n"
        "The tool required careful guidance and validation. For instance, it did not proactively suggest the crucial `-mavx2` and `-mfma` compiler flags, which led to compilation errors that I had to diagnose. It also produced malformed JSON in the shell script, requiring a fix in the Python parser. This reinforces the need for the programmer to possess the underlying domain knowledge to guide the tool and troubleshoot its output.\n\n"
        "Impact on my role as a programmer:\n"
        "Using the AI shifted my role from a traditional coder to that of a technical director and quality assurance engineer. My primary tasks became defining the problem with precision, breaking it down into components the AI could handle, and then critically reviewing, debugging, and integrating the generated code."
    )
    pdf.chapter_body(ai_log_text)

    pdf.output(PDF_FILENAME, 'F')
    print(f"\nReport successfully generated: {PDF_FILENAME}")


# --- Performance Analysis Functions ---

def calculate_speedups(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate speedup factors and relative performance improvements."""
    result_df = df.copy()
    
    # Calculate speedup factors (how many times faster)
    result_df["avx2_speedup"] = result_df["baseline_time"] / result_df["avx2_time"]
    result_df["unroll_speedup"] = result_df["baseline_time"] / result_df["unroll_time"]
    result_df["interchange_speedup"] = result_df["baseline_time"] / result_df["interchange_time"]
    
    # Calculate percentage improvements (positive = faster, negative = slower)
    result_df["avx2_improvement"] = ((result_df["baseline_time"] - result_df["avx2_time"]) / result_df["baseline_time"]) * 100
    result_df["unroll_improvement"] = ((result_df["baseline_time"] - result_df["unroll_time"]) / result_df["baseline_time"]) * 100
    result_df["interchange_improvement"] = ((result_df["baseline_time"] - result_df["interchange_time"]) / result_df["baseline_time"]) * 100
    
    return result_df

# --- Main Execution ---

def main():
    """Main execution flow for generating the report from results.json."""
    # Step 1: Read and process the benchmark results from the JSON file
    try:
        df = pd.read_json(RESULTS_FILENAME)
        
        # --- Rename columns to match the script's internal naming convention ---
        df = df.rename(columns={
            'baseline_Mv_time': 'baseline_time',
            'hw1_avx2_time': 'avx2_time',
            'hw1_unroll_time': 'unroll_time',
            'hw1_interchange_time': 'interchange_time',
            'hw1_baseline_time': 'hw1_baseline_time' # Keep this for potential future use
        })
        
        # Ensure only the main optimization columns exist for the report
        df = df[['n', 'baseline_time', 'avx2_time', 'unroll_time', 'interchange_time']]

    except Exception as e:
        print(f"Error reading or processing {RESULTS_FILENAME}: {e}")
        print("Please ensure 'run_benchmarks.sh' has been executed successfully first.")
        exit(1)

    if df.empty:
        print(f"{RESULTS_FILENAME} is empty. No report to generate.")
        return

    print("\n--- Processed Benchmark Summary ---")
    print(df.round(6))
    
    # Step 2: Generate all report components
    print("\n--- Generating Report Components ---")
    generate_performance_chart(df)
    generate_pdf_report(df)
    
    # Step 3: Clean up temporary files
    if os.path.exists(CHART_FILENAME):
        os.remove(CHART_FILENAME)
        print(f"Cleaned up temporary file: {CHART_FILENAME}")

    # Step 4: Create the final submission archive
    create_submission_archive()


if __name__ == "__main__":
    main()

