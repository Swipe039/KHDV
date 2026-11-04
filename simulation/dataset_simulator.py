import argparse
from dataclasses import replace

from simulation.config import SimulationConfig
from simulation.csv_io import write_dataset
from simulation.generator import generate_dataset

def parse_weights(text):
    return tuple(int(part) for part in text.split(","))

def main():
    """
    Thực hiện sinh bộ dữ liệu giả lập
    """
    default_args = SimulationConfig()
    parser = argparse.ArgumentParser()
    parser.add_argument("--students", type=int, default=2000) # Dùng 2000 SV
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--out", default="data/generated")

    parser.add_argument("--sessions-per-day", type=int, default=default_args.sessions_per_day)
    parser.add_argument("--motorbike-usage-rate", type=float, default=default_args.motorbike_usage_rate)
    parser.add_argument("--register-rate", type=float, default=default_args.register_rate)
    parser.add_argument("--sparse-rate", type=float, default=default_args.sparse_rate)
    parser.add_argument("--days-weights", type=parse_weights, default=default_args.days_weights_distribution)
    
    args = parser.parse_args()

    config = replace(
        default_args,
        sessions_per_day = args.sessions_per_day,
        register_rate=args.register_rate,
        sparse_rate=args.sparse_rate,
        days_weights_distribution=args.days_weights,
    )

    # Tạo dataset TKB và yêu cầu dky 
    entries, requests = generate_dataset(args.students, config=config, seed=args.seed)

    write_dataset(args.out, entries, requests)
    num_registrations = sum(1 for _, registration in requests if registration)
    print(f"students={args.students} entries={len(entries)} blocks={len(requests)} num_registrations={num_registrations}")

if __name__ ==  "__main__":
    main()