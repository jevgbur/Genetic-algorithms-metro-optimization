import argparse
import csv
import os
import pickle
from typing import Dict, Iterable, List, Optional, Tuple

DEFAULT_SCORE_KEYS = ["score", "Score", "Score as %", "fitness"]


def load_pickle(path: str) -> Dict:
    with open(path, "rb") as f:
        return pickle.load(f)


def extract_generation_differences(
    generations: Dict,
    score_keys: Optional[Iterable[str]] = None,
) -> Optional[Dict[str, object]]:
    score_keys = list(score_keys or DEFAULT_SCORE_KEYS)

    gen0_scores = []
    other_gens_scores = []

    for generation_id, kids in generations.items():
        if not isinstance(kids, dict):
            continue

        for kid_id, kid_data in kids.items():
            if not isinstance(kid_data, dict):
                continue

            score_value = None
            for score_key in score_keys:
                if score_key in kid_data:
                    score_value = kid_data[score_key]
                    break

            if score_value is None:
                continue

            try:
                score_value = float(score_value)
            except (TypeError, ValueError):
                continue

            if generation_id == 0:
                gen0_scores.append(score_value)
            else:
                other_gens_scores.append((generation_id, score_value))

    if not gen0_scores or not other_gens_scores:
        return None

    gen0_best = max(gen0_scores)
    other_best_gen, other_best_score = max(other_gens_scores, key=lambda x: x[1])

    difference = other_best_score - gen0_best

    return {
        "gen0_best_score": gen0_best,
        "overall_best_score": other_best_score,
        "difference": difference,
        "best_gen": other_best_gen,
    }


def find_pickle_files(root_dir: str) -> List[str]:
    pickle_files: List[str] = []
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.lower().endswith(".pkl"):
                pickle_files.append(os.path.join(dirpath, filename))
    return sorted(pickle_files)


def write_csv(results: List[Dict[str, object]], csv_path: str) -> None:
    fieldnames = ["pickle_file", "gen0_best_score", "overall_best_score", "difference", "best_gen"]
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for entry in results:
            writer.writerow(
                {
                    "pickle_file": entry["pickle_file"],
                    "gen0_best_score": entry["gen0_best_score"],
                    "overall_best_score": entry["overall_best_score"],
                    "difference": entry["difference"],
                    "best_gen": entry["best_gen"],
                }
            )


def write_averages_csv(results: List[Dict[str, object]], csv_path: str) -> None:
    if not results:
        return

    avg_gen0 = sum(entry["gen0_best_score"] for entry in results) / len(results)
    avg_overall = sum(entry["overall_best_score"] for entry in results) / len(results)
    avg_difference = sum(entry["difference"] for entry in results) / len(results)

    fieldnames = ["avg_gen0_best_score", "avg_overall_best_score", "avg_difference"]
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow(
            {
                "avg_gen0_best_score": avg_gen0,
                "avg_overall_best_score": avg_overall,
                "avg_difference": avg_difference,
            }
        )


def process_synthetic_folder(
    input_dir: str,
    score_keys: Optional[Iterable[str]] = None,
) -> List[Dict[str, object]]:
    pickle_files = find_pickle_files(input_dir)
    if not pickle_files:
        raise FileNotFoundError(f"No .pkl files found in {input_dir}")

    all_results: List[Dict[str, object]] = []
    for pickle_path in pickle_files:
        generations = load_pickle(pickle_path)
        diff_data = extract_generation_differences(generations, score_keys=score_keys)
        if diff_data:
            all_results.append(
                {
                    "pickle_file": os.path.relpath(pickle_path, input_dir),
                    "gen0_best_score": diff_data["gen0_best_score"],
                    "overall_best_score": diff_data["overall_best_score"],
                    "difference": diff_data["difference"],
                    "best_gen": diff_data["best_gen"],
                }
            )
    return all_results


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract generation differences from population pickle files."
    )
    parser.add_argument(
        "--folder",
        choices=["Synthetic", "Extension_Population", "Built_from_scratch_population", "all"],
        default="all",
        help="Which population folder to process. Default: all",
    )
    parser.add_argument(
        "--score-keys",
        nargs="+",
        default=DEFAULT_SCORE_KEYS,
        help="Candidate score field names to look for inside each child record.",
    )

    args = parser.parse_args()

    # Map folder names to paths
    folder_map = {
        "Synthetic": "Results/Synthetic",
        "Extension_Population": "Results/Extension_Population",
        "Built_from_scratch_population": "Results/Built_from_scratch_population",
    }

    if args.folder == "all":
        population_dirs = list(folder_map.values())
    else:
        population_dirs = [folder_map[args.folder]]

    for pop_dir in population_dirs:
        if not os.path.exists(pop_dir):
            print(f"Directory {pop_dir} does not exist, skipping.")
            continue

        results = process_synthetic_folder(pop_dir, score_keys=args.score_keys)

        # Determine output paths
        dir_name = os.path.basename(pop_dir)
        detailed_csv = os.path.join(pop_dir, f"{dir_name}_generation_differences.csv")
        averages_csv = os.path.join(pop_dir, f"{dir_name}_averages.csv")

        write_csv(results, detailed_csv)
        write_averages_csv(results, averages_csv)

        print(f"Processed {pop_dir}: {len(results)} cycles to {detailed_csv} and averages to {averages_csv}")


if __name__ == "__main__":
    main()
