# Dataset Card：VLM Evaluation Lab Benchmark

## 1. 数据集简介

本数据集是 `vlm-evaluation-lab` 项目中自建的小型 VLM benchmark，用于测试 Vision-Language Model 在不同类型图像问答任务上的表现。

本数据集的目标不是追求大规模，而是构造一个覆盖多种视觉能力的小型评估集，用于观察模型在 OCR、图表理解、表格理解、论文图理解、UI 截图理解、现实场景理解和幻觉控制等任务中的表现。

当前版本主要用于评估：

```text
Qwen/Qwen2.5-VL-3B-Instruct
```

后续可继续用于 InternVL、LLaVA 等模型的对比实验。

---

## 2. 数据集规模

当前版本包含：

| 项目 | 数量 |
|---|---:|
| 图像数量 | 40 |
| 问题数量 | 40 |
| 每张图像问题数 | 1 |
| 标准答案数量 | 40 |
| 当前评估模型 | Qwen2.5-VL-3B-Instruct |

相关文件：

```text
data/images/
data/questions.csv
results/qwen_vl_40_images.csv
evaluation/manual_scores.csv
```

---

## 3. 图像类型分布

当前数据集中的图像类型如下：

| image_type | 数量 | 说明 |
|---|---:|---|
| academic_figure | 8 | 模型架构图、论文图、流程图等 |
| chart | 6 | 折线图、柱状图、散点图等 |
| table | 6 | 实验结果表、benchmark 表、模型对比表 |
| ui_screenshot | 5 | GitHub、Hugging Face、IDE、软件界面截图 |
| scene_photo | 8 | 现实场景图片、物体图片、场景 OCR 图片 |
| ocr_document | 2 | 普通文档截图 |
| ocr_paper | 2 | 论文标题或论文内容截图 |
| ocr_code_screenshot | 1 | 代码截图 |
| ocr_bilingual_document | 1 | 中英文混合文档截图 |
| poster_photo | 1 | 海报或包装类图片 |

从任务覆盖角度看，可以大致归纳为：

| 大类 | 覆盖内容 |
|---|---|
| 科学图理解 | academic_figure |
| 图表理解 | chart |
| 表格理解 | table |
| OCR | ocr_document / ocr_paper / ocr_code_screenshot / ocr_bilingual_document / scene OCR |
| UI 理解 | ui_screenshot |
| 现实场景理解 | scene_photo / poster_photo |
| 幻觉控制 | no-answer 类型问题 |

---

## 4. 测试能力标签

`data/questions.csv` 中使用 `skill_type` 字段标记每个问题主要测试的能力。

当前包含的主要能力包括：

| 能力类型 | 说明 |
|---|---|
| OCR | 识别图像中的文字 |
| academic_OCR | 识别论文标题、论文截图中的关键信息 |
| code_OCR | 识别代码截图中的变量或参数 |
| bilingual_OCR | 识别中英文混合文本 |
| Chinese_OCR | 识别中文文本 |
| scene_OCR | 识别现实场景中的文字 |
| chart_understanding | 理解图表中的数值、趋势和坐标轴 |
| chart_comparison | 对图表中不同曲线或类别进行比较 |
| table_understanding | 读取表格中的行、列和值 |
| table_comparison | 比较表格中的模型或指标 |
| architecture_understanding | 理解模型架构图中的模块和流程 |
| architecture_comparison | 比较不同架构图中的模块差异 |
| scientific_figure | 理解论文图和科学图示 |
| UI_understanding | 理解网页、IDE 或软件界面截图 |
| object_recognition | 识别图中物体或场景 |
| counting | 计数 |
| spatial_reasoning | 判断空间关系 |
| hallucination_risk | 判断模型是否会编造图中没有的信息 |

---

## 5. CSV 字段说明

`data/questions.csv` 是本数据集的核心标注文件。

字段如下：

| 字段 | 含义 |
|---|---|
| image_id | 图像编号，例如 `chart_01` |
| question_id | 问题编号，例如 `chart_01_q1` |
| image_path | 图像相对路径 |
| image_type | 图像类型 |
| skill_type | 主要测试能力 |
| difficulty | 问题难度，分为 easy / medium / hard |
| question | 给 VLM 的问题 |
| expected_answer | 人工标注的参考答案 |
| answer_type | 答案类型 |
| source | 图像来源说明 |
| notes | 备注信息 |

---

## 6. answer_type 说明

当前数据集中使用的 `answer_type` 包括：

| answer_type | 含义 |
|---|---|
| short_text | 简短文本答案，例如模型名、月份、标签名 |
| number | 数字或数值类答案 |
| yes_no | 是 / 否判断 |
| evidence_based_reasoning | 需要基于图像证据进行解释 |
| no_answer | 图中无法判断，模型应承认不确定 |

其中 `no_answer` 类型主要用于测试模型的 hallucination risk，即模型是否会编造图中不存在的信息。

---

## 7. 问题设计原则

本数据集在设计问题时遵循以下原则：

1. 每个问题尽量能从图像中直接回答；
2. 每个问题都提供人工标注的 `expected_answer`；
3. 问题类型尽量覆盖 OCR、图表、表格、UI、现实场景和科学图理解；
4. 避免只问泛泛的 “What is shown in this image?”；
5. 保留少量 no-answer 问题，用于测试模型是否会幻觉；
6. 对图表和表格问题，尽量让答案可明确评分；
7. 对部分复杂图片，只要求模型识别可见信息，不要求模型做超出图像本身的专业判断。

---

## 8. 数据来源说明

本数据集主要由以下来源构成：

| 来源类型 | 说明 |
|---|---|
| 自制图表 | 用于测试图表趋势、数值读取和模型比较 |
| 自制或整理表格 | 用于测试表格行列定位和数值读取 |
| 论文 / 架构图截图 | 用于测试 scientific figure 和 architecture understanding |
| 软件界面截图 | 用于测试 UI understanding |
| 文档 / 代码截图 | 用于测试 OCR |
| 现实场景照片 | 用于测试 object recognition、scene understanding 和 scene OCR |

本数据集主要用于个人学习、模型评估和项目展示，不用于商业训练。

如果后续将仓库公开，需要注意检查图片来源，避免上传包含隐私信息、版权风险或不适合公开展示的截图。

---

## 9. 当前评估状态

当前已经完成 Qwen2.5-VL-3B-Instruct 的完整推理和人工评分。

相关结果文件：

```text
results/qwen_vl_40_images.csv
evaluation/rubric.md
evaluation/manual_scores.csv
analysis/error_cases.md
notes/qwen_vl_observations.md
```

评分概览：

| 指标 | 结果 |
|---|---:|
| 总问题数 | 40 |
| 成功输出 | 40 / 40 |
| 2 分样本 | 31 |
| 1 分样本 | 4 |
| 0 分样本 | 5 |
| 平均分 | 1.65 / 2 |

主要发现：

- Qwen2.5-VL-3B 在清晰架构图、简单图表、普通表格和 UI 截图上表现较好；
- 容易出错的任务包括复杂曲线图比较、密集表格数值读取、中文书法 OCR、海报标题 OCR 和软件快捷键识别；
- no-answer 类问题整体表现较谨慎，模型能够在部分问题中承认图中无法确定。

---

## 10. 数据集局限性

当前数据集仍然是一个小型 benchmark，存在以下局限：

1. 样本数量较少，目前只有 40 张图像和 40 个问题；
2. 每张图像目前只有 1 个问题，无法充分覆盖同一图像的多种能力；
3. 部分图片来源于截图或现实照片，图像质量和清晰度不完全统一；
4. 当前样本中 CWT / 工业图像相关内容还不够充分；
5. 当前评估以人工评分为主，尚未接入 VLMEvalKit 等正式评测工具；
6. 当前只完成 Qwen2.5-VL 的评估，还没有完成第二模型对比；
7. 数据集不是标准公开 benchmark，结果只能用于项目内分析，不能直接代表模型的通用能力。

---

## 11. 后续改进方向

后续可以从以下方向扩展数据集：

1. 增加每张图像的问题数量，从 1 个扩展到 2–3 个；
2. 增加 CWT 时频图、混淆矩阵、t-SNE、故障诊断实验图等领域图像；
3. 增加更多 hard cases，例如密集表格、小字号 UI、复杂多曲线图；
4. 为部分问题增加英文版本，用于中英文 prompt 对比；
5. 为 no-answer 问题增加更多样本，系统测试 hallucination risk；
6. 使用 InternVL 或 LLaVA 跑同一批样本，形成模型对比；
7. 后续了解 VLMEvalKit，并比较自建小 benchmark 与正式评测流程的差异。

---

## 12. 当前版本总结

当前版本的数据集已经能够支持一个完整的 Qwen2.5-VL 单模型评估闭环：

```text
40 张图像
→ 40 个问题
→ Qwen2.5-VL 推理
→ 人工评分
→ 错误类型分析
```

它的主要价值不是规模，而是帮助建立 VLM evaluation 的基本流程意识：

```text
如何构造测试集
如何设计问题
如何标注 expected_answer
如何记录模型输出
如何人工评分
如何分析模型错误
如何为后续模型对比做准备
```
