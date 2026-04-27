import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict

# ==============================
# System Parameters
# ==============================
WCET = np.array([2, 3, 2, 2, 2, 2, 3])
Deadlines = np.array([10, 10, 20, 20, 40, 40, 80])
IDs = np.array([1, 2, 3, 4, 5, 6, 7])

hyperperiod = np.lcm.reduce(Deadlines)
number_jobs = (hyperperiod / Deadlines).astype(int)
job_count = {tid: number_jobs[i] for i, tid in enumerate(IDs)}

# ==============================
# Backtracking Engine (Handles all 3 cases)
# ==============================
def generate_permutations(task_ids, number_jobs_dict, mode="strict", top_k=1):
    """
    Modes:
    - 'strict': No deadlines can be missed.
    - 'allow_miss': Task 5 is allowed to miss its deadline (we target exactly 1 miss).
    - 'skip_late': If Task 5 is going to miss its deadline, it is skipped.
    """
    results = []
    memo = {}
    total_jobs_local = sum(number_jobs_dict[tid] for tid in task_ids)

    def backtrack(current_perm, job_done, current_time, total_waiting, misses):
        # Terminal condition: all jobs are processed (or skipped)
        if sum(job_done.values()) == total_jobs_local:
            results.append((total_waiting, misses, tuple(current_perm)))
            return

        # Memoization to prune redundant paths
        state_key = (tuple(sorted(job_done.items())), current_time)
        if state_key in memo and memo[state_key] <= total_waiting:
            return
        memo[state_key] = total_waiting

        candidates = []
        for tid in task_ids:
            idx = tid - 1
            if job_done[tid] < number_jobs_dict[tid]:
                job_num = job_done[tid] + 1
                release = (job_num - 1) * Deadlines[idx]
                deadline = job_num * Deadlines[idx]
                candidates.append((release, deadline, WCET[idx], tid, job_num))

        # Heuristic sorting: prioritize T5 in 'allow_miss' mode
        if mode == "allow_miss":
            candidates.sort(key=lambda x: (x[3] != 5, x[0], x[1]))
        else:
            candidates.sort(key=lambda x: (x[0], x[1]))

        for release, deadline, wcet, tid, job_num in candidates:
            start_time = max(current_time, release)
            finish_time = start_time + wcet
            waiting = start_time - release

            # Deadline Check
            if finish_time > deadline:
                if tid == 5:
                    if mode == "allow_miss":
                        # Accept the miss for Task 5
                        job_done[tid] += 1
                        current_perm.append((tid, job_num))
                        backtrack(current_perm, job_done, finish_time, total_waiting + waiting, misses + 1)
                        current_perm.pop()
                        job_done[tid] -= 1
                        continue
                    elif mode == "skip_late":
                        # Drop/Skip Task 5 entirely without scheduling it
                        job_done[tid] += 1
                        backtrack(current_perm, job_done, current_time, total_waiting, misses)
                        job_done[tid] -= 1
                        continue
                    else:
                        continue # Strict mode: abandon this branch
                else:
                    continue # Other tasks must strictly meet deadlines

            # Normal Execution (deadline respected)
            job_done[tid] += 1
            current_perm.append((tid, job_num))
            backtrack(current_perm, job_done, finish_time, total_waiting + waiting, misses)
            current_perm.pop()
            job_done[tid] -= 1

    # Start backtracking
    backtrack([], defaultdict(int), 0, 0, 0)

    # Filter results for 'allow_miss' to ensure T5 missed exactly once
    if mode == "allow_miss":
        valid_results = [r for r in results if r[1] == 1]
    else:
        valid_results = results

    # Return the best permutations based on total waiting time
    return sorted(valid_results, key=lambda x: x[0])[:top_k]

def progressive_schedule(mode="strict"):
    current_ids = list(IDs[:4])
    for new_tid in IDs[4:]:
        current_ids.append(new_tid)
        current_jobs = {tid: job_count[tid] for tid in current_ids}
        # We calculate top 3 and keep the best to avoid local minima
        current_best = generate_permutations(current_ids, current_jobs, mode=mode, top_k=3)
    return current_best[-1] if current_best else None

# ==============================
# Gantt Chart Visualization
# ==============================
def visualize_schedule(permutation, title):
    task_colors = plt.colormaps.get_cmap('tab10')
    timeline = []
    current_time = 0

    for task_id, job_num in permutation:
        idx = task_id - 1
        release = (job_num - 1) * Deadlines[idx]
        start_time = max(current_time, release)
        end_time = start_time + WCET[idx]
        missed = (end_time > job_num * Deadlines[idx])
        timeline.append((task_id, job_num, start_time, end_time, missed))
        current_time = end_time

    fig, ax = plt.subplots(figsize=(12, 5))
    task_positions = {tid: (len(IDs) - i - 1) * 10 for i, tid in enumerate(IDs)}

    for task, job, start, end, missed in timeline:
        color = 'red' if missed else task_colors((task - 1) % 10)
        y_pos = task_positions[task]
        ax.broken_barh([(start, end - start)], (y_pos, 8), facecolors=color, edgecolor='black', linewidth=0.5)
        ax.text(start + (end - start)/2, y_pos + 4, f"T{task}.{job}", 
                ha='center', va='center', color='white', fontsize=8, fontweight='bold')

    ax.set_yticks([task_positions[tid] + 4 for tid in IDs])
    ax.set_yticklabels([f'Task {tid}' for tid in IDs])
    ax.set_xlabel("Time")
    ax.set_title(title)
    ax.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.show()

# ==============================
# Execution
# ==============================
if __name__ == "__main__":
    print("--- REAL-TIME SCHEDULING SEARCH ---")
    
    # CASE 1: Strict Schedule
    print("\n1. Calculating Strict Schedule (No deadline missed)...")
    res_strict = progressive_schedule(mode="strict")
    if res_strict:
        print(f"-> Case 1 | Total waiting time: {res_strict[0]}")
        visualize_schedule(res_strict[2], f"Schedule (Strict / No deadline missed) | Waiting Time: {res_strict[0]}")

    # CASE 2: Allow Miss for Task 5
    print("\n2. Calculating Schedule with Task 5 allowed to miss...")
    res_miss = progressive_schedule(mode="allow_miss")
    if res_miss:
        print(f"-> Case 2 | Total waiting time: {res_miss[0]} | T5 Misses: {res_miss[1]}")
        visualize_schedule(res_miss[2], f"Schedule with Task 5 delayed (red) | Waiting Time: {res_miss[0]}")

    # CASE 3: Skip Task 5 if late
    print("\n3. Calculating Schedule with Task 5 skipped if late...")
    res_skip = progressive_schedule(mode="skip_late")
    if res_skip:
        print(f"-> Case 3 | Total waiting time: {res_skip[0]}")
        visualize_schedule(res_skip[2], f"Schedule (Task 5 skipped if late) | Waiting Time: {res_skip[0]}")