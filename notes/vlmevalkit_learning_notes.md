# VLMEvalKit 学习笔记

## 1. 学习目标

本文件用于记录我对 VLMEvalKit 正式评估流程的初步理解。

这一步的目标不是马上完整部署 VLMEvalKit，而是搞清楚：

```text
正式 VLM benchmark 是如何组织模型、组织数据、跑推理、做后处理和计算指标的。
```

结合本项目来说，我需要理解：

```text
我的手动 benchmark 和 VLMEvalKit 这种正式评测工具之间有什么区别。
```

---

## 2. VLMEvalKit 是什么？

VLMEvalKit 是 OpenCompass 团队维护的一个开源多模态模型评测工具包，主要用于评估 Large Vision-Language Models / Large Multi-Modality Models。

它的核心作用是：

```text
把“模型调用、benchmark 数据加载、推理、答案后处理、指标计算、结果保存”这些流程统一起来。
```

如果没有这种工具，评估不同 VLM 时通常会遇到很多重复工作：

```text
每个 benchmark 的数据格式不同
每个模型的输入格式不同
每个任务的答案抽取方式不同
每个指标的计算方式不同
结果难以复现
```

VLMEvalKit 试图把这些流程标准化。

---

## 3. 正式评估的基本流程

VLMEvalKit 的整体流程可以理解为：

```text
选择模型
→ 选择 benchmark
→ 加载数据
→ 调用模型生成答案
→ 后处理模型输出
→ 抽取最终答案
→ 计算指标
→ 保存评估结果
```

可以画成：

```text
Model Config
     ↓
Dataset Config
     ↓
run.py
     ↓
Model Inference
     ↓
Answer Extraction / Post-processing
     ↓
Metric Calculation
     ↓
Evaluation Result
```

这和我现在手写脚本的区别在于：

```text
我现在是自己写 run_qwen_vl.py、run_internvl.py、manual_scores.csv；
VLMEvalKit 是把这些步骤封装成统一框架。
```

---

## 4. VLMEvalKit 如何组织模型？

VLMEvalKit 通过统一的模型接口管理不同 VLM。

无论是：

```text
Qwen-VL
InternVL
LLaVA
GPT-4o
Gemini
Claude
其他 API 模型
```

都需要被封装成统一的调用方式。

从评估框架角度看，它不关心模型内部结构到底是什么，而关心：

```text
输入一张图片和一个问题
模型是否能返回一个文本答案
```

所以模型接口的重点是：

```text
build prompt
load image
call model.generate / chat
return text answer
```

这也对应我现在项目里的两个脚本：

```text
scripts/run_qwen_vl.py
scripts/run_internvl.py
```

只不过我现在是手动写两个脚本，而正式工具会尽量把不同模型封装到统一接口下。

---

## 5. VLMEvalKit 如何组织 benchmark？

正式 benchmark 通常包含：

```text
图片 / 视频 / 多模态输入
问题
候选项或标准答案
任务类型
评估指标
数据集 split
```

例如常见任务包括：

```text
VQA
多选题
OCR
图表理解
文档理解
数学推理
幻觉检测
视频理解
多图理解
```

VLMEvalKit 中的数据集一般已经按照固定格式组织好。用户只需要指定数据集名称，框架会自动完成数据加载和评估。

而我的项目中，数据集对应的是：

```text
data/images/
data/questions.csv
```

其中 `questions.csv` 相当于我自己设计的小型 benchmark 数据文件。

---

## 6. VLMEvalKit 如何跑推理？

正式流程通常通过一个统一入口运行，例如：

```text
python run.py --data DATASET_NAME --model MODEL_NAME
```

它可以在一次命令中指定多个模型和多个 benchmark。

推理阶段主要做：

```text
读取样本
构造 prompt
加载图片
调用模型
保存原始输出
```

这和我现在做的事情对应关系如下：

| 我的项目 | VLMEvalKit |
|---|---|
| `run_qwen_vl.py` | 模型推理接口 |
| `run_internvl.py` | 模型推理接口 |
| `questions.csv` | benchmark 数据 |
| `qwen_vl_40_images.csv` | 模型原始输出 |
| `internvl3_2b_40_images.csv` | 模型原始输出 |

---

## 7. 为什么需要结果后处理？

VLM 的输出通常不是一个干净答案，而是一段自然语言。

例如问题是多选题：

```text
Which option is correct? A / B / C / D
```

模型可能回答：

```text
The correct answer is probably B because ...
```

这时候评估工具需要从长回答中抽取出：

```text
B
```

这就是 answer extraction / post-processing。

对于 yes/no、多选题、短文本题，正式评估通常需要把模型的自然语言输出转换为可计算的答案。

在我的项目中，我现在是人工看 `Final Answer`，然后给 0/1/2 分。  
而 VLMEvalKit 会尽量用规则匹配或 LLM judge 来做答案抽取和评分。

---

## 8. VLMEvalKit 如何计算指标？

不同任务的指标不同。

常见指标包括：

```text
Accuracy
Exact Match
F1
Multiple-choice accuracy
LLM-based judge score
Hallucination score
```

对于选择题，指标通常比较明确；  
对于开放问答，评估会更复杂，可能需要 LLM-based answer extraction 或人工检查。

我的项目目前使用的是：

```text
0–2 分人工评分
错误类型标注
case study 分析
```

它不适合做 leaderboard，但很适合学习模型错误模式。

---

## 9. VLMEvalKit 适合什么场景？

适合：

```text
正式比较多个 VLM
跑公开 benchmark
复现论文或 leaderboard 结果
统一评估流程
减少手动数据处理和指标计算
大规模评测几十个模型或数据集
```

不太适合一开始就用于：

```text
刚入门时理解模型错误
自定义小数据集的细致 case study
只有几十条样本的学习型 benchmark
还没有稳定评分规则的探索阶段
```

因此，对我当前项目来说，VLMEvalKit 不是马上替代手动评估，而是帮助我理解正式评测流程。

---

## 10. 它对科研 / 实习有什么价值？

VLMEvalKit 这类工具体现了大模型评估中的几个核心能力：

```text
模型接口统一
数据集接口统一
评估指标统一
推理结果可复现
多模型多任务横向对比
结果后处理自动化
```

这些能力在大模型算法岗、模型评测岗、多模态算法实习中都很重要。

未来如果我要做更正式的 VLM 项目，可以考虑：

```text
把自己的 benchmark 转成 VLMEvalKit 支持的格式
用 VLMEvalKit 跑公开 benchmark
对比自己手动评估和正式 benchmark 的差异
```

---

## 11. 和当前项目的关系

当前项目已经完成了一个手动版评估闭环：

```text
自建数据集
→ Qwen / InternVL 推理
→ 人工评分
→ 错误类型分析
→ 模型对比
```

VLMEvalKit 对应的是更正式、更规模化的版本：

```text
标准 benchmark
→ 统一模型接口
→ 自动推理
→ 自动后处理
→ 自动指标计算
→ 可复现结果
```

所以我现在需要掌握的不是“马上完全用 VLMEvalKit 替代当前项目”，而是理解：

```text
为什么正式评估不能只靠我手动看 CSV
为什么模型接口和数据集接口要标准化
为什么答案抽取和指标计算很重要
为什么结果可复现对科研和实习项目很重要
```

---

## 12. 阶段性理解

通过了解 VLMEvalKit，我现在可以把 VLM 评估分成两个层次：

### 1. 学习型手动评估

特点：

```text
样本少
人工评分
case study 详细
容易理解模型错误
适合入门和项目展示
```

我的 `vlm-evaluation-lab` 当前就属于这一类。

### 2. 正式 benchmark 评估

特点：

```text
样本多
流程标准
指标自动计算
支持多模型多数据集
结果更容易复现
适合论文、leaderboard 和大规模对比
```

VLMEvalKit 属于这一类。

两者不是替代关系，而是递进关系：

```text
先通过手动评估理解模型怎么错
再通过正式工具理解大规模评测怎么做
```
