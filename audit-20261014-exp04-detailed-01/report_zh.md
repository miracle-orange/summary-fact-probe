# exp04-2gpu 完整数据分析

## 1. 结论与可信边界

本分析覆盖pilot全部30场会议、60份模型事实列表、240份纪要和840份成功评审缓存。五来源各6条；30场共601条参考事实。
**主结论：事实辅助主要提高按参考定义的覆盖，而不是三项质量同步提升；增益因来源和样本而异。large抽取明显优于small，并没有稳定地转化为同等纪要收益。参考事实辅助是诊断干预，不是真实部署的免费输入，也不是已证实的质量上界。**

**特别警告：复核发现部分明显过宽松的参考匹配、至少一例疑似支持漏判及称谓分句偏差。因此，下面是精确的现有机器评审结果，不是全部人工正确性认证；不能仅凭这些分数认定Academic事实辅助有害或large必然更好。**

原实验代码、配置、数据、生成、评测缓存和日志未改动；未启动模型、重生成文本、调用评审API、读取凭据或执行commit/push。所有新文件均位于这个新独立审计目录。

## 2. 指标、实验组与完整性核验

small=Qwen3-8B，large=Qwen3-32B。direct为原文直接纪要；s_to_*、l_to_*分别使用small、large抽取事实；gold_to_*使用数据中的参考事实。辅助组仍可读取完整原文，并可纠正/补充事实列表。

- 完整性C = 匹配参考事实数 / 参考事实数。不是原文所有重要信息的穷尽召回率。
- 简洁性Q = 至少匹配一条参考事实的不同句子数 / 总句数。不是长度、文笔或重复率指标；没有匹配参考的有效补充也会降低Q。
- 忠实性F = 被评审判为原文支持的分解主张数 / 分解主张总数。100%只代表此评审未标记错误。
- 抽取覆盖按参考匹配计算；抽取支持直接评审每个列表项，不做同样的主张分解，不能与纪要F直接横比。
- 宏平均每会议等权；微平均先合并分子、分母。总体宏平均也等权五来源，因为每来源都是6条。百分点简称pp。

300份指标全部重新计算一致；300个生成请求哈希、840个评审请求哈希全部对应当前pilot数据与协议快照；48行原报告宏平均精确一致。成功缓存全部finish_reason=stop；响应身份记录为small/large或Pro/deepseek-ai/DeepSeek-V3.2。此校验不证明评审语义正确，也不是网络或模型权重字节级证明。

现评测状态requested=300、failures=[]。保留的旧错误记录包括：0761 small抽取length截断；0290 large事实匹配和0400 l_to_l纪要匹配曾返回错误条数。后两项旧diagnostics仍记录失败，但当前成功缓存与指标均通过，不应当作现存缺失，也不应抹去失败历史。

## 3. 整体结果：均值之外

| 组 | C宏/微 | Q宏/微 | F宏/微 | 匹配参考/601 | 不支持主张/全部 | 全部支持纪要 | 平均输出tokens |
| --- | --- | --- | --- | --- | --- | --- | --- |
| direct_s | 39.41%/36.27% | 66.25%/66.07% | 97.62%/97.60% | 218 | 15/624 | 21/30 | 179.9 |
| direct_l | 48.61%/46.09% | 73.16%/71.63% | 98.07%/98.03% | 277 | 14/710 | 19/30 | 217.5 |
| s_to_s | 53.03%/51.25% | 67.62%/57.76% | 95.83%/95.75% | 308 | 37/870 | 12/30 | 335.3 |
| s_to_l | 56.56%/54.24% | 71.59%/70.53% | 95.53%/96.00% | 326 | 33/825 | 14/30 | 288.9 |
| l_to_s | 53.82%/52.08% | 63.81%/63.49% | 96.26%/96.55% | 313 | 31/898 | 14/30 | 341.1 |
| l_to_l | 59.05%/58.24% | 68.42%/66.77% | 95.75%/95.96% | 350 | 37/915 | 11/30 | 328.1 |
| gold_to_s | 74.50%/72.71% | 88.82%/89.22% | 95.99%/96.39% | 437 | 30/830 | 16/30 | 297.5 |
| gold_to_l | 76.34%/74.38% | 85.23%/85.51% | 96.97%/97.37% | 447 | 21/799 | 19/30 | 305.3 |

### 3.1 配对提升是否普遍

以下95%百分位区间采用2000次会议级配对bootstrap，C/Q/F种子分别为42/43/44。它们是pilot描述性不确定性，不含评审误差，不作多重比较校正，也不证明因果机制或推广到全部会议。

| 完整性对比 | 平均差pp | 中位差pp | 95%区间pp | 胜/平/负 |
| --- | --- | --- | --- | --- |
| direct_l - direct_s | +9.20 | +5.41 | [+1.65,+16.90] | 16/5/9 |
| s_to_s - direct_s | +13.62 | +13.66 | [+4.89,+21.69] | 22/5/3 |
| l_to_s - direct_s | +14.41 | +18.86 | [+3.39,+24.47] | 21/2/7 |
| gold_to_s - direct_s | +35.09 | +34.52 | [+27.15,+43.22] | 27/2/1 |
| s_to_l - direct_l | +7.95 | +12.50 | [+0.44,+15.03] | 22/1/7 |
| l_to_l - direct_l | +10.44 | +10.12 | [+2.12,+18.85] | 18/4/8 |
| gold_to_l - direct_l | +27.73 | +32.29 | [+19.36,+35.48] | 27/2/1 |
| l_to_s - s_to_s | +0.79 | -1.85 | [-5.29,+6.47] | 12/3/15 |
| l_to_l - s_to_l | +2.49 | +3.99 | [-4.72,+9.82] | 16/2/12 |
| s_to_l - s_to_s | +3.53 | +0.00 | [-2.69,+10.09] | 14/4/12 |
| l_to_l - l_to_s | +5.22 | +5.32 | [-0.59,+12.08] | 18/3/9 |
| gold_to_l - gold_to_s | +1.83 | +6.23 | [-4.97,+8.21] | 16/1/13 |
| gold_to_s - s_to_s | +21.47 | +22.25 | [+15.11,+27.70] | 25/2/3 |
| gold_to_s - l_to_s | +20.68 | +22.25 | [+14.55,+26.84] | 25/2/3 |
| gold_to_l - s_to_l | +19.78 | +11.32 | [+12.10,+27.06] | 25/2/3 |
| gold_to_l - l_to_l | +17.29 | +18.33 | [+9.92,+24.21] | 21/4/5 |

**解读**：s_to_s相对direct_s为22胜5平3负；l_to_l相对direct_l为18胜4平8负。提高总体均值不等于每会议受益。更换为large事实，small生成平均只再提升0.79pp（12胜3平15负），large生成只提升2.49pp（16胜2平12负），两者区间跨0；不能宣称large事实普遍更有用。

直接生成时large相对small覆盖多9.20pp；固定事实后large生成优势为3.53pp（small事实）、5.22pp（large事实）、1.83pp（参考事实），各区间跨0。这与选择信息的重要性一致，但不足以把直接模型差距全部归因于事实选择：提示、采样结果、长度与评审误差同时参与。

### 3.2 覆盖提升的代价

模型事实辅助后的宏F都低于对应直接组：s_to_s −1.79pp、l_to_s −1.36pp、s_to_l −2.54pp、l_to_l −2.32pp。后两项名义bootstrap区间分别为[−5.04,−0.02]和[−4.42,−0.15]pp；仅作诊断，尤其−0.02pp贴近0，不宜包装为稳健显著结论。

全部支持的纪要数从direct_s 21/30降至s_to_s 12/30，从direct_l 19/30降至l_to_l 11/30。即使平均F仍约96%，至少有一个不支持标签的会议比例并不低。所有240份纪要共218条主张被判不支持；60份抽取共57个列表项被判不支持。

| 对比 | 覆盖升且F不降 | 覆盖升但F下降 | C/Q/F帕累托改善 | 帕累托恶化 |
| --- | --- | --- | --- | --- |
| s_to_s - direct_s | 13 | 9 | 9 | 6 |
| l_to_s - direct_s | 13 | 8 | 9 | 9 |
| s_to_l - direct_l | 13 | 9 | 9 | 7 |
| l_to_l - direct_l | 9 | 9 | 6 | 9 |
| gold_to_s - direct_s | 18 | 9 | 18 | 2 |
| gold_to_l - direct_l | 20 | 7 | 17 | 1 |

帕累托改善指三项均不降且至少一项严格升；这里只是原评分下的计数，没有任意加权总分。

s_to_s平均输出335.3tokens，direct_s为179.9，增加约86%；l_to_l为328.1，direct_l为217.5，增加约51%。但没有定长约束，所以不能视为在同等长度预算下比较。small/large事实抽取另需平均411.5/534.3输出tokens；顺序流程每会议抽取+纪要约746.8tokens（s_to_s）或862.4tokens（l_to_l），不是纪要一个步骤的成本。跨组复用抽取会改变摊销方式，不能把token数直接换算为墙钟或API费用。

s_to_s的Q宏67.62%、微57.76%，差近10pp。1469占64个切分句但仅13句匹配参考，1020为23句/9句匹配；长纪要/分句碎片在微平均里权重更大。高F或高Q都不代表覆盖充分，例如direct_s仍只匹配218/601。

## 4. 抽取与纪要：不能把两阶段等同

| 抽取模型 | 宏覆盖 | 微覆盖 | 宏支持 | 微支持 | 事实数总计 | 不支持列表项 | 两条事实样本 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| small | 52.65% | 51.75% | 89.10% | 91.52% | 448 | 38 | 7 |
| large | 68.33% | 67.89% | 96.24% | 96.92% | 617 | 19 | 0 |

large较small宏抽取覆盖提高15.69pp、宏支持提高7.14pp，参考匹配总计408 vs 311，事实617 vs 448；这是清晰的抽取阶段差异，但模型大小还伴随内容粒度变化。

### 4.1 参考匹配迁移

| 组 | 抽取匹配 | 纪要匹配 | 两者匹配 | 仅纪要匹配 | 仅抽取匹配 | 匹配保留率 |
| --- | --- | --- | --- | --- | --- | --- |
| s_to_s | 311 | 308 | 258 | 50 | 53 | 82.96% |
| s_to_l | 311 | 326 | 253 | 73 | 58 | 81.35% |
| l_to_s | 408 | 313 | 294 | 19 | 114 | 72.06% |
| l_to_l | 408 | 350 | 325 | 25 | 83 | 79.66% |

small事实辅助中出现50/73条仅纪要匹配参考，large事实辅助中为19/25条。辅助组能从原文补充；抽取缺失不是纪要无法覆盖的硬上限。反过来large列表里114/83条已匹配参考未进入small/large纪要，表明有事实≠使用事实。这里是两个独立匹配评审的集合迁移，不是已证实的逐条心理/因果路径；不把同句改写和评审差异当成真实补充/遗漏的铁证。

### 4.2 两条事实子群

7条small两事实样本（0078、0290、0571、0761、1696、1719、1776）中，direct_s C=30.58%，s_to_s=42.96%，l_to_s=51.72%，l_to_l=60.77%。其他23条s_to_s=56.10%、l_to_s=54.47%。两条子群中更换large事实，small生成平均+8.75pp；其余组反而−1.63pp。总体+0.79pp混合了方向不同的子群。

但子群不是随机分组，混合ECTSum、MeetingBank、Committee；不能把差异当作两条事实的因果效应。0761自身辅助C从42.31%降到19.23%，而0078自身辅助从31.58%升到73.68%，因此“两条事实就必然拖垮纪要”不成立。

相关性仅探索：small事实数与抽取覆盖Spearman=0.643，large为0.106；增加large事实条数不是覆盖保证。输入tokens与large覆盖Spearman=−0.607，与small为−0.306，混合来源、参考数和会议复杂度，不能断言长输入导致失败。不同组输出长度与覆盖相关性也并非普遍正值。详见correlations.json。

## 5. 五来源：不同任务有不同瓶颈

下表覆盖对角辅助提升（s_to_s−direct_s、l_to_l−direct_l）和gold−direct。详细八组分布、中位数、范围、16类对比与六样本归因见[source_analysis.md](source_analysis.md)。

| 来源 | direct_s C | direct_l C | small自身辅助Δpp | large自身辅助Δpp | gold_to_s C | gold_to_l C |
| --- | --- | --- | --- | --- | --- | --- |
| ECTSum | 36.46% | 38.60% | +18.71 | +29.01 | 76.32% | 79.34% |
| MeetingBank | 30.92% | 45.83% | +32.17 | +14.63 | 80.22% | 69.47% |
| QMSum-Academic | 52.50% | 58.06% | -4.33 | -3.36 | 79.74% | 89.47% |
| QMSum-Committee | 27.27% | 37.64% | +10.49 | +11.66 | 50.77% | 49.72% |
| QMSum-Product | 49.91% | 62.91% | +11.07 | +0.27 | 85.47% | 93.68% |

### ECTSum

数值/财务细节比概括主题更影响覆盖。直接模型差仅2.14pp（2胜2平2负），而small、large自身事实辅助分别+18.71/+29.01pp，都6/6提高。large抽取覆盖81.46%、small62.80%。0571和1776两条事实列表漏掉大量业绩/指引/分部指标：l_to_l相比direct_l分别+50.00/+53.12pp；与small事实相比large事实也更有帮助。但0550 small79条不等于最高质量，large有数值关系表述风险；不能以条数选赢家。

### MeetingBank

small事实3/6只有两条，但small自身辅助平均+32.17pp（5胜1平），说明原文仍发挥补充作用。l_to_s C66.09%高于l_to_l60.46%，gold_to_s80.22%也高于gold_to_l69.47%，不是large生成处处胜。0078将large总体收益拖低：direct_l73.68%→l_to_l36.84%→gold_to_l31.58%；人工对照显示这三段都写到两议员提议和3–2投票，故不能把差值解释为“辅助组漏了最终投票”，应先核查逐参考匹配。1696关于tiny homes的纪要补充与最终11–0票数也应分别判断。

### QMSum-Academic

抽取覆盖仅约49–51%，参考多为实验结果、具体配置和排期。按原评审small自身辅助−4.33pp、large自身辅助−3.36pp；但0064 direct_s、0795 direct_l明显过度匹配，0378 s_to_l也过度匹配，正负效应均受影响。仅排除0064后small自身辅助在剩余5条为+5.47pp，方向翻转。参考辅助约79.74/89.47%不是可靠人工上界；准确结论是这里同时存在信息筛选/表达与评审质量问题，不能直接得出事实辅助有害。

### QMSum-Committee

参考事实覆盖多议题、发言者和具体政策条件。large抽取63.01%、small36.59%，但l_to_s仅29.35%甚至低于s_to_s37.76%；固定large事实换large生成则+19.95pp且6/6提高。0761是最大样本差：l_to_s0/26、l_to_l18/26，前者主要列举主题，后者保留具体答复。gold_to_l相对l_to_l仅+0.42pp且2胜1平3负，不是金标准列表必然充分利用。0400 gold_to_l概括过宽（4/22），明显低于gold_to_s（14/22）。

### QMSum-Product

事实抽取覆盖small66.82%、large66.23%几乎持平，但支持small73.67%、large91.19%，问题更多是提议/定案、目标/现状、角色归属，而非条数。direct_l62.91%，s_to_l63.60%、l_to_l63.17%，模型事实的边际覆盖收益近0。参考辅助将C提到85.47/93.68%，却使F降至90.76/93.92%；gold_to_s全部6份都有不支持主张。1218成本/材料与1557降本决策是典型风险；应先清理参考的状态/数值/归属并做人工核对，不应只奖励参考词出现。

## 6. 全部30样本索引与具体解释

下面每行均为独立会议；八组C完整展示，列顺序与上文一致。每个样本的三指标分子/分母、12组局部差值、相对直接组每一条新增/丢失参考、不支持主张与纪要原文，均在[sample_analysis.md](sample_analysis.md)。

| 样本 | 来源 | 事实S/L | direct_s | direct_l | s_to_s | s_to_l | l_to_s | l_to_l | gold_to_s | gold_to_l |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| meeting-0031 | ECTSum | 30/19 | 38.46% | 30.77% | 57.69% | 53.85% | 53.85% | 42.31% | 76.92% | 65.38% |
| meeting-0064 | QMSum-Academic | 12/14 | 100.00% | 66.67% | 46.67% | 40.00% | 40.00% | 53.33% | 93.33% | 80.00% |
| meeting-0078 | MeetingBank | 2/13 | 31.58% | 73.68% | 73.68% | 47.37% | 52.63% | 36.84% | 73.68% | 31.58% |
| meeting-0136 | QMSum-Product | 10/12 | 50.00% | 50.00% | 64.29% | 57.14% | 64.29% | 64.29% | 85.71% | 100.00% |
| meeting-0160 | QMSum-Product | 11/12 | 71.43% | 57.14% | 78.57% | 78.57% | 64.29% | 71.43% | 92.86% | 85.71% |
| meeting-0174 | QMSum-Academic | 11/10 | 64.29% | 57.14% | 64.29% | 64.29% | 28.57% | 57.14% | 78.57% | 71.43% |
| meeting-0214 | QMSum-Product | 8/13 | 66.67% | 66.67% | 66.67% | 50.00% | 58.33% | 58.33% | 83.33% | 100.00% |
| meeting-0281 | QMSum-Academic | 12/13 | 61.54% | 53.85% | 61.54% | 61.54% | 61.54% | 53.85% | 84.62% | 92.31% |
| meeting-0290 | QMSum-Committee | 2/21 | 4.76% | 52.38% | 23.81% | 71.43% | 33.33% | 38.10% | 38.10% | 61.90% |
| meeting-0291 | QMSum-Product | 16/9 | 55.00% | 80.00% | 65.00% | 85.00% | 60.00% | 75.00% | 80.00% | 95.00% |
| meeting-0337 | MeetingBank | 8/14 | 29.41% | 23.53% | 52.94% | 58.82% | 76.47% | 70.59% | 76.47% | 64.71% |
| meeting-0378 | QMSum-Academic | 18/10 | 0.00% | 50.00% | 35.71% | 100.00% | 57.14% | 57.14% | 50.00% | 100.00% |
| meeting-0400 | QMSum-Committee | 18/19 | 13.64% | 13.64% | 31.82% | 36.36% | 27.27% | 50.00% | 63.64% | 18.18% |
| meeting-0475 | QMSum-Academic | 11/11 | 3.45% | 20.69% | 37.93% | 34.48% | 37.93% | 44.83% | 86.21% | 93.10% |
| meeting-0506 | ECTSum | 31/16 | 51.85% | 51.85% | 77.78% | 74.07% | 74.07% | 85.19% | 66.67% | 85.19% |
| meeting-0550 | ECTSum | 79/19 | 47.83% | 39.13% | 60.87% | 43.48% | 47.83% | 56.52% | 86.96% | 82.61% |
| meeting-0571 | ECTSum | 2/42 | 33.33% | 33.33% | 44.44% | 55.56% | 66.67% | 83.33% | 77.78% | 83.33% |
| meeting-0621 | MeetingBank | 22/27 | 11.11% | 44.44% | 61.11% | 61.11% | 55.56% | 50.00% | 88.89% | 66.67% |
| meeting-0761 | QMSum-Committee | 2/28 | 42.31% | 50.00% | 19.23% | 23.08% | 0.00% | 69.23% | 42.31% | 53.85% |
| meeting-0795 | QMSum-Academic | 11/15 | 85.71% | 100.00% | 42.86% | 61.90% | 57.14% | 61.90% | 85.71% | 100.00% |
| meeting-1020 | QMSum-Committee | 25/53 | 0.00% | 22.58% | 38.71% | 35.48% | 25.81% | 38.71% | 25.81% | 35.48% |
| meeting-1218 | QMSum-Product | 12/16 | 20.00% | 60.00% | 55.00% | 70.00% | 65.00% | 60.00% | 80.00% | 95.00% |
| meeting-1226 | ECTSum | 16/40 | 34.78% | 60.87% | 65.22% | 73.91% | 86.96% | 69.57% | 65.22% | 78.26% |
| meeting-1386 | QMSum-Committee | 10/20 | 52.94% | 70.59% | 58.82% | 64.71% | 64.71% | 70.59% | 76.47% | 70.59% |
| meeting-1469 | QMSum-Committee | 35/27 | 50.00% | 16.67% | 54.17% | 29.17% | 25.00% | 29.17% | 58.33% | 58.33% |
| meeting-1557 | QMSum-Product | 10/20 | 36.36% | 63.64% | 36.36% | 40.91% | 59.09% | 50.00% | 90.91% | 86.36% |
| meeting-1696 | MeetingBank | 2/10 | 31.25% | 50.00% | 56.25% | 75.00% | 75.00% | 37.50% | 87.50% | 81.25% |
| meeting-1719 | MeetingBank | 2/16 | 58.33% | 50.00% | 58.33% | 50.00% | 75.00% | 91.67% | 83.33% | 91.67% |
| meeting-1726 | MeetingBank | 18/34 | 23.81% | 33.33% | 76.19% | 71.43% | 61.90% | 76.19% | 71.43% | 80.95% |
| meeting-1776 | ECTSum | 2/44 | 12.50% | 15.62% | 25.00% | 28.12% | 59.38% | 68.75% | 84.38% | 81.25% |

### 逐样本诊断摘要

这些摘要解释实际分数差和匹配变化；未做全文人工复核的样本不作真假认证，机器新增/丢失的完整内容已逐条列在附件。

- **meeting-0031**：自身辅助small +19.23pp、large +11.54pp。large抽取仅19条而small30条；增加条数不一定增加纪要收益。参考列表辅助small取得最高覆盖，需同时检查忠实性。
- **meeting-0064**：自身辅助small -53.33pp、large -13.33pp。direct_s被过宽松地判15/15，未写周四4点等细节；其100%不能作为辅助组退化的可信基线。事实列表中‘1或4点’也不等于最终确定4点。
- **meeting-0078**：自身辅助small +42.11pp、large -36.84pp。small仅2事实却s_to_s达到14/19；三份large纪要均含3–2投票，低分不能解读为最终投票遗漏。需复核发言者/理由的逐项匹配。
- **meeting-0136**：自身辅助small +14.29pp、large +14.29pp。s_to_s有把麦克风提议归给Marketing的主张；原文该句由Industrial Designer提出。l_to_l的Bluetooth通信芯片被判不支持，但原文有明确描述，支持分数也存在误判。
- **meeting-0160**：自身辅助small +7.14pp、large +14.29pp。direct_s强于direct_l不是异常运行的证明。s_to_s将五千万利润目标写成remote本身的profit margin，需区别总体项目利润与单位产品口径。
- **meeting-0174**：自身辅助small +0.00pp、large +0.00pp。更换large事实导致l_to_s相对s_to_s覆盖减少35.71pp，而l_to_l忠实性为18/21；事实提供与生成采用并非同一个问题。
- **meeting-0214**：自身辅助small +0.00pp、large -8.33pp。small自身辅助不增加匹配参考，large自身辅助反而下降；gold_to_l覆盖全部12条但4/24主张被判不支持，直接展示全覆盖≠全忠实。
- **meeting-0281**：自身辅助small +0.00pp、large +0.00pp。两模型自身辅助相对直接都覆盖持平，参考辅助large最好；gold_to_l仍有3/21主张被判不支持，需要核查有无扩展推断。
- **meeting-0290**：自身辅助small +19.05pp、large -14.29pp。small2事实集中于法案总体意图和咨询过程；large事实更丰富，但s_to_l高于l_to_l，列表更长不能保证生成保留更多政策细节。
- **meeting-0291**：自身辅助small +10.00pp、large -5.00pp。small16事实、large9事实，参考辅助表现更强；large自身辅助相对direct_l少一条匹配，说明辅助提示也可能改变选择。
- **meeting-0337**：自身辅助small +23.53pp、large +47.06pp。l_to_s与gold_to_s同达13/17，large自身辅助相比direct_l增8/17，是MeetingBank中large收益的重要正向样本。
- **meeting-0378**：自身辅助small +35.71pp、large +7.14pp。direct_s仅综述PLP/MLP课题，0/14并非无内容；s_to_l被评14/14，但‘仅silence输出89.1%’等细节未准确呈现，且F仅17/20。
- **meeting-0400**：自身辅助small +18.18pp、large +36.36pp。gold_to_s14/22、gold_to_l4/22，后者更像概况而不是逐项政策/经费条件。原文Global Wales3.5m为原则同意，不应自动解读为拨款已落实。
- **meeting-0475**：自身辅助small +34.48pp、large +24.14pp。direct_s谈到Eurospeech论文获接收、在线归一化、MFCC、VTS等，但仅匹配1/29条参考，缺少多数具体结果/参数；低覆盖不等于总结完全无关。
- **meeting-0506**：自身辅助small +25.93pp、large +33.33pp。l_to_l与gold_to_l同23/27，small自身辅助也增加7/27；模型事实在此已能接近参考输入下的缓存覆盖，但非全部参考均保留。
- **meeting-0550**：自身辅助small +13.04pp、large +17.39pp。small79条包含程序性信息和语义重复；gold_to_s20/23最佳。large抽取把总目标含已实现金额写成额外金额等关系风险，不能只以事实数或支持均值判断。
- **meeting-0571**：自身辅助small +11.11pp、large +50.00pp。small2事实只有销售和需求，large42条补财务/养老金/指引；l_to_l与gold_to_l都15/18，比direct_l多9条，是大事实列表有用的明确例子。
- **meeting-0621**：自身辅助small +50.00pp、large +5.56pp。gold_to_s16/18优于模型辅助，small自身辅助多9条，large自身辅助只多1条；收益大小还依赖原始基线与所选细节。
- **meeting-0761**：自身辅助small -23.08pp、large +19.23pp。small2事实的历史截断不影响当前成功缓存完整性；l_to_s主要列举主题获0/26，l_to_l18/26。gold_to_s忠实性23/27，参考输入也能引出错误扩展。
- **meeting-0795**：自身辅助small -42.86pp、large -38.10pp。direct_l获21/21，但未给出6:00送机/7:20航班、HTK3.0、6小时训练等多项细节；辅助相对其‘退化’不可按原评分作质量结论。
- **meeting-1020**：自身辅助small +38.71pp、large +16.13pp。direct_s0/31，s_to_s与l_to_l同12/31；后者抽取53条仍未形成高参考覆盖。多个致辞/归属与金额需要单独审阅。
- **meeting-1218**：自身辅助small +35.00pp、large +0.00pp。small自身辅助从4/20升11/20，却有4/32主张不支持；gold_to_s16/20但成本在12.50预算内等主张被标记，决策与评价状态不可混淆。
- **meeting-1226**：自身辅助small +30.43pp、large +8.70pp。l_to_s20/23优于两参考辅助，是large财务细节可有效利用但不是参考输入上界的例外；注意small列表有调整后口径省略问题。
- **meeting-1386**：自身辅助small +5.88pp、large +0.00pp。large直接和自身辅助覆盖持平；gold_to_s最高13/17。small事实到small生成只小幅提升，不能从单个强direct_l归纳全部Committee。
- **meeting-1469**：自身辅助small +4.17pp、large +12.50pp。s_to_s长而逐人复述；NLTK将Hon.切碎，64句仅13匹配。其完整性只增加1/24，不应把长篇与高覆盖等同，Q也受分句实现影响。
- **meeting-1557**：自身辅助small +0.00pp、large -13.64pp。small自身辅助覆盖持平，large自身辅助下降3/22；l_to_s忠实性最低22/27。数字按钮节省、滚轮功能与LCD偏好需要原文状态/归属核对。
- **meeting-1696**：自身辅助small +25.00pp、large -12.50pp。small2事实但s_to_l12/16，l_to_l仅6/16；gold_to_s14/16最高。tiny homes的最终11–0投票与规模、成本应分别查验，原文有转录噪声。
- **meeting-1719**：自身辅助small +0.00pp、large +41.67pp。small2事实包含最终Jan15和4–1票数，不是只读开头；small自身辅助覆盖持平，l_to_l/gold_to_l11/12，s_to_l则有3/19主张不支持。
- **meeting-1726**：自身辅助small +52.38pp、large +42.86pp。small自身辅助较direct_s增11/21、large自身辅助增9/21，都是MeetingBank均值提升的强驱动；gold_to_l17/21最佳，但尚非全覆盖。
- **meeting-1776**：自身辅助small +12.50pp、large +53.12pp。small2事实覆盖收入/亏损；l_to_l22/32比direct_l多17条。长large列表仍漏部分分部细节，gold_to_s27/32最高，不能把全指标财务覆盖归为单一条数问题。

## 7. 人工发现的评审边界与敏感性

### 7.1 三例过度匹配

**meeting-0064 direct_s，R15**

参考：The group scheduled the next meeting for Thursday at 4:00 PM to discuss Grad A's thesis proposal.

被判完整蕴含的句子：They also mention the use of JavaBayes for probabilistic modeling and plan to meet again to review and provide feedback on the work.

**meeting-0795 direct_l，R2**

参考：Professor F will drive the students to the airport at 6:00 AM to catch a 7:20 AM flight to OGI.

被判完整蕴含的句子：The group discusses plans for a field trip to OGI, logistics including an early morning departure and transportation arrangements.

**meeting-0378 s_to_l，R9**

参考：Using only the silence output from the neural network improves recognition accuracy to 89.1%.

被判完整蕴含的句子：The baseline system achieved 82% accuracy, while using a multi-English training set with PLP and delta features improved it to 89.1%.

0064的‘计划再次见面’不足以支持周四4点并讨论Grad A论文提案；0795的‘early morning’不支持6:00/7:20和谁驾车；0378将89.1%用于另一配置，不能支持‘仅silence输出’的精确结果。这些是现有文本可直接复核的宽松匹配，不需要新模型调用。

### 7.2 支持误判与分句偏差

0136 l_to_l主张‘One proposed chip is a Bluetooth chip for communication.’被判不支持；原文Industrial Designer明确说Bluetooth chip负责两个设备通信。此项至少是需要修正/复核的疑似漏判，不可把所有不支持标签都当成真实幻觉。相反，s_to_s的Marketing麦克风角色归属有原文反证。

1469 s_to_s：64个分句中有28个单独的Hon./Mr./Ms.片段；第一句还在Hon.处被截开。13/64=20.31%的Q混入分句碎片惩罚，不能直接当作真正的有效句比例。此次未替换分句器、重评或改分。

### 7.3 保持原分的排除敏感性

以下只是排除可疑样本后的重汇总，不是人工纠正分数，也不是挑选最有利子集。排除样本同时损失部分真实信息，应与完整30条并列阅读。

| 排除 | 来源 | n | 对比 | 覆盖均差pp |
| --- | --- | --- | --- | --- |
| meeting-0064 | ALL | 29 | s_to_s - direct_s | +15.93 |
| meeting-0064 | ALL | 29 | l_to_s - direct_s | +16.98 |
| meeting-0064 | ALL | 29 | l_to_l - direct_l | +11.26 |
| meeting-0064 | ALL | 29 | s_to_l - direct_l | +9.15 |
| meeting-0064 | QMSum-Academic | 5 | s_to_s - direct_s | +5.47 |
| meeting-0064 | QMSum-Academic | 5 | l_to_s - direct_s | +5.47 |
| meeting-0064 | QMSum-Academic | 5 | l_to_l - direct_l | -1.36 |
| meeting-0064 | QMSum-Academic | 5 | s_to_l - direct_l | +8.11 |
| meeting-0064,meeting-0378,meeting-0795 | ALL | 27 | s_to_s - direct_s | +17.37 |
| meeting-0064,meeting-0378,meeting-0795 | ALL | 27 | l_to_s - direct_s | +17.18 |
| meeting-0064,meeting-0378,meeting-0795 | ALL | 27 | l_to_l - direct_l | +13.24 |
| meeting-0064,meeting-0378,meeting-0795 | ALL | 27 | s_to_l - direct_l | +9.38 |
| meeting-0064,meeting-0378,meeting-0795 | QMSum-Academic | 3 | s_to_s - direct_s | +11.49 |
| meeting-0064,meeting-0378,meeting-0795 | QMSum-Academic | 3 | l_to_s - direct_s | -0.41 |
| meeting-0064,meeting-0378,meeting-0795 | QMSum-Academic | 3 | l_to_l - direct_l | +8.05 |
| meeting-0064,meeting-0378,meeting-0795 | QMSum-Academic | 3 | s_to_l - direct_l | +9.54 |

原评审下Academic small自身辅助−4.33pp，仅剔除0064后+5.47pp，说明该方向对单例异常敏感。其它排除组合见上表；不把剩余3条当成足以推广的Academic估计。

## 8. 对整体实验的准确解释

1. **能确认的流程事实**：pilot与全部成功缓存完整、对应当前输入；既有数值可复现；没有因缺项而形成不公平的均值。
2. **能确认的描述性结果**：按缓存口径辅助组覆盖平均更高，来源与样本异质性大，忠实性不总同步改善，large抽取收益未等比例传到纪要。
3. **人工能确认的内容事实**：至少三例参考匹配过宽松；有疑似支持漏判和实际角色错配；NLP分句会改变简洁率分母。因此分数精确不等于测量准确。
4. **尚不能确认的机制**：单次相同seed下的结果无法量化采样/服务运行方差；温度、重复惩罚、并发与模型规模不能凭此分离。没有把观察关联宣称为因果归因。
5. **尚不能确认的推广**：pilot含每来源最短/最长样本，不是简单随机样本；总体来源权重75/75/50/30/70而pilot等权。source_weight_sensitivity.csv只按来源比例重加权，不校正来源内有意选长度极端，不能当成300条真实成绩。
6. **尚不能确认的成本排名**：这是缓存token统计，不是同一运行窗口下的完整延迟、显存、实际成本测量。此次没有执行新评测或模型服务。

建议首先人工盲审上述匹配异常和Product状态/数值，统一完整蕴含标准并检查参考文本本身是否忠实；随后再考虑受控多seed、定长预算和更大测试集。当前不宜把Q/F的微小名义差值包装成确定排名，也不宜把gold视为没有错误的上界。

## 9. 文件索引与阅读路径

- [sample_analysis.md](sample_analysis.md)：30个样本逐一，全部八组三指标与分子/分母、增减参考事实及不支持主张。
- [source_analysis.md](source_analysis.md)：五来源八组均值/中位/范围、抽取分布、胜平负与极端样本。
- [sample_completeness.png](sample_completeness.png)：30×8完整性热图；[metric_distributions.png](metric_distributions.png)：三指标分布。
- [summary_metrics_recomputed.csv](summary_metrics_recomputed.csv)、[fact_metrics_recomputed.csv](fact_metrics_recomputed.csv)：逐样本完整可计算数值。
- [summary_distribution_by_source.csv](summary_distribution_by_source.csv)、[fact_distribution_by_source.csv](fact_distribution_by_source.csv)：宏/微、四分位、标准差、范围与总计。
- [paired_contrasts.csv](paired_contrasts.csv)：整体/来源16对比×3指标，含CI、胜平负、去掉任一样本后的均值范围；[per_sample_contrasts.csv](per_sample_contrasts.csv)：1440条个体差值。
- [reference_transitions.csv](reference_transitions.csv)、[summary_reference_alignment.csv](summary_reference_alignment.csv)、[fact_reference_alignment.csv](fact_reference_alignment.csv)：原文参考→事实→句子的逐项对齐。
- [judge_unsupported_claims.csv](judge_unsupported_claims.csv)：全部275个缓存不支持标签，不能不经复核当作真实错误。
- [sample_evidence.json](sample_evidence.json)：全部30样本参考、60列表、240纪要、分句、分解主张与匹配；[human_review_evidence.json](human_review_evidence.json)：明确的人工核对证据。
- [validation.json](validation.json)、[cache_validation.csv](cache_validation.csv)：重算、哈希和状态核验；[preserved_errors.json](preserved_errors.json)：历史错误摘要。
- [analyze.py](analyze.py)、[deliver.py](deliver.py)：复现脚本。输出使用排他创建，直接重跑到此目录会拒绝覆盖；应在新的独立目录运行。

