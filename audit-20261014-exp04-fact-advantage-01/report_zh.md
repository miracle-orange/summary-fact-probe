# 在large事实抽取占优的样本上比较八组纪要

## 核心结论

**在抽取指标large占优的条件下，更换large facts对small生成的参考覆盖帮助更明显；对large生成不是稳定的逐样本增益。同用large facts时，两生成模型的平均覆盖差很小，但不能据此证明能力等价。**

主16条固定small生成：l_to_s−s_to_s完整性+11.41pp，12胜1平3负；固定large生成：l_to_l−s_to_l仅+1.59pp，9胜1平6负。明显优势8条分别为+12.21pp（6胜2负）和+4.75pp（4胜4负）。

固定large facts时，主16条large生成只比small高0.62pp，明显优势8条反而低0.06pp；区间较宽，不能把近似均值解释为统计等价。原文直接生成的差距则为19.53/16.17pp，这些不同控制条件不应混合比较。

覆盖并非唯一质量：主16条更换large facts后small生成忠实性−1.15pp、简洁性+1.90pp；large生成忠实性+2.43pp、简洁性−8.04pp。不能将参考覆盖增加称作三项质量全面提升。

排除0378、0795两例已知纪要匹配异常后，剩余14条small/large生成更换facts的覆盖变化为+10.49/+4.88pp，固定large facts的生成模型差仅+0.37pp。主观察仍存在，但不是全部内容已经人工核实。

## 1. 分析问题与筛选口径

问题不是全部30条谁的纪要均值更高，而是：在同一会议上，large抽取比small更好时，换用large事实是否使small/large生成更好，以及这与直接生成、参考事实辅助的差距是什么。

**主分析16条**：large抽取参考覆盖率严格高于small，且原文支持率不低于small。此筛选只用抽取指标，不用任何纪要分数。

**明显优势8条**：在主条件上，再要求覆盖提高至少20个百分点。20pp是展示明显差异的分析阈值，不是原协议预注册规则，不作‘显著性’解释。

其他敏感性口径包括：覆盖/支持都严格提高（6条）、任一提高而另一不降的帕累托优势（19条）、仅要求覆盖提高（18条）以及排除既知评审异常后的主子集（14条）。

‘更好’在此明确指现有覆盖/支持口径占优，不是经过全部原文人工核验的绝对质量顺序。参考不穷尽所有重要信息，large可能仍遗漏small独有的重要事实；事实粒度、重复和提议/定案状态也未被这两个指标充分表达。

## 2. 哪些样本入选，哪些不能混入

| 样本 | 来源 | small覆盖→large覆盖 | 覆盖差pp | small支持→large支持 | 明显优势≥20pp | large为参考超集 |
| --- | --- | --- | --- | --- | --- | --- |
| meeting-0078 | MeetingBank | 10.53%→84.21% | +73.68 | 50.00%→92.31% | 是 | 是 |
| meeting-0290 | QMSum-Committee | 9.52%→42.86% | +33.33 | 100.00%→100.00% | 是 | 是 |
| meeting-0337 | MeetingBank | 64.71%→82.35% | +17.65 | 87.50%→100.00% | 否 | 是 |
| meeting-0378 | QMSum-Academic | 50.00%→64.29% | +14.29 | 100.00%→100.00% | 否 | 否 |
| meeting-0400 | QMSum-Committee | 31.82%→68.18% | +36.36 | 83.33%→100.00% | 是 | 否 |
| meeting-0475 | QMSum-Academic | 37.93%→44.83% | +6.90 | 100.00%→100.00% | 否 | 否 |
| meeting-0571 | ECTSum | 5.56%→100.00% | +94.44 | 100.00%→100.00% | 是 | 是 |
| meeting-0795 | QMSum-Academic | 33.33%→47.62% | +14.29 | 90.91%→100.00% | 否 | 否 |
| meeting-1020 | QMSum-Committee | 51.61%→61.29% | +9.68 | 100.00%→100.00% | 否 | 否 |
| meeting-1218 | QMSum-Product | 55.00%→65.00% | +10.00 | 75.00%→87.50% | 否 | 否 |
| meeting-1226 | ECTSum | 73.91%→100.00% | +26.09 | 100.00%→100.00% | 是 | 是 |
| meeting-1386 | QMSum-Committee | 64.71%→82.35% | +17.65 | 100.00%→100.00% | 否 | 否 |
| meeting-1557 | QMSum-Product | 40.91%→50.00% | +9.09 | 70.00%→100.00% | 否 | 否 |
| meeting-1696 | MeetingBank | 37.50%→81.25% | +43.75 | 100.00%→100.00% | 是 | 否 |
| meeting-1719 | MeetingBank | 33.33%→91.67% | +58.33 | 100.00%→100.00% | 是 | 是 |
| meeting-1776 | ECTSum | 9.38%→68.75% | +59.38 | 100.00%→100.00% | 是 | 是 |

0136（覆盖+14.29pp、支持−5.00pp）和0761（覆盖+61.54pp、支持−3.57pp）属于权衡，不能在不声明取舍时当作large双指标占优。0064、0160、0214、1726虽支持更高，但覆盖更低；0281、0621、1469覆盖相同而支持更高，计入19条帕累托口径而不计入覆盖严格提高的16条主分析。

0031、0174、0506、0550在上述双指标中small占优；0291指标持平，但覆盖事实身份不同，持平也不是内容完全相同。完整30条分类保存在all_sample_selection.csv。

## 3. 八组到底分别控制了什么

| 组 | 纪要生成模型 | 辅助事实 |
| --- | --- | --- |
| direct_s | small | 无（原文直接生成） |
| direct_l | large | 无（原文直接生成） |
| s_to_s | small | small抽取 |
| s_to_l | large | small抽取 |
| l_to_s | small | large抽取 |
| l_to_l | large | large抽取 |
| gold_to_s | small | 参考事实 |
| gold_to_l | large | 参考事实 |

**判断事实抽取优势是否传递，应先固定生成模型**：l_to_s−s_to_s与l_to_l−s_to_l。直接比较l_to_l−s_to_s同时改变了抽取和生成，不能单独归因于facts。

**判断生成模型利用同一事实的能力，应固定事实来源**：s_to_l−s_to_s、l_to_l−l_to_s、gold_to_l−gold_to_s。direct_l−direct_s是无外部事实时的模型差距。

**判断辅助是否值得使用，应固定生成模型并与direct比较**：s_to_s/l_to_s对direct_s，s_to_l/l_to_l对direct_l。gold用于考察参考信息输入后的剩余差距，不是无误差、免费或必达的上界。辅助组仍有完整原文。

## 4. 主分析：16条覆盖占优且支持不降

N=16；来源构成：ECTSum 3条，MeetingBank 4条，QMSum-Academic 3条，QMSum-Committee 4条，QMSum-Product 2条。

| 抽取模型 | 宏覆盖 | 宏支持 | 平均事实数 |
| --- | --- | --- | --- |
| small | 38.11% | 91.05% | 9.44 |
| large | 70.92% | 98.74% | 22.75 |

| 组 | 完整性C宏/微 | 简洁性Q宏 | 忠实性F宏/微 | 匹配参考/总参考 | 不支持主张/总主张 | 全支持纪要 | 平均输出tokens |
| --- | --- | --- | --- | --- | --- | --- | --- |
| direct_s | 28.00%/25.45% | 53.76% | 96.81%/96.76% | 85/334 | 11/339 | 10/16 | 184.6 |
| direct_l | 47.53%/44.91% | 69.49% | 97.41%/97.25% | 150/334 | 10/363 | 8/16 | 230.8 |
| s_to_s | 46.06%/44.31% | 66.62% | 96.91%/96.90% | 148/334 | 13/420 | 9/16 | 294.6 |
| s_to_l | 56.50%/53.29% | 76.10% | 95.27%/96.06% | 178/334 | 17/431 | 9/16 | 281.3 |
| l_to_s | 57.47%/55.09% | 68.52% | 95.76%/96.34% | 184/334 | 18/492 | 7/16 | 369.2 |
| l_to_l | 58.09%/56.59% | 68.06% | 97.70%/97.86% | 189/334 | 11/515 | 8/16 | 353.9 |
| gold_to_s | 71.57%/70.66% | 86.94% | 96.49%/97.09% | 236/334 | 13/447 | 11/16 | 313.0 |
| gold_to_l | 73.29%/71.86% | 79.99% | 97.13%/97.56% | 240/334 | 10/410 | 10/16 | 320.6 |

### 固定生成模型，更换facts

| 对比 | 指标 | 均差pp | 中位差pp | 95%区间pp | 胜/平/负 |
| --- | --- | --- | --- | --- | --- |
| l_to_s - s_to_s | completeness | +11.41 | +15.48 | [+4.66,+17.97] | 12/1/3 |
| l_to_s - s_to_s | conciseness | +1.90 | -5.40 | [-5.34,+10.02] | 6/0/10 |
| l_to_s - s_to_s | faithfulness | -1.15 | +0.00 | [-3.88,+1.52] | 6/4/6 |
| l_to_l - s_to_l | completeness | +1.59 | +4.55 | [-9.88,+12.71] | 9/1/6 |
| l_to_l - s_to_l | conciseness | -8.04 | -11.46 | [-12.74,-2.26] | 3/0/13 |
| l_to_l - s_to_l | faithfulness | +2.43 | +0.00 | [-0.53,+5.66] | 6/6/4 |

### 其它完整性对比

| 对比 | 平均差pp | 95%区间pp | 胜/平/负 |
| --- | --- | --- | --- |
| direct_l - direct_s | +19.53 | [+10.98,+28.21] | 12/2/2 |
| s_to_l - s_to_s | +10.45 | [+0.93,+21.09] | 12/0/4 |
| l_to_l - l_to_s | +0.62 | [-6.98,+7.31] | 9/1/6 |
| gold_to_l - gold_to_s | +1.72 | [-10.18,+11.95] | 9/0/7 |
| s_to_s - direct_s | +18.05 | [+7.89,+26.90] | 13/2/1 |
| l_to_s - direct_s | +29.47 | [+18.97,+38.68] | 15/0/1 |
| s_to_l - direct_l | +8.97 | [-2.16,+19.71] | 11/1/4 |
| l_to_l - direct_l | +10.56 | [-3.78,+24.05] | 9/2/5 |
| gold_to_s - direct_s | +43.57 | [+34.03,+53.36] | 15/1/0 |
| gold_to_l - direct_l | +25.76 | [+11.91,+38.62] | 13/2/1 |
| gold_to_s - l_to_s | +14.10 | [+6.17,+22.58] | 12/2/2 |
| gold_to_l - l_to_l | +15.20 | [+3.97,+25.72] | 9/3/4 |
| l_to_s - direct_l | +9.94 | [-2.61,+21.56] | 11/0/5 |
| s_to_l - direct_s | +28.50 | [+15.03,+41.88] | 14/0/2 |

### 来源内的facts更换收益

| 来源 | N | 对比 | C平均变化pp | 胜/平/负 |
| --- | --- | --- | --- | --- |
| ECTSum | 3 | l_to_s - s_to_s | +26.11 | 3/0/0 |
| ECTSum | 3 | l_to_l - s_to_l | +21.35 | 2/0/1 |
| MeetingBank | 4 | l_to_s - s_to_s | +9.47 | 3/0/1 |
| MeetingBank | 4 | l_to_l - s_to_l | +1.35 | 2/0/2 |
| QMSum-Academic | 3 | l_to_s - s_to_s | +11.90 | 2/1/0 |
| QMSum-Academic | 3 | l_to_l - s_to_l | -10.84 | 1/1/1 |
| QMSum-Committee | 4 | l_to_s - s_to_s | -0.51 | 2/0/2 |
| QMSum-Committee | 4 | l_to_l - s_to_l | -2.65 | 3/0/1 |
| QMSum-Product | 2 | l_to_s - s_to_s | +16.36 | 2/0/0 |
| QMSum-Product | 2 | l_to_l - s_to_l | -0.45 | 1/0/1 |
## 5. 明显优势：8条覆盖提高至少20pp

N=8；来源构成：ECTSum 3条，MeetingBank 3条，QMSum-Committee 2条。

| 抽取模型 | 宏覆盖 | 宏支持 | 平均事实数 |
| --- | --- | --- | --- |
| small | 26.44% | 91.67% | 5.75 |
| large | 79.61% | 99.04% | 25.62 |

| 组 | 完整性C宏/微 | 简洁性Q宏 | 忠实性F宏/微 | 匹配参考/总参考 | 不支持主张/总主张 | 全支持纪要 | 平均输出tokens |
| --- | --- | --- | --- | --- | --- | --- | --- |
| direct_s | 27.52%/24.54% | 60.89% | 96.02%/96.18% | 40/163 | 6/157 | 4/8 | 196.8 |
| direct_l | 43.69%/41.10% | 73.31% | 96.27%/96.26% | 67/163 | 7/187 | 3/8 | 238.6 |
| s_to_s | 47.32%/44.79% | 69.41% | 98.46%/98.54% | 73/163 | 3/205 | 6/8 | 283.0 |
| s_to_l | 54.72%/52.76% | 74.49% | 95.12%/96.30% | 86/163 | 8/216 | 4/8 | 311.0 |
| l_to_s | 59.53%/58.28% | 68.66% | 97.01%/97.75% | 95/163 | 6/267 | 4/8 | 444.2 |
| l_to_l | 59.47%/58.90% | 66.63% | 98.23%/98.57% | 96/163 | 4/280 | 5/8 | 439.8 |
| gold_to_s | 71.70%/71.17% | 84.43% | 97.13%/97.87% | 116/163 | 5/235 | 6/8 | 346.9 |
| gold_to_l | 65.93%/65.03% | 77.19% | 97.66%/98.10% | 106/163 | 4/211 | 6/8 | 334.5 |

### 固定生成模型，更换facts

| 对比 | 指标 | 均差pp | 中位差pp | 95%区间pp | 胜/平/负 |
| --- | --- | --- | --- | --- | --- |
| l_to_s - s_to_s | completeness | +12.21 | +17.71 | [+0.55,+22.23] | 6/0/2 |
| l_to_s - s_to_s | conciseness | -0.75 | -7.55 | [-8.98,+9.59] | 2/0/6 |
| l_to_s - s_to_s | faithfulness | -1.45 | +0.00 | [-4.53,+1.53] | 2/3/3 |
| l_to_l - s_to_l | completeness | +4.75 | +4.64 | [-15.17,+24.67] | 4/0/4 |
| l_to_l - s_to_l | conciseness | -7.86 | -12.06 | [-15.29,+1.92] | 1/0/7 |
| l_to_l - s_to_l | faithfulness | +3.12 | +0.00 | [-1.28,+8.67] | 3/3/2 |

### 其它完整性对比

| 对比 | 平均差pp | 95%区间pp | 胜/平/负 |
| --- | --- | --- | --- |
| direct_l - direct_s | +16.17 | [+2.73,+30.08] | 5/2/1 |
| s_to_l - s_to_s | +7.40 | [-5.58,+21.94] | 6/0/2 |
| l_to_l - l_to_s | -0.06 | [-14.24,+13.02] | 5/0/3 |
| gold_to_l - gold_to_s | -5.77 | [-23.15,+8.51] | 4/0/4 |
| s_to_s - direct_s | +19.80 | [+11.72,+27.95] | 7/1/0 |
| l_to_s - direct_s | +32.01 | [+23.02,+41.63] | 8/0/0 |
| s_to_l - direct_l | +11.03 | [-0.50,+20.22] | 6/1/1 |
| l_to_l - direct_l | +15.78 | [-6.76,+37.71] | 5/0/3 |
| gold_to_s - direct_s | +44.18 | [+35.44,+54.78] | 8/0/0 |
| gold_to_l - direct_l | +22.24 | [+0.16,+41.85] | 7/0/1 |
| gold_to_s - l_to_s | +12.17 | [+0.98,+22.77] | 7/0/1 |
| gold_to_l - l_to_l | +6.46 | [-7.76,+20.63] | 4/2/2 |
| l_to_s - direct_l | +15.84 | [-0.37,+30.35] | 6/0/2 |
| s_to_l - direct_s | +27.20 | [+13.00,+42.44] | 7/0/1 |

### 来源内的facts更换收益

| 来源 | N | 对比 | C平均变化pp | 胜/平/负 |
| --- | --- | --- | --- | --- |
| ECTSum | 3 | l_to_s - s_to_s | +26.11 | 3/0/0 |
| ECTSum | 3 | l_to_l - s_to_l | +21.35 | 2/0/1 |
| MeetingBank | 3 | l_to_s - s_to_s | +4.79 | 2/0/1 |
| MeetingBank | 3 | l_to_l - s_to_l | -2.12 | 1/0/2 |
| QMSum-Committee | 2 | l_to_s - s_to_s | +2.49 | 1/0/1 |
| QMSum-Committee | 2 | l_to_l - s_to_l | -9.85 | 1/0/1 |

## 6. 主子集每个样本的八组差异

C/Q/F均来自既有评审；分母分别为参考数、NLTK分句数、评审分解主张数。ID从1开始。新增/丢失指两次匹配标签之差，不是人工已确认的全部增减。

### meeting-0078 · MeetingBank

抽取覆盖10.53%→84.21%；支持50.00%→92.31%；事实2→13条。large独有匹配参考14条，small独有0条。

| 组 | 覆盖分子/分母 | C | 匹配句/总句 | Q | 支持主张/总主张 | F | 输出tokens |
| --- | --- | --- | --- | --- | --- | --- | --- |
| direct_s | 6/19 | 31.58% | 4/5 | 80.00% | 17/18 | 94.44% | 184 |
| direct_l | 14/19 | 73.68% | 8/9 | 88.89% | 20/21 | 95.24% | 234 |
| s_to_s | 14/19 | 73.68% | 5/7 | 71.43% | 20/20 | 100.00% | 247 |
| s_to_l | 9/19 | 47.37% | 6/7 | 85.71% | 18/19 | 94.74% | 224 |
| l_to_s | 10/19 | 52.63% | 7/8 | 87.50% | 21/22 | 95.45% | 299 |
| l_to_l | 7/19 | 36.84% | 5/7 | 71.43% | 23/24 | 95.83% | 259 |
| gold_to_s | 14/19 | 73.68% | 9/11 | 81.82% | 34/34 | 100.00% | 287 |
| gold_to_l | 6/19 | 31.58% | 4/5 | 80.00% | 22/22 | 100.00% | 191 |

**l_to_s − s_to_s**：C-21.05pp、Q+16.07pp、F-4.55pp；参考匹配新增1、丢失5。
- 新增 R4：Members of the public must pay a monetary deposit to appeal a decision, whereas City Council members are not subject to this financial requirement.
- 丢失 R8：Thomas Ellerby, a property owner, supported the referral, stating that a recent call for review on his St. Charles Street property caused financial cost and mental anguish.
- 丢失 R9：Janet Gibson opposed the referral, citing a historical example where the call for review process saved a Victorian home on Morton Street.
- 丢失 R15：Vice Mayor Vella supported the referral, stating that obtaining support from a second Council member is not an overly cumbersome requirement.
- 丢失 R16：Mayor Spencer opposed the referral, arguing that the Brown Act restricts Council members to speaking with only one other member outside of meetings.
- 丢失 R17：Mayor Spencer argued that the City Council is the elected body responsible for exercising due diligence on appointed board decisions.

**l_to_l − s_to_l**：C-10.53pp、Q-14.29pp、F+1.10pp；参考匹配新增1、丢失3。
- 新增 R9：Janet Gibson opposed the referral, citing a historical example where the call for review process saved a Victorian home on Morton Street.
- 丢失 R5：Council Member Ashcraft argued that requiring two Council members to initiate a review validates the necessity of the appeal.
- 丢失 R10：Gretchen Lipow opposed the referral, arguing that requiring two Council members to initiate a review restricts citizen access to the appeal process.
- 丢失 R13：Council Member Oddie supported the referral, arguing that Council members should have 'skin in the game' or consensus before initiating a review.

**内容核对**：direct_l、l_to_l、gold_to_l三份纪要都保留3–2最终投票。低分不能解释为辅助丢失投票；差异需按具体发言者/理由匹配复核。small事实有把拟议两议员规则当现行规则的风险。

### meeting-0290 · QMSum-Committee

抽取覆盖9.52%→42.86%；支持100.00%→100.00%；事实2→21条。large独有匹配参考7条，small独有0条。

| 组 | 覆盖分子/分母 | C | 匹配句/总句 | Q | 支持主张/总主张 | F | 输出tokens |
| --- | --- | --- | --- | --- | --- | --- | --- |
| direct_s | 1/21 | 4.76% | 1/4 | 25.00% | 17/17 | 100.00% | 158 |
| direct_l | 11/21 | 52.38% | 5/6 | 83.33% | 19/19 | 100.00% | 200 |
| s_to_s | 5/21 | 23.81% | 5/7 | 71.43% | 24/24 | 100.00% | 245 |
| s_to_l | 15/21 | 71.43% | 8/9 | 88.89% | 18/21 | 85.71% | 286 |
| l_to_s | 7/21 | 33.33% | 5/8 | 62.50% | 23/23 | 100.00% | 282 |
| l_to_l | 8/21 | 38.10% | 6/8 | 75.00% | 19/19 | 100.00% | 304 |
| gold_to_s | 8/21 | 38.10% | 5/7 | 71.43% | 18/21 | 85.71% | 252 |
| gold_to_l | 13/21 | 61.90% | 7/9 | 77.78% | 19/19 | 100.00% | 336 |

**l_to_s − s_to_s**：C+9.52pp、Q-8.93pp、F+0.00pp；参考匹配新增4、丢失2。
- 新增 R1：Alastair Birch represents the Association of Directors of Education Wales at the committee meeting.
- 新增 R2：Sally Jenkins represents the Association of Directors of Social Services at the committee meeting.
- 新增 R3：Councillor Huw David represents the Welsh Local Government Association at the committee meeting.
- 新增 R18：Councillor Huw David stated that there should be a duty on Welsh Government Ministers to raise awareness of the Bill.
- 丢失 R8：The reasonable punishment defence potentially permits an arbitrary level of violence that can lead to more serious physical or sexual abuse.
- 丢失 R17：The witnesses emphasized that the intention of the legislation is not to criminalise parents but to support them.

**l_to_l − s_to_l**：C-33.33pp、Q-13.89pp、F+14.29pp；参考匹配新增2、丢失9。
- 新增 R13：The Welsh Local Government Association believes the state's paramount role is to protect children from harm.
- 新增 R19：The exact costs of implementing the Children (Abolition of Defence of Reasonable Punishment) (Wales) Bill are currently difficult to quantify.
- 丢失 R1：Alastair Birch represents the Association of Directors of Education Wales at the committee meeting.
- 丢失 R2：Sally Jenkins represents the Association of Directors of Social Services at the committee meeting.
- 丢失 R3：Councillor Huw David represents the Welsh Local Government Association at the committee meeting.
- 丢失 R6：The United Nations has criticised current legislation for retaining the defence of reasonable punishment.
- 丢失 R7：Social services evidence suggests that physical punishment is emotionally damaging and harmful to children.
- 丢失 R8：The reasonable punishment defence potentially permits an arbitrary level of violence that can lead to more serious physical or sexual abuse.
- 丢失 R9：The Association of Directors of Social Services does not believe a specific definition of corporal punishment needs to be on the face of the Bill.
- 丢失 R14：Children's social services in Wales are currently experiencing high pressure and record numbers of contacts.
- 丢失 R15：The rise in looked-after children in Wales is attributed to multiple factors, including austerity and increased awareness of adverse childhood experiences.

### meeting-0337 · MeetingBank

抽取覆盖64.71%→82.35%；支持87.50%→100.00%；事实8→14条。large独有匹配参考3条，small独有0条。

| 组 | 覆盖分子/分母 | C | 匹配句/总句 | Q | 支持主张/总主张 | F | 输出tokens |
| --- | --- | --- | --- | --- | --- | --- | --- |
| direct_s | 5/17 | 29.41% | 4/4 | 100.00% | 13/13 | 100.00% | 134 |
| direct_l | 4/17 | 23.53% | 3/6 | 50.00% | 17/17 | 100.00% | 172 |
| s_to_s | 9/17 | 52.94% | 5/5 | 100.00% | 20/21 | 95.24% | 193 |
| s_to_l | 10/17 | 58.82% | 8/8 | 100.00% | 25/25 | 100.00% | 235 |
| l_to_s | 13/17 | 76.47% | 8/10 | 80.00% | 26/26 | 100.00% | 327 |
| l_to_l | 12/17 | 70.59% | 8/9 | 88.89% | 24/25 | 96.00% | 314 |
| gold_to_s | 13/17 | 76.47% | 9/9 | 100.00% | 26/26 | 100.00% | 298 |
| gold_to_l | 11/17 | 64.71% | 6/8 | 75.00% | 20/20 | 100.00% | 233 |

**l_to_s − s_to_s**：C+23.53pp、Q-20.00pp、F+4.76pp；参考匹配新增5、丢失1。
- 新增 R5：On-call contract tasks exceeding $100,000 generally require a minimum of three mini-bids.
- 新增 R6：The Platte to Park Hill project is being publicly procured separately from the on-call contracts due to its size exceeding on-call limits.
- 新增 R9：Contractors who supported preliminary engineering for the Platte to Park Hill project are generally precluded from pursuing the project's construction to prevent conflicts of interest.
- 新增 R11：Descriptions of active construction projects are available on the Denver government website under Public Works.
- 新增 R15：Councilwoman Ortega voted against Resolutions 1276 through 1289 because she requires detailed contract information upfront rather than in retrospective reports.
- 丢失 R12：The Washington Street widening design project exceeds the $500,000 threshold and will be procured as a separate hard-bid project.

**l_to_l − s_to_l**：C+11.76pp、Q-11.11pp、F-4.00pp；参考匹配新增3、丢失1。
- 新增 R9：Contractors who supported preliminary engineering for the Platte to Park Hill project are generally precluded from pursuing the project's construction to prevent conflicts of interest.
- 新增 R11：Descriptions of active construction projects are available on the Denver government website under Public Works.
- 新增 R13：Resolutions 1276 through 1289 represent 14 separate on-call contracts solicited under one Request for Qualifications (RFQ).
- 丢失 R12：The Washington Street widening design project exceeds the $500,000 threshold and will be procured as a separate hard-bid project.

### meeting-0378 · QMSum-Academic

抽取覆盖50.00%→64.29%；支持100.00%→100.00%；事实18→10条。large独有匹配参考5条，small独有3条。

| 组 | 覆盖分子/分母 | C | 匹配句/总句 | Q | 支持主张/总主张 | F | 输出tokens |
| --- | --- | --- | --- | --- | --- | --- | --- |
| direct_s | 0/14 | 0.00% | 0/6 | 0.00% | 23/23 | 100.00% | 183 |
| direct_l | 7/14 | 50.00% | 6/16 | 37.50% | 22/22 | 100.00% | 412 |
| s_to_s | 5/14 | 35.71% | 4/11 | 36.36% | 16/17 | 94.12% | 273 |
| s_to_l | 14/14 | 100.00% | 9/13 | 69.23% | 17/20 | 85.00% | 303 |
| l_to_s | 8/14 | 57.14% | 7/10 | 70.00% | 25/26 | 96.15% | 269 |
| l_to_l | 8/14 | 57.14% | 6/9 | 66.67% | 26/27 | 96.30% | 263 |
| gold_to_s | 7/14 | 50.00% | 5/9 | 55.56% | 19/19 | 100.00% | 240 |
| gold_to_l | 14/14 | 100.00% | 10/13 | 76.92% | 17/18 | 94.44% | 351 |

**l_to_s − s_to_s**：C+21.43pp、Q+33.64pp、F+2.04pp；参考匹配新增5、丢失2。
- 新增 R1：Using delta features with PLP features significantly improves performance compared to using PLP features without deltas.
- 新增 R2：Neural networks trained on the TIMIT database perform better on the Italian mismatched condition than networks trained on other languages.
- 新增 R5：MSG features perform significantly worse than PLP features on the Italian database.
- 新增 R7：Using a neural network improves recognition accuracy to approximately 90% even when features are not correctly normalized.
- 新增 R11：Multi-Layer Perceptrons trained on non-target tasks increase the error rate compared to straight features unless the features have poor normalization.
- 丢失 R10：Variances of feature streams in the HTK system can be scaled to effectively change the weight of the streams.
- 丢失 R13：Grad C is developing a multi-band belief-net structure with coupled Hidden Markov Models.

**l_to_l − s_to_l**：C-42.86pp、Q-2.56pp、F+11.30pp；参考匹配新增0、丢失6。
- 丢失 R2：Neural networks trained on the TIMIT database perform better on the Italian mismatched condition than networks trained on other languages.
- 丢失 R3：A neural network trained on a large database containing multiple languages and noise types performs better than a network trained only on French, Spanish, and English.
- 丢失 R4：MSG features perform as well as PLP features on the TI-digits task.
- 丢失 R9：Using only the silence output from the neural network improves recognition accuracy to 89.1%.
- 丢失 R10：Variances of feature streams in the HTK system can be scaled to effectively change the weight of the streams.
- 丢失 R11：Multi-Layer Perceptrons trained on non-target tasks increase the error rate compared to straight features unless the features have poor normalization.

**已知评审异常**：0378 s_to_l与0795 direct_l有过宽松的100%参考匹配；此样本对比不能直接当作人工质量结论。敏感性结果另列。

### meeting-0400 · QMSum-Committee

抽取覆盖31.82%→68.18%；支持83.33%→100.00%；事实18→19条。large独有匹配参考10条，small独有2条。

| 组 | 覆盖分子/分母 | C | 匹配句/总句 | Q | 支持主张/总主张 | F | 输出tokens |
| --- | --- | --- | --- | --- | --- | --- | --- |
| direct_s | 3/22 | 13.64% | 3/6 | 50.00% | 12/13 | 92.31% | 192 |
| direct_l | 3/22 | 13.64% | 3/5 | 60.00% | 15/15 | 100.00% | 196 |
| s_to_s | 7/22 | 31.82% | 5/8 | 62.50% | 23/25 | 92.00% | 288 |
| s_to_l | 8/22 | 36.36% | 7/11 | 63.64% | 26/27 | 96.30% | 346 |
| l_to_s | 6/22 | 27.27% | 5/10 | 50.00% | 25/26 | 96.15% | 336 |
| l_to_l | 11/22 | 50.00% | 8/14 | 57.14% | 30/32 | 93.75% | 467 |
| gold_to_s | 14/22 | 63.64% | 11/12 | 91.67% | 37/37 | 100.00% | 390 |
| gold_to_l | 4/22 | 18.18% | 3/6 | 50.00% | 24/24 | 100.00% | 258 |

**l_to_s − s_to_s**：C-4.55pp、Q-12.50pp、F+4.15pp；参考匹配新增2、丢失3。
- 新增 R9：Under a 'no deal' Brexit scenario, Welsh higher education institutions would likely lose access to approximately 50 per cent of current Horizon 2020 activity due to reverting to third-country status.
- 新增 R22：The Welsh Government has allocated £10 million to encourage further education colleges to respond to skills shortages identified by regional skills partnerships.
- 丢失 R5：Approximately £15 million per year is allocated to the Welsh further education sector specifically for apprenticeships.
- 丢失 R6：The Welsh Government's European transition team meets fortnightly to coordinate Brexit preparations across all government departments.
- 丢失 R13：The Welsh Government has agreed in principle to provide £3.5 million in funding to the Global Wales initiative to boost international student recruitment.

**l_to_l − s_to_l**：C+13.64pp、Q-6.49pp、F-2.55pp；参考匹配新增5、丢失2。
- 新增 R2：The UK Treasury has provided a letter guaranteeing funding for higher education activity until December 2020, even in a 'no deal' Brexit scenario.
- 新增 R13：The Welsh Government has agreed in principle to provide £3.5 million in funding to the Global Wales initiative to boost international student recruitment.
- 新增 R14：The Global Wales initiative specifically targets student recruitment markets in the United States of America and Vietnam.
- 新增 R15：The UK Home Office extended the post-study work visa pilot scheme to include Cardiff University and the University of Wales Trinity Saint David.
- 新增 R20：The Welsh Government has committed £5 million to the Higher Education Funding Council for Wales to support postgraduate studies.
- 丢失 R6：The Welsh Government's European transition team meets fortnightly to coordinate Brexit preparations across all government departments.
- 丢失 R22：The Welsh Government has allocated £10 million to encourage further education colleges to respond to skills shortages identified by regional skills partnerships.

### meeting-0475 · QMSum-Academic

抽取覆盖37.93%→44.83%；支持100.00%→100.00%；事实11→11条。large独有匹配参考4条，small独有2条。

| 组 | 覆盖分子/分母 | C | 匹配句/总句 | Q | 支持主张/总主张 | F | 输出tokens |
| --- | --- | --- | --- | --- | --- | --- | --- |
| direct_s | 1/29 | 3.45% | 1/4 | 25.00% | 19/19 | 100.00% | 164 |
| direct_l | 6/29 | 20.69% | 4/8 | 50.00% | 16/16 | 100.00% | 203 |
| s_to_s | 11/29 | 37.93% | 7/12 | 58.33% | 27/27 | 100.00% | 333 |
| s_to_l | 10/29 | 34.48% | 7/9 | 77.78% | 29/29 | 100.00% | 241 |
| l_to_s | 11/29 | 37.93% | 7/11 | 63.64% | 30/30 | 100.00% | 262 |
| l_to_l | 13/29 | 44.83% | 7/11 | 63.64% | 27/27 | 100.00% | 268 |
| gold_to_s | 25/29 | 86.21% | 12/12 | 100.00% | 28/28 | 100.00% | 400 |
| gold_to_l | 27/29 | 93.10% | 13/14 | 92.86% | 33/33 | 100.00% | 403 |

**l_to_s − s_to_s**：C+0.00pp、Q+5.30pp、F+0.00pp；参考匹配新增2、丢失2。
- 新增 R13：Grad A plans to conduct experiments using perfect knowledge of voicing to zero out non-voiced probabilities in LNA files.
- 新增 R15：Grad G fixed a Matlab bug in the phase normalization code, resulting in intelligible speech output.
- 丢失 R8：Using LDA filters derived from clean speech improved recognition rates on TI-digits from 82.7% to 85.1% compared to filters derived from noisy speech.
- 丢失 R27：PhD E estimates noise statistics using only the first ten frames of an utterance.

**l_to_l − s_to_l**：C+10.34pp、Q-14.14pp、F+0.00pp；参考匹配新增5、丢失2。
- 新增 R2：The Eurospeech conference will take place in Aalborg, Denmark, in September.
- 新增 R13：Grad A plans to conduct experiments using perfect knowledge of voicing to zero out non-voiced probabilities in LNA files.
- 新增 R15：Grad G fixed a Matlab bug in the phase normalization code, resulting in intelligible speech output.
- 新增 R16：Grad G found that phase normalization results were inferior to results obtained by subtracting log magnitude means.
- 新增 R23：PhD D plans to implement modified Wiener filtering using filters provided by Hynek that utilize adjacent frames.
- 丢失 R8：Using LDA filters derived from clean speech improved recognition rates on TI-digits from 82.7% to 85.1% compared to filters derived from noisy speech.
- 丢失 R11：Coefficient C0 performs better than log energy for mismatched testing conditions without noise compensation.

### meeting-0571 · ECTSum

抽取覆盖5.56%→100.00%；支持100.00%→100.00%；事实2→42条。large独有匹配参考17条，small独有0条。

| 组 | 覆盖分子/分母 | C | 匹配句/总句 | Q | 支持主张/总主张 | F | 输出tokens |
| --- | --- | --- | --- | --- | --- | --- | --- |
| direct_s | 6/18 | 33.33% | 6/8 | 75.00% | 23/23 | 100.00% | 259 |
| direct_l | 6/18 | 33.33% | 6/8 | 75.00% | 19/22 | 86.36% | 235 |
| s_to_s | 8/18 | 44.44% | 7/9 | 77.78% | 29/29 | 100.00% | 326 |
| s_to_l | 10/18 | 55.56% | 8/11 | 72.73% | 34/34 | 100.00% | 373 |
| l_to_s | 12/18 | 66.67% | 10/14 | 71.43% | 34/36 | 94.44% | 481 |
| l_to_l | 15/18 | 83.33% | 10/16 | 62.50% | 48/48 | 100.00% | 593 |
| gold_to_s | 14/18 | 77.78% | 6/8 | 75.00% | 27/27 | 100.00% | 381 |
| gold_to_l | 15/18 | 83.33% | 12/14 | 85.71% | 30/32 | 93.75% | 422 |

**l_to_s − s_to_s**：C+22.22pp、Q-6.35pp、F-5.56pp；参考匹配新增4、丢失0。
- 新增 R6：CTS Corporation's operating cash flow for the third quarter was $21 million, down from $26 million in the same period of 2020.
- 新增 R9：CTS Corporation's sales to transportation customers declined by 5% year-over-year in the third quarter.
- 新增 R10：CTS Corporation's sales to non-transportation markets increased 24% year-over-year in the third quarter.
- 新增 R16：CTS Corporation achieved $0.03 per share in savings from restructuring activities in the third quarter.

**l_to_l − s_to_l**：C+27.78pp、Q-10.23pp、F+0.00pp；参考匹配新增5、丢失0。
- 新增 R4：CTS Corporation reported a GAAP loss of $1.97 per share for the third quarter of 2021.
- 新增 R5：CTS Corporation recorded a noncash charge of $106 million before tax related to the U.S. pension plan termination.
- 新增 R6：CTS Corporation's operating cash flow for the third quarter was $21 million, down from $26 million in the same period of 2020.
- 新增 R15：CTS Corporation's long-term debt balance was $50 million at the end of the third quarter of 2021.
- 新增 R16：CTS Corporation achieved $0.03 per share in savings from restructuring activities in the third quarter.

### meeting-0795 · QMSum-Academic

抽取覆盖33.33%→47.62%；支持90.91%→100.00%；事实11→15条。large独有匹配参考5条，small独有2条。

| 组 | 覆盖分子/分母 | C | 匹配句/总句 | Q | 支持主张/总主张 | F | 输出tokens |
| --- | --- | --- | --- | --- | --- | --- | --- |
| direct_s | 18/21 | 85.71% | 5/6 | 83.33% | 24/27 | 88.89% | 192 |
| direct_l | 21/21 | 100.00% | 5/5 | 100.00% | 16/16 | 100.00% | 154 |
| s_to_s | 9/21 | 42.86% | 6/11 | 54.55% | 28/28 | 100.00% | 313 |
| s_to_l | 13/21 | 61.90% | 5/7 | 71.43% | 28/28 | 100.00% | 201 |
| l_to_s | 12/21 | 57.14% | 6/12 | 50.00% | 24/27 | 88.89% | 308 |
| l_to_l | 13/21 | 61.90% | 5/9 | 55.56% | 26/26 | 100.00% | 222 |
| gold_to_s | 18/21 | 85.71% | 10/10 | 100.00% | 40/40 | 100.00% | 324 |
| gold_to_l | 21/21 | 100.00% | 9/10 | 90.00% | 30/30 | 100.00% | 317 |

**l_to_s − s_to_s**：C+14.29pp、Q-4.55pp、F-11.11pp；参考匹配新增4、丢失1。
- 新增 R2：Professor F will drive the students to the airport at 6:00 AM to catch a 7:20 AM flight to OGI.
- 新增 R11：Grad C intends to compare a neural network trained on TIMIT data against a network trained on digits alone.
- 新增 R16：The group plans to utilize SPERT boards and multiple workstations to handle the computational load of the experiments.
- 新增 R17：The institute's 10-megabit network speed is a bottleneck for moving data between the central file server and computational machines.
- 丢失 R18：The group is acquiring four additional 36-gigabyte drives to increase disk space on the central file server.

**l_to_l − s_to_l**：C+0.00pp、Q-15.87pp、F+0.00pp；参考匹配新增3、丢失3。
- 新增 R11：Grad C intends to compare a neural network trained on TIMIT data against a network trained on digits alone.
- 新增 R15：The group discusses the computational time required, noting that HTK training takes about six hours and neural network training takes one to two days.
- 新增 R16：The group plans to utilize SPERT boards and multiple workstations to handle the computational load of the experiments.
- 丢失 R3：PhD G is preparing a French digit database of microphone speech downsampled to eight kilohertz.
- 丢失 R4：PhD G has added Aurora-2 noises to the training portion of the French database.
- 丢失 R12：PhD E is working on the Italian database and preparing the HTK baseline.

**已知评审异常**：0378 s_to_l与0795 direct_l有过宽松的100%参考匹配；此样本对比不能直接当作人工质量结论。敏感性结果另列。

### meeting-1020 · QMSum-Committee

抽取覆盖51.61%→61.29%；支持100.00%→100.00%；事实25→53条。large独有匹配参考4条，small独有1条。

| 组 | 覆盖分子/分母 | C | 匹配句/总句 | Q | 支持主张/总主张 | F | 输出tokens |
| --- | --- | --- | --- | --- | --- | --- | --- |
| direct_s | 0/31 | 0.00% | 0/4 | 0.00% | 28/28 | 100.00% | 203 |
| direct_l | 7/31 | 22.58% | 3/5 | 60.00% | 29/30 | 96.67% | 192 |
| s_to_s | 12/31 | 38.71% | 9/23 | 39.13% | 36/38 | 94.74% | 613 |
| s_to_l | 11/31 | 35.48% | 5/7 | 71.43% | 24/24 | 100.00% | 303 |
| l_to_s | 8/31 | 25.81% | 3/9 | 33.33% | 31/31 | 100.00% | 322 |
| l_to_l | 12/31 | 38.71% | 5/9 | 55.56% | 30/30 | 100.00% | 260 |
| gold_to_s | 8/31 | 25.81% | 3/5 | 60.00% | 20/22 | 90.91% | 177 |
| gold_to_l | 11/31 | 35.48% | 4/6 | 66.67% | 25/25 | 100.00% | 196 |

**l_to_s − s_to_s**：C-12.90pp、Q-5.80pp、F+5.26pp；参考匹配新增2、丢失6。
- 新增 R4：Mr. Garnett Genuis presented a petition supporting Bill S-204, which would criminalize forced organ harvesting and trafficking abroad.
- 新增 R17：Hon. Anita Anand stated that the Government of Canada will not pay for N95 masks that are unusable.
- 丢失 R7：Prime Minister Justin Trudeau announced legislation to provide a one-time payment to Canadians with disabilities.
- 丢失 R8：Prime Minister Justin Trudeau proposed legislation to increase the flexibility of the Canada Emergency Response Benefit and expand the wage subsidy.
- 丢失 R15：Hon. Mlanie Joly confirmed that the wage subsidy has been extended until the end of August.
- 丢失 R20：Hon. Patty Hajdu stated that Health Canada can approve antibody tests in as little as five to seven days.
- 丢失 R21：Hon. Bill Blair confirmed that the Canadian Armed Forces will continue to provide support in Quebec long-term care homes until mid-September.
- 丢失 R30：Mr. Randall Garrison called on the government to lift the ban on blood donations from gay men.

**l_to_l − s_to_l**：C+3.23pp、Q-15.87pp、F+0.00pp；参考匹配新增5、丢失4。
- 新增 R4：Mr. Garnett Genuis presented a petition supporting Bill S-204, which would criminalize forced organ harvesting and trafficking abroad.
- 新增 R9：Hon. Andrew Scheer stated that the interim Auditor General expects to complete 14 performance audits annually, down from 27, due to resource constraints.
- 新增 R15：Hon. Mlanie Joly confirmed that the wage subsidy has been extended until the end of August.
- 新增 R20：Hon. Patty Hajdu stated that Health Canada can approve antibody tests in as little as five to seven days.
- 新增 R31：Hon. Marco Mendicino stated that the government has introduced hundreds of millions of dollars in support for farmers.
- 丢失 R7：Prime Minister Justin Trudeau announced legislation to provide a one-time payment to Canadians with disabilities.
- 丢失 R8：Prime Minister Justin Trudeau proposed legislation to increase the flexibility of the Canada Emergency Response Benefit and expand the wage subsidy.
- 丢失 R21：Hon. Bill Blair confirmed that the Canadian Armed Forces will continue to provide support in Quebec long-term care homes until mid-September.
- 丢失 R30：Mr. Randall Garrison called on the government to lift the ban on blood donations from gay men.

### meeting-1218 · QMSum-Product

抽取覆盖55.00%→65.00%；支持75.00%→87.50%；事实12→16条。large独有匹配参考3条，small独有1条。

| 组 | 覆盖分子/分母 | C | 匹配句/总句 | Q | 支持主张/总主张 | F | 输出tokens |
| --- | --- | --- | --- | --- | --- | --- | --- |
| direct_s | 4/20 | 20.00% | 2/6 | 33.33% | 23/25 | 92.00% | 159 |
| direct_l | 12/20 | 60.00% | 7/9 | 77.78% | 24/25 | 96.00% | 238 |
| s_to_s | 11/20 | 55.00% | 7/9 | 77.78% | 28/32 | 87.50% | 253 |
| s_to_l | 14/20 | 70.00% | 9/11 | 81.82% | 33/33 | 100.00% | 268 |
| l_to_s | 13/20 | 65.00% | 7/10 | 70.00% | 26/28 | 92.86% | 265 |
| l_to_l | 12/20 | 60.00% | 7/10 | 70.00% | 34/36 | 94.44% | 271 |
| gold_to_s | 16/20 | 80.00% | 8/8 | 100.00% | 20/23 | 86.96% | 200 |
| gold_to_l | 19/20 | 95.00% | 11/12 | 91.67% | 26/27 | 96.30% | 295 |

**l_to_s − s_to_s**：C+10.00pp、Q-7.78pp、F+5.36pp；参考匹配新增3、丢失1。
- 新增 R2：The remote control prototype is named 'Ninja Homer'.
- 新增 R4：The team removed the kinetic power feature due to cost constraints.
- 新增 R7：The remote control features a red power button.
- 丢失 R3：The remote control is powered by a battery.

**l_to_l − s_to_l**：C-10.00pp、Q-11.82pp、F-5.56pp；参考匹配新增1、丢失3。
- 新增 R20：The team found the digital pens to be clunky but intuitive.
- 丢失 R3：The remote control is powered by a battery.
- 丢失 R4：The team removed the kinetic power feature due to cost constraints.
- 丢失 R11：The team opted for standard colored buttons instead of special colors to reduce costs.

### meeting-1226 · ECTSum

抽取覆盖73.91%→100.00%；支持100.00%→100.00%；事实16→40条。large独有匹配参考6条，small独有0条。

| 组 | 覆盖分子/分母 | C | 匹配句/总句 | Q | 支持主张/总主张 | F | 输出tokens |
| --- | --- | --- | --- | --- | --- | --- | --- |
| direct_s | 8/23 | 34.78% | 6/6 | 100.00% | 22/22 | 100.00% | 195 |
| direct_l | 14/23 | 60.87% | 9/10 | 90.00% | 28/28 | 100.00% | 290 |
| s_to_s | 15/23 | 65.22% | 9/10 | 90.00% | 30/30 | 100.00% | 402 |
| s_to_l | 17/23 | 73.91% | 10/10 | 100.00% | 31/31 | 100.00% | 367 |
| l_to_s | 20/23 | 86.96% | 13/16 | 81.25% | 50/50 | 100.00% | 693 |
| l_to_l | 16/23 | 69.57% | 9/11 | 81.82% | 35/35 | 100.00% | 397 |
| gold_to_s | 15/23 | 65.22% | 10/11 | 90.91% | 34/34 | 100.00% | 373 |
| gold_to_l | 18/23 | 78.26% | 12/14 | 85.71% | 39/39 | 100.00% | 473 |

**l_to_s − s_to_s**：C+21.74pp、Q-8.75pp、F+0.00pp；参考匹配新增5、丢失0。
- 新增 R5：The government healthcare consulting business is experiencing mid-single-digit growth.
- 新增 R6：The Benefits and Insurance group maintained client retention rates of over 90%.
- 新增 R11：Third-quarter same unit revenue grew by 8.3% compared to the previous year.
- 新增 R16：Third-quarter margin on income before tax declined to 10.3% due to the normalization of discretionary expenses like marketing and travel.
- 新增 R18：The company utilized approximately $85 million to repurchase 2.7 million shares through September 30.

**l_to_l − s_to_l**：C-4.35pp、Q-18.18pp、F+0.00pp；参考匹配新增2、丢失3。
- 新增 R11：Third-quarter same unit revenue grew by 8.3% compared to the previous year.
- 新增 R14：Newly acquired operations contributed 10.3% to total revenue growth in the third quarter.
- 丢失 R16：Third-quarter margin on income before tax declined to 10.3% due to the normalization of discretionary expenses like marketing and travel.
- 丢失 R19：Debt outstanding on the unsecured $400 million credit line was $190.2 million at September 30.
- 丢失 R20：Adjusted EBITDA for the first nine months was $153.5 million, up 21% from the previous year.

### meeting-1386 · QMSum-Committee

抽取覆盖64.71%→82.35%；支持100.00%→100.00%；事实10→20条。large独有匹配参考4条，small独有1条。

| 组 | 覆盖分子/分母 | C | 匹配句/总句 | Q | 支持主张/总主张 | F | 输出tokens |
| --- | --- | --- | --- | --- | --- | --- | --- |
| direct_s | 9/17 | 52.94% | 3/5 | 60.00% | 20/20 | 100.00% | 169 |
| direct_l | 12/17 | 70.59% | 6/9 | 66.67% | 22/23 | 95.65% | 245 |
| s_to_s | 10/17 | 58.82% | 7/9 | 77.78% | 29/29 | 100.00% | 315 |
| s_to_l | 11/17 | 64.71% | 7/8 | 87.50% | 27/29 | 93.10% | 247 |
| l_to_s | 11/17 | 64.71% | 9/10 | 90.00% | 29/30 | 96.67% | 354 |
| l_to_l | 12/17 | 70.59% | 8/9 | 88.89% | 32/33 | 96.97% | 328 |
| gold_to_s | 13/17 | 76.47% | 9/9 | 100.00% | 27/27 | 100.00% | 317 |
| gold_to_l | 12/17 | 70.59% | 9/13 | 69.23% | 25/27 | 92.59% | 400 |

**l_to_s − s_to_s**：C+5.88pp、Q+12.22pp、F-3.33pp；参考匹配新增4、丢失3。
- 新增 R2：Qualifications Wales conducted a review into the Welsh Baccalaureate that highlighted both positive learner experiences and concerns regarding workload and well-being.
- 新增 R3：The Welsh Baccalaureate became a graded qualification in 2015 to increase rigour.
- 新增 R6：The Welsh Baccalaureate will become a dedicated performance measure for schools starting the following year.
- 新增 R10：Universities use the Welsh Baccalaureate in various ways, including as an A-level equivalent, for lowering grade offers, or as part of personal statements.
- 丢失 R5：A design group within Qualifications Wales is addressing issues regarding teacher workload and assessment onerousness related to the Welsh Baccalaureate.
- 丢失 R8：The Welsh Government is working with Qualifications Wales to develop a joint communication plan to improve employer understanding of the Welsh Baccalaureate.
- 丢失 R9：Kirsty Williams AM asserts that Russell Group universities, including Oxford and Cambridge, value the Welsh Baccalaureate qualification.

**l_to_l − s_to_l**：C+5.88pp、Q+1.39pp、F+3.87pp；参考匹配新增4、丢失3。
- 新增 R3：The Welsh Baccalaureate became a graded qualification in 2015 to increase rigour.
- 新增 R6：The Welsh Baccalaureate will become a dedicated performance measure for schools starting the following year.
- 新增 R9：Kirsty Williams AM asserts that Russell Group universities, including Oxford and Cambridge, value the Welsh Baccalaureate qualification.
- 新增 R11：Universities Wales rejected the Children, Young People and Education Committee's invitation to submit oral or written evidence regarding the Welsh Baccalaureate.
- 丢失 R8：The Welsh Government is working with Qualifications Wales to develop a joint communication plan to improve employer understanding of the Welsh Baccalaureate.
- 丢失 R10：Universities use the Welsh Baccalaureate in various ways, including as an A-level equivalent, for lowering grade offers, or as part of personal statements.
- 丢失 R15：New Initial Teacher Education (ITE) accreditation criteria require teachers to possess the pedagogical skills necessary to deliver the Welsh Baccalaureate.

### meeting-1557 · QMSum-Product

抽取覆盖40.91%→50.00%；支持70.00%→100.00%；事实10→20条。large独有匹配参考3条，small独有1条。

| 组 | 覆盖分子/分母 | C | 匹配句/总句 | Q | 支持主张/总主张 | F | 输出tokens |
| --- | --- | --- | --- | --- | --- | --- | --- |
| direct_s | 8/22 | 36.36% | 5/7 | 71.43% | 27/27 | 100.00% | 175 |
| direct_l | 14/22 | 63.64% | 5/6 | 83.33% | 27/27 | 100.00% | 167 |
| s_to_s | 8/22 | 36.36% | 4/6 | 66.67% | 21/23 | 91.30% | 156 |
| s_to_l | 9/22 | 40.91% | 5/8 | 62.50% | 23/27 | 85.19% | 215 |
| l_to_s | 13/22 | 59.09% | 9/10 | 90.00% | 22/27 | 81.48% | 246 |
| l_to_l | 11/22 | 50.00% | 6/9 | 66.67% | 29/31 | 93.55% | 218 |
| gold_to_s | 20/22 | 90.91% | 11/11 | 100.00% | 24/27 | 88.89% | 277 |
| gold_to_l | 19/22 | 86.36% | 10/10 | 100.00% | 17/19 | 89.47% | 259 |

**l_to_s − s_to_s**：C+22.73pp、Q+23.33pp、F-9.82pp；参考匹配新增6、丢失1。
- 新增 R2：The team decides to use normal batteries instead of kinetic energy or a hand dynamo.
- 新增 R4：The team removes the number buttons one through nine to save 4.50 Euros.
- 新增 R10：The team decides to apply a special color to the plastic casing.
- 新增 R13：The team rates the remote's match to young user behavior as a 3 out of 7.
- 新增 R18：The team names the product 'The Real Remote'.
- 新增 R22：Marketing considers the digital pen more effective for their work than the Smartboard screen.
- 丢失 R12：The final design consists of a single-curved plastic case with one integrated scroll-wheel button and an LCD screen.

**l_to_l − s_to_l**：C+9.09pp、Q+4.17pp、F+8.36pp；参考匹配新增2、丢失0。
- 新增 R2：The team decides to use normal batteries instead of kinetic energy or a hand dynamo.
- 新增 R12：The final design consists of a single-curved plastic case with one integrated scroll-wheel button and an LCD screen.

### meeting-1696 · MeetingBank

抽取覆盖37.50%→81.25%；支持100.00%→100.00%；事实2→10条。large独有匹配参考8条，small独有1条。

| 组 | 覆盖分子/分母 | C | 匹配句/总句 | Q | 支持主张/总主张 | F | 输出tokens |
| --- | --- | --- | --- | --- | --- | --- | --- |
| direct_s | 5/16 | 31.25% | 4/7 | 57.14% | 19/21 | 90.48% | 236 |
| direct_l | 8/16 | 50.00% | 6/8 | 75.00% | 24/25 | 96.00% | 229 |
| s_to_s | 9/16 | 56.25% | 6/8 | 75.00% | 22/23 | 95.65% | 243 |
| s_to_l | 12/16 | 75.00% | 7/9 | 77.78% | 28/28 | 100.00% | 303 |
| l_to_s | 12/16 | 75.00% | 7/10 | 70.00% | 27/27 | 100.00% | 368 |
| l_to_l | 6/16 | 37.50% | 4/7 | 57.14% | 26/27 | 96.30% | 258 |
| gold_to_s | 14/16 | 87.50% | 8/8 | 100.00% | 26/26 | 100.00% | 343 |
| gold_to_l | 13/16 | 81.25% | 6/8 | 75.00% | 23/23 | 100.00% | 302 |

**l_to_s − s_to_s**：C+18.75pp、Q-5.00pp、F+4.35pp；参考匹配新增5、丢失2。
- 新增 R6：The tiny home village currently operates under a six-month temporary unlisted use permit.
- 新增 R9：Urban Land Conservancy is partnering with McWhinney to develop 325 market-rate apartments on the Blake Street side of the site.
- 新增 R11：The Beloved Community Village features 11 tiny homes and currently houses 16 residents.
- 新增 R13：The Beloved Community Village reported zero police calls during its first 180 days of operation.
- 新增 R14：The Denver Community Planning and Development department is in the early stages of a project to review zoning regulations for group living.
- 丢失 R2：The property at 1420 38th Street is currently zoned RMU-30 with waivers under Former Chapter 59.
- 丢失 R16：Council Bill 1421 passed with 11 votes in favor and 0 against.

**l_to_l − s_to_l**：C-37.50pp、Q-20.63pp、F-3.70pp；参考匹配新增1、丢失7。
- 新增 R15：City Council members expressed concern regarding the non-renewable nature of the six-month temporary use permit for tiny homes.
- 丢失 R2：The property at 1420 38th Street is currently zoned RMU-30 with waivers under Former Chapter 59.
- 丢失 R3：The proposed zoning for the 1420 38th Street property is C-MX-8 (Urban Center Neighborhood Context Mixed Use).
- 丢失 R4：The subject property is located directly across from the 38th and Blake RTD Station.
- 丢失 R6：The tiny home village currently operates under a six-month temporary unlisted use permit.
- 丢失 R10：Urban Land Conservancy is partnering with Medici Development Corporation to develop 65 units of affordable housing at the 38th and Walnut site.
- 丢失 R11：The Beloved Community Village features 11 tiny homes and currently houses 16 residents.
- 丢失 R14：The Denver Community Planning and Development department is in the early stages of a project to review zoning regulations for group living.

### meeting-1719 · MeetingBank

抽取覆盖33.33%→91.67%；支持100.00%→100.00%；事实2→16条。large独有匹配参考7条，small独有0条。

| 组 | 覆盖分子/分母 | C | 匹配句/总句 | Q | 支持主张/总主张 | F | 输出tokens |
| --- | --- | --- | --- | --- | --- | --- | --- |
| direct_s | 7/12 | 58.33% | 4/5 | 80.00% | 20/22 | 90.91% | 185 |
| direct_l | 6/12 | 50.00% | 5/7 | 71.43% | 21/22 | 95.45% | 233 |
| s_to_s | 7/12 | 58.33% | 4/7 | 57.14% | 21/21 | 100.00% | 216 |
| s_to_l | 6/12 | 50.00% | 4/7 | 57.14% | 16/19 | 84.21% | 227 |
| l_to_s | 9/12 | 75.00% | 6/7 | 85.71% | 18/20 | 90.00% | 284 |
| l_to_l | 11/12 | 91.67% | 8/10 | 80.00% | 26/26 | 100.00% | 308 |
| gold_to_s | 10/12 | 83.33% | 8/10 | 80.00% | 21/23 | 91.30% | 302 |
| gold_to_l | 11/12 | 91.67% | 5/6 | 83.33% | 14/16 | 87.50% | 287 |

**l_to_s − s_to_s**：C+16.67pp、Q+28.57pp、F-10.00pp；参考匹配新增3、丢失1。
- 新增 R5：Public speaker Doug Biggs stated that delaying the McKay Avenue project beyond two years will incur financial penalties according to the lease.
- 新增 R10：Councilmember Daysog voted against placing the Carrying Alameda Act on the April ballot because he prefers a November 2020 election.
- 新增 R11：A subcommittee consisting of the Vice Mayor and Councilmember Oddie was formed to draft the ballot question and arguments for the Carrying Alameda Act.
- 丢失 R7：The City Council decided not to place the McKay Avenue Open Space Fiscal Responsibility Measure on the ballot.

**l_to_l − s_to_l**：C+41.67pp、Q+22.86pp、F+15.79pp；参考匹配新增5、丢失0。
- 新增 R4：The McKay Avenue Open Space Fiscal Responsibility Measure would compel the City Attorney to file a lawsuit to determine if acquiring the property constitutes a taking and to identify a funding source prior to implementation.
- 新增 R5：Public speaker Doug Biggs stated that delaying the McKay Avenue project beyond two years will incur financial penalties according to the lease.
- 新增 R7：The City Council decided not to place the McKay Avenue Open Space Fiscal Responsibility Measure on the ballot.
- 新增 R8：The City Council intends to direct the City Attorney to file a court action regarding the property value if the citizens' initiative passes, rather than using a ballot measure to mandate this action.
- 新增 R10：Councilmember Daysog voted against placing the Carrying Alameda Act on the April ballot because he prefers a November 2020 election.

**关键例外**：large整体覆盖高，但small两条保留最终4–1投票，large列表遗漏；‘large整体更好’不等于small信息是large的严格子集。

### meeting-1776 · ECTSum

抽取覆盖9.38%→68.75%；支持100.00%→100.00%；事实2→44条。large独有匹配参考19条，small独有0条。

| 组 | 覆盖分子/分母 | C | 匹配句/总句 | Q | 支持主张/总主张 | F | 输出tokens |
| --- | --- | --- | --- | --- | --- | --- | --- |
| direct_s | 4/32 | 12.50% | 1/5 | 20.00% | 21/21 | 100.00% | 165 |
| direct_l | 5/32 | 15.62% | 3/7 | 42.86% | 34/35 | 97.14% | 292 |
| s_to_s | 8/32 | 25.00% | 5/10 | 50.00% | 33/33 | 100.00% | 297 |
| s_to_l | 9/32 | 28.12% | 5/10 | 50.00% | 37/37 | 100.00% | 362 |
| l_to_s | 19/32 | 59.38% | 9/22 | 40.91% | 63/63 | 100.00% | 811 |
| l_to_l | 22/32 | 68.75% | 12/25 | 48.00% | 69/69 | 100.00% | 932 |
| gold_to_s | 27/32 | 84.38% | 11/13 | 84.62% | 33/33 | 100.00% | 447 |
| gold_to_l | 26/32 | 81.25% | 8/10 | 80.00% | 36/36 | 100.00% | 407 |

**l_to_s − s_to_s**：C+34.38pp、Q-9.09pp、F+0.00pp；参考匹配新增13、丢失2。
- 新增 R4：NOV's EBITDA fell to breakeven levels in the first quarter of 2021.
- 新增 R10：NOV has reduced costs by $12.6 billion since 2014.
- 新增 R13：NOV ended the first quarter of 2021 with $1.61 billion in cash.
- 新增 R14：NOV ended the first quarter of 2021 with $1.85 billion in gross debt.
- 新增 R15：NOV fully redeemed the remaining $183 million of senior notes due in December 2022 following the end of the first quarter of 2021.
- 新增 R19：Seven out of eight Wellbore Technologies business units posted sequential growth in the first quarter of 2021.
- 新增 R20：NOV expects Wellbore Technologies revenue to grow 8% to 10% sequentially in the second quarter of 2021.
- 新增 R24：The Completion & Production Solutions segment achieved a book-to-bill ratio of 127% in the first quarter of 2021.
- 新增 R25：NOV expects Completion & Production Solutions revenue to improve between 15% to 25% sequentially in the second quarter of 2021.
- 新增 R26：The Rig Technologies segment generated revenues of $431 million in the first quarter of 2021.
- 新增 R29：The Rig Technologies segment had a book-to-bill ratio of 59% in the first quarter of 2021.
- 新增 R31：NOV is pursuing over $400 million in potential offshore wind projects.
- 新增 R32：NOV booked an order for the design and jacking systems for a European wind turbine installation vessel during the first quarter of 2021.
- 丢失 R17：Wellbore Technologies revenue increased 11% sequentially in the first quarter of 2021.
- 丢失 R22：Completion & Production Solutions revenue decreased 20% sequentially in the first quarter of 2021.

**l_to_l − s_to_l**：C+40.62pp、Q-2.00pp、F+0.00pp；参考匹配新增16、丢失3。
- 新增 R4：NOV's EBITDA fell to breakeven levels in the first quarter of 2021.
- 新增 R7：NOV experienced higher costs due to execution issues on a new pipe design project.
- 新增 R9：NOV's annualized revenue run rate in the first quarter of 2021 was down 45% compared to five quarters prior.
- 新增 R10：NOV has reduced costs by $12.6 billion since 2014.
- 新增 R13：NOV ended the first quarter of 2021 with $1.61 billion in cash.
- 新增 R14：NOV ended the first quarter of 2021 with $1.85 billion in gross debt.
- 新增 R15：NOV fully redeemed the remaining $183 million of senior notes due in December 2022 following the end of the first quarter of 2021.
- 新增 R19：Seven out of eight Wellbore Technologies business units posted sequential growth in the first quarter of 2021.
- 新增 R20：NOV expects Wellbore Technologies revenue to grow 8% to 10% sequentially in the second quarter of 2021.
- 新增 R25：NOV expects Completion & Production Solutions revenue to improve between 15% to 25% sequentially in the second quarter of 2021.
- 新增 R26：The Rig Technologies segment generated revenues of $431 million in the first quarter of 2021.
- 新增 R27：Rig Technologies revenue decreased 1% sequentially in the first quarter of 2021.
- 新增 R29：The Rig Technologies segment had a book-to-bill ratio of 59% in the first quarter of 2021.
- 新增 R30：NOV began manufacturing the first two rigs from its new plant in Saudi Arabia during the first quarter of 2021.
- 新增 R31：NOV is pursuing over $400 million in potential offshore wind projects.
- 新增 R32：NOV booked an order for the design and jacking systems for a European wind turbine installation vessel during the first quarter of 2021.
- 丢失 R11：NOV realized $52 million in annualized cost savings during the first quarter of 2021.
- 丢失 R12：NOV expects to achieve total cost savings of $106 million in 2021.
- 丢失 R17：Wellbore Technologies revenue increased 11% sequentially in the first quarter of 2021.

## 7. 筛选口径敏感性与交互

以下对比保持同一子集内配对；不同子集改变来源/样本组成，不能把子集之间均值差当成抽取质量的因果效应。

| 子集 | N | l_to_s−s_to_s C/Q/F pp | l_to_l−s_to_l C/Q/F pp |
| --- | --- | --- | --- |
| primary_coverage_up_support_not_down | 16 | +11.41 / +1.90 / -1.15 | +1.59 / -8.04 / +2.43 |
| strong_coverage_20pp_support_not_down | 8 | +12.21 / -0.75 / -1.45 | +4.75 / -7.86 / +3.12 |
| strict_both_up | 6 | +7.49 / -0.90 / -1.87 | +2.33 / -9.24 / -0.44 |
| pareto_either_up | 19 | +7.78 / +3.84 / -0.25 | +0.35 / -7.18 / +1.77 |
| coverage_only_up | 18 | +9.08 / -1.94 / -1.14 | +4.37 / -4.34 / +1.74 |
| primary_excluding_known_judge_anomalies | 14 | +10.49 / +0.09 / -0.67 | +4.88 / -7.87 / +1.97 |
| not_primary | 14 | -11.35 / -10.33 / +2.24 | +3.52 / +2.39 / -2.29 |

交互量=(l_to_l−s_to_l)−(l_to_s−s_to_s)，比较large生成是否比small生成更能受益于更换large facts；并非把所有组简单相减就能作机制归因。

| 子集 | 指标 | 交互pp | 95%区间pp |
| --- | --- | --- | --- |
| primary_coverage_up_support_not_down | completeness | -9.82 | [-23.01,+1.86] |
| primary_coverage_up_support_not_down | conciseness | -9.94 | [-16.00,-4.07] |
| primary_coverage_up_support_not_down | faithfulness | +3.58 | [-1.53,+8.71] |
| strong_coverage_20pp_support_not_down | completeness | -7.46 | [-27.53,+10.41] |
| strong_coverage_20pp_support_not_down | conciseness | -7.11 | [-15.37,+0.10] |
| strong_coverage_20pp_support_not_down | faithfulness | +4.57 | [-2.12,+12.15] |

## 8. 解释与限制

1. 这里回答的是条件比较：在抽取指标large占优的同一批会议上，固定生成模型后换facts是否更好。不是所有30条平均，也不是假设large永远占优。
2. 指标优势不意味着参考集合严格包含。主子集中large可能增加多条同时漏掉small独有参考；表中的参考超集列直接揭示此差异。
3. 支持率不下降仍可能增加绝对不支持项数，且长复合列表项和短原子项并不等粒度；不能把率的帕累托优势当成全部事实质量认证。
4. 两阶段仍有完整原文：small事实遗漏可由生成补充，large事实新增可被生成忽略；reference_propagation.csv给出匹配层面的传递。
5. 原评审并非可靠人工真值：0378/0795的过宽松匹配、0078逐项匹配差异等需复核。主分析去除既知异常后另列14条结果；明显优势8条不包含0378/0795。
6. 配对bootstrap为2000次会议级重采样、95%百分位区间，种子42/43/44对应C/Q/F；单会议来源区间退化，没有推断意义。未校正多重比较，不包含评审误差。
7. 子集是用实验后观察抽取结果选出，阈值非预注册，且来源数不均、pilot有最短/最长富集；只能解释这些样本，不能据此推广总体或证明模型规模因果机制。
8. 更丰富的facts可能改变长度/提示和采样结果，没有定长控制与多seed重复；不把任何一项差值完全归因于一个因素。

## 9. 数据文件

- [all_sample_selection.csv](all_sample_selection.csv)：全30样本指标优势、权衡/持平分类和所有筛选标志。
- [cohorts.json](cohorts.json)：每个子集的完整样本ID。
- [primary_sample_eight_arms.csv](primary_sample_eight_arms.csv)：主16条的128份纪要完整分子/分母与评分。
- [cohort_summary_metrics.csv](cohort_summary_metrics.csv)、[cohort_fact_metrics.csv](cohort_fact_metrics.csv)：整体/来源内八组分布与抽取质量。
- [paired_contrasts.csv](paired_contrasts.csv)：16类对比三指标，胜平负及区间。
- [reference_propagation.csv](reference_propagation.csv)：新增/丢失参考及large独有抽取信息的利用计数。
- [fact_source_generator_interaction.csv](fact_source_generator_interaction.csv)：事实来源×生成模型交互。
- [validation.json](validation.json)、[analyze.py](analyze.py)：输入对应性和可复现脚本。未改原实验，未重生成、重评或调用API。

