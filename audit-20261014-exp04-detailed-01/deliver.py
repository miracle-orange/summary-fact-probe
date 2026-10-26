import csv
import json
import math
import statistics
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RUN = ROOT.parent / "runs/exp04-2gpu"
DATA = ROOT.parent / "data/processed/meetings.jsonl"
ARMS = ["direct_s", "direct_l", "s_to_s", "s_to_l", "l_to_s", "l_to_l", "gold_to_s", "gold_to_l"]
METRICS = ["completeness", "conciseness", "faithfulness"]


def read_csv(name):
    with (ROOT / name).open(encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def number(record, name):
    return float(record[name])


def percent(value):
    return f"{value * 100:.2f}%"


def table(headers, records):
    return ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |",
            *["| " + " | ".join(map(str, row)) + " |" for row in records]]


def save_json(name, value):
    with (ROOT / name).open("x", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def main():
    summaries = read_csv("summary_metrics_recomputed.csv")
    facts = read_csv("fact_metrics_recomputed.csv")
    aggregates = read_csv("summary_distribution_by_source.csv")
    contrasts = read_csv("paired_contrasts.csv")
    fact_aggregates = read_csv("fact_distribution_by_source.csv")
    transitions = read_csv("reference_transitions.csv")
    evidence = json.loads((ROOT / "sample_evidence.json").read_text())
    original = {row["sample_id"]: row for row in map(json.loads, DATA.open(encoding="utf-8"))}
    index = {(row["sample_id"], row["arm"]): row for row in summaries}
    fact_index = {(row["sample_id"], row["source"]): row for row in facts}
    sample_ids = list(evidence)
    source_names = sorted({row["dataset"] for row in summaries})
    sensitivity = []
    for excluded in [("meeting-0064",), ("meeting-0064", "meeting-0378", "meeting-0795")]:
        for dataset in ["ALL", "QMSum-Academic"]:
            selected = [sid for sid in sample_ids if sid not in excluded and (dataset == "ALL" or evidence[sid]["dataset"] == dataset)]
            for first, second in [("s_to_s", "direct_s"), ("l_to_s", "direct_s"), ("l_to_l", "direct_l"), ("s_to_l", "direct_l")]:
                values = [number(index[sid, first], "completeness") - number(index[sid, second], "completeness") for sid in selected]
                sensitivity.append({"excluded_samples": list(excluded), "dataset": dataset, "contrast": f"{first} - {second}",
                                    "n": len(values), "mean_difference": statistics.fmean(values)})
    save_json("judge_anomaly_sensitivity.json", sensitivity)
    review = []
    for sid, arm, reference_index in [("meeting-0064", "direct_s", 14), ("meeting-0795", "direct_l", 1), ("meeting-0378", "s_to_l", 8)]:
        item = evidence[sid]["summaries"][arm]
        match = next(value for value in item["matches"] if value["fact_idx"] == reference_index)
        review.append({"sample_id": sid, "arm": arm, "issue": "overinclusive_reference_match", "reference_id": reference_index + 1,
                       "reference": evidence[sid]["reference_facts"][reference_index],
                       "judge_matched_sentence_id": match["align_unit_idx"] + 1,
                       "judge_matched_sentence": item["sentences"][match["align_unit_idx"]],
                       "summary": item["summary"]})
    source = original["meeting-0136"]["conversation"]
    position = source.index("Industrial Designer: And uh well the Bluetooth chip")
    review.append({"sample_id": "meeting-0136", "arm": "l_to_l", "issue": "apparently_false_negative_support",
                   "judge_unsupported_claim": evidence["meeting-0136"]["summaries"]["l_to_l"]["atomic_facts"][8],
                   "source_start": position, "source_end": position + 800, "source_excerpt": source[position:position + 800]})
    item = evidence["meeting-1469"]["summaries"]["s_to_s"]
    isolated = [idx for idx, text in enumerate(item["sentences"]) if text in ("Hon.", "Mr.", "Ms.")]
    review.append({"sample_id": "meeting-1469", "arm": "s_to_s", "issue": "honorific_sentence_fragmentation",
                   "sentence_count": len(item["sentences"]), "isolated_honorific_count": len(isolated),
                   "isolated_honorific_sentence_ids": [idx + 1 for idx in isolated], "first_sentences": item["sentences"][:12]})
    save_json("human_review_evidence.json", review)
    joint = []
    for first, second in [("s_to_s", "direct_s"), ("l_to_s", "direct_s"), ("s_to_l", "direct_l"), ("l_to_l", "direct_l"), ("gold_to_s", "direct_s"), ("gold_to_l", "direct_l")]:
        differences = [[number(index[sid, first], metric) - number(index[sid, second], metric) for metric in METRICS] for sid in sample_ids]
        joint.append({"contrast": f"{first} - {second}", "n": len(sample_ids),
                      "coverage_improved_without_fidelity_loss": sum(values[0] > 1e-12 and values[2] >= -1e-12 for values in differences),
                      "coverage_improved_with_fidelity_loss": sum(values[0] > 1e-12 and values[2] < -1e-12 for values in differences),
                      "pareto_improved": sum(all(value >= -1e-12 for value in values) and any(value > 1e-12 for value in values) for values in differences),
                      "pareto_worsened": sum(all(value <= 1e-12 for value in values) and any(value < -1e-12 for value in values) for values in differences)})
    save_json("joint_quality_changes.json", joint)
    lines = ["# exp04-2gpu 完整数据分析", "", "## 1. 结论与可信边界", "",
             "本分析覆盖pilot全部30场会议、60份模型事实列表、240份纪要和840份成功评审缓存。五来源各6条；30场共601条参考事实。",
             "**主结论：事实辅助主要提高按参考定义的覆盖，而不是三项质量同步提升；增益因来源和样本而异。large抽取明显优于small，并没有稳定地转化为同等纪要收益。参考事实辅助是诊断干预，不是真实部署的免费输入，也不是已证实的质量上界。**", "",
             "**特别警告：复核发现部分明显过宽松的参考匹配、至少一例疑似支持漏判及称谓分句偏差。因此，下面是精确的现有机器评审结果，不是全部人工正确性认证；不能仅凭这些分数认定Academic事实辅助有害或large必然更好。**", "",
             "原实验代码、配置、数据、生成、评测缓存和日志未改动；未启动模型、重生成文本、调用评审API、读取凭据或执行commit/push。所有新文件均位于这个新独立审计目录。", "",
             "## 2. 指标、实验组与完整性核验", "",
             "small=Qwen3-8B，large=Qwen3-32B。direct为原文直接纪要；s_to_*、l_to_*分别使用small、large抽取事实；gold_to_*使用数据中的参考事实。辅助组仍可读取完整原文，并可纠正/补充事实列表。", "",
             "- 完整性C = 匹配参考事实数 / 参考事实数。不是原文所有重要信息的穷尽召回率。",
             "- 简洁性Q = 至少匹配一条参考事实的不同句子数 / 总句数。不是长度、文笔或重复率指标；没有匹配参考的有效补充也会降低Q。",
             "- 忠实性F = 被评审判为原文支持的分解主张数 / 分解主张总数。100%只代表此评审未标记错误。",
             "- 抽取覆盖按参考匹配计算；抽取支持直接评审每个列表项，不做同样的主张分解，不能与纪要F直接横比。",
             "- 宏平均每会议等权；微平均先合并分子、分母。总体宏平均也等权五来源，因为每来源都是6条。百分点简称pp。", "",
             "300份指标全部重新计算一致；300个生成请求哈希、840个评审请求哈希全部对应当前pilot数据与协议快照；48行原报告宏平均精确一致。成功缓存全部finish_reason=stop；响应身份记录为small/large或Pro/deepseek-ai/DeepSeek-V3.2。此校验不证明评审语义正确，也不是网络或模型权重字节级证明。", "",
             "现评测状态requested=300、failures=[]。保留的旧错误记录包括：0761 small抽取length截断；0290 large事实匹配和0400 l_to_l纪要匹配曾返回错误条数。后两项旧diagnostics仍记录失败，但当前成功缓存与指标均通过，不应当作现存缺失，也不应抹去失败历史。", "",
             "## 3. 整体结果：均值之外", ""]
    overall = [row for row in aggregates if row["dataset"] == "ALL"]
    lines.extend(table(["组", "C宏/微", "Q宏/微", "F宏/微", "匹配参考/601", "不支持主张/全部", "全部支持纪要", "平均输出tokens"], [
        [row["arm"], f"{percent(number(row,'completeness_mean'))}/{percent(number(row,'completeness_micro'))}",
         f"{percent(number(row,'conciseness_mean'))}/{percent(number(row,'conciseness_micro'))}",
         f"{percent(number(row,'faithfulness_mean'))}/{percent(number(row,'faithfulness_micro'))}", row["total_matched_reference_count"],
         f"{row['total_unsupported_claim_count']}/{row['total_atomic_fact_count']}", f"{row['all_supported_summary_count']}/30", f"{number(row,'mean_completion_tokens'):.1f}"] for row in overall]))
    lines.extend(["", "### 3.1 配对提升是否普遍", "",
                  "以下95%百分位区间采用2000次会议级配对bootstrap，C/Q/F种子分别为42/43/44。它们是pilot描述性不确定性，不含评审误差，不作多重比较校正，也不证明因果机制或推广到全部会议。", ""])
    lines.extend(table(["完整性对比", "平均差pp", "中位差pp", "95%区间pp", "胜/平/负"], [
        [row["contrast"], f"{number(row,'mean_difference') * 100:+.2f}", f"{number(row,'median_difference') * 100:+.2f}",
         f"[{number(row,'ci_lower') * 100:+.2f},{number(row,'ci_upper') * 100:+.2f}]", f"{row['wins']}/{row['ties']}/{row['losses']}"]
        for row in contrasts if row["dataset"] == "ALL" and row["metric"] == "completeness"]))
    lines.extend(["", "**解读**：s_to_s相对direct_s为22胜5平3负；l_to_l相对direct_l为18胜4平8负。提高总体均值不等于每会议受益。更换为large事实，small生成平均只再提升0.79pp（12胜3平15负），large生成只提升2.49pp（16胜2平12负），两者区间跨0；不能宣称large事实普遍更有用。", "",
                  "直接生成时large相对small覆盖多9.20pp；固定事实后large生成优势为3.53pp（small事实）、5.22pp（large事实）、1.83pp（参考事实），各区间跨0。这与选择信息的重要性一致，但不足以把直接模型差距全部归因于事实选择：提示、采样结果、长度与评审误差同时参与。", "",
                  "### 3.2 覆盖提升的代价", "",
                  "模型事实辅助后的宏F都低于对应直接组：s_to_s −1.79pp、l_to_s −1.36pp、s_to_l −2.54pp、l_to_l −2.32pp。后两项名义bootstrap区间分别为[−5.04,−0.02]和[−4.42,−0.15]pp；仅作诊断，尤其−0.02pp贴近0，不宜包装为稳健显著结论。", "",
                  "全部支持的纪要数从direct_s 21/30降至s_to_s 12/30，从direct_l 19/30降至l_to_l 11/30。即使平均F仍约96%，至少有一个不支持标签的会议比例并不低。所有240份纪要共218条主张被判不支持；60份抽取共57个列表项被判不支持。", ""])
    lines.extend(table(["对比", "覆盖升且F不降", "覆盖升但F下降", "C/Q/F帕累托改善", "帕累托恶化"], [
        [row["contrast"], row["coverage_improved_without_fidelity_loss"], row["coverage_improved_with_fidelity_loss"], row["pareto_improved"], row["pareto_worsened"]] for row in joint]))
    lines.extend(["", "帕累托改善指三项均不降且至少一项严格升；这里只是原评分下的计数，没有任意加权总分。", "",
                  "s_to_s平均输出335.3tokens，direct_s为179.9，增加约86%；l_to_l为328.1，direct_l为217.5，增加约51%。但没有定长约束，所以不能视为在同等长度预算下比较。small/large事实抽取另需平均411.5/534.3输出tokens；顺序流程每会议抽取+纪要约746.8tokens（s_to_s）或862.4tokens（l_to_l），不是纪要一个步骤的成本。跨组复用抽取会改变摊销方式，不能把token数直接换算为墙钟或API费用。", "",
                  "s_to_s的Q宏67.62%、微57.76%，差近10pp。1469占64个切分句但仅13句匹配参考，1020为23句/9句匹配；长纪要/分句碎片在微平均里权重更大。高F或高Q都不代表覆盖充分，例如direct_s仍只匹配218/601。", "",
                  "## 4. 抽取与纪要：不能把两阶段等同", ""])
    lines.extend(table(["抽取模型", "宏覆盖", "微覆盖", "宏支持", "微支持", "事实数总计", "不支持列表项", "两条事实样本"], [
        [row["source"], percent(number(row,"coverage_mean")), percent(number(row,"coverage_micro")), percent(number(row,"support_mean")),
         percent(number(row,"support_micro")), row["total_fact_count"], row["total_unsupported_count"], row["two_fact_count"]]
        for row in fact_aggregates if row["dataset"] == "ALL"]))
    lines.extend(["", "large较small宏抽取覆盖提高15.69pp、宏支持提高7.14pp，参考匹配总计408 vs 311，事实617 vs 448；这是清晰的抽取阶段差异，但模型大小还伴随内容粒度变化。", "",
                  "### 4.1 参考匹配迁移", ""])
    transition_totals = []
    for arm in ["s_to_s", "s_to_l", "l_to_s", "l_to_l"]:
        group = [row for row in transitions if row["arm"] == arm]
        values = [sum(int(row[key]) for row in group) for key in ["extraction_matched", "summary_matched", "both_matched", "summary_only_matched", "extraction_only_matched"]]
        transition_totals.append([arm, *values, percent(values[2] / values[0])])
    lines.extend(table(["组", "抽取匹配", "纪要匹配", "两者匹配", "仅纪要匹配", "仅抽取匹配", "匹配保留率"], transition_totals))
    lines.extend(["", "small事实辅助中出现50/73条仅纪要匹配参考，large事实辅助中为19/25条。辅助组能从原文补充；抽取缺失不是纪要无法覆盖的硬上限。反过来large列表里114/83条已匹配参考未进入small/large纪要，表明有事实≠使用事实。这里是两个独立匹配评审的集合迁移，不是已证实的逐条心理/因果路径；不把同句改写和评审差异当成真实补充/遗漏的铁证。", "",
                  "### 4.2 两条事实子群", "",
                  "7条small两事实样本（0078、0290、0571、0761、1696、1719、1776）中，direct_s C=30.58%，s_to_s=42.96%，l_to_s=51.72%，l_to_l=60.77%。其他23条s_to_s=56.10%、l_to_s=54.47%。两条子群中更换large事实，small生成平均+8.75pp；其余组反而−1.63pp。总体+0.79pp混合了方向不同的子群。", "",
                  "但子群不是随机分组，混合ECTSum、MeetingBank、Committee；不能把差异当作两条事实的因果效应。0761自身辅助C从42.31%降到19.23%，而0078自身辅助从31.58%升到73.68%，因此“两条事实就必然拖垮纪要”不成立。", "",
                  "相关性仅探索：small事实数与抽取覆盖Spearman=0.643，large为0.106；增加large事实条数不是覆盖保证。输入tokens与large覆盖Spearman=−0.607，与small为−0.306，混合来源、参考数和会议复杂度，不能断言长输入导致失败。不同组输出长度与覆盖相关性也并非普遍正值。详见correlations.json。", "",
                  "## 5. 五来源：不同任务有不同瓶颈", "",
                  "下表覆盖对角辅助提升（s_to_s−direct_s、l_to_l−direct_l）和gold−direct。详细八组分布、中位数、范围、16类对比与六样本归因见[source_analysis.md](source_analysis.md)。", ""])
    source_table = []
    for dataset in source_names:
        def get(arm):
            return next(row for row in aggregates if row["dataset"] == dataset and row["arm"] == arm)
        source_table.append([dataset, percent(number(get("direct_s"), "completeness_mean")), percent(number(get("direct_l"), "completeness_mean")),
                             f"{(number(get('s_to_s'),'completeness_mean') - number(get('direct_s'),'completeness_mean')) * 100:+.2f}",
                             f"{(number(get('l_to_l'),'completeness_mean') - number(get('direct_l'),'completeness_mean')) * 100:+.2f}",
                             percent(number(get("gold_to_s"), "completeness_mean")), percent(number(get("gold_to_l"), "completeness_mean"))])
    lines.extend(table(["来源", "direct_s C", "direct_l C", "small自身辅助Δpp", "large自身辅助Δpp", "gold_to_s C", "gold_to_l C"], source_table))
    lines.extend(["", "### ECTSum", "",
                  "数值/财务细节比概括主题更影响覆盖。直接模型差仅2.14pp（2胜2平2负），而small、large自身事实辅助分别+18.71/+29.01pp，都6/6提高。large抽取覆盖81.46%、small62.80%。0571和1776两条事实列表漏掉大量业绩/指引/分部指标：l_to_l相比direct_l分别+50.00/+53.12pp；与small事实相比large事实也更有帮助。但0550 small79条不等于最高质量，large有数值关系表述风险；不能以条数选赢家。", "",
                  "### MeetingBank", "",
                  "small事实3/6只有两条，但small自身辅助平均+32.17pp（5胜1平），说明原文仍发挥补充作用。l_to_s C66.09%高于l_to_l60.46%，gold_to_s80.22%也高于gold_to_l69.47%，不是large生成处处胜。0078将large总体收益拖低：direct_l73.68%→l_to_l36.84%→gold_to_l31.58%；人工对照显示这三段都写到两议员提议和3–2投票，故不能把差值解释为“辅助组漏了最终投票”，应先核查逐参考匹配。1696关于tiny homes的纪要补充与最终11–0票数也应分别判断。", "",
                  "### QMSum-Academic", "",
                  "抽取覆盖仅约49–51%，参考多为实验结果、具体配置和排期。按原评审small自身辅助−4.33pp、large自身辅助−3.36pp；但0064 direct_s、0795 direct_l明显过度匹配，0378 s_to_l也过度匹配，正负效应均受影响。仅排除0064后small自身辅助在剩余5条为+5.47pp，方向翻转。参考辅助约79.74/89.47%不是可靠人工上界；准确结论是这里同时存在信息筛选/表达与评审质量问题，不能直接得出事实辅助有害。", "",
                  "### QMSum-Committee", "",
                  "参考事实覆盖多议题、发言者和具体政策条件。large抽取63.01%、small36.59%，但l_to_s仅29.35%甚至低于s_to_s37.76%；固定large事实换large生成则+19.95pp且6/6提高。0761是最大样本差：l_to_s0/26、l_to_l18/26，前者主要列举主题，后者保留具体答复。gold_to_l相对l_to_l仅+0.42pp且2胜1平3负，不是金标准列表必然充分利用。0400 gold_to_l概括过宽（4/22），明显低于gold_to_s（14/22）。", "",
                  "### QMSum-Product", "",
                  "事实抽取覆盖small66.82%、large66.23%几乎持平，但支持small73.67%、large91.19%，问题更多是提议/定案、目标/现状、角色归属，而非条数。direct_l62.91%，s_to_l63.60%、l_to_l63.17%，模型事实的边际覆盖收益近0。参考辅助将C提到85.47/93.68%，却使F降至90.76/93.92%；gold_to_s全部6份都有不支持主张。1218成本/材料与1557降本决策是典型风险；应先清理参考的状态/数值/归属并做人工核对，不应只奖励参考词出现。", "",
                  "## 6. 全部30样本索引与具体解释", "",
                  "下面每行均为独立会议；八组C完整展示，列顺序与上文一致。每个样本的三指标分子/分母、12组局部差值、相对直接组每一条新增/丢失参考、不支持主张与纪要原文，均在[sample_analysis.md](sample_analysis.md)。", ""])
    lines.extend(table(["样本", "来源", "事实S/L", *ARMS], [[sid, evidence[sid]["dataset"],
                                                           f"{fact_index[sid,'small']['fact_count']}/{fact_index[sid,'large']['fact_count']}",
                                                           *[percent(number(index[sid, arm], "completeness")) for arm in ARMS]] for sid in sample_ids]))
    lines.extend(["", "### 逐样本诊断摘要", "",
                  "这些摘要解释实际分数差和匹配变化；未做全文人工复核的样本不作真假认证，机器新增/丢失的完整内容已逐条列在附件。", ""])
    notes = {
        "meeting-0031": "large抽取仅19条而small30条；增加条数不一定增加纪要收益。参考列表辅助small取得最高覆盖，需同时检查忠实性。",
        "meeting-0064": "direct_s被过宽松地判15/15，未写周四4点等细节；其100%不能作为辅助组退化的可信基线。事实列表中‘1或4点’也不等于最终确定4点。",
        "meeting-0078": "small仅2事实却s_to_s达到14/19；三份large纪要均含3–2投票，低分不能解读为最终投票遗漏。需复核发言者/理由的逐项匹配。",
        "meeting-0136": "s_to_s有把麦克风提议归给Marketing的主张；原文该句由Industrial Designer提出。l_to_l的Bluetooth通信芯片被判不支持，但原文有明确描述，支持分数也存在误判。",
        "meeting-0160": "direct_s强于direct_l不是异常运行的证明。s_to_s将五千万利润目标写成remote本身的profit margin，需区别总体项目利润与单位产品口径。",
        "meeting-0174": "更换large事实导致l_to_s相对s_to_s覆盖减少35.71pp，而l_to_l忠实性为18/21；事实提供与生成采用并非同一个问题。",
        "meeting-0214": "small自身辅助不增加匹配参考，large自身辅助反而下降；gold_to_l覆盖全部12条但4/24主张被判不支持，直接展示全覆盖≠全忠实。",
        "meeting-0281": "两模型自身辅助相对直接都覆盖持平，参考辅助large最好；gold_to_l仍有3/21主张被判不支持，需要核查有无扩展推断。",
        "meeting-0290": "small2事实集中于法案总体意图和咨询过程；large事实更丰富，但s_to_l高于l_to_l，列表更长不能保证生成保留更多政策细节。",
        "meeting-0291": "small16事实、large9事实，参考辅助表现更强；large自身辅助相对direct_l少一条匹配，说明辅助提示也可能改变选择。",
        "meeting-0337": "l_to_s与gold_to_s同达13/17，large自身辅助相比direct_l增8/17，是MeetingBank中large收益的重要正向样本。",
        "meeting-0378": "direct_s仅综述PLP/MLP课题，0/14并非无内容；s_to_l被评14/14，但‘仅silence输出89.1%’等细节未准确呈现，且F仅17/20。",
        "meeting-0400": "gold_to_s14/22、gold_to_l4/22，后者更像概况而不是逐项政策/经费条件。原文Global Wales3.5m为原则同意，不应自动解读为拨款已落实。",
        "meeting-0475": "direct_s谈到Eurospeech论文获接收、在线归一化、MFCC、VTS等，但仅匹配1/29条参考，缺少多数具体结果/参数；低覆盖不等于总结完全无关。",
        "meeting-0506": "l_to_l与gold_to_l同23/27，small自身辅助也增加7/27；模型事实在此已能接近参考输入下的缓存覆盖，但非全部参考均保留。",
        "meeting-0550": "small79条包含程序性信息和语义重复；gold_to_s20/23最佳。large抽取把总目标含已实现金额写成额外金额等关系风险，不能只以事实数或支持均值判断。",
        "meeting-0571": "small2事实只有销售和需求，large42条补财务/养老金/指引；l_to_l与gold_to_l都15/18，比direct_l多9条，是大事实列表有用的明确例子。",
        "meeting-0621": "gold_to_s16/18优于模型辅助，small自身辅助多9条，large自身辅助只多1条；收益大小还依赖原始基线与所选细节。",
        "meeting-0761": "small2事实的历史截断不影响当前成功缓存完整性；l_to_s主要列举主题获0/26，l_to_l18/26。gold_to_s忠实性23/27，参考输入也能引出错误扩展。",
        "meeting-0795": "direct_l获21/21，但未给出6:00送机/7:20航班、HTK3.0、6小时训练等多项细节；辅助相对其‘退化’不可按原评分作质量结论。",
        "meeting-1020": "direct_s0/31，s_to_s与l_to_l同12/31；后者抽取53条仍未形成高参考覆盖。多个致辞/归属与金额需要单独审阅。",
        "meeting-1218": "small自身辅助从4/20升11/20，却有4/32主张不支持；gold_to_s16/20但成本在12.50预算内等主张被标记，决策与评价状态不可混淆。",
        "meeting-1226": "l_to_s20/23优于两参考辅助，是large财务细节可有效利用但不是参考输入上界的例外；注意small列表有调整后口径省略问题。",
        "meeting-1386": "large直接和自身辅助覆盖持平；gold_to_s最高13/17。small事实到small生成只小幅提升，不能从单个强direct_l归纳全部Committee。",
        "meeting-1469": "s_to_s长而逐人复述；NLTK将Hon.切碎，64句仅13匹配。其完整性只增加1/24，不应把长篇与高覆盖等同，Q也受分句实现影响。",
        "meeting-1557": "small自身辅助覆盖持平，large自身辅助下降3/22；l_to_s忠实性最低22/27。数字按钮节省、滚轮功能与LCD偏好需要原文状态/归属核对。",
        "meeting-1696": "small2事实但s_to_l12/16，l_to_l仅6/16；gold_to_s14/16最高。tiny homes的最终11–0投票与规模、成本应分别查验，原文有转录噪声。",
        "meeting-1719": "small2事实包含最终Jan15和4–1票数，不是只读开头；small自身辅助覆盖持平，l_to_l/gold_to_l11/12，s_to_l则有3/19主张不支持。",
        "meeting-1726": "small自身辅助较direct_s增11/21、large自身辅助增9/21，都是MeetingBank均值提升的强驱动；gold_to_l17/21最佳，但尚非全覆盖。",
        "meeting-1776": "small2事实覆盖收入/亏损；l_to_l22/32比direct_l多17条。长large列表仍漏部分分部细节，gold_to_s27/32最高，不能把全指标财务覆盖归为单一条数问题。",
    }
    assert set(notes) == set(sample_ids)
    for sid in sample_ids:
        baseline_small = number(index[sid, "direct_s"], "completeness")
        baseline_large = number(index[sid, "direct_l"], "completeness")
        small_change = (number(index[sid, "s_to_s"], "completeness") - baseline_small) * 100
        large_change = (number(index[sid, "l_to_l"], "completeness") - baseline_large) * 100
        lines.append(f"- **{sid}**：自身辅助small {small_change:+.2f}pp、large {large_change:+.2f}pp。{notes[sid]}")
    lines.extend(["", "## 7. 人工发现的评审边界与敏感性", "",
                  "### 7.1 三例过度匹配", ""])
    for item in review[:3]:
        lines.extend([f"**{item['sample_id']} {item['arm']}，R{item['reference_id']}**", "",
                      f"参考：{item['reference']}", "", f"被判完整蕴含的句子：{item['judge_matched_sentence']}", ""])
    lines.extend(["0064的‘计划再次见面’不足以支持周四4点并讨论Grad A论文提案；0795的‘early morning’不支持6:00/7:20和谁驾车；0378将89.1%用于另一配置，不能支持‘仅silence输出’的精确结果。这些是现有文本可直接复核的宽松匹配，不需要新模型调用。", "",
                  "### 7.2 支持误判与分句偏差", "",
                  "0136 l_to_l主张‘One proposed chip is a Bluetooth chip for communication.’被判不支持；原文Industrial Designer明确说Bluetooth chip负责两个设备通信。此项至少是需要修正/复核的疑似漏判，不可把所有不支持标签都当成真实幻觉。相反，s_to_s的Marketing麦克风角色归属有原文反证。", "",
                  f"1469 s_to_s：64个分句中有{len(isolated)}个单独的Hon./Mr./Ms.片段；第一句还在Hon.处被截开。13/64=20.31%的Q混入分句碎片惩罚，不能直接当作真正的有效句比例。此次未替换分句器、重评或改分。", "",
                  "### 7.3 保持原分的排除敏感性", "",
                  "以下只是排除可疑样本后的重汇总，不是人工纠正分数，也不是挑选最有利子集。排除样本同时损失部分真实信息，应与完整30条并列阅读。", ""])
    lines.extend(table(["排除", "来源", "n", "对比", "覆盖均差pp"], [[",".join(item["excluded_samples"]), item["dataset"], item["n"], item["contrast"],
                                                                 f"{item['mean_difference'] * 100:+.2f}"] for item in sensitivity]))
    lines.extend(["", "原评审下Academic small自身辅助−4.33pp，仅剔除0064后+5.47pp，说明该方向对单例异常敏感。其它排除组合见上表；不把剩余3条当成足以推广的Academic估计。", "",
                  "## 8. 对整体实验的准确解释", "",
                  "1. **能确认的流程事实**：pilot与全部成功缓存完整、对应当前输入；既有数值可复现；没有因缺项而形成不公平的均值。",
                  "2. **能确认的描述性结果**：按缓存口径辅助组覆盖平均更高，来源与样本异质性大，忠实性不总同步改善，large抽取收益未等比例传到纪要。",
                  "3. **人工能确认的内容事实**：至少三例参考匹配过宽松；有疑似支持漏判和实际角色错配；NLP分句会改变简洁率分母。因此分数精确不等于测量准确。",
                  "4. **尚不能确认的机制**：单次相同seed下的结果无法量化采样/服务运行方差；温度、重复惩罚、并发与模型规模不能凭此分离。没有把观察关联宣称为因果归因。",
                  "5. **尚不能确认的推广**：pilot含每来源最短/最长样本，不是简单随机样本；总体来源权重75/75/50/30/70而pilot等权。source_weight_sensitivity.csv只按来源比例重加权，不校正来源内有意选长度极端，不能当成300条真实成绩。",
                  "6. **尚不能确认的成本排名**：这是缓存token统计，不是同一运行窗口下的完整延迟、显存、实际成本测量。此次没有执行新评测或模型服务。", "",
                  "建议首先人工盲审上述匹配异常和Product状态/数值，统一完整蕴含标准并检查参考文本本身是否忠实；随后再考虑受控多seed、定长预算和更大测试集。当前不宜把Q/F的微小名义差值包装成确定排名，也不宜把gold视为没有错误的上界。", "",
                  "## 9. 文件索引与阅读路径", "",
                  "- [sample_analysis.md](sample_analysis.md)：30个样本逐一，全部八组三指标与分子/分母、增减参考事实及不支持主张。",
                  "- [source_analysis.md](source_analysis.md)：五来源八组均值/中位/范围、抽取分布、胜平负与极端样本。",
                  "- [sample_completeness.png](sample_completeness.png)：30×8完整性热图；[metric_distributions.png](metric_distributions.png)：三指标分布。",
                  "- [summary_metrics_recomputed.csv](summary_metrics_recomputed.csv)、[fact_metrics_recomputed.csv](fact_metrics_recomputed.csv)：逐样本完整可计算数值。",
                  "- [summary_distribution_by_source.csv](summary_distribution_by_source.csv)、[fact_distribution_by_source.csv](fact_distribution_by_source.csv)：宏/微、四分位、标准差、范围与总计。",
                  "- [paired_contrasts.csv](paired_contrasts.csv)：整体/来源16对比×3指标，含CI、胜平负、去掉任一样本后的均值范围；[per_sample_contrasts.csv](per_sample_contrasts.csv)：1440条个体差值。",
                  "- [reference_transitions.csv](reference_transitions.csv)、[summary_reference_alignment.csv](summary_reference_alignment.csv)、[fact_reference_alignment.csv](fact_reference_alignment.csv)：原文参考→事实→句子的逐项对齐。",
                  "- [judge_unsupported_claims.csv](judge_unsupported_claims.csv)：全部275个缓存不支持标签，不能不经复核当作真实错误。",
                  "- [sample_evidence.json](sample_evidence.json)：全部30样本参考、60列表、240纪要、分句、分解主张与匹配；[human_review_evidence.json](human_review_evidence.json)：明确的人工核对证据。",
                  "- [validation.json](validation.json)、[cache_validation.csv](cache_validation.csv)：重算、哈希和状态核验；[preserved_errors.json](preserved_errors.json)：历史错误摘要。",
                  "- [analyze.py](analyze.py)、[deliver.py](deliver.py)：复现脚本。输出使用排他创建，直接重跑到此目录会拒绝覆盖；应在新的独立目录运行。", ""])
    with (ROOT / "report_zh.md").open("x", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")
    draw_figures(sample_ids, index, summaries)
    print("DELIVERY_COMPLETE", "sample_count", len(sample_ids), "honorific_fragments", len(isolated), "review_cases", len(review))
    print("SENSITIVITY", json.dumps(sensitivity, ensure_ascii=False))
    print("JOINT", json.dumps(joint, ensure_ascii=False))


def draw_figures(sample_ids, index, summaries):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plotting
    import numpy

    matrix = numpy.array([[number(index[sid, arm], "completeness") for arm in ARMS] for sid in sample_ids])
    figure, axis = plotting.subplots(figsize=(11, 13))
    image = axis.imshow(matrix, vmin=0, vmax=1, cmap="YlGnBu", aspect="auto")
    axis.set_xticks(range(len(ARMS)), ARMS, rotation=35, ha="right")
    axis.set_yticks(range(len(sample_ids)), sample_ids)
    for row_index in range(len(sample_ids)):
        for column_index in range(len(ARMS)):
            value = matrix[row_index, column_index]
            axis.text(column_index, row_index, f"{value * 100:.0f}", ha="center", va="center", fontsize=7,
                      color="white" if value > 0.7 else "black")
    axis.set_title("Cached reference completeness (%) by meeting and arm")
    figure.colorbar(image, ax=axis, label="Completeness")
    figure.tight_layout()
    path = ROOT / "sample_completeness.png"
    assert not path.exists()
    figure.savefig(path, dpi=160)
    plotting.close(figure)
    figure, axes = plotting.subplots(1, 3, figsize=(15, 5))
    for axis, metric in zip(axes, METRICS):
        groups = [[number(row, metric) * 100 for row in summaries if row["arm"] == arm] for arm in ARMS]
        axis.boxplot(groups, labels=ARMS, showmeans=True)
        axis.tick_params(axis="x", labelrotation=55)
        axis.set_title(metric)
        axis.set_ylabel("Percent")
        axis.grid(axis="y", alpha=0.2)
    figure.suptitle("Cached 30-meeting distributions (judge anomalies not corrected)")
    figure.tight_layout()
    path = ROOT / "metric_distributions.png"
    assert not path.exists()
    figure.savefig(path, dpi=160)
    plotting.close(figure)


if __name__ == "__main__":
    main()