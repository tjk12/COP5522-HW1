# create_report.py
import subprocess
import re
import os
import matplotlib.pyplot as plt
from fpdf import FPDF
import pandas as pd
import json

# --- Configuration ---
# This script now reads its data from results.json
RESULTS_FILENAME = "results.json"
PDF_FILENAME = "hw1.pdf"
LOG_FILENAME = "LOG.txt"
CHART_FILENAME = "performance_chart.png"

# This dictionary helps structure the report. The keys should match those in results.json.
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

        # List of files to include in the tar file, as specified
        # Note: The old 'generate_report.py' is replaced by 'create_report.py' and 'run_benchmarks.sh'
        files_to_archive = [
            "avx2.cpp",
            "create_report.py",
            "run_benchmarks.sh",
            "hw1.pdf",
            "interchange.cpp",
            "LOG.txt",
            "makefile",
            "Mv.cpp",
            "unroll.cpp",
            "results.json",
            "reporter.py"
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
    """Assembles the final PDF report."""
    pdf = PDF()
    pdf.add_page()
    
    pdf.chapter_title('1. Optimization Techniques')
    intro_text = (
        "This report compares several optimization techniques for matrix-vector multiplication against a baseline compiled with g++ -O3.\n\n"
        "1.  AVX2 SIMD: Leverages data parallelism by processing 4 doubles simultaneously using Advanced Vector Extensions.\n"
        "2.  Loop Unrolling: Reduces loop overhead by manually processing 8 elements per inner-loop iteration.\n"
        "3.  Loop Interchange: Swaps the inner and outer loops to demonstrate the negative impact of poor memory access patterns (cache performance)."
    )
    pdf.chapter_body(intro_text)

    pdf.chapter_title('2. Performance Chart')
    pdf.image(CHART_FILENAME, x=pdf.l_margin, w=(pdf.w - 2 * pdf.l_margin))
    pdf.ln(5)

    pdf.chapter_title('3. AI Usage Log')
    ai_log_text = (
        "AI Tool Used: Google Gemini\n\n"
        "How I used the AI as a programming tool:\n"
        "1.  Code Scaffolding: I prompted the AI to generate initial boilerplate for the C++ programs (argument parsing, timing), which I then reviewed and adapted for the project's specific needs.\n"
        "2.  Syntax and Concept Lookup: I used the AI to look up the specific syntax for AVX2 intrinsics (`_mm256_fmadd_pd`, etc.) and to get a template for the horizontal sum logic, which I then integrated and validated within my `avx2.cpp` implementation.\n"
        "3.  Makefile Structure: I requested a basic `makefile` structure for handling multiple C++ targets, which I then customized with the specific compiler flags (`-march=native`) and targets required for this assignment.\n"
        "4.  Automation Scripting: The AI significantly accelerated the creation of the report generator. I had it generate individual functions for running benchmarks, creating plots, and building tables. I then assembled these components, debugged the integration, and refined the final report layout.\n\n"
        "Where the AI tool was useful:\n"
        "The tool excelled at accelerating development by handling repetitive or syntactically complex tasks. It was invaluable for quickly generating templates and looking up function calls, which allowed me to focus more on the high-level optimization strategy and the analysis of the results.\n\n"
        "Where the AI tool fell short:\n"
        "The tool required careful guidance and validation. For instance, its initial C++ code failed to compile due to a linker error (using `gcc` instead of `g++`), which I had to diagnose and correct. It also did not proactively suggest the crucial `-march=native` flag, reinforcing the need for the programmer to possess the underlying domain knowledge.\n\n"
        "Impact on my role as a programmer:\n"
        "Using the AI shifted my role from a traditional coder to that of a technical director and quality assurance engineer. My primary tasks became defining the problem with precision, breaking it down into components the AI could handle, and then critically reviewing, debugging, and integrating the generated code."
    )
    pdf.chapter_body(ai_log_text)

    pdf.output(PDF_FILENAME, 'F')
    print(f"\nReport successfully generated: {PDF_FILENAME}")


def main():
    """Main execution flow for generating the report from results.json."""
    # Step 1: Read the benchmark results from the JSON file
    try:
        df = pd.read_json(RESULTS_FILENAME)
    except Exception as e:
        print(f"Error reading {RESULTS_FILENAME}: {e}")
        print("Please ensure 'run_benchmarks.sh' has been executed successfully first.")
        exit(1)

    if df.empty:
        print(f"{RESULTS_FILENAME} is empty. No report to generate.")
        return


    print("\n--- Benchmark Summary from results.json ---")
    print(df.round(6))

    # Step 3: Generate all report components
    generate_performance_chart(df)
    generate_pdf_report(df)
    
    # Step 4: Clean up temporary files
    if os.path.exists(CHART_FILENAME):
        os.remove(CHART_FILENAME)

    # Step 5: Create the final submission archive
    create_submission_archive()


if __name__ == "__main__":
    main()

