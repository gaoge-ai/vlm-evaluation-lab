# Dataset Card

本数据集是 `vlm-evaluation-lab` 中自建的小型 VLM benchmark，用于评估视觉语言模型在不同图像问答任务上的表现。

## 数据概况

- 图像数量：40
- 问题数量：40
- 每张图像对应 1 个问题
- 每个问题提供人工标注的 `expected_answer`

数据文件：

```text
data/images/
data/questions.csv
```

## 覆盖任务

当前样本主要覆盖：

- OCR
- 图表理解
- 表格理解
- 模型架构图 / 论文图理解
- UI 截图理解
- 现实场景与物体识别
- No-answer / 幻觉控制

## 标注字段

`questions.csv` 主要包含：

```text
image_id
question_id
image_path
image_type
skill_type
difficulty
question
expected_answer
answer_type
```

其中：

- `image_type`：图像类型
- `skill_type`：主要测试能力
- `difficulty`：easy / medium / hard
- `expected_answer`：人工参考答案
- `answer_type`：答案类型，如 short_text、number、yes_no、evidence_based_reasoning、no_answer

## 使用说明

该数据集主要用于项目内的模型对比、人工评分和错误分析，不作为标准公开 benchmark。
