# VLM Evaluation Lab 项目总结报告

## 1. Project Motivation

本项目 `vlm-evaluation-lab` 是一个面向 Vision-Language Model（VLM）的入门级评估项目。

最初做这个项目的原因，是希望从“知道一些多模态大模型名字”进一步过渡到“能够实际运行模型、构造测试集、记录输出、设计评分标准，并分析模型能力边界”。

在项目开始之前，我对 VLM 的理解主要停留在：

```text
Qwen2.5-VL、InternVL、LLaVA 是多模态模型；
它们可以输入图片和文本；
它们可以回答图像相关问题。
```

但这种理解还不够具体。真正进入项目后，我发现 VLM 评估并不是简单问一句 “What is shown in this image?”，而是需要系统考虑：

```text
什么样的图片适合测试 VLM？
问题应该怎么设计？
模型回答如何保存？
标准答案如何制定？
回答对错如何判断？
错误类型如何归类？
不同模型之间如何公平比较？
```

因此，本项目的核心目标不是追求大规模 benchmark，而是完整走通一次小型 VLM evaluation 闭环：

```text
数据构造
→ 模型推理
→ 结果记录
→ 人工评分
→ 错误分析
→ 模型对比
→ 项目总结
```

这个过程帮助我从“跑模型”进一步转向“评估模型”。

---

## 2. Project Overview

本项目当前完成了一个小型自建 VLM benchmark，并基于该 benchmark 对两个开源 VLM 进行了评估：

```text
Qwen/Qwen2.5-VL-3B-Instruct
OpenGVLab/InternVL3-2B-hf
```

当前项目规模如下：

| 项目 | 数量 |
|---|---:|
| 图像数量 | 40 |
| 问题数量 | 40 |
| 每张图片问题数 | 1 |
| 评估模型数量 | 2 |
| 人工评分文件 | 2 |
| 模型对比表 | 1 |
| 错误分析文件 | 1 |
| 模型对比分析文件 | 1 |

当前已经完成的核心文件包括：

```text
data/questions.csv
data/dataset_card.md
results/qwen_vl_40_images.csv
results/internvl3_2b_40_images.csv
evaluation/rubric.md
evaluation/manual_scores.csv
evaluation/manual_scores_internvl.csv
results/model_comparison_table.csv
analysis/error_cases.md
analysis/model_comparison.md
notes/qwen_vl_observations.md
notes/vlmevalkit_learning_notes.md
evaluation/formal_eval_vs_manual_eval.md
notes/vlm_concepts.md
```

---

## 3. Test Set Construction

### 3.1 数据集设计目标

本项目的数据集不是随机找图片，而是围绕 VLM 常见能力构造。

我希望它能够覆盖以下能力：

```text
OCR
图表理解
表格理解
架构图 / 论文图理解
UI 截图理解
现实场景理解
空间关系 / 计数
幻觉控制
```

因此，数据集中的图片类型包括：

| 图像类型 | 测试目的 |
|---|---|
| 架构图 / 论文图 | 测试 scientific figure understanding |
| 折线图 / 柱状图 / 散点图 | 测试 chart understanding |
| 表格 / benchmark 表 | 测试 table understanding |
| 文档 / 代码 / 论文截图 | 测试 OCR |
| UI / 网页 / 软件截图 | 测试 UI understanding |
| 现实场景 / 海报 | 测试 object recognition、scene OCR 和 visual description |
| no-answer 问题 | 测试 hallucination risk |

### 3.2 questions.csv 字段

本项目使用 `data/questions.csv` 作为 benchmark 的核心标注文件。

每条样本包含：

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
source
notes
```

其中最重要的是：

| 字段 | 作用 |
|---|---|
| image_id | 图像编号 |
| question | 输入给 VLM 的问题 |
| expected_answer | 人工标注的参考答案 |
| image_type | 图片类型 |
| skill_type | 主要测试能力 |
| answer_type | 答案类型 |
| difficulty | 难度标记 |

### 3.3 数据集特点

当前数据集有几个特点：

1. 规模较小，但任务覆盖较广；
2. 每张图片只有一个问题，便于快速跑通完整流程；
3. 既包含普通视觉问答，也包含图表、表格、UI 和 OCR 等真实应用任务；
4. 保留了部分 hard cases，例如中文书法 OCR、密集 benchmark 表格、复杂曲线图和软件快捷键；
5. 包含 no-answer 问题，用于观察模型是否会编造图中看不到的信息。

这个数据集不能代表模型的通用能力，但适合用于学习型 VLM evaluation 和 case study。

---

## 4. Models Evaluated

### 4.1 Qwen2.5-VL-3B-Instruct

第一个模型选择的是：

```text
Qwen/Qwen2.5-VL-3B-Instruct
```

选择原因：

1. Qwen-VL 系列是当前主流开源 VLM 之一；
2. 对中文问题支持较好；
3. 能处理 OCR、图表、表格、UI、普通图像问答等多种任务；
4. 模型规模适中，适合本地跑通；
5. 适合作为后续多模型对比的主模型。

### 4.2 InternVL3-2B

第二个模型选择的是：

```text
OpenGVLab/InternVL3-2B-hf
```

选择原因：

1. InternVL 是当前比较重要的开源多模态模型系列；
2. 模型规模较小，适合本地推理；
3. Hugging Face Transformers 版本相对容易接入；
4. 适合与 Qwen2.5-VL 进行轻量级对比；
5. 能帮助观察不同 VLM 在 OCR、图表、表格和 UI 任务上的差异。

### 4.3 模型推理方式

两个模型均使用相同的 `data/questions.csv` 进行推理，并尽量保持 prompt 一致。

当前主要使用 `structured_zh` prompt，核心要求是：

```text
请严格基于图像内容回答问题。
不要猜测图中看不到的信息。
如果图中无法判断，请明确回答“图中无法确定”。
```

这个 prompt 的目的不是让模型回答更长，而是控制模型不要随意幻觉，并尽量让输出结构化。

---

## 5. Evaluation Rubric

### 5.1 评分标准

本项目使用 0–2 分制进行人工评分。

| 分数 | 含义 | 判断标准 |
|---:|---|---|
| 2 | 正确 | 回答与 expected_answer 一致，且能从图像中找到依据 |
| 1 | 部分正确 | 方向基本正确，但有遗漏、轻微误读、细节错误或表达不完整 |
| 0 | 错误 | 答案错误、读错图像、编造信息、答非所问或无法支持 |

评分时最重要的原则是：

```text
主要看答案是否正确，而不是语言是否流畅。
```

也就是说，模型回答得很自然、很长、很像推理，并不代表它真正看懂了图像。

### 5.2 错误类型

本项目记录的主要错误类型包括：

```text
OCR Error
Number Error
Chart Misinterpretation
Table Misreading
Architecture Misreading
UI Misreading
Object Error
Counting Error
Spatial Error
Hallucination
Unsupported Inference
Over-general Answer
Format Error
Partially Correct
```

这些错误类型的作用是把“模型错了”进一步拆开。

例如：

```text
读错书法字 → OCR Error
读错表格数值 → Table Misreading / Number Error
看错曲线最高点 → Chart Misinterpretation
编造图中没有的信息 → Hallucination
回答太泛泛 → Over-general Answer
```

---

## 6. Qwen2.5-VL Results

Qwen2.5-VL 的评分结果如下：

| 指标 | 结果 |
|---|---:|
| 总问题数 | 40 |
| 2 分样本 | 31 |
| 1 分样本 | 4 |
| 0 分样本 | 5 |
| 平均分 | 1.65 / 2 |

### 6.1 Qwen 表现较好的任务

Qwen2.5-VL 在以下任务中表现较好：

```text
结构清晰的模型架构图
简单柱状图 / 折线图
普通表格对比
代码截图 OCR
普通文档 OCR
GitHub / Hugging Face / PyCharm 等 UI 截图
no-answer 类反幻觉问题
```

代表性成功案例包括：

| image_id | 任务类型 | 表现 |
|---|---|---|
| architecture_01 | scientific_figure | 正确识别 BERT 预训练部分的 NSP 和 Mask LM |
| architecture_04 | architecture_understanding | 正确识别 InternVL3.5-Flash 中新增 Visual Resolution Router |
| chart_01 | chart_understanding | 正确识别降雨量最高月份 June 和 180 mm |
| table_02 | table_comparison | 正确判断 Clean 数据集最高准确率模型为 MobileViT-S |
| architecture_06 | hallucination_risk | 正确回答图中没有提供训练数据集名称 |

### 6.2 Qwen 的主要错误

Qwen 的主要错误集中在：

| image_id | 错误类型 | 问题 |
|---|---|---|
| chart_04 | Chart Misinterpretation | 多曲线图中误判 SNR=-4 dB 下最高模型 |
| OCR_03 | OCR Error | 没有从论文标题中提取出 16x16 |
| scene_02 | OCR Error | 中文书法“大音希声”识别错误 |
| table_06 | Table Misreading | 密集 benchmark 表格中 MathVista mini 数值读错 |
| ui_05 | UI Misreading | VS Code 快捷键 Ctrl+O 误读 |

这些错误说明，Qwen2.5-VL 并不是“看不懂图”，而是容易在细粒度视觉定位、密集信息读取和艺术化文字 OCR 上出错。

---

## 7. InternVL3-2B Results

InternVL3-2B 的评分结果如下：

| 指标 | 结果 |
|---|---:|
| 总问题数 | 40 |
| 2 分样本 | 31 |
| 1 分样本 | 4 |
| 0 分样本 | 5 |
| 平均分 | 1.65 / 2 |

### 7.1 InternVL 表现较好的任务

InternVL 在以下任务中表现较好：

```text
普通 OCR
论文标题细节提取
UI 快捷键读取
no-answer 问题
部分图表数值读取
```

代表性表现包括：

| image_id | 表现 |
|---|---|
| OCR_03 | 正确从论文标题中提取 16x16 |
| ui_05 | 正确读取 VS Code 中“打开文件”的快捷键 Ctrl+O |
| chart_03 | 正确读取 August 和 300 kWh |
| architecture_06 | 正确判断图中没有提供训练数据集名称 |

### 7.2 InternVL 的主要错误

InternVL 的错误主要集中在：

| image_id | 错误类型 | 问题 |
|---|---|---|
| architecture_03 | Architecture Misreading | 架构图局部步骤判断错误 |
| chart_06 | Chart Misinterpretation | 散点图中最大参数量模型误判 |
| scene_02 | OCR Error | 中文书法 OCR 错误 |
| table_05 | Table Misreading | HumanEval 最高分模型误判 |
| table_06 | Table Misreading | MathVista mini 数值读错 |

InternVL 的明显短板是表格理解不够稳定，尤其是密集 benchmark 表格中的行列定位和模型名称对应关系。

---

## 8. Model Comparison

### 8.1 总体对比

两个模型的总体结果非常接近：

| 模型 | 2 分 | 1 分 | 0 分 | 平均分 |
|---|---:|---:|---:|---:|
| Qwen2.5-VL-3B-Instruct | 31 | 4 | 5 | 1.65 / 2 |
| InternVL3-2B | 31 | 4 | 5 | 1.65 / 2 |

从总分看，两者完全一致。  
但这并不意味着两个模型能力完全相同。

真正有价值的是错误分布。

### 8.2 逐样本对比

逐样本比较结果如下：

| 对比结果 | 数量 |
|---|---:|
| Both correct | 28 |
| Qwen better | 4 |
| InternVL better | 4 |
| Both problematic | 4 |

说明：

1. 大多数简单或中等难度样本，两个模型都能正确完成；
2. 两个模型总分相同，但各自出错的位置不同；
3. 少数 hard cases 能揭示模型能力边界；
4. 模型对比不能只看平均分，必须看任务类型和错误类型。

### 8.3 Qwen 更好的地方

Qwen 在以下样本上优于 InternVL：

| image_id | 说明 |
|---|---|
| architecture_03 | Qwen 部分理解架构图流程，InternVL 判断错误 |
| chart_06 | Qwen 正确判断参数量最大模型，InternVL 误判 |
| table_04 | Qwen 正确读取 InternVL3.5-38B 的 Vision Encoder 和参数量 |
| table_05 | Qwen 正确判断 HumanEval 最高分模型 |

可以看出，Qwen 在本项目中相对更稳的是：

```text
表格理解
部分架构图理解
散点图参数量判断
结构化信息定位
```

### 8.4 InternVL 更好的地方

InternVL 在以下样本上优于 Qwen：

| image_id | 说明 |
|---|---|
| chart_03 | InternVL 正确读取单位和数值，Qwen 单位写错 |
| chart_04 | InternVL 部分识别 mobilevit，Qwen 判断为 resnet50 |
| OCR_03 | InternVL 正确提取论文标题中的 16x16 |
| ui_05 | InternVL 正确读取 VS Code 快捷键 Ctrl+O |

可以看出，InternVL 在本项目中相对更稳的是：

```text
部分 OCR 细节
UI 快捷键读取
论文标题信息提取
部分图表细节读取
```

### 8.5 两个模型共同困难的地方

两个模型都存在问题的样本包括：

| image_id | 问题 |
|---|---|
| scene_01 | 现实物体识别不够直接，回答加入不确定描述 |
| scene_02 | 中文书法 OCR 错误 |
| scene_07 | 电影海报标题识别不完整 |
| table_06 | 密集 benchmark 表格数值读取错误 |

这些共同错误说明，当前 VLM 在以下任务上仍然不稳定：

```text
中文书法 OCR
海报 / 艺术字体 OCR
密集表格行列定位
细粒度物体描述
```

---

## 9. Error Taxonomy

通过本项目，我发现 VLM 错误不能简单写成“答错了”，而应该拆成不同类型。

### 9.1 OCR Error

OCR Error 是最常见也最直观的错误。

典型案例：

```text
scene_02：中文书法“大音希声”识别失败
scene_07：电影海报标题识别不完整
OCR_03：Qwen 未提取论文标题中的 16x16
```

这说明 OCR 能力不是单一能力。普通文档 OCR、代码 OCR、论文标题 OCR、UI 小字号 OCR、中文书法 OCR、海报 OCR 的难度完全不同。

### 9.2 Chart Misinterpretation

图表理解错误通常不是模型完全没看懂图，而是：

```text
图例对应错
曲线位置判断错
横坐标定位错
单位读错
趋势理解不精确
```

典型案例：

```text
chart_04：复杂曲线图中 SNR=-4 dB 的最高模型误判
chart_06：散点图中参数量最大模型误判
```

### 9.3 Table Misreading

表格错误主要来自行列定位。

典型案例：

```text
table_06：两个模型都读错 MathVista mini 数值
table_05：InternVL 误判 HumanEval 最高分模型
table_04：InternVL 读错 Vision Encoder
```

这说明表格理解比普通 OCR 更难，因为模型不仅要读出文字，还要理解二维结构。

### 9.4 Architecture Misreading

架构图错误常常发生在局部流程和模块关系上。

典型案例：

```text
architecture_03：模型没有准确理解 Noised Latent 进入 DiT Block 前的步骤
```

这类错误说明模型可能识别了图中的元素，但对箭头、流程和模块关系的理解不够精确。

### 9.5 Hallucination

本项目中，两个模型在 no-answer 类问题上整体表现较好。

例如：

```text
architecture_06：图中没有训练数据集名称，模型没有乱猜
scene_04：仅凭建筑照片无法确定城市名称，模型没有编造
```

这说明 structured prompt 中加入“不确定就回答无法确定”的约束是有价值的。

---

## 10. Prompt Sensitivity Discussion

本项目没有系统开展 prompt sensitivity 实验。

这是一个有意识的取舍。

原因是：

1. 当前项目的主线是先完成 VLM evaluation 闭环；
2. 已经完成两个模型推理、人工评分和模型对比；
3. 大规模 prompt 对比会显著增加运行和整理成本；
4. 对当前阶段来说，错误分析和模型对比的价值高于机械尝试多个 prompt。

不过，从当前实验仍然可以得到一个初步观察：

```text
结构化 prompt 能改善回答格式和不确定性表达，
但不一定能显著提高事实正确性。
```

例如，`structured_zh` prompt 要求模型：

```text
不要猜测图中看不到的信息；
如果无法判断，请回答“图中无法确定”。
```

这对 no-answer 类问题有帮助。  
但对于复杂图表、密集表格、书法 OCR 等问题，即使使用结构化 prompt，模型仍然可能出错。

因此，后续如果继续做 prompt sensitivity，应该重点围绕 hard cases，而不是对全部样本机械测试。

建议后续只选 8–10 个样本进行轻量实验：

```text
chart_04
chart_06
OCR_03
scene_02
scene_07
table_06
ui_05
architecture_03
```

比较两类 prompt 即可：

```text
direct prompt
evidence-aware prompt
```

重点观察：

```text
是否减少幻觉？
是否更愿意承认不确定？
是否改善表格/图表定位？
是否只是让回答变长，而没有提高正确性？
```

---

## 11. VLMEvalKit Learning

在项目后期，我补充了解了 VLMEvalKit 正式评估流程。

我的理解是，VLMEvalKit 解决的是更正式、更规模化的 VLM benchmark 问题。

它的流程可以概括为：

```text
选择模型
→ 选择 benchmark
→ 加载数据
→ 调用模型推理
→ 后处理模型输出
→ 抽取最终答案
→ 计算指标
→ 保存结果
```

这和当前项目的手动评估形成对比：

| 维度 | 当前项目 | VLMEvalKit |
|---|---|---|
| 数据 | 自建 40 图像 / 40 问题 | 标准公开 benchmark |
| 模型接口 | 手写脚本 | 统一模型接口 |
| 答案评估 | 人工 0–2 分 | 自动指标 / 后处理 / LLM judge |
| 错误分析 | 详细 case study | 更偏大规模指标统计 |
| 适合阶段 | 学习、项目展示 | 正式评测、论文复现、leaderboard |

这一步让我明白：

```text
手动 benchmark 和正式评测工具不是对立关系。
```

手动评估适合理解模型为什么错；  
VLMEvalKit 适合大规模、标准化、可复现的模型比较。

对我当前阶段来说，最合理的路线是：

```text
先通过手动评估理解 VLM 错误模式，
再学习正式工具如何组织大规模 benchmark。
```

---

## 12. VLM Concepts Learned

通过本项目，我对 VLM 的核心概念有了更清晰的理解。

### 12.1 VLM 基本结构

典型 VLM 可以简化为：

```text
Image → Vision Encoder → Projector / Adapter → LLM → Answer
```

LLM 本身不能直接理解图片，所以图片需要先经过视觉编码器，变成视觉特征，再通过 projector / adapter 转成语言模型可以处理的 visual tokens。

### 12.2 Image Token 和 Visual Token Budget

图像进入 LLM 后，本质上会被表示成 image tokens。

这解释了为什么以下任务比较难：

```text
高分辨率文档
密集表格
小字号 UI
复杂图表
长文本截图
```

因为视觉 token 数量有限，如果细节没有被保留下来，模型就容易读错。

### 12.3 Grounding、Recognition、Reasoning 的区别

项目中一个重要收获是：

```text
看见了 ≠ 定位对了 ≠ 推理对了。
```

例如：

```text
模型可能看到表格，但读错行列；
模型可能看到标题，但没有提取出 16x16；
模型可能看到曲线，但误判某个横坐标位置的最高值。
```

因此 VLM evaluation 不能只看模型是否“像是理解了”，而要检查答案是否真正基于图像证据。

### 12.4 为什么 VLM 会幻觉

VLM 幻觉可能来自：

```text
LLM 语言先验太强
视觉信息不完整
prompt 没有限制
训练数据鼓励模型积极回答
```

本项目中的 no-answer 问题帮助我理解了：

```text
承认图中无法确定，本身也是一种能力。
```

---

## 13. Lessons Learned

### 13.1 VLM evaluation 不是跑 demo

项目开始时，我可能会以为 VLM evaluation 就是：

```text
找一些图片
问几个问题
看模型回答得怎么样
```

但真正做完后，我发现完整评估至少包括：

```text
测试集设计
问题设计
标准答案设计
推理脚本
输出记录
评分标准
人工评分
错误类型分析
模型对比
总结报告
```

这才是一个真正可展示的项目闭环。

### 13.2 Benchmark 的价值在于能力覆盖

普通猫狗图、风景图并不能充分测试 VLM。

更有价值的图片包括：

```text
论文图
图表
表格
UI 截图
代码截图
文档截图
复杂现实场景
领域相关图像
```

这些任务更接近真实应用，也更能暴露模型的能力边界。

### 13.3 总分不是全部

Qwen 和 InternVL 的平均分都是 1.65 / 2。  
如果只看总分，会觉得它们差不多。

但进一步分析后发现：

```text
Qwen 表格更稳；
InternVL OCR 和 UI 细节更稳；
两个模型都怕中文书法、海报标题和密集表格。
```

所以模型比较不能只看一个平均分，而要按任务类型和错误类型分析。

### 13.4 人工错误分析很重要

正式 benchmark 可以给出分数，但刚入门时，更重要的是知道模型为什么错。

本项目让我学会把错误拆成：

```text
OCR 错误
图表误判
表格误读
UI 误读
架构图误解
幻觉
过度泛化
推理错误
```

这种能力对后续读论文、做实验、写报告和做算法岗项目都有帮助。

---

## 14. Limitations

当前项目仍然有明显局限。

### 14.1 数据规模较小

当前只有：

```text
40 张图像
40 个问题
```

它适合学习和展示，但不能代表模型的通用能力。

### 14.2 每张图片只有一个问题

这限制了数据利用率。

同一张图其实可以设计多个问题，例如：

```text
OCR 问题
定位问题
推理问题
no-answer 问题
```

后续可以扩展成每张图 2–3 个问题。

### 14.3 Prompt 对比没有系统完成

本项目没有正式生成 `prompt_sensitivity.csv`。  
这不是核心缺失，但如果后续要让项目更完整，可以围绕 hard cases 做一个轻量 prompt sensitivity study。

### 14.4 领域图像还不够充分

当前项目中 CWT 时频图、混淆矩阵、t-SNE、故障诊断图等 domain-specific 图片还不够多。

如果要结合个人背景，后续可以增加：

```text
CWT 时频图
电机故障诊断混淆矩阵
t-SNE 特征图
模型轻量化对比图
噪声鲁棒性折线图
```

### 14.5 评分仍然带有人工主观性

虽然已经有 rubric，但 0/1/2 分评分仍然有一定主观性。

后续可以考虑：

```text
增加更细的评分规则
加入第二评分人
使用 LLM-as-a-judge 辅助检查
设计更多可自动匹配的短答案问题
```

---

## 15. Next Step

如果继续推进这个方向，我建议按下面路线走：

### 15.1 短期：完善当前 evaluation lab

```text
更新 README
补充 prompt sensitivity mini study
增加 10–20 个 hard cases
补充 domain-specific CWT 图像
整理 GitHub 项目结构
```

### 15.2 中期：接入更正式评估流程

```text
学习 VLMEvalKit 自定义数据集格式
尝试跑一个公开 mini benchmark
把当前 questions.csv 转成更标准的评估格式
增加自动评分脚本
```

### 15.3 长期：走向 Domain-specific VLM

后续可以从 VLM Evaluation 走向 VLM Fine-tuning。

例如：

```text
构造领域图像问答数据
选择 Qwen2.5-VL 或 InternVL 做 LoRA 微调
评估模型在 CWT / 故障诊断图上的表现
比较微调前后在 domain-specific 任务上的差异
```

这样就可以形成更接近算法岗的项目路线：

```text
VLM Evaluation
→ Error Analysis
→ Domain Data Construction
→ VLM Fine-tuning
→ Domain-specific VLM Evaluation
```

---

## 16. Resume / Portfolio Summary

这个项目可以总结为：

```text
Built a VLM evaluation lab to compare Qwen2.5-VL and InternVL3 on a self-constructed multimodal benchmark covering OCR, chart understanding, table understanding, UI screenshots, scientific figures, scene understanding, and hallucination-risk questions. Designed a 0–2 manual evaluation rubric, scored model outputs, categorized error types, and analyzed model-specific strengths and shared failure cases.
```

中文表述可以是：

```text
构建了一个小型 VLM 评估实验室，基于自建 40 图像 / 40 问题 benchmark，对 Qwen2.5-VL 和 InternVL3 进行多模态能力评估，覆盖 OCR、图表理解、表格理解、UI 截图、论文图、现实场景和幻觉风险任务。设计 0–2 分人工评分标准，完成模型输出评分、错误类型分析和双模型对比，分析不同 VLM 在细粒度视觉理解任务中的能力边界。
```

---

## 17. Final Conclusion

本项目最大的收获，不是简单跑通了两个 VLM，而是完整走通了一次多模态模型评估流程。

通过这个项目，我理解到：

```text
VLM 评估不是看模型会不会描述图片，
而是要系统判断它能否基于图像证据完成不同类型的视觉语言任务。
```

在这个过程中，我完成了：

```text
自建 benchmark
模型推理
人工评分
错误分析
模型对比
VLMEvalKit 流程学习
VLM 概念整理
项目报告
```

这让我对 VLM 的理解从“模型层面的概念”推进到了“项目层面的实践”。

最终，本项目为后续继续学习多模态模型提供了一个基础框架：

```text
先评估模型
再理解错误
再扩展数据
再尝试微调
最后走向领域多模态模型应用
```

这也是我接下来从 VLM 入门走向 VLM fine-tuning / domain-specific VLM 的基础。
