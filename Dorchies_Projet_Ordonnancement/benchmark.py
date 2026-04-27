import subprocess
import time
import numpy as np

def benchmark_task():
    print("Compiling task1.c...")
    subprocess.run(["gcc", "-O0", "task1.c", "-o", "task1"], check=True)
    
    os_times = []
    c_times = []
    iterations = 1000

    print("Running benchmarks (1000 iterations)... Please wait.")
    for _ in range(iterations):
        # Start external OS timer
        start_time = time.perf_counter()
        
        # Run C executable and capture output
        result = subprocess.run(["./task1"], capture_output=True, text=True)
        
        # Stop external OS timer
        end_time = time.perf_counter()
        
        # Convert total OS time strictly to MILLISECONDS (ms)
        # perf_counter returns seconds natively
        os_times.append((end_time - start_time)*1000)
        
        # Extract pure calculation time measured by C in NANOSECONDS (ns)
        for line in result.stdout.splitlines():
            if line.startswith("C_TIME_NS:"):
                c_times.append(float(line.split(":")[1]))

    # Helper function to print stats with dynamic units and decimals
    def print_stats(title, times, unit, decimals):
        print(f"\n=== {title} ===")
        print(f"Min: {np.min(times):.{decimals}f} {unit}")
        print(f"Max (WCET): {np.max(times):.{decimals}f} {unit}")
        print(f"Q1: {np.percentile(times, 25):.{decimals}f} {unit}")
        print(f"Q2 (Median): {np.median(times):.{decimals}f} {unit}")
        print(f"Q3: {np.percentile(times, 75):.{decimals}f} {unit}")

    # Display OS Time in seconds
    print_stats("Global OS Time (Process Creation + Execution) - Measured by Python", os_times, "ms", 6)
    
    # Display pure calculation time in nanoseconds
    print_stats("Pure Calculation Time (Multiplication only) - Measured by C", c_times, "ns", 0)

if __name__ == "__main__":
    benchmark_task()