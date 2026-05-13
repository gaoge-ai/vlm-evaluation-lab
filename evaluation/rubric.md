# Qwen2.5-VL 评分标准 Rubric

## 1. 文件目的

本文件用于评价 `Qwen/Qwen2.5-VL-3B-Instruct` 在本项目 40 个图像问答样本上的回答质量。

评分结果后续会写入：

```text
evaluation/manual_scores.csv
```

主要目标不是简单判断“对/错”，而是记录：

- 模型是否回答正确；
- 错误属于哪种类型；
- 哪些任务对 VLM 更困难；
- 后续如何整理 `error_cases.md` 和最终报告。

---

## 2. 总体评分规则

采用 0–2 分制。

| 分数 | 含义 | 判断标准 |
|---:|---|---|
| 2 | 正确 | 回答与 `expected_answer` 一致，且能从图像中找到依据 |
| 1 | 部分正确 | 方向基本对，但有遗漏、轻微误读、表达不完整或细节错误 |
| 0 | 错误 | 答案错误、读错图像、编造信息、答非所问或无法支持 |

评分时优先看 **Final Answer 是否正确**，不要因为模型解释得流畅就给高分。

---

## 3. 不同任务的评分重点

### 3.1 OCR

关注模型是否准确识别图中文字。

| 分数 | 标准 |
|---:|---|
| 2 | 关键文字完全读对 |
| 1 | 大意正确，但有少量漏字、错字或格式问题 |
| 0 | 关键文字读错，或没有识别出应识别的信息 |

常见错误类型：

```text
OCR Error
```

---

### 3.2 图表理解 Chart Understanding

关注模型是否读懂坐标轴、图例、曲线、柱子和趋势。

| 分数 | 标准 |
|---:|---|
| 2 | 正确识别最高值、最低值、趋势、模型名称或对应数值 |
| 1 | 趋势大体正确，但数值、单位或细节有小错误 |
| 0 | 曲线、图例、数值或趋势判断错误 |

常见错误类型：

```text
Chart Misinterpretation
Number Error
```

---

### 3.3 表格理解 Table Understanding

关注模型是否读对行、列和对应数值。

| 分数 | 标准 |
|---:|---|
| 2 | 正确定位行列，并读出正确答案 |
| 1 | 找到大致位置，但数值或细节有轻微错误 |
| 0 | 读错行列、读错数值或比较错误 |

常见错误类型：

```text
Table Misreading
Number Error
```

---

### 3.4 架构图 / 论文图 Scientific Figure

关注模型是否识别出图中的模块、箭头、流程和任务标签。

| 分数 | 标准 |
|---:|---|
| 2 | 正确识别关键模块或结构关系 |
| 1 | 大体理解正确，但遗漏部分细节或解释略泛 |
| 0 | 模块、关系或流程理解错误 |

常见错误类型：

```text
Architecture Misreading
Reasoning Error
```

---

### 3.5 UI 截图理解

关注模型是否识别出软件界面、网页元素、按钮、快捷键或模型名称。

| 分数 | 标准 |
|---:|---|
| 2 | 正确读出目标 UI 信息 |
| 1 | 界面类型判断正确，但局部细节有小错误 |
| 0 | 软件、按钮、快捷键或页面信息判断错误 |

常见错误类型：

```text
UI Misreading
OCR Error
```

---

### 3.6 现实场景 / 物体识别

关注模型是否识别出图中可见物体、场景、数量和空间关系。

| 分数 | 标准 |
|---:|---|
| 2 | 正确识别目标物体、数量或关系 |
| 1 | 大体正确，但遗漏部分细节 |
| 0 | 物体、数量或空间关系判断错误 |

常见错误类型：

```text
Object Error
Counting Error
Spatial Error
```

---

### 3.7 No-answer / 幻觉风险问题

如果问题本身无法从图像中判断，好的模型应该承认“不确定”。

| 分数 | 标准 |
|---:|---|
| 2 | 明确回答图中无法确定，没有乱猜 |
| 1 | 表达了不确定，但仍有少量猜测 |
| 0 | 编造图中不存在的信息 |

常见错误类型：

```text
Hallucination
Unsupported Inference
```

---

## 4. 错误类型标签

在 `manual_scores.csv` 的 `error_type` 字段中，建议使用下面这些标签。

| 错误类型 | 含义 |
|---|---|
| Correct | 完全正确 |
| Partially Correct | 部分正确 |
| OCR Error | 文字识别错误 |
| Number Error | 数字、单位或数值读取错误 |
| Chart Misinterpretation | 图表趋势、曲线、柱子或图例理解错误 |
| Table Misreading | 表格行列或单元格读取错误 |
| Architecture Misreading | 架构图模块或流程理解错误 |
| UI Misreading | UI 界面元素读取错误 |
| Object Error | 物体识别错误 |
| Counting Error | 数量判断错误 |
| Spatial Error | 空间关系判断错误 |
| Hallucination | 编造图中不存在的信息 |
| Unsupported Inference | 推断没有图像依据 |
| Over-general Answer | 回答过于泛泛 |
| Format Error | 没有按要求格式回答 |

一般来说：

```text
2 分 → Correct
1 分 → Partially Correct 或具体错误类型
0 分 → 选择最主要的错误类型
```

---

## 5. manual_scores.csv 建议字段

后续评分表建议包含以下字段：

```text
image_id
question_id
image_type
skill_type
answer_type
difficulty
question
expected_answer
model_name
model_answer
score
error_type
comment
```

其中最重要的是：

| 字段 | 作用 |
|---|---|
| score | 0 / 1 / 2 分 |
| error_type | 错误类型 |
| comment | 一句话说明为什么这样打分 |

---

## 6. 当前项目中的评分示例

| image_id | 简要情况 | 分数 | 错误类型 |
|---|---|---:|---|
| architecture_01 | 正确识别 NSP 和 Mask LM | 2 | Correct |
| chart_01 | 正确识别最高降雨月份 June 和 180 mm | 2 | Correct |
| chart_04 | 将 SNR=-4 dB 下最高准确率模型误判为 resnet50 | 0 | Chart Misinterpretation |
| OCR_03 | 标题中有 16x16，但模型回答图中无法确定 | 0 | OCR Error |
| table_06 | MathVista mini 数值读错 | 0 | Table Misreading |
| scene_02 | 中文书法“大音希声”识别错误 | 0 | OCR Error |
| architecture_06 | 正确回答图中没有给出数据集名称 | 2 | Correct |

---

## 7. 评分原则

评分时遵循以下原则：

1. 主要看答案是否正确，而不是语言是否流畅；
2. 答案必须能从图像中找到依据；
3. 图表和表格题要重视数字、单位、行列对应关系；
4. OCR 题要重视关键文字是否读对；
5. no-answer 题中，承认“图中无法确定”是正确表现；
6. 不要奖励没有图像依据的合理猜测；
7. 如果模型一部分对、一部分错，通常给 1 分；
8. `comment` 字段要用一句话说明打分原因。

---

## 8. 下一步

使用本评分标准，对 `results/qwen_vl_40_images.csv` 中的 40 条回答进行人工评分，生成：

```text
evaluation/manual_scores.csv
```

之后再根据评分结果整理：

```text
analysis/error_cases.md
```
