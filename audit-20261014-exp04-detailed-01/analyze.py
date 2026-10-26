from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import random
import statistics
import sys
from collections import Counter
from pathlib import Path

sys.dont_write_bytecode = True
os.environ["NLTK_DATA"] = "/home/ma-user/work/dataset/summary-fact-probe/cache/nltk"
BASE = Path("/home/ma-user/work/dataset/summary-fact-probe")
PROJECT = BASE / "meeting-fact-probe"
RUN = (PROJECT / "runs/exp04-2gpu").resolve()
DESTINATION = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT / "src"))

from meeting_probe.common import canonical_hash, load_json, numbered, render, sha256_file
from meeting_probe.evaluate import (
    _request, _sentences, _validate_decompose, _validate_match, _validate_verify, summary_metrics,
)
from meeting_probe.generate import ARMS, _generation_request, _validate_facts, _validate_summary, select_rows
from meeting_probe.report import METRICS, paired_bootstrap

CONTRASTS = [
    ("direct_l", "direct_s"),
    ("s_to_s", "direct_s"), ("l_to_s", "direct_s"), ("gold_to_s", "direct_s"),
    ("s_to_l", "direct_l"), ("l_to_l", "direct_l"), ("gold_to_l", "direct_l"),
    ("l_to_s", "s_to_s"), ("l_to_l", "s_to_l"),
    ("s_to_l", "s_to_s"), ("l_to_l", "l_to_s"), ("gold_to_l", "gold_to_s"),
    ("gold_to_s", "s_to_s"), ("gold_to_s", "l_to_s"),
    ("gold_to_l", "s_to_l"), ("gold_to_l", "l_to_l"),
]


def dump_json(name, value):
    with (DESTINATION / name).open("x", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2, allow_nan=False)
        handle.write("\n")


def dump_csv(name, records):
    with (DESTINATION / name).open("x", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)


def describe(values):
    quartiles = statistics.quantiles(values, n=4, method="inclusive") if len(values) > 1 else [values[0]] * 3
    return {"n": len(values), "mean": statistics.fmean(values), "median": statistics.median(values),
            "sd": statistics.stdev(values) if len(values) > 1 else 0.0,
            "min": min(values), "q1": quartiles[0], "q3": quartiles[2], "max": max(values)}


def ranks(values):
    ordered = sorted(set(values))
    assigned = {}
    position = 1
    for value in ordered:
        count = values.count(value)
        assigned[value] = position + (count - 1) / 2
        position += count
    return [assigned[value] for value in values]


def correlation(left, right, rank=False):
    if rank:
        left, right = ranks(left), ranks(right)
    if len(set(left)) < 2 or len(set(right)) < 2:
        return None
    return statistics.correlation(left, right)


def markdown_table(headers, records):
    return ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |",
            *["| " + " | ".join(map(str, record)) + " |" for record in records]]


def percentage(value):
    return f"{value * 100:.2f}%"


def read_checked(path, request, validator, checks, kind):
    record = load_json(path)
    assert record["status"] == "ok", str(path)
    assert record["metadata"]["finish_reason"] == "stop", str(path)
    validator(record["output"])
    assert record["request_hash"] == canonical_hash(request), f"Request hash mismatch: {path}"
    checks.append({"path": str(path.relative_to(RUN)), "kind": kind, "sha256": sha256_file(path),
                   "request_hash_matches": True, "finish_reason": record["metadata"]["finish_reason"],
                   "response_model": record["metadata"].get("model"),
                   "attempts": record["metadata"].get("attempts"),
                   "prompt_tokens": record["metadata"].get("usage", {}).get("prompt_tokens"),
                   "completion_tokens": record["metadata"].get("usage", {}).get("completion_tokens")})
    return record


def main():
    snapshot = load_json(RUN / "protocol-snapshot.json")
    experiment, prompts = snapshot["experiment"], snapshot["prompts"]
    generation, judge = experiment["generation"], experiment["judge"]
    rows = select_rows(PROJECT / "data/processed/meetings.jsonl", "pilot")
    all_rows = select_rows(PROJECT / "data/processed/meetings.jsonl", "all")
    assert len(rows) == 30
    checks, fact_records, summary_records, evidence, mismatches = [], [], [], {}, []
    previous = {(item["sample_id"], item["model"]): item["key_facts"] for item in load_json(
        BASE / "audit-20261014-exp04-01/raw_facts.json") if item["run"] == "pilot"}
    for row in rows:
        sample_id, dataset, references = row["sample_id"], row["dataset"], row["key_facts"]
        evidence[sample_id] = {"dataset": dataset, "reference_facts": references,
                               "source_chars": len(row["conversation"]), "facts": {}, "summaries": {}}
        fact_lists = {}
        for role in ("small", "large"):
            request = _generation_request(prompts["generation_system"], render(prompts["extract"], SOURCE=row["conversation"]),
                                          generation, generation["max_tokens_extract"], stage="extract")
            fact_path = RUN / "generation/facts" / role / f"{sample_id}.json"
            output = read_checked(fact_path, request, _validate_facts, checks, "generation_facts")
            facts = output["output"]["key_facts"]
            fact_lists[role] = facts
            assert facts == previous[sample_id, role], f"Extraction changed since audit: {sample_id}/{role}"
            match_request = _request(judge, prompts, render(prompts["match"], REFERENCE_FACTS=numbered(references),
                                                           CANDIDATE_UNITS=numbered(facts)))
            match = read_checked(RUN / "evaluation/facts" / role / "match" / f"{sample_id}.json", match_request,
                                 lambda value: _validate_match(value, len(references), len(facts)), checks, "judge_fact_match")
            verify_request = _request(judge, prompts, render(prompts["verify"], EVIDENCE=row["conversation"], CLAIMS=numbered(facts)))
            verify = read_checked(RUN / "evaluation/facts" / role / "verify" / f"{sample_id}.json", verify_request,
                                  lambda value: _validate_verify(value, len(facts)), checks, "judge_fact_verify")
            covered = {item["fact_idx"] for item in match["output"]["matches"] if item["align_unit_idx"] is not None}
            unsupported = [item["fact_idx"] for item in verify["output"]["verifications"] if item["conclusion"] != "supported"]
            metrics = load_json(RUN / "metrics/facts" / role / f"{sample_id}.json")
            computed = {"coverage": len(covered) / len(references), "support": (len(facts) - len(unsupported)) / len(facts),
                        "fact_count": len(facts), "character_count": sum(map(len, facts))}
            assert metrics["status"] == "ok" and metrics["sample_id"] == sample_id and metrics["dataset"] == dataset and metrics["source"] == role
            assert all(math.isclose(metrics[name], value, abs_tol=1e-12) for name, value in computed.items()), str(fact_path)
            fact_records.append({"sample_id": sample_id, "dataset": dataset, "source": role, "reference_count": len(references),
                                 "covered_reference_count": len(covered), "supported_count": len(facts) - len(unsupported),
                                 "unsupported_count": len(unsupported), **computed,
                                 "mean_fact_chars": sum(map(len, facts)) / len(facts), "exact_duplicate_count": len(facts) - len(set(facts)),
                                 "prompt_tokens": output["metadata"]["usage"]["prompt_tokens"],
                                 "completion_tokens": output["metadata"]["usage"]["completion_tokens"],
                                 "error_file_present": fact_path.with_suffix(".error.json").is_file(),
                                 "covered_reference_ids": json.dumps(sorted(covered)), "unsupported_fact_ids": json.dumps(unsupported)})
            evidence[sample_id]["facts"][role] = {"key_facts": facts, "covered_reference_ids": sorted(covered),
                                                "matches": match["output"]["matches"], "unsupported_ids": unsupported}
        for arm, (generator, fact_source) in ARMS.items():
            if fact_source is None:
                user = render(prompts["direct"], SOURCE=row["conversation"])
            else:
                auxiliary = references if fact_source == "gold" else fact_lists[fact_source]
                user = render(prompts["assisted"], SOURCE=row["conversation"], FACTS_JSON=json.dumps(auxiliary, ensure_ascii=False))
            request = _generation_request(prompts["generation_system"], user, generation, generation["max_tokens_summary"], stage="summary")
            summary_path = RUN / "generation/summaries" / arm / f"{sample_id}.json"
            output = read_checked(summary_path, request, _validate_summary, checks, "generation_summary")
            text = output["output"]["summary"]
            sentences = _sentences(text)
            match_request = _request(judge, prompts, render(prompts["match"], REFERENCE_FACTS=numbered(references),
                                                           CANDIDATE_UNITS=numbered(sentences)))
            match = read_checked(RUN / "evaluation/summaries" / arm / "match" / f"{sample_id}.json", match_request,
                                 lambda value: _validate_match(value, len(references), len(sentences)), checks, "judge_summary_match")
            decompose_request = _request(judge, prompts, render(prompts["decompose"], SUMMARY=text))
            decompose = read_checked(RUN / "evaluation/summaries" / arm / "decompose" / f"{sample_id}.json", decompose_request,
                                     _validate_decompose, checks, "judge_summary_decompose")
            claims = decompose["output"]["atomic_facts"]
            verify_request = _request(judge, prompts, render(prompts["verify"], EVIDENCE=row["conversation"], CLAIMS=numbered(claims)))
            verify = read_checked(RUN / "evaluation/summaries" / arm / "verify" / f"{sample_id}.json", verify_request,
                                  lambda value: _validate_verify(value, len(claims)), checks, "judge_summary_verify")
            computed = summary_metrics(len(sentences), len(references), match["output"]["matches"], verify["output"]["verifications"])
            metrics_path = RUN / "metrics/summaries" / arm / f"{sample_id}.json"
            metrics = load_json(metrics_path)
            assert metrics["status"] == "ok" and metrics["sample_id"] == sample_id and metrics["dataset"] == dataset and metrics["arm"] == arm
            assert metrics["sentence_count"] == len(sentences) and metrics["atomic_fact_count"] == len(claims)
            assert all(math.isclose(metrics[name], value, abs_tol=1e-12) for name, value in computed.items()), str(metrics_path)
            covered = {item["fact_idx"] for item in match["output"]["matches"] if item["align_unit_idx"] is not None}
            aligned = {item["align_unit_idx"] for item in match["output"]["matches"] if item["align_unit_idx"] is not None}
            unsupported = [item["fact_idx"] for item in verify["output"]["verifications"] if item["conclusion"] != "supported"]
            summary_records.append({"sample_id": sample_id, "dataset": dataset, "arm": arm, "generator": generator,
                                    "fact_source": fact_source or "none", "reference_count": len(references),
                                    "matched_reference_count": len(covered), "aligned_sentence_count": len(aligned),
                                    "sentence_count": len(sentences), "supported_claim_count": len(claims) - len(unsupported),
                                    "unsupported_claim_count": len(unsupported), "atomic_fact_count": len(claims), **computed,
                                    "summary_chars": len(text), "prompt_tokens": output["metadata"]["usage"]["prompt_tokens"],
                                    "completion_tokens": output["metadata"]["usage"]["completion_tokens"],
                                    "covered_reference_ids": json.dumps(sorted(covered)), "unsupported_claim_ids": json.dumps(unsupported)})
            evidence[sample_id]["summaries"][arm] = {"summary": text, "sentences": sentences, "atomic_facts": claims,
                                                     "covered_reference_ids": sorted(covered), "matches": match["output"]["matches"],
                                                     "unsupported_ids": unsupported}
    assert len(fact_records) == 60 and len(summary_records) == 240 and len(checks) == 1140
    dump_csv("fact_metrics_recomputed.csv", fact_records)
    dump_csv("summary_metrics_recomputed.csv", summary_records)
    dump_csv("cache_validation.csv", checks)
    dump_json("sample_evidence.json", evidence)
    summary_index = {(item["sample_id"], item["arm"]): item for item in summary_records}
    fact_index = {(item["sample_id"], item["source"]): item for item in fact_records}
    datasets = sorted({row["dataset"] for row in rows})
    populations = Counter(row["dataset"] for row in all_rows)
    aggregation = []
    for dataset in ("ALL", *datasets):
        for arm in ARMS:
            group = [item for item in summary_records if item["arm"] == arm and (dataset == "ALL" or item["dataset"] == dataset)]
            aggregate = {"dataset": dataset, "arm": arm, "n": len(group)}
            for metric in METRICS:
                aggregate.update({f"{metric}_{name}": value for name, value in describe([item[metric] for item in group]).items() if name != "n"})
            aggregate.update({"completeness_micro": sum(item["matched_reference_count"] for item in group) / sum(item["reference_count"] for item in group),
                              "conciseness_micro": sum(item["aligned_sentence_count"] for item in group) / sum(item["sentence_count"] for item in group),
                              "faithfulness_micro": sum(item["supported_claim_count"] for item in group) / sum(item["atomic_fact_count"] for item in group),
                              "total_reference_count": sum(item["reference_count"] for item in group),
                              "total_matched_reference_count": sum(item["matched_reference_count"] for item in group),
                              "total_sentence_count": sum(item["sentence_count"] for item in group),
                              "total_atomic_fact_count": sum(item["atomic_fact_count"] for item in group),
                              "total_unsupported_claim_count": sum(item["unsupported_claim_count"] for item in group),
                              "all_supported_summary_count": sum(item["unsupported_claim_count"] == 0 for item in group),
                              "mean_completion_tokens": statistics.fmean(item["completion_tokens"] for item in group),
                              "median_completion_tokens": statistics.median(item["completion_tokens"] for item in group),
                              "mean_summary_chars": statistics.fmean(item["summary_chars"] for item in group),
                              "mean_sentence_count": statistics.fmean(item["sentence_count"] for item in group)})
            aggregation.append(aggregate)
    dump_csv("summary_distribution_by_source.csv", aggregation)
    fact_aggregation = []
    for dataset in ("ALL", *datasets):
        for role in ("small", "large"):
            group = [item for item in fact_records if item["source"] == role and (dataset == "ALL" or item["dataset"] == dataset)]
            aggregate = {"dataset": dataset, "source": role, "n": len(group)}
            for metric in ("coverage", "support", "fact_count", "character_count", "completion_tokens"):
                aggregate.update({f"{metric}_{name}": value for name, value in describe([item[metric] for item in group]).items() if name != "n"})
            aggregate.update({"coverage_micro": sum(item["covered_reference_count"] for item in group) / sum(item["reference_count"] for item in group),
                              "support_micro": sum(item["supported_count"] for item in group) / sum(item["fact_count"] for item in group),
                              "total_fact_count": sum(item["fact_count"] for item in group),
                              "total_covered_reference_count": sum(item["covered_reference_count"] for item in group),
                              "total_reference_count": sum(item["reference_count"] for item in group),
                              "total_unsupported_count": sum(item["unsupported_count"] for item in group),
                              "two_fact_count": sum(item["fact_count"] == 2 for item in group)})
            fact_aggregation.append(aggregate)
    dump_csv("fact_distribution_by_source.csv", fact_aggregation)
    contrasts, per_sample_contrasts = [], []
    for dataset in ("ALL", *datasets):
        selected = [row for row in rows if dataset == "ALL" or row["dataset"] == dataset]
        for left_arm, right_arm in CONTRASTS:
            for metric_index, metric in enumerate(METRICS):
                left = [summary_index[row["sample_id"], left_arm][metric] for row in selected]
                right = [summary_index[row["sample_id"], right_arm][metric] for row in selected]
                differences = [first - second for first, second in zip(left, right)]
                observed, lower, upper = paired_bootstrap(left, right, 2000, 0.95, 42 + metric_index)
                contributions = sorted(zip(differences, [row["sample_id"] for row in selected]))
                leave_one_out = [(sum(differences) - difference) / (len(differences) - 1) for difference in differences]
                contrasts.append({"dataset": dataset, "contrast": f"{left_arm} - {right_arm}", "metric": metric,
                                  "n": len(selected), "mean_difference": observed, "median_difference": statistics.median(differences),
                                  "ci_lower": lower, "ci_upper": upper, "wins": sum(value > 1e-12 for value in differences),
                                  "ties": sum(abs(value) <= 1e-12 for value in differences), "losses": sum(value < -1e-12 for value in differences),
                                  "min_difference": min(differences), "max_difference": max(differences),
                                  "leave_one_out_mean_min": min(leave_one_out), "leave_one_out_mean_max": max(leave_one_out),
                                  "most_negative_sample": contributions[0][1], "most_positive_sample": contributions[-1][1]})
                if dataset == "ALL":
                    per_sample_contrasts.extend({"sample_id": row["sample_id"], "dataset": row["dataset"],
                                                 "contrast": f"{left_arm} - {right_arm}", "metric": metric,
                                                 "difference": difference} for row, difference in zip(selected, differences))
    dump_csv("paired_contrasts.csv", contrasts)
    dump_csv("per_sample_contrasts.csv", per_sample_contrasts)
    reference_transitions, unsupported_claims, fact_alignment, summary_alignment = [], [], [], []
    for row in rows:
        sample_id = row["sample_id"]
        for role, item in evidence[sample_id]["facts"].items():
            for match in item["matches"]:
                index = match["align_unit_idx"]
                fact_alignment.append({"sample_id": sample_id, "dataset": row["dataset"], "source": role,
                                       "reference_id": match["fact_idx"] + 1, "reference_text": row["key_facts"][match["fact_idx"]],
                                       "matched_fact_id": index + 1 if index is not None else "", "matched_fact_text": item["key_facts"][index] if index is not None else ""})
            for index in item["unsupported_ids"]:
                unsupported_claims.append({"sample_id": sample_id, "dataset": row["dataset"], "kind": "extraction", "arm_or_source": role,
                                           "claim_id": index + 1, "claim": item["key_facts"][index]})
        for arm, item in evidence[sample_id]["summaries"].items():
            for match in item["matches"]:
                index = match["align_unit_idx"]
                summary_alignment.append({"sample_id": sample_id, "dataset": row["dataset"], "arm": arm,
                                          "reference_id": match["fact_idx"] + 1, "reference_text": row["key_facts"][match["fact_idx"]],
                                          "matched_sentence_id": index + 1 if index is not None else "", "matched_sentence": item["sentences"][index] if index is not None else ""})
            for index in item["unsupported_ids"]:
                unsupported_claims.append({"sample_id": sample_id, "dataset": row["dataset"], "kind": "summary", "arm_or_source": arm,
                                           "claim_id": index + 1, "claim": item["atomic_facts"][index]})
            source = ARMS[arm][1]
            if source not in ("small", "large"):
                continue
            supplied = set(evidence[sample_id]["facts"][source]["covered_reference_ids"])
            retained = set(item["covered_reference_ids"])
            reference_transitions.append({"sample_id": sample_id, "dataset": row["dataset"], "arm": arm, "fact_source": source,
                                          "extraction_matched": len(supplied), "summary_matched": len(retained),
                                          "both_matched": len(supplied & retained), "summary_only_matched": len(retained - supplied),
                                          "extraction_only_matched": len(supplied - retained),
                                          "summary_only_ids": json.dumps(sorted(retained - supplied)),
                                          "extraction_only_ids": json.dumps(sorted(supplied - retained))})
    dump_csv("reference_transitions.csv", reference_transitions)
    dump_csv("judge_unsupported_claims.csv", unsupported_claims)
    dump_csv("fact_reference_alignment.csv", fact_alignment)
    dump_csv("summary_reference_alignment.csv", summary_alignment)
    correlations = []
    for role in ("small", "large"):
        group = [item for item in fact_records if item["source"] == role]
        for left_name, right_name in [("fact_count", "coverage"), ("fact_count", "support"), ("prompt_tokens", "coverage")]:
            correlations.append({"group": role, "left": left_name, "right": right_name,
                                 "n": len(group), "pearson": correlation([item[left_name] for item in group], [item[right_name] for item in group]),
                                 "spearman": correlation([item[left_name] for item in group], [item[right_name] for item in group], True)})
        for generator in ("small", "large"):
            arm = f"{'s' if role == 'small' else 'l'}_to_{'s' if generator == 'small' else 'l'}"
            correlations.append({"group": arm, "left": "extraction_coverage", "right": "summary_completeness", "n": len(rows),
                                 "pearson": correlation([fact_index[row["sample_id"], role]["coverage"] for row in rows],
                                                        [summary_index[row["sample_id"], arm]["completeness"] for row in rows]),
                                 "spearman": correlation([fact_index[row["sample_id"], role]["coverage"] for row in rows],
                                                         [summary_index[row["sample_id"], arm]["completeness"] for row in rows], True)})
    for arm in ARMS:
        group = [item for item in summary_records if item["arm"] == arm]
        correlations.append({"group": arm, "left": "completion_tokens", "right": "completeness", "n": len(group),
                             "pearson": correlation([item["completion_tokens"] for item in group], [item["completeness"] for item in group]),
                             "spearman": correlation([item["completion_tokens"] for item in group], [item["completeness"] for item in group], True)})
    fact_differences = [fact_index[row["sample_id"], "large"]["coverage"] - fact_index[row["sample_id"], "small"]["coverage"] for row in rows]
    for generator in ("s", "l"):
        differences = [summary_index[row["sample_id"], f"l_to_{generator}"]["completeness"] - summary_index[row["sample_id"], f"s_to_{generator}"]["completeness"] for row in rows]
        correlations.append({"group": f"l_to_{generator} - s_to_{generator}", "left": "large_minus_small_extraction_coverage",
                             "right": "large_minus_small_assisted_completeness", "n": len(rows),
                             "pearson": correlation(fact_differences, differences), "spearman": correlation(fact_differences, differences, True)})
    dump_json("correlations.json", correlations)
    cohorts = []
    two_ids = {item["sample_id"] for item in fact_records if item["source"] == "small" and item["fact_count"] == 2}
    for label, sample_ids in [("small_two_facts", two_ids), ("other_23", {row["sample_id"] for row in rows} - two_ids)]:
        for arm in ARMS:
            group = [item for item in summary_records if item["arm"] == arm and item["sample_id"] in sample_ids]
            cohorts.append({"cohort": label, "arm": arm, "n": len(group),
                            **{metric: statistics.fmean(item[metric] for item in group) for metric in METRICS},
                            "mean_completion_tokens": statistics.fmean(item["completion_tokens"] for item in group)})
    dump_csv("two_fact_cohort.csv", cohorts)
    source_lengths = [{"dataset": dataset, "pilot_count": 6, "population_count": populations[dataset],
                       "source_chars": describe([len(row["conversation"]) for row in rows if row["dataset"] == dataset]),
                       "prompt_tokens": describe([fact_index[row["sample_id"], "small"]["prompt_tokens"] for row in rows if row["dataset"] == dataset]),
                       "reference_counts": describe([len(row["key_facts"]) for row in rows if row["dataset"] == dataset])} for dataset in datasets]
    dump_json("source_characteristics.json", source_lengths)
    sensitivity = []
    for arm in ARMS:
        aggregate = next(item for item in aggregation if item["dataset"] == "ALL" and item["arm"] == arm)
        sensitivity.append({"arm": arm, **{f"{metric}_pilot_macro": aggregate[f"{metric}_mean"] for metric in METRICS},
                            **{f"{metric}_source_population_reweighted": sum(
                                populations[dataset] / len(all_rows) * next(item for item in aggregation if item["dataset"] == dataset and item["arm"] == arm)[f"{metric}_mean"]
                                for dataset in datasets) for metric in METRICS}})
    dump_csv("source_weight_sensitivity.csv", sensitivity)
    report_matches = []
    with (RUN / "report/summary-metrics.csv").open(encoding="utf-8-sig") as handle:
        for item in csv.DictReader(handle):
            aggregate = next(record for record in aggregation if record["arm"] == item["arm"] and record["dataset"] == item["dataset"])
            assert int(item["n"]) == aggregate["n"]
            assert all(math.isclose(float(item[metric]), aggregate[f"{metric}_mean"], abs_tol=1e-12) for metric in METRICS)
            report_matches.append((item["dataset"], item["arm"]))
    error_paths = [path for category in ("generation", "evaluation", "metrics/errors") for path in (RUN / category).rglob("*.json")
                   if ".ipynb_checkpoints" not in path.parts and (path.name.endswith(".error.json") or category == "metrics/errors")]
    errors = []
    for path in sorted(set(error_paths)):
        value = load_json(path)
        errors.append({"path": str(path.relative_to(RUN)), "status": value.get("status"), "problem": value.get("problem"),
                       "error": value.get("error"), "finish_reason": (value.get("metadata") or {}).get("finish_reason")})
    dump_json("preserved_errors.json", errors)
    validation = {"run": str(RUN), "pilot_count": len(rows), "fact_metrics_recomputed": len(fact_records),
                  "summary_metrics_recomputed": len(summary_records), "generation_hashes_verified": 300,
                  "judge_hashes_verified": 840, "existing_report_rows_verified": len(report_matches),
                  "processed_data_sha256": sha256_file(PROJECT / "data/processed/meetings.jsonl"),
                  "snapshot_sha256": sha256_file(RUN / "protocol-snapshot.json"),
                  "evaluation_status": load_json(RUN / "metrics/evaluation-status.json"),
                  "facts_unchanged_since_prior_audit": True, "total_reference_facts": sum(len(row["key_facts"]) for row in rows),
                  "total_judge_unsupported_claims": len(unsupported_claims), "errors_retained": len(errors)}
    dump_json("validation.json", validation)
    write_sample_reports(rows, fact_index, summary_index, evidence, per_sample_contrasts)
    write_source_reports(datasets, rows, fact_aggregation, aggregation, contrasts, summary_index, source_lengths)
    draw_figures(rows, fact_index, summary_index, aggregation)
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    print("OVERALL", json.dumps([item for item in aggregation if item["dataset"] == "ALL"], ensure_ascii=False))
    print("FACTS", json.dumps(fact_aggregation, ensure_ascii=False))
    print("CONTRASTS", json.dumps([item for item in contrasts if item["dataset"] == "ALL" and item["metric"] == "completeness"], ensure_ascii=False))


def write_sample_reports(rows, fact_index, summary_index, evidence, contrasts):
    lines = ["# 30个样本逐一分析", "", "所有百分比均为缓存评审结果，不是人工真值；事实/句子/主张编号从1开始。",
             "覆盖=匹配参考事实/参考总数；简洁=至少匹配一条参考事实的句子/全部句子；忠实=获评支持的分解主张/全部分解主张。",
             "未列入参考事实的有效内容不会提高覆盖或简洁指标。完整文本与匹配位于 sample_evidence.json 和 alignment CSV。", ""]
    for row in rows:
        sample_id = row["sample_id"]
        lines.extend([f"## {sample_id} · {row['dataset']}", "", f"原文{len(row['conversation'])}字符；参考事实{len(row['key_facts'])}条。", "", "### 抽取", ""])
        lines.extend(markdown_table(["来源", "事实数", "覆盖分子/分母", "覆盖", "支持分子/分母", "支持", "输出tokens"], [
            [role, fact_index[sample_id, role]["fact_count"], f"{fact_index[sample_id, role]['covered_reference_count']}/{len(row['key_facts'])}",
             percentage(fact_index[sample_id, role]["coverage"]), f"{fact_index[sample_id, role]['supported_count']}/{fact_index[sample_id, role]['fact_count']}",
             percentage(fact_index[sample_id, role]["support"]), fact_index[sample_id, role]["completion_tokens"]] for role in ("small", "large")]))
        lines.extend(["", "### 八组纪要", ""])
        lines.extend(markdown_table(["组", "覆盖分子/分母", "完整性", "有效句/总句", "简洁性", "支持主张/总主张", "忠实性", "输出tokens"], [
            [arm, f"{summary_index[sample_id, arm]['matched_reference_count']}/{len(row['key_facts'])}", percentage(summary_index[sample_id, arm]["completeness"]),
             f"{summary_index[sample_id, arm]['aligned_sentence_count']}/{summary_index[sample_id, arm]['sentence_count']}", percentage(summary_index[sample_id, arm]["conciseness"]),
             f"{summary_index[sample_id, arm]['supported_claim_count']}/{summary_index[sample_id, arm]['atomic_fact_count']}", percentage(summary_index[sample_id, arm]["faithfulness"]),
             summary_index[sample_id, arm]["completion_tokens"]] for arm in ARMS]))
        lines.extend(["", "### 本样本对比", ""])
        for left_arm, right_arm in CONTRASTS[:12]:
            first, second = summary_index[sample_id, left_arm], summary_index[sample_id, right_arm]
            differences = [100 * (first[metric] - second[metric]) for metric in METRICS]
            lines.append(f"- {left_arm} − {right_arm}：完整性{differences[0]:+.2f}、简洁性{differences[1]:+.2f}、忠实性{differences[2]:+.2f}个百分点；匹配参考数{first['matched_reference_count'] - second['matched_reference_count']:+d}。")
        for generator in ("s", "l"):
            baseline = set(evidence[sample_id]["summaries"][f"direct_{generator}"]["covered_reference_ids"])
            for source in ("s", "l", "gold"):
                arm = f"{source}_to_{generator}"
                covered = set(evidence[sample_id]["summaries"][arm]["covered_reference_ids"])
                gained, lost = sorted(covered - baseline), sorted(baseline - covered)
                lines.extend(["", f"**{arm}相对direct_{generator}新增/丢失的参考事实**：新增{len(gained)}条，丢失{len(lost)}条。"])
                for label, identifiers in [("新增", gained), ("丢失", lost)]:
                    for index in identifiers:
                        lines.append(f"- {label} R{index + 1}：{row['key_facts'][index]}")
        lines.extend(["", "### 评审判为不支持的主张", ""])
        found = False
        for kind, items in [("抽取", evidence[sample_id]["facts"]), ("纪要", evidence[sample_id]["summaries"])]:
            for name, item in items.items():
                claims = item["key_facts"] if kind == "抽取" else item["atomic_facts"]
                for index in item["unsupported_ids"]:
                    found = True
                    lines.append(f"- {kind} {name} #{index + 1}：{claims[index]}")
        if not found:
            lines.append("缓存评审未标记不支持主张；这不等于人工核验全部正确。")
        lines.extend(["", "### 直接纪要及模型自身事实辅助纪要原文", ""])
        for arm in ("direct_s", "s_to_s", "direct_l", "l_to_l"):
            lines.extend([f"**{arm}**", "", evidence[sample_id]["summaries"][arm]["summary"], ""])
    with (DESTINATION / "sample_analysis.md").open("x", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")


def write_source_reports(datasets, rows, fact_aggregation, aggregation, contrasts, summary_index, characteristics):
    lines = ["# 五来源分别分析", "", "每来源6条，含最短/最长及4条确定性随机中间样本。来源内bootstrap仅诊断，不作总体显著性认证。", ""]
    for dataset in datasets:
        features = next(item for item in characteristics if item["dataset"] == dataset)
        lines.extend([f"## {dataset}", "", f"pilot 6条，全量来源{features['population_count']}条；输入tokens中位数{features['prompt_tokens']['median']:.0f}，范围{features['prompt_tokens']['min']}–{features['prompt_tokens']['max']}；参考数中位数{features['reference_counts']['median']:.1f}，范围{features['reference_counts']['min']}–{features['reference_counts']['max']}。", "", "### 抽取", ""])
        lines.extend(markdown_table(["来源", "平均/中位事实数", "宏覆盖", "微覆盖", "宏支持", "不支持数/事实总数", "两条样本"], [
            [item["source"], f"{item['fact_count_mean']:.2f}/{item['fact_count_median']:.1f}", percentage(item["coverage_mean"]), percentage(item["coverage_micro"]),
             percentage(item["support_mean"]), f"{item['total_unsupported_count']}/{item['total_fact_count']}", item["two_fact_count"]]
            for item in fact_aggregation if item["dataset"] == dataset]))
        lines.extend(["", "### 八组纪要", ""])
        lines.extend(markdown_table(["组", "完整性均值/中位数/范围", "简洁性均值", "忠实性均值", "完全支持份数", "平均tokens"], [
            [item["arm"], f"{percentage(item['completeness_mean'])}/{percentage(item['completeness_median'])}/[{percentage(item['completeness_min'])},{percentage(item['completeness_max'])}]",
             percentage(item["conciseness_mean"]), percentage(item["faithfulness_mean"]), f"{item['all_supported_summary_count']}/6", f"{item['mean_completion_tokens']:.1f}"]
            for item in aggregation if item["dataset"] == dataset]))
        lines.extend(["", "### 完整性配对差值", ""])
        lines.extend(markdown_table(["对比", "平均/中位差值pp", "胜/平/负", "范围pp", "最大提升样本", "最大下降样本"], [
            [item["contrast"], f"{100 * item['mean_difference']:+.2f}/{100 * item['median_difference']:+.2f}", f"{item['wins']}/{item['ties']}/{item['losses']}",
             f"[{100 * item['min_difference']:+.2f},{100 * item['max_difference']:+.2f}]", item["most_positive_sample"], item["most_negative_sample"]]
            for item in contrasts if item["dataset"] == dataset and item["metric"] == "completeness"]))
        lines.extend(["", "### 该来源六个样本", ""])
        for row in rows:
            if row["dataset"] != dataset:
                continue
            sample_id = row["sample_id"]
            values = [summary_index[sample_id, arm]["completeness"] for arm in ARMS]
            best = max(values)
            best_arms = [arm for arm, value in zip(ARMS, values) if math.isclose(value, best)]
            small_gain = summary_index[sample_id, "s_to_s"]["completeness"] - summary_index[sample_id, "direct_s"]["completeness"]
            large_gain = summary_index[sample_id, "l_to_l"]["completeness"] - summary_index[sample_id, "direct_l"]["completeness"]
            lines.append(f"- {sample_id}：最佳参考覆盖组{','.join(best_arms)}={percentage(best)}；small自身辅助{100 * small_gain:+.2f}pp，large自身辅助{100 * large_gain:+.2f}pp。最佳覆盖不等于最佳总体质量。")
        lines.append("")
    with (DESTINATION / "source_analysis.md").open("x", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")


def draw_figures(rows, fact_index, summary_index, aggregation):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plotting
        import numpy
    except ImportError:
        return
    arms = list(ARMS)
    matrix = numpy.array([[summary_index[row["sample_id"], arm]["completeness"] for arm in arms] for row in rows])
    figure, axis = plotting.subplots(figsize=(10, 13))
    image = axis.imshow(matrix, vmin=0, vmax=1, cmap="YlGnBu", aspect="auto")
    axis.set_xticks(range(len(arms)), arms, rotation=35, ha="right")
    axis.set_yticks(range(len(rows)), [row["sample_id"] for row in rows])
    for row_index in range(len(rows)):
        for column_index in range(len(arms)):
            value = matrix[row_index, column_index]
            axis.text(column_index, row_index, f"{100 * value:.0f}", ha="center", va="center", fontsize=7,
                      color="white" if value > 0.7 else "black")
    axis.set_title("Reference completeness (%) by sample and arm")
    figure.colorbar(image, ax=axis, label="Reference completeness")
    figure.tight_layout()
    path = DESTINATION / "sample_completeness.png"
    assert not path.exists()
    figure.savefig(path, dpi=170)
    plotting.close(figure)
    figure, axes = plotting.subplots(1, 3, figsize=(15, 4.5))
    for axis, metric in zip(axes, METRICS):
        groups = [[summary_index[row["sample_id"], arm][metric] * 100 for row in rows] for arm in arms]
        axis.boxplot(groups, tick_labels=arms, showmeans=True)
        axis.tick_params(axis="x", labelrotation=55)
        axis.set_title(metric)
        axis.set_ylabel("Percent")
        axis.grid(axis="y", alpha=0.2)
    figure.suptitle("30-sample distributions; means are not the whole result")
    figure.tight_layout()
    path = DESTINATION / "metric_distributions.png"
    assert not path.exists()
    figure.savefig(path, dpi=170)
    plotting.close(figure)


if __name__ == "__main__":
    main()