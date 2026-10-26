import csv
import hashlib
import json
import math
import random
import statistics
from collections import Counter
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BASE = ROOT.parent
PRIOR = BASE / "audit-20261014-exp04-detailed-01"
RUN = BASE / "runs/exp04-2gpu"
ARMS = ["direct_s", "direct_l", "s_to_s", "s_to_l", "l_to_s", "l_to_l", "gold_to_s", "gold_to_l"]
METRICS = ["completeness", "conciseness", "faithfulness"]
COMPARISONS = [
    ("l_to_s", "s_to_s"), ("l_to_l", "s_to_l"),
    ("direct_l", "direct_s"), ("s_to_l", "s_to_s"), ("l_to_l", "l_to_s"), ("gold_to_l", "gold_to_s"),
    ("s_to_s", "direct_s"), ("l_to_s", "direct_s"),
    ("s_to_l", "direct_l"), ("l_to_l", "direct_l"),
    ("gold_to_s", "direct_s"), ("gold_to_l", "direct_l"),
    ("gold_to_s", "l_to_s"), ("gold_to_l", "l_to_l"),
    ("l_to_s", "direct_l"), ("s_to_l", "direct_s"),
]


def read_csv(name):
    with (PRIOR / name).open(encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def number(row, name):
    return float(row[name])


def save_json(name, data):
    with (ROOT / name).open("x", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2, allow_nan=False)
        handle.write("\n")


def save_csv(name, rows):
    with (ROOT / name).open("x", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def table(headers, rows):
    return ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |",
            *["| " + " | ".join(map(str, row)) + " |" for row in rows]]


def percentage(value):
    return f"{value * 100:.2f}%"


def bootstrap(values, seed=42):
    generator = random.Random(seed)
    means = sorted(statistics.fmean(values[generator.randrange(len(values))] for _ in values) for _ in range(2000))
    def quantile(fraction):
        position = (len(means) - 1) * fraction
        lower = int(position)
        return means[lower] + (means[min(lower + 1, len(means) - 1)] - means[lower]) * (position - lower)
    return quantile(0.025), quantile(0.975)


def main():
    facts = read_csv("fact_metrics_recomputed.csv")
    summaries = read_csv("summary_metrics_recomputed.csv")
    evidence = json.loads((PRIOR / "sample_evidence.json").read_text())
    fact_index = {(row["sample_id"], row["source"]): row for row in facts}
    index = {(row["sample_id"], row["arm"]): row for row in summaries}
    sample_ids = sorted(evidence)
    assert len(fact_index) == 60 and len(index) == 240 and len(sample_ids) == 30
    for row in facts:
        original = json.loads((RUN / "metrics/facts" / row["source"] / f"{row['sample_id']}.json").read_text())
        for name in ["coverage", "support", "fact_count", "character_count"]:
            assert math.isclose(number(row, name), original[name], abs_tol=1e-12)
    for row in summaries:
        original = json.loads((RUN / "metrics/summaries" / row["arm"] / f"{row['sample_id']}.json").read_text())
        for name in [*METRICS, "sentence_count", "atomic_fact_count"]:
            assert math.isclose(number(row, name), original[name], abs_tol=1e-12)
    manifest = read_csv("cache_validation.csv")
    for row in manifest:
        assert hashlib.sha256((RUN / row["path"]).read_bytes()).hexdigest().upper() == row["sha256"]
    cohorts = {name: [] for name in ["primary_coverage_up_support_not_down", "strong_coverage_20pp_support_not_down",
                                    "strict_both_up", "pareto_either_up", "coverage_only_up",
                                    "primary_excluding_known_judge_anomalies", "not_primary"]}
    selection = []
    for sid in sample_ids:
        small, large = fact_index[sid, "small"], fact_index[sid, "large"]
        reference_count = int(small["reference_count"])
        assert reference_count == int(large["reference_count"])
        coverage_delta = Fraction(int(large["covered_reference_count"]) - int(small["covered_reference_count"]), reference_count)
        support_delta = Fraction(int(large["supported_count"]), int(large["fact_count"])) - Fraction(int(small["supported_count"]), int(small["fact_count"]))
        conditions = {
            "primary_coverage_up_support_not_down": coverage_delta > 0 and support_delta >= 0,
            "strong_coverage_20pp_support_not_down": coverage_delta >= Fraction(1, 5) and support_delta >= 0,
            "strict_both_up": coverage_delta > 0 and support_delta > 0,
            "pareto_either_up": coverage_delta >= 0 and support_delta >= 0 and (coverage_delta > 0 or support_delta > 0),
            "coverage_only_up": coverage_delta > 0,
            "primary_excluding_known_judge_anomalies": coverage_delta > 0 and support_delta >= 0 and sid not in ["meeting-0378", "meeting-0795"],
            "not_primary": not (coverage_delta > 0 and support_delta >= 0),
        }
        if coverage_delta > 0 and support_delta >= 0:
            category = "large_coverage_dominant"
        elif coverage_delta >= 0 and support_delta >= 0 and support_delta > 0:
            category = "equal_coverage_higher_support"
        elif coverage_delta <= 0 and support_delta <= 0 and (coverage_delta < 0 or support_delta < 0):
            category = "small_dominant"
        elif coverage_delta == 0 and support_delta == 0:
            category = "metric_tie"
        else:
            category = "coverage_support_tradeoff"
        small_covered = set(evidence[sid]["facts"]["small"]["covered_reference_ids"])
        large_covered = set(evidence[sid]["facts"]["large"]["covered_reference_ids"])
        selection.append({"sample_id": sid, "dataset": small["dataset"], "category": category,
                          "small_coverage": number(small, "coverage"), "large_coverage": number(large, "coverage"),
                          "coverage_delta": float(coverage_delta), "small_support": number(small, "support"),
                          "large_support": number(large, "support"), "support_delta": float(support_delta),
                          "small_fact_count": int(small["fact_count"]), "large_fact_count": int(large["fact_count"]),
                          "small_reference_matches": len(small_covered), "large_reference_matches": len(large_covered),
                          "large_only_references": len(large_covered - small_covered), "small_only_references": len(small_covered - large_covered),
                          "large_reference_superset": small_covered <= large_covered,
                          **conditions})
        for name, included in conditions.items():
            if included:
                cohorts[name].append(sid)
    assert len(cohorts["primary_coverage_up_support_not_down"]) == 16
    assert len(cohorts["strong_coverage_20pp_support_not_down"]) == 8
    assert len(cohorts["strict_both_up"]) == 6
    assert len(cohorts["pareto_either_up"]) == 19
    save_csv("all_sample_selection.csv", selection)
    save_json("cohorts.json", cohorts)
    aggregates, fact_aggregates, paired, interactions = [], [], [], []
    for cohort, identifiers in cohorts.items():
        for dataset in ["ALL", *sorted({evidence[sid]["dataset"] for sid in identifiers})]:
            selected = [sid for sid in identifiers if dataset == "ALL" or evidence[sid]["dataset"] == dataset]
            for arm in ARMS:
                group = [index[sid, arm] for sid in selected]
                aggregate = {"cohort": cohort, "dataset": dataset, "arm": arm, "n": len(group)}
                for metric in METRICS:
                    values = [number(row, metric) for row in group]
                    aggregate.update({f"{metric}_mean": statistics.fmean(values), f"{metric}_median": statistics.median(values),
                                      f"{metric}_min": min(values), f"{metric}_max": max(values)})
                aggregate.update({"mean_completion_tokens": statistics.fmean(number(row, "completion_tokens") for row in group),
                                  "reference_count": sum(int(row["reference_count"]) for row in group),
                                  "matched_reference_count": sum(int(row["matched_reference_count"]) for row in group),
                                  "atomic_claim_count": sum(int(row["atomic_fact_count"]) for row in group),
                                  "unsupported_claim_count": sum(int(row["unsupported_claim_count"]) for row in group),
                                  "all_supported_summary_count": sum(int(row["unsupported_claim_count"]) == 0 for row in group),
                                  "completeness_micro": sum(int(row["matched_reference_count"]) for row in group) / sum(int(row["reference_count"]) for row in group),
                                  "faithfulness_micro": sum(int(row["supported_claim_count"]) for row in group) / sum(int(row["atomic_fact_count"]) for row in group),
                                  "conciseness_micro": sum(int(row["aligned_sentence_count"]) for row in group) / sum(int(row["sentence_count"]) for row in group)})
                aggregates.append(aggregate)
            for role in ["small", "large"]:
                group = [fact_index[sid, role] for sid in selected]
                fact_aggregates.append({"cohort": cohort, "dataset": dataset, "source": role, "n": len(group),
                                        "coverage_mean": statistics.fmean(number(row, "coverage") for row in group),
                                        "support_mean": statistics.fmean(number(row, "support") for row in group),
                                        "fact_count_mean": statistics.fmean(number(row, "fact_count") for row in group)})
            for left, right in COMPARISONS:
                for metric_index, metric in enumerate(METRICS):
                    differences = [number(index[sid, left], metric) - number(index[sid, right], metric) for sid in selected]
                    lower, upper = bootstrap(differences, 42 + metric_index)
                    paired.append({"cohort": cohort, "dataset": dataset, "contrast": f"{left} - {right}", "metric": metric, "n": len(selected),
                                   "mean_difference": statistics.fmean(differences), "median_difference": statistics.median(differences),
                                   "ci_lower": lower, "ci_upper": upper, "wins": sum(value > 1e-12 for value in differences),
                                   "ties": sum(abs(value) <= 1e-12 for value in differences), "losses": sum(value < -1e-12 for value in differences),
                                   "min_difference": min(differences), "max_difference": max(differences)})
            for metric_index, metric in enumerate(METRICS):
                differences = [(number(index[sid, "l_to_l"], metric) - number(index[sid, "s_to_l"], metric)) -
                               (number(index[sid, "l_to_s"], metric) - number(index[sid, "s_to_s"], metric)) for sid in selected]
                lower, upper = bootstrap(differences, 42 + metric_index)
                interactions.append({"cohort": cohort, "dataset": dataset, "metric": metric, "n": len(selected),
                                     "expression": "(l_to_l - s_to_l) - (l_to_s - s_to_s)",
                                     "mean_difference": statistics.fmean(differences), "ci_lower": lower, "ci_upper": upper})
    save_csv("cohort_summary_metrics.csv", aggregates)
    save_csv("cohort_fact_metrics.csv", fact_aggregates)
    save_csv("paired_contrasts.csv", paired)
    save_csv("fact_source_generator_interaction.csv", interactions)
    primary = cohorts["primary_coverage_up_support_not_down"]
    save_csv("primary_sample_eight_arms.csv", [row for row in summaries if row["sample_id"] in primary])
    propagation = []
    for sid in primary:
        small_refs = set(evidence[sid]["facts"]["small"]["covered_reference_ids"])
        large_refs = set(evidence[sid]["facts"]["large"]["covered_reference_ids"])
        for generator in ["s", "l"]:
            from_small = set(evidence[sid]["summaries"][f"s_to_{generator}"]["covered_reference_ids"])
            from_large = set(evidence[sid]["summaries"][f"l_to_{generator}"]["covered_reference_ids"])
            large_only = large_refs - small_refs
            propagation.append({"sample_id": sid, "dataset": evidence[sid]["dataset"], "generator": generator,
                                "large_only_extraction_reference_count": len(large_only),
                                "large_only_seen_in_small_fact_summary": len(large_only & from_small),
                                "large_only_seen_in_large_fact_summary": len(large_only & from_large),
                                "summary_gained_reference_count": len(from_large - from_small),
                                "summary_lost_reference_count": len(from_small - from_large),
                                "gained_reference_ids": json.dumps([value + 1 for value in sorted(from_large - from_small)]),
                                "lost_reference_ids": json.dumps([value + 1 for value in sorted(from_small - from_large)])})
    save_csv("reference_propagation.csv", propagation)
    write_report(cohorts, selection, index, evidence, aggregates, fact_aggregates, paired, interactions, propagation)
    save_json("validation.json", {"original_metrics_verified": 300, "original_cache_digests_verified": len(manifest),
                                  "selection_uses_summary_scores": False, "primary_n": len(primary), "strong_n": 8,
                                  "category_counts": dict(Counter(row["category"] for row in selection)),
                                  "input_sha256": {name: hashlib.sha256((PRIOR / name).read_bytes()).hexdigest() for name in ["fact_metrics_recomputed.csv", "summary_metrics_recomputed.csv", "sample_evidence.json"]}})
    print("PRIMARY", primary)
    print("STRONG", cohorts["strong_coverage_20pp_support_not_down"])
    for cohort in ["primary_coverage_up_support_not_down", "strong_coverage_20pp_support_not_down"]:
        print("COHORT", cohort)
        for row in aggregates:
            if row["cohort"] == cohort and row["dataset"] == "ALL":
                print(row["arm"], *[round(row[f"{metric}_mean"] * 100, 2) for metric in METRICS])
        for row in paired:
            if row["cohort"] == cohort and row["dataset"] == "ALL" and row["contrast"] in ["l_to_s - s_to_s", "l_to_l - s_to_l"]:
                print("FIXED_GENERATOR", row["contrast"], row["metric"], "delta", round(row["mean_difference"] * 100, 3),
                      "CI", round(row["ci_lower"] * 100, 3), round(row["ci_upper"] * 100, 3), "W/T/L", row["wins"], row["ties"], row["losses"])


def write_report(cohorts, selection, index, evidence, aggregates, fact_aggregates, paired, interactions, propagation):
    primary_name = "primary_coverage_up_support_not_down"
    strong_name = "strong_coverage_20pp_support_not_down"
    primary = cohorts[primary_name]
    lines = ["# 在large事实抽取占优的样本上比较八组纪要", "",
             "## 核心结论", "",
             "**在抽取指标large占优的条件下，更换large facts对small生成的参考覆盖帮助更明显；对large生成不是稳定的逐样本增益。同用large facts时，两生成模型的平均覆盖差很小，但不能据此证明能力等价。**", "",
             "主16条固定small生成：l_to_s−s_to_s完整性+11.41pp，12胜1平3负；固定large生成：l_to_l−s_to_l仅+1.59pp，9胜1平6负。明显优势8条分别为+12.21pp（6胜2负）和+4.75pp（4胜4负）。", "",
             "固定large facts时，主16条large生成只比small高0.62pp，明显优势8条反而低0.06pp；区间较宽，不能把近似均值解释为统计等价。原文直接生成的差距则为19.53/16.17pp，这些不同控制条件不应混合比较。", "",
             "覆盖并非唯一质量：主16条更换large facts后small生成忠实性−1.15pp、简洁性+1.90pp；large生成忠实性+2.43pp、简洁性−8.04pp。不能将参考覆盖增加称作三项质量全面提升。", "",
             "排除0378、0795两例已知纪要匹配异常后，剩余14条small/large生成更换facts的覆盖变化为+10.49/+4.88pp，固定large facts的生成模型差仅+0.37pp。主观察仍存在，但不是全部内容已经人工核实。", "",
             "## 1. 分析问题与筛选口径", "",
             "问题不是全部30条谁的纪要均值更高，而是：在同一会议上，large抽取比small更好时，换用large事实是否使small/large生成更好，以及这与直接生成、参考事实辅助的差距是什么。", "",
             "**主分析16条**：large抽取参考覆盖率严格高于small，且原文支持率不低于small。此筛选只用抽取指标，不用任何纪要分数。", "",
             "**明显优势8条**：在主条件上，再要求覆盖提高至少20个百分点。20pp是展示明显差异的分析阈值，不是原协议预注册规则，不作‘显著性’解释。", "",
             "其他敏感性口径包括：覆盖/支持都严格提高（6条）、任一提高而另一不降的帕累托优势（19条）、仅要求覆盖提高（18条）以及排除既知评审异常后的主子集（14条）。", "",
             "‘更好’在此明确指现有覆盖/支持口径占优，不是经过全部原文人工核验的绝对质量顺序。参考不穷尽所有重要信息，large可能仍遗漏small独有的重要事实；事实粒度、重复和提议/定案状态也未被这两个指标充分表达。", "",
             "## 2. 哪些样本入选，哪些不能混入", ""]
    lines.extend(table(["样本", "来源", "small覆盖→large覆盖", "覆盖差pp", "small支持→large支持", "明显优势≥20pp", "large为参考超集"], [
        [row["sample_id"], row["dataset"], f"{percentage(row['small_coverage'])}→{percentage(row['large_coverage'])}",
         f"{row['coverage_delta'] * 100:+.2f}", f"{percentage(row['small_support'])}→{percentage(row['large_support'])}",
         "是" if row[strong_name] else "否", "是" if row["large_reference_superset"] else "否"] for row in selection if row[primary_name]]))
    lines.extend(["", "0136（覆盖+14.29pp、支持−5.00pp）和0761（覆盖+61.54pp、支持−3.57pp）属于权衡，不能在不声明取舍时当作large双指标占优。0064、0160、0214、1726虽支持更高，但覆盖更低；0281、0621、1469覆盖相同而支持更高，计入19条帕累托口径而不计入覆盖严格提高的16条主分析。", "",
                  "0031、0174、0506、0550在上述双指标中small占优；0291指标持平，但覆盖事实身份不同，持平也不是内容完全相同。完整30条分类保存在all_sample_selection.csv。", "",
                  "## 3. 八组到底分别控制了什么", ""])
    lines.extend(table(["组", "纪要生成模型", "辅助事实"], [
        [arm, "small" if arm.endswith("_s") else "large", "无（原文直接生成）" if arm.startswith("direct") else
         "small抽取" if arm.startswith("s_to") else "large抽取" if arm.startswith("l_to") else "参考事实"] for arm in ARMS]))
    lines.extend(["", "**判断事实抽取优势是否传递，应先固定生成模型**：l_to_s−s_to_s与l_to_l−s_to_l。直接比较l_to_l−s_to_s同时改变了抽取和生成，不能单独归因于facts。", "",
                  "**判断生成模型利用同一事实的能力，应固定事实来源**：s_to_l−s_to_s、l_to_l−l_to_s、gold_to_l−gold_to_s。direct_l−direct_s是无外部事实时的模型差距。", "",
                  "**判断辅助是否值得使用，应固定生成模型并与direct比较**：s_to_s/l_to_s对direct_s，s_to_l/l_to_l对direct_l。gold用于考察参考信息输入后的剩余差距，不是无误差、免费或必达的上界。辅助组仍有完整原文。", ""])
    for cohort_name, title in [(primary_name, "4. 主分析：16条覆盖占优且支持不降"), (strong_name, "5. 明显优势：8条覆盖提高至少20pp")]:
        identifiers = cohorts[cohort_name]
        lines.extend([f"## {title}", "", f"N={len(identifiers)}；来源构成：" + "，".join(f"{dataset} {count}条" for dataset, count in sorted(Counter(evidence[sid]['dataset'] for sid in identifiers).items())) + "。", ""])
        fact_rows = [row for row in fact_aggregates if row["cohort"] == cohort_name and row["dataset"] == "ALL"]
        lines.extend(table(["抽取模型", "宏覆盖", "宏支持", "平均事实数"], [[row["source"], percentage(row["coverage_mean"]), percentage(row["support_mean"]), f"{row['fact_count_mean']:.2f}"] for row in fact_rows]))
        lines.append("")
        group = [row for row in aggregates if row["cohort"] == cohort_name and row["dataset"] == "ALL"]
        lines.extend(table(["组", "完整性C宏/微", "简洁性Q宏", "忠实性F宏/微", "匹配参考/总参考", "不支持主张/总主张", "全支持纪要", "平均输出tokens"], [
            [row["arm"], f"{percentage(row['completeness_mean'])}/{percentage(row['completeness_micro'])}", percentage(row["conciseness_mean"]),
             f"{percentage(row['faithfulness_mean'])}/{percentage(row['faithfulness_micro'])}", f"{row['matched_reference_count']}/{row['reference_count']}",
             f"{row['unsupported_claim_count']}/{row['atomic_claim_count']}", f"{row['all_supported_summary_count']}/{row['n']}", f"{row['mean_completion_tokens']:.1f}"] for row in group]))
        lines.extend(["", "### 固定生成模型，更换facts", ""])
        lines.extend(table(["对比", "指标", "均差pp", "中位差pp", "95%区间pp", "胜/平/负"], [
            [row["contrast"], row["metric"], f"{row['mean_difference'] * 100:+.2f}", f"{row['median_difference'] * 100:+.2f}",
             f"[{row['ci_lower'] * 100:+.2f},{row['ci_upper'] * 100:+.2f}]", f"{row['wins']}/{row['ties']}/{row['losses']}"]
            for row in paired if row["cohort"] == cohort_name and row["dataset"] == "ALL" and row["contrast"] in ["l_to_s - s_to_s", "l_to_l - s_to_l"]]))
        lines.extend(["", "### 其它完整性对比", ""])
        lines.extend(table(["对比", "平均差pp", "95%区间pp", "胜/平/负"], [
            [row["contrast"], f"{row['mean_difference'] * 100:+.2f}", f"[{row['ci_lower'] * 100:+.2f},{row['ci_upper'] * 100:+.2f}]",
             f"{row['wins']}/{row['ties']}/{row['losses']}"] for row in paired
            if row["cohort"] == cohort_name and row["dataset"] == "ALL" and row["metric"] == "completeness" and row["contrast"] not in ["l_to_s - s_to_s", "l_to_l - s_to_l"]]))
        lines.extend(["", "### 来源内的facts更换收益", ""])
        lines.extend(table(["来源", "N", "对比", "C平均变化pp", "胜/平/负"], [
            [row["dataset"], row["n"], row["contrast"], f"{row['mean_difference'] * 100:+.2f}", f"{row['wins']}/{row['ties']}/{row['losses']}"]
            for row in paired if row["cohort"] == cohort_name and row["dataset"] != "ALL" and row["metric"] == "completeness" and row["contrast"] in ["l_to_s - s_to_s", "l_to_l - s_to_l"]]))
    lines.extend(["", "## 6. 主子集每个样本的八组差异", "",
                  "C/Q/F均来自既有评审；分母分别为参考数、NLTK分句数、评审分解主张数。ID从1开始。新增/丢失指两次匹配标签之差，不是人工已确认的全部增减。", ""])
    for sid in primary:
        item = next(row for row in selection if row["sample_id"] == sid)
        lines.extend([f"### {sid} · {item['dataset']}", "", f"抽取覆盖{percentage(item['small_coverage'])}→{percentage(item['large_coverage'])}；支持{percentage(item['small_support'])}→{percentage(item['large_support'])}；事实{item['small_fact_count']}→{item['large_fact_count']}条。large独有匹配参考{item['large_only_references']}条，small独有{item['small_only_references']}条。", ""])
        lines.extend(table(["组", "覆盖分子/分母", "C", "匹配句/总句", "Q", "支持主张/总主张", "F", "输出tokens"], [
            [arm, f"{index[sid,arm]['matched_reference_count']}/{index[sid,arm]['reference_count']}", percentage(number(index[sid,arm],"completeness")),
             f"{index[sid,arm]['aligned_sentence_count']}/{index[sid,arm]['sentence_count']}", percentage(number(index[sid,arm],"conciseness")),
             f"{index[sid,arm]['supported_claim_count']}/{index[sid,arm]['atomic_fact_count']}", percentage(number(index[sid,arm],"faithfulness")), index[sid,arm]["completion_tokens"]] for arm in ARMS]))
        for generator in ["s", "l"]:
            left, right = f"l_to_{generator}", f"s_to_{generator}"
            changes = [100 * (number(index[sid,left], metric) - number(index[sid,right], metric)) for metric in METRICS]
            value = next(row for row in propagation if row["sample_id"] == sid and row["generator"] == generator)
            lines.extend(["", f"**{left} − {right}**：C{changes[0]:+.2f}pp、Q{changes[1]:+.2f}pp、F{changes[2]:+.2f}pp；参考匹配新增{value['summary_gained_reference_count']}、丢失{value['summary_lost_reference_count']}。"])
            for label, name in [("新增", "gained_reference_ids"), ("丢失", "lost_reference_ids")]:
                for reference_id in json.loads(value[name]):
                    lines.append(f"- {label} R{reference_id}：{evidence[sid]['reference_facts'][reference_id - 1]}")
        if sid in ["meeting-0378", "meeting-0795"]:
            lines.extend(["", "**已知评审异常**：0378 s_to_l与0795 direct_l有过宽松的100%参考匹配；此样本对比不能直接当作人工质量结论。敏感性结果另列。"])
        if sid == "meeting-0078":
            lines.extend(["", "**内容核对**：direct_l、l_to_l、gold_to_l三份纪要都保留3–2最终投票。低分不能解释为辅助丢失投票；差异需按具体发言者/理由匹配复核。small事实有把拟议两议员规则当现行规则的风险。"])
        if sid == "meeting-1719":
            lines.extend(["", "**关键例外**：large整体覆盖高，但small两条保留最终4–1投票，large列表遗漏；‘large整体更好’不等于small信息是large的严格子集。"])
        lines.append("")
    lines.extend(["## 7. 筛选口径敏感性与交互", "",
                  "以下对比保持同一子集内配对；不同子集改变来源/样本组成，不能把子集之间均值差当成抽取质量的因果效应。", ""])
    lines.extend(table(["子集", "N", "l_to_s−s_to_s C/Q/F pp", "l_to_l−s_to_l C/Q/F pp"], [
        [cohort, len(identifiers), *[" / ".join(f"{next(row for row in paired if row['cohort']==cohort and row['dataset']=='ALL' and row['contrast']==contrast and row['metric']==metric)['mean_difference'] * 100:+.2f}" for metric in METRICS)
                                   for contrast in ["l_to_s - s_to_s", "l_to_l - s_to_l"]]] for cohort, identifiers in cohorts.items()]))
    lines.extend(["", "交互量=(l_to_l−s_to_l)−(l_to_s−s_to_s)，比较large生成是否比small生成更能受益于更换large facts；并非把所有组简单相减就能作机制归因。", ""])
    lines.extend(table(["子集", "指标", "交互pp", "95%区间pp"], [
        [row["cohort"], row["metric"], f"{row['mean_difference'] * 100:+.2f}", f"[{row['ci_lower'] * 100:+.2f},{row['ci_upper'] * 100:+.2f}]"]
        for row in interactions if row["cohort"] in [primary_name, strong_name] and row["dataset"] == "ALL"]))
    lines.extend(["", "## 8. 解释与限制", "",
                  "1. 这里回答的是条件比较：在抽取指标large占优的同一批会议上，固定生成模型后换facts是否更好。不是所有30条平均，也不是假设large永远占优。",
                  "2. 指标优势不意味着参考集合严格包含。主子集中large可能增加多条同时漏掉small独有参考；表中的参考超集列直接揭示此差异。",
                  "3. 支持率不下降仍可能增加绝对不支持项数，且长复合列表项和短原子项并不等粒度；不能把率的帕累托优势当成全部事实质量认证。",
                  "4. 两阶段仍有完整原文：small事实遗漏可由生成补充，large事实新增可被生成忽略；reference_propagation.csv给出匹配层面的传递。",
                  "5. 原评审并非可靠人工真值：0378/0795的过宽松匹配、0078逐项匹配差异等需复核。主分析去除既知异常后另列14条结果；明显优势8条不包含0378/0795。",
                  "6. 配对bootstrap为2000次会议级重采样、95%百分位区间，种子42/43/44对应C/Q/F；单会议来源区间退化，没有推断意义。未校正多重比较，不包含评审误差。",
                  "7. 子集是用实验后观察抽取结果选出，阈值非预注册，且来源数不均、pilot有最短/最长富集；只能解释这些样本，不能据此推广总体或证明模型规模因果机制。",
                  "8. 更丰富的facts可能改变长度/提示和采样结果，没有定长控制与多seed重复；不把任何一项差值完全归因于一个因素。", "",
                  "## 9. 数据文件", "",
                  "- [all_sample_selection.csv](all_sample_selection.csv)：全30样本指标优势、权衡/持平分类和所有筛选标志。",
                  "- [cohorts.json](cohorts.json)：每个子集的完整样本ID。",
                  "- [primary_sample_eight_arms.csv](primary_sample_eight_arms.csv)：主16条的128份纪要完整分子/分母与评分。",
                  "- [cohort_summary_metrics.csv](cohort_summary_metrics.csv)、[cohort_fact_metrics.csv](cohort_fact_metrics.csv)：整体/来源内八组分布与抽取质量。",
                  "- [paired_contrasts.csv](paired_contrasts.csv)：16类对比三指标，胜平负及区间。",
                  "- [reference_propagation.csv](reference_propagation.csv)：新增/丢失参考及large独有抽取信息的利用计数。",
                  "- [fact_source_generator_interaction.csv](fact_source_generator_interaction.csv)：事实来源×生成模型交互。",
                  "- [validation.json](validation.json)、[analyze.py](analyze.py)：输入对应性和可复现脚本。未改原实验，未重生成、重评或调用API。", ""])
    with (ROOT / "report_zh.md").open("x", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()