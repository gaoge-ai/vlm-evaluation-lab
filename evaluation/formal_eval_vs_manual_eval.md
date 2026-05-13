# 手动评估 vs VLMEvalKit 正式评估

## 1. 文件目的

本文件用于比较当前 `vlm-evaluation-lab` 项目的手动评估方式和 VLMEvalKit 代表的正式 VLM benchmark 评估方式。

核心问题是：

```text
我现在做的手动 benchmark 有什么价值？
它和正式评估工具有什么区别？
如果后续想升级成更正式的评估流程，需要补什么？
```

---

## 2. 总体对比

| 维度 | 当前手动评估 | VLMEvalKit 正式评估 |
|---|---|---|
| 主要目的 | 学习 VLM 评估流程，分析模型错误 | 大规模、可复现地评估多个 VLM |
| 数据规模 | 小规模，当前 40 张图像 / 40 个问题 | 通常是公开 benchmark，样本更多 |
| 数据来源 | 自建数据集 | 标准公开数据集或已适配 benchmark |
| 模型调用 | 自己写脚本，如 `run_qwen_vl.py` | 统一模型接口 |
| Prompt 控制 | 自己手动设计 | benchmark / 模型接口中统一管理 |
| 输出记录 | 手动保存 CSV | 框架自动保存结果 |
| 答案抽取 | 人工查看 `model_answer` | 规则匹配或 LLM-based extraction |
| 评分方式 | 人工 0–2 分评分 | 自动指标，如 accuracy / exact match / judge score |
| 错误分析 | 人工总结 case | 通常偏指标统计，case 需要额外分析 |
| 可复现性 | 中等，依赖自己记录清楚 | 更高，流程和接口标准化 |
| 适合阶段 | 入门、项目展示、理解 bad case | 论文复现、leaderboard、大规模模型对比 |

---

## 3. 当前项目文件与正式评估流程的对应关系

| 当前项目文件 | 在正式评估中的对应角色 |
|---|---|
| `data/images/` | benchmark 图像数据 |
| `data/questions.csv` | benchmark 标注文件 |
| `scripts/run_qwen_vl.py` | Qwen 模型推理接口 |
| `scripts/run_internvl.py` | InternVL 模型推理接口 |
| `results/qwen_vl_40_images.csv` | Qwen 原始预测结果 |
| `results/internvl3_2b_40_images.csv` | InternVL 原始预测结果 |
| `evaluation/rubric.md` | 评分规则 |
| `evaluation/manual_scores.csv` | Qwen 人工评分结果 |
| `evaluation/manual_scores_internvl.csv` | InternVL 人工评分结果 |
| `results/model_comparison_table.csv` | 多模型对比结果表 |
| `analysis/error_cases.md` | 错误案例分析 |
| `analysis/model_comparison.md` | 模型对比分析 |

可以看到，我现在其实已经手动实现了一个小型评估框架的核心流程。

区别是：

```text
VLMEvalKit 会把这些流程标准化、自动化、规模化。
```

---

## 4. 手动评估的优势

当前手动评估虽然不够“正式”，但它对学习非常有价值。

### 4.1 更容易理解模型错误

手动看每条输出时，可以发现很多自动指标看不到的问题，例如：

```text
模型看到了文字，但没有转化成答案
回答看起来合理，但其实读错了表格
模型没有幻觉，但回答过于保守
两个模型总分相同，但错误类型不同
```

这些观察对理解 VLM 非常重要。

### 4.2 适合做 case study

本项目中的典型 case 包括：

```text
中文书法 OCR 错误
复杂折线图误判
密集表格数值读错
VS Code 快捷键误读
论文标题 16x16 提取失败
```

这些样本不只是“错了”，还能帮助分析：

```text
OCR 难在哪里
图表理解难在哪里
表格行列定位为什么容易错
VLM 为什么会出现局部误读
```

### 4.3 适合项目展示

对于 GitHub portfolio、实习简历或套磁来说，手动 benchmark 可以展示：

```text
我能构造数据集
我能跑模型
我能设计评分标准
我能分析错误类型
我能比较两个模型
```

这比单纯跑一个公开 benchmark 更能体现个人理解。

---

## 5. 手动评估的局限

### 5.1 样本数量少

当前只有：

```text
40 张图像
40 个问题
```

这个规模适合学习和 case study，但不能代表模型的通用能力。

### 5.2 评分存在主观性

虽然已经设计了 0–2 分 rubric，但人工评分仍可能受主观判断影响。

例如：

```text
模型名称拼写错误是否给 1 分
单位写错是否给 1 分
答案部分正确但解释错误如何评分
```

这些都需要更严格的一致性标准。

### 5.3 缺少自动化指标

当前主要依靠人工评分，不能像正式 benchmark 那样自动计算大规模 accuracy。

如果样本扩展到几千条，人工评分成本会非常高。

### 5.4 可复现性不如正式工具

虽然当前项目已经保存了脚本和 CSV，但仍然依赖本地环境、模型版本和个人评分标准。

正式工具通常会更重视：

```text
统一数据下载
统一模型接口
统一后处理规则
统一输出格式
统一评估指标
```

---

## 6. VLMEvalKit 的优势

VLMEvalKit 的优势可以总结为：

```text
统一、自动、可复现、可扩展。
```

具体包括：

1. 用统一入口运行多个模型；
2. 用统一方式加载多个 benchmark；
3. 自动保存推理结果；
4. 自动做答案抽取和后处理；
5. 自动计算指标；
6. 支持公开 benchmark 和 leaderboard 风格结果；
7. 适合多模型、多数据集、大规模评测。

---

## 7. VLMEvalKit 的局限

VLMEvalKit 也不是万能的。

对我当前阶段来说，它可能有以下问题：

1. 环境配置和依赖较重；
2. 对自建小数据集不一定马上方便；
3. 自动指标无法替代人工错误分析；
4. 部分开放问答任务仍然需要 LLM judge 或人工检查；
5. 如果只想理解模型为什么错，直接看 case 反而更有效。

所以当前项目不需要一开始就完全依赖 VLMEvalKit。

更合理的路线是：

```text
先完成手动 benchmark 闭环
再学习正式评估流程
最后考虑把自建数据集适配到正式工具中
```

---

## 8. 如果要把当前项目升级成正式评估，需要补什么？

### 8.1 数据层面

```text
增加样本数量
每张图片增加多个问题
统一图片来源和命名
检查版权和隐私风险
补充更多 domain-specific 图片
```

### 8.2 标注层面

```text
让 expected_answer 更标准化
减少主观答案
增加 answer_type
为选择题设置选项
设计可自动匹配的答案格式
```

### 8.3 推理层面

```text
统一模型接口
统一 prompt 模板
记录模型版本和参数
记录推理时间和硬件环境
```

### 8.4 评估层面

```text
把 0–2 分评分规则进一步标准化
增加自动评分脚本
统计不同 skill_type 的准确率
输出模型对比汇总表
```

### 8.5 工具层面

```text
研究 VLMEvalKit 自定义 dataset 接口
尝试把 questions.csv 转成正式 benchmark 格式
尝试用 VLMEvalKit 跑一个 mini benchmark
```

---

## 9. 当前项目应该怎么定位？

当前项目不应该定位成：

```text
一个正式 leaderboard 级别 benchmark
```

而应该定位成：

```text
一个面向学习和项目展示的小型 VLM evaluation lab
```

它的价值在于完整走通了：

```text
数据构造
→ 模型推理
→ 人工评分
→ 错误分析
→ 模型对比
→ 项目报告
```

这正是 VLM 项目入门阶段最重要的闭环。

---

## 10. 阶段性结论

手动评估和 VLMEvalKit 正式评估不是对立关系。

它们的关系更像是：

```text
手动评估：帮助我理解模型能力和错误模式
正式评估：帮助我规模化、标准化、复现评估流程
```

对我当前阶段来说，最合理的策略是：

1. 保留当前手动 benchmark，继续做好 case study；
2. 理解 VLMEvalKit 的正式评估流程；
3. 暂时不花大量时间强行部署复杂 benchmark；
4. 后续如果需要更正式的结果，再尝试接入 VLMEvalKit 或类似工具。

最终目标不是“为了用工具而用工具”，而是理解：

```text
一个可靠的 VLM 评估系统应该如何组织。
```
