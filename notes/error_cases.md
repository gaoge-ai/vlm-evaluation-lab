# Error Cases Analysis

## 1. 文件目的

本文件基于 `evaluation/manual_scores.csv`，对 Qwen2.5-VL-3B-Instruct 在本项目 40 个图像问答样本上的表现进行错误类型分析。

它的作用是将模型输出从“单条回答”整理成可以用于项目报告的分析结论，重点回答：

- 哪些任务模型表现较好；
- 哪些任务模型容易出错；
- 错误主要集中在哪些类型；
- 后续是否需要补充数据、修改问题或进行模型对比。

---

## 2. 总体评分结果

本轮评估共包含 40 个问题，使用 0–2 分制进行人工评分。

| 指标 | 结果 |
|---|---:|
| 总问题数 | 40 |
| 2 分样本 | 31 |
| 1 分样本 | 4 |
| 0 分样本 | 5 |
| 平均得分 | 1.65 / 2 |

整体来看，Qwen2.5-VL-3B-Instruct 在本 benchmark 上表现较稳定。大多数结构清晰的架构图、图表、表格、OCR 截图和 UI 截图都能被正确理解。

模型的主要问题集中在：

- 复杂图表中的曲线 / 图例判断；
- 密集表格中的精确数值读取；
- 中文书法、海报等非标准字体 OCR；
- 软件界面中的快捷键细节读取；
- 少数架构图中的模块关系解释不够准确。

---

## 3. 得分分布

| 分数 | 数量 | 说明 |
|---:|---:|---|
| 2 | 31 | 回答正确，且能从图像中找到依据 |
| 1 | 4 | 部分正确，但存在细节遗漏、轻微误读或表达不够准确 |
| 0 | 5 | 关键答案错误，或图像信息读取失败 |

从得分分布来看，模型在多数样本上能够完成基本视觉问答任务，但在需要精确定位、精确读取和细粒度对比的任务上仍然存在明显风险。

---

## 4. 错误类型统计

| 错误类型 | 数量 | 代表样本 |
|---|---:|---|
| Architecture Misreading | 1 | architecture_03 |
| Number Error | 1 | chart_03 |
| Chart Misinterpretation | 1 | chart_04 |
| OCR Error | 3 | OCR_03, scene_02, scene_07 |
| Partially Correct | 1 | scene_01 |
| Table Misreading | 1 | table_06 |
| UI Misreading | 1 | ui_05 |

说明：

- `OCR Error` 是本轮最常见的错误类型，主要出现在论文标题细节、中文书法和电影海报标题中；
- `Chart Misinterpretation` 和 `Table Misreading` 虽然数量不多，但代表了 VLM 在真实评测中非常关键的问题：模型看起来理解了图表/表格，但在精确值或对应关系上出错；
- `UI Misreading` 说明软件界面截图中的小字号文字、快捷键信息仍然需要人工核查。

---

## 5. 成功案例分析

以下是本轮中比较有代表性的成功案例。

| Case | image_id | skill_type | 得分 | 成功原因 |
|---:|---|---|---:|---|
| 1 | architecture_01 | scientific_figure | 2 | 正确识别 BERT 预训练部分的两个任务标签 NSP 和 Mask LM。 |
| 2 | architecture_04 | architecture_understanding | 2 | 正确识别 InternVL3.5-Flash 相比 InternVL3.5 增加了 Visual Resolution Router（ViR）。 |
| 3 | chart_01 | chart_understanding | 2 | 正确识别降雨量最高月份为 June，数值为 180 mm。 |
| 4 | table_02 | table_comparison | 2 | 正确判断 Clean 数据集上测试准确率最高的模型是 MobileViT-S，准确率为 100.00%。 |
| 5 | ui_03 | UI_understanding | 2 | 正确读取 Hugging Face Trending 列表第一位模型名称。 |
| 6 | architecture_06 | hallucination_risk | 2 | 正确判断图中没有提供训练数据集名称，没有进行无依据猜测。 |
| 7 | scene_04 | hallucination_risk | 2 | 正确回答仅凭建筑照片无法确定准确城市名称，表现出较好的不确定性控制。 |
| 8 | table_05 | table_understanding | 2 | 正确判断 HumanEval 行中最高分模型为 Claude 3.5 Sonnet，分数为 92.0。 |

这些成功案例说明，Qwen2.5-VL-3B 在以下任务上表现较好：

- 结构清晰的模型架构图；
- 简单柱状图 / 折线图；
- 行列结构清楚的表格；
- 文字清晰的 UI 截图；
- 明确的 no-answer / anti-hallucination 问题。

---

## 6. 失败案例分析

以下是本轮中最值得关注的错误案例。

### 6.1 chart_04：复杂折线图曲线误判

| 项目 | 内容 |
|---|---|
| image_id | chart_04 |
| skill_type | chart_comparison |
| expected_answer | mobilevit 在 SNR=-4 dB 时准确率最高 |
| model_answer | resnet50 |
| score | 0 |
| error_type | Chart Misinterpretation |

错误分析：

模型在多曲线图中错误判断了 SNR=-4 dB 位置上最高准确率对应的模型。该错误说明模型可能没有准确对应图例、曲线颜色和目标横坐标位置。

这类错误比较重要，因为模型回答看起来像是理解了图表，但实际上在关键比较点上出错。

---

### 6.2 OCR_03：论文标题细节未正确提取

| 项目 | 内容 |
|---|---|
| image_id | OCR_03 |
| skill_type | academic_OCR |
| expected_answer | 16x16 |
| model_answer | 图中无法确定 |
| score | 0 |
| error_type | OCR Error |

错误分析：

图中标题包含 “An Image is Worth 16x16 Words”，但模型最终没有提取出 image patch 的大小，而是回答“图中无法确定”。

这个样本说明模型有时即使观察到相关文本，也可能无法把关键信息转化为最终答案。

---

### 6.3 scene_02：中文书法 OCR 错误

| 项目 | 内容 |
|---|---|
| image_id | scene_02 |
| skill_type | scene_OCR |
| expected_answer | 大音希声 |
| model_answer | 大青师朴 |
| score | 0 |
| error_type | OCR Error |

错误分析：

模型将书法作品中的“大音希声”误读为“大青师朴”。这说明 Qwen2.5-VL-3B 对艺术化中文字体、书法字体或低清晰度中文 OCR 仍然不稳定。

该错误也说明，中文 OCR 的难度不仅取决于语言，还取决于字体形态、图片清晰度和文字布局。

---

### 6.4 table_06：密集 benchmark 表格数值读错

| 项目 | 内容 |
|---|---|
| image_id | table_06 |
| skill_type | table_understanding |
| expected_answer | Qwen2.5-VL 72B 在 MathVista mini 上得分 74.8 |
| model_answer | 70.5 |
| score | 0 |
| error_type | Table Misreading |

错误分析：

模型在密集表格中读取了错误数值，说明它可能定位到了错误的行列交叉位置。

这类错误在真实评测中非常关键，因为表格理解任务不仅要求识别文字，还要求准确定位行列关系。

---

### 6.5 ui_05：VS Code 快捷键误读

| 项目 | 内容 |
|---|---|
| image_id | ui_05 |
| skill_type | UI_understanding |
| expected_answer | Ctrl+O |
| model_answer | Ctrl+K |
| score | 0 |
| error_type | UI Misreading |

错误分析：

模型错误读取了 VS Code 中“打开文件”的快捷键。该错误说明模型对软件界面中的小字号文本、快捷键和局部 UI 元素仍然存在误读风险。

UI 理解任务中，模型不仅要识别界面类型，还需要准确读取局部文字信息。

---

## 7. 部分正确案例分析

以下样本并非完全错误，但存在细节不准确或回答不够直接的问题。

| image_id | 得分 | 错误类型 | 分析 |
|---|---:|---|---|
| architecture_03 | 1 | Architecture Misreading | 模型识别到了 Patchify，但对 Noised Latent 与 Embed 的关系解释不够准确。 |
| chart_03 | 1 | Number Error | 模型判断月份和总量基本正确，但单位写成 `kvWh`，存在轻微单位错误。 |
| scene_01 | 1 | Partially Correct | 回答中提到可能是 water bottle，但加入了 collectible item 等不确定描述，答案不够直接。 |
| scene_07 | 1 | OCR Error | 只识别出 The Movie，遗漏关键的 F1，电影名称不完整。 |

这些样本说明，模型并不总是完全失败，很多时候是“看懂了大概，但关键细节不够准确”。

---

## 8. 任务类型层面的观察

### 8.1 架构图理解

模型在架构图理解上整体表现较好，能够识别 BERT、CLIP、MAE、InternVL 和 Swin Transformer 等图中的关键模块和标签。

主要风险是：

- 对模块之间关系解释过度；
- 把已有背景知识和图中信息混在一起；
- 对箭头、分支和嵌入模块的细节理解不够精确。

---

### 8.2 图表理解

简单图表表现较好，例如最高柱子、最大值、最高平均准确率等问题。

主要风险是：

- 多曲线图中图例和曲线对应错误；
- 横坐标特定位置的比较错误；
- 单位细节出错。

---

### 8.3 表格理解

结构清晰的表格表现较好，但密集 benchmark 表格中出现了明显行列定位错误。

主要风险是：

- 读错行列交叉位置；
- 读取相邻单元格数值；
- 对多模型、多指标表格中的目标列定位不稳。

---

### 8.4 OCR

清晰截图、代码截图和普通文档 OCR 表现较好。

主要风险是：

- 中文书法 OCR；
- 海报标题 OCR；
- 论文标题中的关键细节提取；
- 小字号 UI 文本。

---

### 8.5 UI 理解

模型能够识别 GitHub、Hugging Face、PyCharm 等界面信息，但对局部快捷键类问题不够稳定。

主要风险是：

- 快捷键误读；
- 小字号文字误读；
- 局部 UI 元素定位错误。

---

### 8.6 Hallucination 控制

本轮模型在 no-answer 类问题上整体表现较好，例如能够承认建筑照片无法确定城市名称，也能判断架构图没有提供训练数据集名称。

这说明结构化 prompt 中“不要猜测图中看不到的信息”的约束具有一定作用。

---

## 9. 阶段性结论

本轮错误分析表明，Qwen2.5-VL-3B-Instruct 在本项目 benchmark 上具备较好的基础视觉问答能力，尤其适合处理：

- 清晰架构图；
- 简单图表；
- 结构化表格；
- 普通 OCR 截图；
- 常见 UI 截图；
- no-answer 类反幻觉问题。

但它在以下任务上仍然需要谨慎使用：

- 复杂多曲线图比较；
- 密集表格精确数值读取；
- 艺术化中文 OCR；
- 海报标题 OCR；
- 软件界面快捷键读取；
- 需要精确定位的细粒度视觉问题。

因此，后续模型对比时应重点观察第二个模型是否也会在这些 case 上出错。如果两个模型都出错，说明这些任务可能是当前 VLM 的共性难点；如果只有 Qwen2.5-VL 出错，则说明该错误可能与模型本身的视觉细节处理能力有关。

---

## 10. 下一步建议

接下来建议优先完成以下任务：

1. 保留本文件作为 Qwen 单模型错误分析结果；
2. 如果继续跑第二模型，应优先关注本文件中的 bad cases；
3. 第二模型可以先跑 20 个代表性样本，而不是一开始完整跑 40 个；
4. 模型对比时重点比较 OCR、Chart、Table、UI 和 Hallucination 任务；
5. 最终报告中可以将本文件中的成功案例和失败案例整理成 case study。
