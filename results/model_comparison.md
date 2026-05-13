# 模型对比分析：Qwen2.5-VL vs InternVL3-2B

## 1. 文件目的

本文件基于两个模型的人工评分结果，比较 Qwen2.5-VL-3B-Instruct 与 InternVL3-2B 在本项目 40 个图像问答样本上的表现差异。

使用的评分文件：

```text
evaluation/manual_scores.csv
evaluation/manual_scores_internvl.csv
```

生成的逐样本对比表：

```text
results/model_comparison_table.csv
```

本次对比关注的不是简单判断“哪个模型更强”，而是分析两个模型在不同任务类型上的优势、短板和共性错误。

---

## 2. 总体结果

| 模型 | 样本数 | 2 分 | 1 分 | 0 分 | 平均分 |
|---|---:|---:|---:|---:|---:|
| Qwen2.5-VL-3B-Instruct | 40 | 31 | 4 | 5 | 1.65 / 2 |
| InternVL3-2B | 40 | 31 | 4 | 5 | 1.65 / 2 |

从总分看，两个模型在本 benchmark 上的总体表现非常接近：

```text
Qwen2.5-VL：1.65 / 2
InternVL3-2B：1.65 / 2
```

两者的得分分布也完全一致：

```text
2 分：31 条
1 分：4 条
0 分：5 条
```

因此，本轮实验不能简单得出“某一个模型明显更强”的结论。更有价值的地方在于：**两个模型虽然总分相同，但错误位置和能力侧重点不同。**

---

## 3. 逐样本胜负关系

| 对比结果 | 数量 |
|---|---:|
| Both correct | 28 |
| Both problematic | 4 |
| Qwen better | 4 |
| InternVL better | 4 |

其中：

- 两个模型都答对的样本有 28 条；
- 两个模型都存在问题的样本有 4 条；
- Qwen 明显优于 InternVL 的样本有 4 条；
- InternVL 明显优于 Qwen 的样本有 4 条。

这说明两者在多数简单或中等难度样本上表现一致，但在少数细节任务上会出现明显差异。

---

## 4. 按任务大类对比

| 任务大类 | 样本数 | Qwen 平均分 | InternVL 平均分 | InternVL - Qwen |
|---|---:|---:|---:|---:|
| OCR 文档 | 6 | 1.667 | 2.0 | 0.333 |
| UI 截图 | 5 | 1.6 | 2.0 | 0.4 |
| 图表 | 6 | 1.5 | 1.5 | 0.0 |
| 架构图 / 论文图 | 8 | 1.875 | 1.75 | -0.125 |
| 现实场景 / 海报 | 9 | 1.556 | 1.556 | 0.0 |
| 表格 | 6 | 1.667 | 1.167 | -0.5 |

初步观察：

- **OCR 文档类任务**：InternVL 表现更好，尤其是 `OCR_03` 中正确提取了论文标题里的 `16x16`，而 Qwen 没有提取成功。
- **UI 截图任务**：InternVL 表现更好，尤其是 `ui_05` 中正确读取了 VS Code 的 `Ctrl+O` 快捷键。
- **表格任务**：Qwen 明显更稳定，InternVL 在 `table_04`、`table_05`、`table_06` 中均出现不同程度的表格误读。
- **架构图 / 论文图任务**：Qwen 略好，InternVL 在 `architecture_03` 中对关键步骤判断错误。
- **图表任务**：两者平均分相同，但错误点不同。Qwen 在 `chart_04` 复杂曲线比较中失败，InternVL 在 `chart_06` 散点图最大参数量判断中失败。
- **现实场景 / 海报任务**：两者表现基本一致，中文书法和海报标题仍是共同难点。

---

## 5. Qwen 更好的案例

| image_id | skill_type | Qwen 分数 | InternVL 分数 | 差异说明 |
|---|---|---:|---:|---|
| architecture_03 | architecture_understanding | 1 | 0 | Qwen：识别到 Patchify，但把 Noised Latent 与 Embed 的关系说得不够准确；timestep 和 label 才是通过 Embed 输入。 InternVL：问题询问 Noised Latent 进入 DiT Block 前经过哪一步，expected_answer 为 Patchify，但模型回答 Linear and Reshape，关键步骤判断错误。 |
| chart_06 | scatter_plot_understanding | 2 | 0 | Qwen：正确识别参数量最大的模型为 swin。 InternVL：散点图中参数量最大的模型应为 swin，但模型误判为 mobilelevit_s。 |
| table_04 | table_understanding | 2 | 1 | Qwen：正确读取 InternVL3.5-38B 的 Vision Encoder 和总参数量。 InternVL：总参数量 38.4B 判断正确，但 Vision Encoder 应为 InternViT-6B，模型误读为 InternViT-300M。 |
| table_05 | table_comparison | 2 | 0 | Qwen：正确判断 HumanEval 行中最高分模型为 Claude 3.5 Sonnet，分数 92.0。 InternVL：HumanEval 最高分模型应为 Claude 3.5 Sonnet，但模型误判为 Llama 3 405B；虽然分数 92.0 相同，但关键模型名称错误。 |

这些样本说明 Qwen 在本项目中相对更擅长：

- 部分模型架构图的流程理解；
- 表格行列关系定位；
- benchmark 表格中的模型/指标对应关系；
- 散点图中参数量对比。

---

## 6. InternVL 更好的案例

| image_id | skill_type | Qwen 分数 | InternVL 分数 | 差异说明 |
|---|---|---:|---:|---|
| chart_03 | stacked_chart_understanding | 1 | 2 | InternVL：正确识别总能耗最高月份为 August，数值为 300 kWh。 Qwen：月份和总量判断正确，但单位写成 kvWh，存在轻微单位错误。 |
| chart_04 | chart_comparison | 0 | 1 | InternVL：模型回答 mobilelevit，基本接近 expected_answer 中的 mobilevit，但模型名称拼写不准确，因此记为部分正确。 Qwen：在 SNR=-4 dB 时将最高准确率模型误判为 resnet50，expected_answer 为 mobilevit。 |
| OCR_03 | academic_OCR | 0 | 2 | InternVL：正确从论文标题 An Image is Worth 16x16 Words 中提取出 patch 大小 16x16。 Qwen：虽然观察到标题中的 16x16，但最终回答图中无法确定，未提取出关键答案。 |
| ui_05 | UI_understanding | 0 | 2 | InternVL：正确读取 VS Code 中“打开文件”的快捷键为 Ctrl+O。 Qwen：将 VS Code 中打开文件快捷键 Ctrl+O 误读为 Ctrl+K。 |

这些样本说明 InternVL 在本项目中相对更擅长：

- 部分 OCR 细节提取；
- UI 截图中的快捷键读取；
- 简单数值和单位读取；
- 部分复杂曲线图中模型名称判断。

---

## 7. 两个模型都存在问题的案例

| image_id | skill_type | Qwen 分数 | InternVL 分数 | 差异说明 |
|---|---|---:|---:|---|
| scene_01 | object_recognition | 1 | 1 | InternVL：模型识别到这是杯子或容器，但加入 Harry Potter/Gryffindor 等无关细节，且没有明确回答红色保温杯或水杯。 Qwen：回答中提到可能是 water bottle，但同时加入 collectible item 等不确定描述，答案不够直接。 |
| scene_02 | scene_OCR | 0 | 0 | InternVL：将书法作品“大音希声”误读为“静佛音火”，中文书法 OCR 失败。 Qwen：将书法作品“大音希声”误读为“大青师朴”。 |
| scene_07 | scene_OCR | 1 | 1 | InternVL：只识别出 THE MOVIE，遗漏关键的 F1，电影名称不完整。 Qwen：只识别出 The Movie，遗漏关键的 F1，电影名称不完整。 |
| table_06 | table_understanding | 0 | 0 | InternVL：Qwen2.5-VL 72B 在 MathVista mini 上的得分应为 74.8，模型误读为 67.7。 Qwen：在 MathVista mini 行中读错 Qwen2.5-VL 72B 的得分，将 74.8 误读为 70.5。 |

这些样本值得重点关注，因为它们可能代表当前 VLM 的共性难点：

- `scene_02`：中文书法 OCR，两者都识别错误；
- `scene_07`：电影海报标题 OCR，两者都只识别出部分信息；
- `table_06`：密集 benchmark 表格数值读取，两者都读错；
- `scene_01`：现实物体识别中，两者都能大致识别容器/杯子，但回答不够直接；
- `architecture_03`：架构图局部流程理解，两者都没有完全答准；
- `chart_04`：复杂图表比较，两者都没有完全达到标准答案。

---

## 8. 错误类型对比

| 错误类型 | Qwen 数量 | InternVL 数量 |
|---|---:|---:|
| Architecture Misreading | 1 | 1 |
| Chart Misinterpretation | 1 | 1 |
| Number Error | 1 | 0 |
| OCR Error | 3 | 2 |
| Partially Correct | 1 | 2 |
| Table Misreading | 1 | 3 |
| UI Misreading | 1 | 0 |

可以看到：

- Qwen 的错误更多集中在 OCR、图表和 UI 细节读取；
- InternVL 的错误更多集中在表格误读；
- 两个模型都容易在中文书法、海报标题、密集表格和复杂视觉定位任务中出错。

---

## 9. 关键结论

### 9.1 总分相同，但能力侧重点不同

两个模型平均分都是 1.65 / 2，说明在这个小型 benchmark 上总体能力接近。

但从错误分布看：

```text
Qwen 更稳：表格理解、部分架构图理解、散点图判断
InternVL 更稳：OCR 细节、UI 快捷键读取、论文标题信息提取
```

因此，模型对比不能只看总分，而要看不同任务类型下的具体错误模式。

---

### 9.2 表格理解是 InternVL 的明显短板

InternVL 在表格类任务中的平均分为 1.167 / 2，低于 Qwen 的 1.667 / 2。

典型错误包括：

- `table_04`：Vision Encoder 读错；
- `table_05`：HumanEval 最高分模型判断错误；
- `table_06`：MathVista mini 数值读错。

这说明在密集表格、benchmark 表和多模型多指标对比中，InternVL3-2B 的行列定位不够稳定。

---

### 9.3 OCR 并不是单一能力

InternVL 在普通 OCR 和论文标题细节上表现更好，但两个模型都在中文书法和海报标题上出错。

这说明 OCR 能力需要进一步拆分：

```text
普通文档 OCR
代码截图 OCR
论文标题 OCR
UI 小字号 OCR
中文书法 OCR
海报 / 艺术字体 OCR
```

不能简单说“某模型 OCR 强”或“某模型 OCR 弱”。

---

### 9.4 共性错误更值得后续分析

两个模型都出错的样本比单模型错误更重要，因为它们可能代表当前 VLM 的共同困难点。

本轮中最值得保留为 hard cases 的样本包括：

```text
architecture_03
chart_04
scene_02
scene_07
table_06
```

这些样本可以作为后续 prompt 诊断、第三模型对比或 VLMEvalKit 学习时的重点案例。

---

## 10. 下一步建议

接下来建议：

1. 保留 `results/model_comparison_table.csv` 作为逐样本模型对比表；
2. 在最终报告中重点引用本文件的任务大类对比和代表性 case；
3. 不需要继续盲目扩大 prompt 实验，可以优先围绕 hard cases 做少量 prompt sensitivity；
4. 如果后续跑第三个模型，可以优先测试两个模型都失败的样本；
5. 如果要扩展数据集，应重点增加表格、复杂图表、书法 OCR、海报 OCR 和 UI 小字号文本样本。

---

## 11. 阶段性总结

本轮模型对比说明，Qwen2.5-VL-3B-Instruct 和 InternVL3-2B 在整体得分上接近，但能力结构不同。

Qwen 在表格理解和部分结构化视觉任务上更稳；InternVL 在部分 OCR 和 UI 细节读取上更好。两个模型共同暴露出的难点包括中文书法 OCR、海报标题 OCR、密集表格数值读取和复杂图表定位。

因此，这个 benchmark 的价值不在于得出一个简单排名，而在于帮助识别不同 VLM 的能力边界和错误类型。
