import sys
from collections import Counter

from simulation.csv_io import read_timetable
from solver.blocks import build_blocks

def main():
    entries = read_timetable(sys.argv[1])
    blocks = build_blocks(entries)
    lengths = Counter(block.length for block in blocks)
    total = len(blocks)
    for length in sorted(lengths):
        share = lengths[length] / total
        print(f"length={length} count={lengths[length]} share={share:.1%}")


if __name__ == "__main__":
    main()