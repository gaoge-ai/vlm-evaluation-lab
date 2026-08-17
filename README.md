# VLM Evaluation Lab

一个面向 Vision-Language Model（VLM）的轻量评估项目，围绕自建小型 benchmark，完成：

```text
数据构造 → 模型推理 → 人工评分 → 错误分析 → 模型对比
```

当前评估模型：

- `Qwen/Qwen2.5-VL-3B-Instruct`
- `OpenGVLab/InternVL3-2B-hf`

## Benchmark

当前 benchmark 包含：

- 40 张图像
- 40 个图像问答问题
- 每张图像对应 1 个问题
- 每个问题提供人工参考答案

覆盖任务包括：

- OCR
- 图表理解
- 表格理解
- 架构图 / 论文图理解
- UI 截图理解
- 现实场景与物体识别
- No-answer / 幻觉控制

核心数据：

```text
data/images/
data/questions.csv
data/dataset_card.md
```

## 推理与评估

Qwen2.5-VL：

```powershell
python scripts/run_qwen_vl.py `
  --questions data/questions.csv `
  --output results/qwen_vl_40_images.csv `
  --model_name Qwen/Qwen2.5-VL-3B-Instruct `
  --prompt_mode structured_zh
```

InternVL3-2B：

```powershell
python scripts/run_internvl.py `
  --questions data/questions.csv `
  --output results/internvl3_2b_40_images.csv `
  --model_name OpenGVLab/InternVL3-2B-hf `
  --prompt_mode structured_zh
```

人工评估采用 0–2 分制：

| 分数 | 含义 |
|---:|---|
| 2 | 回答正确，且有图像依据 |
| 1 | 基本正确，但存在遗漏或轻微错误 |
| 0 | 回答错误、误读图像或无依据编造 |

详细评分标准见：

```text
evaluation/rubric.md
```

## 实验结果

| 模型 | 样本数 | 2 分 | 1 分 | 0 分 | 平均分 |
|---|---:|---:|---:|---:|---:|
| Qwen2.5-VL-3B-Instruct | 40 | 31 | 4 | 5 | 1.65 / 2 |
| InternVL3-2B | 40 | 31 | 4 | 5 | 1.65 / 2 |

两个模型总体得分相同，但能力侧重点不同：

- **Qwen2.5-VL**：在表格理解、部分架构图和结构化视觉信息读取上更稳定
- **InternVL3-2B**：在部分 OCR 细节、UI 截图和论文标题信息提取上表现更好
- **共同难点**：中文书法 OCR、海报文字、密集表格数值读取、复杂图表定位

逐样本对比：

| 对比结果 | 数量 |
|---|---:|
| Both correct | 28 |
| Qwen better | 4 |
| InternVL better | 4 |
| Both problematic | 4 |

详细对比见：

```text
results/model_comparison.md
results/model_comparison_table.csv
```

## 项目结构

```text
vlm-evaluation-lab/
├── data/
│   ├── images/
│   ├── questions.csv
│   └── dataset_card.md
├── evaluation/
│   ├── rubric.md
│   ├── manual_scores.csv
│   └── manual_scores_internvl.csv
├── results/
│   ├── qwen_vl_40_images.csv
│   ├── internvl3_2b_40_images.csv
│   ├── model_comparison_table.csv
│   └── model_comparison.md
├── scripts/
│   ├── run_qwen_vl.py
│   └── run_internvl.py
├── notebooks/
│   └── vlm_inference_demo.ipynb
├── requirements.txt
├── LICENSE
└── README.md
```

## 项目说明

该项目主要用于建立完整的 VLM evaluation 流程，并观察不同模型在细粒度视觉任务上的能力差异。当前 benchmark 规模较小，实验结果仅用于项目内分析，不代表模型的通用能力。
