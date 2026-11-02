import argparse
from simulation.csv_io import write_dataset
from simulation.generator import DEFAULT_DAYS, generate_dataset

def main():
    """
    Thực hiện sinh bộ dữ liệu giả lập
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--students", type=int, default=1000)
    parser.add_argument("--days", type=int, default=len(DEFAULT_DAYS))
    parser.add_argument("--sessions-per-day", type=int, default=4)
    parser.add_argument("--attend_rate", type=float, default=0.6)
    parser.add_argument("--wants-rate", type=float, default=0.8)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--out", default="data/generated")
    args = parser.parse_args()

    entries, requests = generate_dataset(
        args.students,
        days=DEFAULT_DAYS[: args.days],
        sessions_per_day=args.sessions_per_day,
        attend_rate=args.attend_rate,
        wants_rate=args.wants_rate,
        seed=args.seed,
    )

    write_dataset(args.out, entries, requests)
    wanted = sum(1 for _, wants in requests if wants)
    print(f"students={args.students} entries={len(entries)} blocks={len(requests)} wanted={wanted}")

if __name__ ==  "__main__":
    main()