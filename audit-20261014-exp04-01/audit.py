from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import statistics
import sys
from collections import Counter
from pathlib import Path

sys.dont_write_bytecode = True
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["USE_TORCH"] = "0"
os.environ["CUDA_VISIBLE_DEVICES"] = ""
BASE = Path("/home/ma-user/work/dataset/summary-fact-probe")
PROJECT = BASE / "meeting-fact-probe"
DESTINATION = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT / "src"))

from meeting_probe.common import canonical_hash, load_json, render, sha256_file
from meeting_probe.context import TokenBudget
from meeting_probe.data import _pilot_ids
from meeting_probe.generate import _generation_request, _validate_facts, check_generation, select_rows

FOCUS = ["meeting-0078", "meeting-0290", "meeting-0571", "meeting-0761",
         "meeting-1696", "meeting-1719", "meeting-1776", "meeting-0550",
         "meeting-0064", "meeting-0136", "meeting-0400", "meeting-1020", "meeting-1226"]


def save_json(name, value):
    with (DESTINATION / name).open("x", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def save_csv(name, rows):
    with (DESTINATION / name).open("x", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def normalized(text):
    return re.sub(r"\s+", " ", text.casefold()).strip().rstrip(".")


def distribution(values):
    return {"median": statistics.median(values), "min": min(values), "max": max(values)}


def collect_evidence():
    import ast
    import importlib.metadata

    rows = {row["sample_id"]: row for row in select_rows(PROJECT / "data/processed/meetings.jsonl", "all")}
    patterns = {
        "meeting-0064": [r"four o", r"thursday", r"Grad E.*constructions"],
        "meeting-0290": [r"274", r"meet.{0,80}cost", r"duty.{0,80}raise"],
        "meeting-0400": [r"3\.5", r"100,000"],
        "meeting-1020": [r"mid.September", r"1\.25 million", r"\$600", r"Alexis Brunelle.Duceppe:"],
        "meeting-0761": [r"border.{0,80}restrict", r"extended", r"executive compensation", r"\$300", r"\$200"],
    }
    source_evidence = []
    for sample_id, queries in patterns.items():
        source = rows[sample_id]["conversation"]
        for query in queries:
            matches = list(re.finditer(query, source, re.IGNORECASE))
            for match in matches:
                start = max(0, match.start() - 220)
                end = min(len(source), match.end() + 600)
                source_evidence.append({"sample_id": sample_id, "query": query, "start": start,
                                        "end": end, "text": source[start:end]})
    for sample_id in ("meeting-0078", "meeting-1696", "meeting-1719", "meeting-0064"):
        source = rows[sample_id]["conversation"]
        source_evidence.append({"sample_id": sample_id, "query": "last_2500_chars",
                                "start": max(0, len(source) - 2500), "end": len(source), "text": source[-2500:]})
    execution = {"logs": [], "models": [], "diagnostic_package_versions": {}}
    for run in ("exp04-2gpu", "exp04-2gpu-pressure"):
        for role in ("small", "large"):
            path = BASE / "runs" / run / "logs" / f"vllm-{role}.log"
            lines = path.read_text(encoding="utf-8").splitlines()
            starts, traffic, anomalies = [], [], []
            for number, line in enumerate(lines, 1):
                if "non-default args: " in line:
                    values = ast.literal_eval(line.split("non-default args: ", 1)[1])
                    starts.append({"splitlines_line": number,
                                   "time": re.search(r"\d\d-\d\d \d\d:\d\d:\d\d", line).group(0),
                                   "settings": {name: values.get(name) for name in (
                                       "model", "served_model_name", "dtype", "seed", "rope_scaling", "max_model_len",
                                       "tensor_parallel_size", "max_num_seqs", "max_num_batched_tokens",
                                       "enable_prefix_caching", "enable_chunked_prefill", "generation_config", "gpu_memory_utilization")}})
                if match := re.search(r"Running: (\d+) reqs, Waiting: (\d+) reqs", line):
                    traffic.append(tuple(map(int, match.groups())))
                if re.search(r"ERROR|Traceback|CUDA out of memory|NCCL error|Abort|abort", line):
                    anomalies.append({"splitlines_line": number, "text": line[:500]})
            execution["logs"].append({"run": run, "role": role, "sha256": sha256_file(path), "starts": starts,
                                      "max_running": max(active for active, waiting in traffic),
                                      "max_running_plus_waiting": max(active + waiting for active, waiting in traffic),
                                      "http_status_counts": dict(Counter(re.findall(
                                          r'POST /v1/chat/completions HTTP/1.1" (\d+)', "\n".join(lines)))),
                                      "anomalies": anomalies})
    for role, model in load_json(BASE / "runs/exp04-2gpu/protocol-snapshot.json")["experiment"]["models"].items():
        path = (PROJECT / model["path"]).resolve()
        metadata = list((path / ".cache/huggingface/download").glob("*.metadata"))
        configuration = load_json(path / "config.json")
        execution["models"].append({"role": role, "path": str(path), "snapshot_revision": model["revision"],
                                     "metadata_count": len(metadata),
                                     "metadata_commits": sorted({item.read_text().splitlines()[0] for item in metadata}),
                                     "configuration": {name: configuration.get(name) for name in (
                                         "architectures", "model_type", "max_position_embeddings", "rope_scaling", "torch_dtype")},
                                     "weight_bytes_verified": False})
    for package in ("transformers", "tokenizers", "vllm", "httpx"):
        execution["diagnostic_package_versions"][package] = importlib.metadata.version(package)
    save_json("source_evidence.json", source_evidence)
    save_json("execution_evidence.json", execution)
    print("Saved source_evidence.json and execution_evidence.json")


def main():
    pilot_path = BASE / "runs/exp04-2gpu"
    pressure_path = BASE / "runs/exp04-2gpu-pressure"
    snapshot = load_json(pilot_path / "protocol-snapshot.json")
    pressure_snapshot = load_json(pressure_path / "protocol-snapshot.json")
    data_path = PROJECT / "data/processed/meetings.jsonl"
    rows = select_rows(data_path, "pilot")
    all_rows = select_rows(data_path, "all")
    row_by_id = {row["sample_id"]: row for row in all_rows}
    assert len(row_by_id) == len(all_rows)
    assert len(rows) == 30
    assert {row["sample_id"] for row in rows} == _pilot_ids(all_rows, 6, 42)
    generation = snapshot["experiment"]["generation"]
    prompts = snapshot["prompts"]
    requests = {
        row["sample_id"]: _generation_request(
            prompts["generation_system"], render(prompts["extract"], SOURCE=row["conversation"]),
            generation, generation["max_tokens_extract"], stage="extract",
        ) for row in all_rows
    }
    budgets = {role: TokenBudget.from_path(PROJECT / model["path"], snapshot["profile"]["max_model_len"])
               for role, model in snapshot["experiment"]["models"].items()}
    records, inventory, errors = {}, [], []
    for label, run_path in [("pilot", pilot_path), ("pressure", pressure_path)]:
        run_snapshot = load_json(run_path / "protocol-snapshot.json")
        chosen_rows = rows if label == "pilot" else [row_by_id[sample_id] for sample_id in sorted({
            path.stem for role in ("small", "large")
            for path in (run_path / "generation/facts" / role).glob("*.json")
            if not path.name.endswith(".error.json")
        })]
        for row in chosen_rows:
            sample_id = row["sample_id"]
            request = requests[sample_id]
            body = {"messages": [{"role": "system", "content": request["system"]},
                                 {"role": "user", "content": request["user"]}], "max_tokens": request["max_tokens"]}
            for role in ("small", "large"):
                path = run_path / "generation/facts" / role / f"{sample_id}.json"
                if not path.is_file():
                    continue
                record = load_json(path)
                _validate_facts(record["output"])
                records[label, sample_id, role] = record
                facts = record["output"]["key_facts"]
                metadata = record["metadata"]
                usage = metadata["usage"]
                local_count = budgets[role].count(body)
                parameters = {name: request[name] for name in (
                    "temperature", "top_p", "repetition_penalty", "seed", "max_tokens")}
                parameters.update({name: value for name, value in request["extra_body"].items()
                                   if name != "chat_template_kwargs"})
                inventory.append({
                    "run": label, "sample_id": sample_id, "dataset": row["dataset"], "model": role,
                    "fact_count": len(facts), "fact_chars": sum(map(len, facts)),
                    "mean_fact_chars": round(sum(map(len, facts)) / len(facts), 3),
                    "exact_duplicates": len(facts) - len(set(facts)),
                    "normalized_duplicates": len(facts) - len({normalized(fact) for fact in facts}),
                    "finish_reason": metadata["finish_reason"], "prompt_tokens": usage["prompt_tokens"],
                    "completion_tokens": usage["completion_tokens"], "local_tokens_recomputed": local_count,
                    "local_tokens_recorded": metadata.get("input_tokens_local"),
                    "token_counts_match": local_count == usage["prompt_tokens"] == metadata.get("input_tokens_local"),
                    "context_limit": metadata.get("context_limit"), "request_hash": record["request_hash"],
                    "request_hash_matches": record["request_hash"] == canonical_hash(request),
                    "actual_request_parameters": json.dumps(metadata.get("request_parameters"), sort_keys=True),
                    "parameters_match": metadata.get("request_parameters") == parameters,
                    "response_model": metadata.get("model"), "attempts": metadata.get("attempts"),
                    "gold_fact_count": len(row["key_facts"]), "source_chars": len(row["conversation"]),
                    "success_file": str(path), "error_file_present": path.with_suffix(".error.json").is_file(),
                })
        for role in ("small", "large"):
            for path in sorted((run_path / "generation/facts" / role).glob("*.error.json")):
                record = load_json(path)
                sample_id = path.name.removesuffix(".error.json")
                metadata = record.get("metadata") or {}
                response = record.get("response")
                content = (response["choices"][0]["message"]["content"] if isinstance(response, dict) else response)
                errors.append({"run": label, "sample_id": sample_id, "model": role, "path": str(path),
                               "problem": record.get("problem"), "request_hash": record.get("request_hash"),
                               "hash_matches": record.get("request_hash") == canonical_hash(requests[sample_id]),
                               "metadata": metadata, "response_content": content,
                               "request": {key: value for key, value in record.get("request", {}).items()
                                           if key in {"model", "messages", "max_tokens", "temperature", "top_p", "top_k",
                                                      "min_p", "repetition_penalty", "presence_penalty", "seed",
                                                      "response_format", "stream", "chat_template_kwargs"}}})
    pilot_inventory = [item for item in inventory if item["run"] == "pilot"]
    save_csv("pilot_stats.csv", pilot_inventory)
    save_csv("all_extraction_stats.csv", inventory)
    save_json("raw_facts.json", [{"run": label, "sample_id": sample_id, "model": role,
                                  "dataset": row_by_id[sample_id]["dataset"],
                                  "key_facts": record["output"]["key_facts"], "metadata": record["metadata"],
                                  "request_hash": record["request_hash"]}
                                 for (label, sample_id, role), record in records.items()])
    save_json("error_evidence.json", errors)
    comparison = []
    for row in rows:
        for role in ("small", "large"):
            sample_id = row["sample_id"]
            if ("pressure", sample_id, role) not in records:
                continue
            first = records["pressure", sample_id, role]
            last = records["pilot", sample_id, role]
            comparison.append({"sample_id": sample_id, "dataset": row["dataset"], "model": role,
                               "pressure_facts": len(first["output"]["key_facts"]),
                               "pilot_facts": len(last["output"]["key_facts"]),
                               "pressure_completion_tokens": first["metadata"]["usage"]["completion_tokens"],
                               "pilot_completion_tokens": last["metadata"]["usage"]["completion_tokens"],
                               "hash_equal": first["request_hash"] == last["request_hash"],
                               "parameters_equal": first["metadata"].get("request_parameters") == last["metadata"].get("request_parameters"),
                               "prompt_tokens_equal": first["metadata"]["usage"]["prompt_tokens"] == last["metadata"]["usage"]["prompt_tokens"],
                               "content_equal": first["output"] == last["output"]})
    save_csv("pressure_comparison.csv", comparison)
    manifest = load_json(data_path.parent / "manifest.json")
    raw_path = Path(manifest["source"])
    raw_matches = None
    if raw_path.is_file():
        raw = load_json(raw_path)
        raw_matches = all(row["conversation"] == raw[row["original_index"]]["conversation"]
                          and row["dataset"] == raw[row["original_index"]]["dataset"]
                          and row["key_facts"] == raw[row["original_index"]]["key_facts"] for row in all_rows)
    summary = {
        "pilot_count": len(rows), "pilot_datasets": dict(Counter(row["dataset"] for row in rows)),
        "snapshot_equal": snapshot == pressure_snapshot,
        "current_configs_equal": {key: load_json(PROJECT / "configs" / name) == snapshot[key]
                                  for key, name in [("experiment", "experiment.json"), ("prompts", "prompts.json"),
                                                    ("profile", "profile-2gpu.json")]},
        "processed_sha256": sha256_file(data_path), "raw_source_exists": raw_path.is_file(),
        "raw_sha256_matches": sha256_file(raw_path) == manifest["sha256"] if raw_path.is_file() else None,
        "all_processed_rows_match_raw": raw_matches,
        "generation_check": check_generation(rows, pilot_path, prompts, generation),
        "all_hashes_match": all(item["request_hash_matches"] for item in inventory),
        "all_token_counts_match": all(item["token_counts_match"] for item in inventory),
        "all_parameters_match": all(item["parameters_match"] for item in inventory),
        "models": {}, "by_dataset": [],
        "pressure_common_results": len(comparison), "pressure_content_equal": sum(item["content_equal"] for item in comparison),
        "errors": [{key: item[key] for key in ("run", "sample_id", "model", "problem", "hash_matches")} for item in errors],
    }
    for role in ("small", "large"):
        group = [item for item in pilot_inventory if item["model"] == role]
        summary["models"][role] = {"facts": distribution([item["fact_count"] for item in group]),
                                   "completion_tokens": distribution([item["completion_tokens"] for item in group]),
                                   "prompt_tokens": distribution([item["prompt_tokens"] for item in group]),
                                   "two_fact_count": sum(item["fact_count"] == 2 for item in group),
                                   "two_fact_share": sum(item["fact_count"] == 2 for item in group) / len(group),
                                   "exact_duplicates_total": sum(item["exact_duplicates"] for item in group),
                                   "normalized_duplicates_total": sum(item["normalized_duplicates"] for item in group)}
        for dataset in sorted(summary["pilot_datasets"]):
            subset = [item for item in group if item["dataset"] == dataset]
            summary["by_dataset"].append({"dataset": dataset, "model": role,
                                          "facts": distribution([item["fact_count"] for item in subset]),
                                          "two_fact_count": sum(item["fact_count"] == 2 for item in subset)})
    save_json("summary.json", summary)
    for sample_id in FOCUS:
        row = row_by_id[sample_id]
        with (DESTINATION / f"{sample_id}.review.txt").open("x", encoding="utf-8") as handle:
            handle.write(f"{sample_id} dataset={row['dataset']} source_chars={len(row['conversation'])}\n")
            for label, role in [("pilot", "small"), ("pilot", "large"), ("pressure", "small"), ("pressure", "large")]:
                record = records.get((label, sample_id, role))
                if record is not None:
                    handle.write(f"\n{label.upper()} {role.upper()} FACTS\n")
                    for number, fact in enumerate(record["output"]["key_facts"], 1):
                        handle.write(f"{number}. {fact}\n")
            handle.write("\nREFERENCE FACTS (NOT EXHAUSTIVE GROUND TRUTH)\n")
            for number, fact in enumerate(row["key_facts"], 1):
                handle.write(f"{number}. {fact}\n")
            handle.write("\nSOURCE (EXACT CONTIGUOUS 800-CHAR BLOCKS; ZERO-BASED OFFSETS)\n")
            for offset in range(0, len(row["conversation"]), 800):
                handle.write(f"\n[C{offset:06d}]\n{row['conversation'][offset:offset + 800]}\n")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print("COMPARISON", json.dumps(comparison, ensure_ascii=False))


if __name__ == "__main__":
    if sys.argv[1:] == ["--evidence-only"]:
        collect_evidence()
    elif not sys.argv[1:]:
        main()
    else:
        raise SystemExit("Usage: audit.py [--evidence-only]; outputs are created exclusively, never overwritten")