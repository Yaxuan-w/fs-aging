import os
import re
from collections import defaultdict

BASE_DIR = "/Users/yxwen/Desktop/results-cp/test7"
RUNS = range(1, 6)
FILES = ["file1", "file2", "file3", "file4"]

def extract_blocks(filepath):
    blocks = []
    with open(filepath, "r") as f:
        for line in f:
            line = line.strip()
            if re.match(r"^\d+", line):
                parts = line.split()
                if len(parts) >= 4:
                    begin = int(parts[1])
                    end = int(parts[2])
                    blocks.append((begin, end))
    return blocks


def extract_readdir_order(filepath):
    files = []
    with open(filepath, "r") as f:
        for line in f:
            line = line.strip()
            if line.startswith("/"):
                files.append(os.path.basename(line))
    return files

def collect_data():
    layout_data = defaultdict(lambda: defaultdict(dict))  # layout_data[file][run][stage] = blocks
    readdir_data = defaultdict(dict)  # readdir_data[run][stage] = list of files

    for run in RUNS:
        for file in FILES:
            for stage, suffix in [("initial", "initial_main"), ("intermediate", "after_main"), ("external", "ext")]:
                layout_file = os.path.join(BASE_DIR, f"{file}_{suffix}_{run}.layout")
                if os.path.exists(layout_file):
                    blocks = extract_blocks(layout_file)
                    layout_data[file][run][stage] = blocks

        for stage, name in [("initial", "readdir_initial_main"),
                            ("intermediate", "readdir_after_main"),
                            ("external", "readdir_ext")]:
            readdir_file = os.path.join(BASE_DIR, f"{name}_{run}.log")
            if os.path.exists(readdir_file):
                readdir_data[run][stage] = extract_readdir_order(readdir_file)

    return layout_data, readdir_data

def same_blocks(*block_lists):
    sets = [set(bl) for bl in block_lists]
    return all(s == sets[0] for s in sets)

def same_order(*orders):
    return all(order == orders[0] for order in orders)

def compare_and_report(layout_data, readdir_data):
    for run in RUNS:
        print(f"\n=== Run {run} ===")

        # for file in FILES:
        #     print(f"\n-- {file} block comparison:")
        #     blocks_initial = layout_data[file][run].get("initial", [])
        #     blocks_intermediate = layout_data[file][run].get("intermediate", [])
        #     blocks_external = layout_data[file][run].get("external", [])

        #     if blocks_intermediate:
        #         if same_blocks(blocks_initial, blocks_intermediate):
        #             print("  [-] All stages have the same blocks on **MAIN**.")
        #         else:
        #             print("  [!] Blocks differ between stages on **MAIN**.")

        #     print(f"  initial:      {blocks_initial}")
        #     print(f"  intermediate: {blocks_intermediate}")
        #     print(f"  external:     {blocks_external}")

        print(f"\n-- readdir() order:")
        initial = readdir_data[run].get("initial", [])
        intermediate = readdir_data[run].get("intermediate", [])
        external = readdir_data[run].get("external", [])

        if not intermediate:
            if same_order(initial, external):
                print("  [-] initial and external have the same readdir() order.")
            else:
                print("  [!] initial and external have different readdir() order.")
        else:
            if same_order(initial, intermediate, external):
                print("  [-] All stages have the same readdir() order.")
            else:
                print("  [!] readdir() order differs across stages.")
                if same_order(initial, intermediate):
                    print("    [-] initial and intermediate have the same readdir() order.")
            

        print(f"  initial:      {initial}")
        print(f"  intermediate: {intermediate}")
        print(f"  external:     {external}")

if __name__ == "__main__":
    layout_data, readdir_data = collect_data()
    compare_and_report(layout_data, readdir_data)
