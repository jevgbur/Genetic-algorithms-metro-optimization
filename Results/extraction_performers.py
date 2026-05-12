import argparse
import csv
import os
import pickle
from typing import Dict, Iterable, List, Optional, Tuple

DEFAULT_SCORE_KEYS = ["Score as %", "Final score"]


def load_pickle(path: str) -> Dict:
    with open(path, "rb") as f:
        return pickle.load(f)


def extract_generation_differences(
    generations: Dict,
    score_keys: Optional[Iterable[str]] = None,
) -> Dict[str, Optional[Dict[str, object]]]:
    score_keys = list(score_keys or DEFAULT_SCORE_KEYS)
    other_keys = [k for k in score_keys if k != score_keys[0]] + [score_keys[0]]  # to get the other key
    results = {}

    for i, score_key in enumerate(score_keys):
        other_key = other_keys[i]
        gen0_kids = []
        other_gens_kids = []

        for generation_id, kids in generations.items():
            if not isinstance(kids, dict):
                continue

            for kid_id, kid_data in kids.items():
                if not isinstance(kid_data, dict):
                    continue

                if score_key in kid_data:
                    score_value = kid_data[score_key]
                    try:
                        score_value = float(score_value)
                    except (TypeError, ValueError):
                        continue

                    other_score = kid_data.get(other_key)
                    if other_score is not None:
                        try:
                            other_score = float(other_score)
                        except (TypeError, ValueError):
                            other_score = None

                    kid_info = {
                        "kid_id": kid_id,
                        "score": score_value,
                        "other_score": other_score,
                        "gen": generation_id
                    }

                    if generation_id == 0:
                        gen0_kids.append(kid_info)
                    else:
                        other_gens_kids.append(kid_info)

        if not gen0_kids or not other_gens_kids:
            results[score_key] = None
            continue

        gen0_best = max(gen0_kids, key=lambda x: x["score"])
        other_best = max(other_gens_kids, key=lambda x: x["score"])

        difference = other_best["score"] - gen0_best["score"]

        results[score_key] = {
            "gen0_best_score": gen0_best["score"],
            "gen0_other_score": gen0_best["other_score"],
            "overall_best_score": other_best["score"],
            "overall_other_score": other_best["other_score"],
            "difference": difference,
            "best_gen": other_best["gen"],
        }

    return results


def find_pickle_files(root_dir: str) -> List[str]:
    pickle_files: List[str] = []
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.lower().endswith(".pkl"):
                pickle_files.append(os.path.join(dirpath, filename))
    return sorted(pickle_files)


def write_csv(results: List[Dict[str, object]], csv_path: str, score_key: str) -> None:
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
        if score_key == "Score as %":
            fieldnames = ["population", "pickle_file", "gen0_best_score_score_as_%", "overall_best_score_as_%", "difference", "best_gen", "gen0_final_score", "overall_final_score"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for entry in results:
                writer.writerow({
                    "population": entry["population"],
                    "pickle_file": entry["pickle_file"],
                    "gen0_best_score_score_as_%": entry["gen0_best_score"],
                    "overall_best_score_as_%": entry["overall_best_score"],
                    "difference": entry["difference"],
                    "best_gen": entry["best_gen"],
                    "gen0_final_score": entry["gen0_other_score"],
                    "overall_final_score": entry["overall_other_score"],
                })
        else:  # "Final score"
            fieldnames = ["population", "pickle_file", "gen0_best_score_final_score", "overall_best_final_score", "difference", "best_gen", "gen0_score_as_%", "overall_score_as_%"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for entry in results:
                writer.writerow({
                    "population": entry["population"],
                    "pickle_file": entry["pickle_file"],
                    "gen0_best_score_final_score": entry["gen0_best_score"],
                    "overall_best_final_score": entry["overall_best_score"],
                    "difference": entry["difference"],
                    "best_gen": entry["best_gen"],
                    "gen0_score_as_%": entry["gen0_other_score"],
                    "overall_score_as_%": entry["overall_other_score"],
                })


def write_averages_csv(results: List[Dict[str, object]], csv_path: str, score_key: str) -> None:
    if not results:
        return

    avg_gen0 = sum(entry["gen0_best_score"] for entry in results) / len(results)
    avg_overall = sum(entry["overall_best_score"] for entry in results) / len(results)
    avg_difference = sum(entry["difference"] for entry in results) / len(results)
    avg_gen0_other = sum(entry["gen0_other_score"] for entry in results if entry["gen0_other_score"] is not None) / len([e for e in results if e["gen0_other_score"] is not None])
    avg_overall_other = sum(entry["overall_other_score"] for entry in results if entry["overall_other_score"] is not None) / len([e for e in results if e["overall_other_score"] is not None])

    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
        if score_key == "Score as %":
            fieldnames = ["avg_gen0_best_score_score_as_%", "avg_overall_best_score_as_%", "avg_difference", "avg_gen0_final_score", "avg_overall_final_score"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow({
                "avg_gen0_best_score_score_as_%": avg_gen0,
                "avg_overall_best_score_as_%": avg_overall,
                "avg_difference": avg_difference,
                "avg_gen0_final_score": avg_gen0_other,
                "avg_overall_final_score": avg_overall_other,
            })
        else:  # "Final score"
            fieldnames = ["avg_gen0_best_score_final_score", "avg_overall_best_final_score", "avg_difference", "avg_gen0_score_as_%", "avg_overall_score_as_%"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow({
                "avg_gen0_best_score_final_score": avg_gen0,
                "avg_overall_best_final_score": avg_overall,
                "avg_difference": avg_difference,
                "avg_gen0_score_as_%": avg_gen0_other,
                "avg_overall_score_as_%": avg_overall_other,
            })


def process_synthetic_folder(
    input_dir: str,
    score_keys: Optional[Iterable[str]] = None,
) -> Dict[str, List[Dict[str, object]]]:
    pickle_files = find_pickle_files(input_dir)
    if not pickle_files:
        raise FileNotFoundError(f"No .pkl files found in {input_dir}")

    score_keys = list(score_keys or DEFAULT_SCORE_KEYS)
    all_results = {score_key: [] for score_key in score_keys}

    for pickle_path in pickle_files:
        generations = load_pickle(pickle_path)
        diff_data_dict = extract_generation_differences(generations, score_keys=score_keys)
        for score_key in score_keys:
            diff_data = diff_data_dict.get(score_key)
            if diff_data:
                all_results[score_key].append(
                    {
                        "pickle_file": os.path.relpath(pickle_path, input_dir),
                        "gen0_best_score": diff_data["gen0_best_score"],
                        "gen0_other_score": diff_data["gen0_other_score"],
                        "overall_best_score": diff_data["overall_best_score"],
                        "overall_other_score": diff_data["overall_other_score"],
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

    population_dirs = list(folder_map.values())

    all_results = {score_key: [] for score_key in args.score_keys}

    for pop_dir in population_dirs:
        if not os.path.exists(pop_dir):
            print(f"Directory {pop_dir} does not exist, skipping.")
            continue

        results_dict = process_synthetic_folder(pop_dir, score_keys=args.score_keys)
        dir_name = os.path.basename(pop_dir)
        for score_key in args.score_keys:
            if score_key in results_dict:
                # Add population to each entry
                for entry in results_dict[score_key]:
                    entry["population"] = dir_name
                all_results[score_key].extend(results_dict[score_key])

    # Write the four outputs
    for score_key in args.score_keys:
        if not all_results[score_key]:
            print(f"No data for {score_key}, skipping.")
            continue

        safe_score_key = score_key.replace(" ", "_").replace("%", "percent")
        detailed_csv = f"Results/generation_differences_{safe_score_key}.csv"
        averages_csv = f"Results/averages_{safe_score_key}.csv"

        write_csv(all_results[score_key], detailed_csv, score_key)
        write_averages_csv(all_results[score_key], averages_csv, score_key)

        print(f"Processed for {score_key}: {len(all_results[score_key])} total entries to {detailed_csv} and {averages_csv}")


if __name__ == "__main__":
    main()