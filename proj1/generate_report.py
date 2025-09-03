# generate_report.py
import subprocess
import re
import os
import matplotlib.pyplot as plt
from fpdf import FPDF
import pandas as pd

# --- Configuration ---
MATRIX_SIZES = [256, 512, 1024, 2048, 4096]
# Define all optimizers to be tested, matching the makefile targets
OPTIMIZERS = {
    "baseline": {"src": "Mv.cpp", "exe": "./baseline"},
    "avx2": {"src": "avx2.cpp", "exe": "./avx2"},
    "unroll": {"src": "unroll.cpp", "exe": "./unroll"},
    "interchange": {"src": "interchange.cpp", "exe": "./interchange"}
}
PDF_FILENAME = "hw1.pdf"
CHART_FILENAME = "performance_chart.png"


def create_submission_archive():
    """Cleans the directory and creates a tar file for submission."""
    print("\n--- Creating Submission Archive ---")
    try:
        # Clean the directory of executables and object files first
        print("Cleaning directory...")
        subprocess.run(["make", "clean"], check=True, capture_output=True, text=True)

        # Get the name of the current directory (e.g., 'hw1')
        dir_name = os.path.basename(os.getcwd())
        archive_name = f"{dir_name}.tar"

        # List of files to include in the tar file, as specified
        files_to_archive = [
            "avx2.cpp",
            "generate_report.py", # Corrected from .ipynb
            "hw1.pdf",
            "interchange.cpp",
            "LOG.txt",
            "makefile", # Assuming the makefile is named 'makefile'
            "Mv.cpp",
            "unroll.cpp"
        ]
        
        # Verify all files exist before trying to archive them
        for f in files_to_archive:
            if not os.path.exists(f):
                print(f"Warning: Submission file '{f}' not found. It will be missing from the archive.")
        
        # Create the tar command
        command = ["tar", "cvf", archive_name] + files_to_archive
        print(f"Executing: {' '.join(command)}")
        
        subprocess.run(command, check=True, capture_output=True, text=True)
        print(f"Successfully created submission archive: {archive_name}")

    except FileNotFoundError:
        print("Error: 'tar' command not found. Cannot create archive.")
    except subprocess.CalledProcessError as e:
        print(f"!!! Archiving Failed !!!\nError message:\n{e.stderr}")
    except Exception as e:
        print(f"An unexpected error occurred during archiving: {e}")



def compile_code():
    """Compiles the C++ code using make."""
    print("--- Compiling all C++ executables using make ---")
    try:
        # The 'make all' command will build all targets defined in the makefile
        subprocess.run(["make", "all"], check=True, capture_output=True, text=True)
        print("Compilation successful for all targets.")
    except subprocess.CalledProcessError as e:
        print("!!! Compilation Failed !!!")
        print(f"Error message:\n{e.stderr}")
        exit(1)

def run_benchmark(executable_path, n):
    """Runs a single benchmark and extracts the execution time."""
    if not os.path.exists(executable_path):
        print(f"Executable {executable_path} not found. Aborting.")
        return None
        
    command = [executable_path, str(n)]
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True, timeout=300)
        match = re.search(r"Execution time: (\d+\.\d+)", result.stdout)
        if match:
            return float(match.group(1))
        return None
    except subprocess.TimeoutExpired:
        print(f"Timeout: {executable_path} with n={n} took too long.")
        return float('inf')
    except subprocess.CalledProcessError as e:
        print(f"Error running {executable_path} with n={n}:\n{e.stderr}")
        return None

def generate_performance_chart(df):
    """Creates and saves a performance comparison chart."""
    plt.figure(figsize=(12, 7))
    
    for opt_name in OPTIMIZERS.keys():
        plt.plot(df['n'], df[f'{opt_name}_time'], 'o-', label=opt_name)
    
    plt.title('Performance Comparison of Optimization Techniques')
    plt.xlabel('Matrix Size (n)')
    plt.ylabel('Execution Time (seconds)')
    plt.xscale('log', base=2)
    plt.yscale('log')
    plt.grid(True, which="both", ls="--")
    plt.legend()
    plt.xticks(df['n'], labels=[str(s) for s in df['n']])
    plt.savefig(CHART_FILENAME)
    print(f"Chart saved to {CHART_FILENAME}")

class PDF(FPDF):
    """Custom PDF class to handle header and footer."""
    def header(self):
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, 'HW1 Performance Report', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')
        
    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12); self.cell(0, 10, title, 0, 1, 'L'); self.ln(2)

    def chapter_body(self, text):
        self.set_font('Arial', '', 11); self.multi_cell(0, 5, text); self.ln()

def generate_pdf_report(df):
    """Assembles the final PDF report."""
    pdf = PDF()
    pdf.add_page()
    
    pdf.chapter_title('1. Optimization Techniques')
    intro_text = (
        "This report compares several optimization techniques for matrix-vector multiplication against a baseline compiled with gcc++ -O3.\n\n"
        "1.  AVX2 SIMD: Leverages data parallelism by processing 4 doubles simultaneously using Advanced Vector Extensions.\n"
        "2.  Loop Unrolling: Reduces loop overhead by manually processing 8 elements per inner-loop iteration.\n"
        "3.  Loop Interchange: Swaps the inner and outer loops to demonstrate the negative impact of poor memory access patterns (cache performance)."
    )
    pdf.chapter_body(intro_text)

    pdf.chapter_title('2. Performance Results (Execution Time in Seconds)')
    pdf.set_font('Arial', 'B', 10)
    
    # Dynamically create headers for the table
    headers = ['Size (n)'] + [f'{name}' for name in OPTIMIZERS] + [f'avx2_speedup']
    
    # Set column widths
    col_widths = {h: 28 for h in headers}
    col_widths['Size (n)'] = 20
    
    for header in headers:
        pdf.cell(col_widths.get(header), 10, header.replace('_time','').title(), 1, 0, 'C')
    pdf.ln()

    pdf.set_font('Arial', '', 9)
    for index, row in df.iterrows():
        pdf.cell(col_widths['Size (n)'], 8, str(int(row['n'])), 1, 0, 'C')
        for name in OPTIMIZERS:
            pdf.cell(col_widths[name], 8, f"{row[f'{name}_time']:.4f}", 1, 0, 'C')
        pdf.cell(col_widths['avx2_speedup'], 8, f"{row['avx2_speedup']:.2f}x", 1, 1, 'C')
    pdf.ln(10)

    pdf.chapter_title('3. Performance Chart')
    img_width = pdf.w - 2 * pdf.l_margin # Make image fit page width
    pdf.image(CHART_FILENAME, x=pdf.l_margin, w=img_width)
    pdf.ln(5)

    pdf.chapter_title('4. AI Usage Log')

    ai_log_text = (
        "AI Tool Used: Google Gemini\n\n"
        "How I used the AI as a programming tool:\n"
        "1.  Code Scaffolding: I prompted the AI to generate initial boilerplate for the C++ programs (argument parsing, timing), which I then reviewed and adapted for the project's specific needs.\n"
        "2.  Syntax and Concept Lookup: I used the AI to look up the specific syntax for AVX2 intrinsics (`_mm256_fmadd_pd`, etc.) and to get a template for the horizontal sum logic, which I then integrated and validated within my `avx2.cpp` implementation.\n"
        "3.  Makefile Structure: I requested a basic `makefile` structure for handling multiple C++ targets, which I then customized with the specific compiler flags (`-march=native`) and targets required for this assignment.\n"
        "4.  Automation Scripting: The AI significantly accelerated the creation of the Python report generator. I had it generate individual functions for running benchmarks, creating plots, and building tables. I then assembled these components, debugged the integration, and refined the final report layout.\n\n"
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
    """Main execution flow."""
    compile_code()
    
    all_results = []
    print("\n--- Running Benchmarks ---")
    for n in MATRIX_SIZES:
        print(f"Testing size n = {n}...")
        result_row = {"n": n}
        for name, info in OPTIMIZERS.items():
            time = run_benchmark(info["exe"], n)
            result_row[f'{name}_time'] = time
            print(f"  - {name}: {time:.4f}s" if time is not None else f"  - {name}: FAILED")
        all_results.append(result_row)

    if not all_results:
        print("\nNo benchmarks completed. Aborting.")
        return

    df = pd.DataFrame(all_results)
    df.dropna(inplace=True) # Remove rows where any test failed
    if df.empty:
        print("\nAll benchmarks failed. Aborting report generation.")
        return

    # Calculate speedup relative to the baseline
    df['avx2_speedup'] = df['baseline_time'] / df['avx2_time']
    
    print("\n--- Benchmark Summary ---")
    print(df.round(4))

    generate_performance_chart(df)
    generate_pdf_report(df)
    
    # Clean up the chart image after embedding it in the PDF
    if os.path.exists(CHART_FILENAME):
        os.remove(CHART_FILENAME)

    create_submission_archive()

if __name__ == "__main__":
    main()


