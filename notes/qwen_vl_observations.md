# Qwen2.5-VL Observations

## 1. Run Information

| Item | Value |
|---|---|
| Model | Qwen/Qwen2.5-VL-3B-Instruct |
| Number of images | 40 |
| Number of questions | 40 |
| Prompt mode | structured_zh |
| Output file | results/qwen_vl_40_images.csv |
| Successful outputs | 40 / 40 |
| Failed outputs | 0 / 40 |
| Average inference time | about 17.2 s / sample |

---

## 2. Overall Impression

初步观察 Qwen2.5-VL-3B-Instruct 在本 benchmark 上的表现：

- OCR：整体表现较好，能够识别清晰截图、代码截图、论文摘要和部分中英文混排文本；但在少数细节 OCR 上仍不稳定，例如论文标题中的 “16x16” 被判断为“图中无法确定”，中文书法作品和电影海报标题也出现了明显误读。
- 图表理解：对简单柱状图、折线图、散点图的最高值、最大参数量等问题表现较好；但在复杂曲线对比中存在误判，例如 SNR=-4 dB 时最高准确率模型判断错误。
- 表格理解：对结构清晰、数字清楚的表格表现较好，能够读取模型名称、准确率、Vision Encoder 和参数量等信息；但在密集 benchmark 表格中出现了数值读取错误，例如 MathVista mini 中 Qwen2.5-VL 72B 的得分被误读。
- 架构图理解：整体表现较强。对 BERT、CLIP、MAE、InternVL、Swin Transformer 等架构图中的模块、任务标签和流程关系能够较准确地识别；但个别回答会把相邻模块关系解释得稍微过度，例如将 Noised Latent 的处理过程描述得比图中问题本身更复杂。
- UI 截图理解：对 GitHub、Hugging Face、PyCharm 等界面截图整体表现较好，能够识别昵称、模型名称和快捷键；但在 VS Code 界面中出现了快捷键误读，说明界面类 OCR 仍需要人工核查。
- 现实场景理解：对常见物体、屏幕数量、电影系列、水果托盘颜色等问题表现较好；但在中文书法、海报标题等场景 OCR 中容易出错。
- 空间关系 / 计数：目前样本数量较少，但已有样本中表现较稳定，能够正确判断屏幕数量和门把手是否可见。
- CWT / 领域图像理解：本轮 40 个问题中暂未明显包含 CWT 时频图类样本，因此该能力还没有被充分测试。后续如果要体现个人项目特色，应补充 CWT、混淆矩阵、t-SNE、故障诊断实验图等样本。
- 幻觉风险：在明确要求“图中无法确定”的问题上，模型表现较好，例如能够承认建筑照片无法确定城市名称、架构图中没有给出训练数据集名称。但在某些 OCR/细节读取任务中，模型会给出看似合理但错误的答案，因此仍需要通过 expected_answer 和人工评分进行核查。

总体来看，Qwen2.5-VL-3B 在“清晰文本 + 结构化图表 + 标准表格 + 常见架构图”上表现较强；主要短板集中在精确细节读取、复杂图表对比、中文艺术字体 OCR、海报标题 OCR 和密集 benchmark 表格数值读取。

---

## 3. Five Good Cases

| Case | image_id | skill_type | Why it is good |
|---:|---|---|---|
| 1 | architecture_01 | scientific_figure | 模型准确识别出 BERT 预训练部分的两个顶部任务标签 NSP 和 Mask LM，回答与 expected_answer 完全一致，说明其对经典模型结构图和图中文字标签有较好的理解能力。 |
| 2 | architecture_04 | architecture_understanding | 模型准确指出 InternVL3.5-Flash 相比 InternVL3.5 额外加入 Visual Resolution Router（ViR），并能解释该模块用于动态选择压缩率，体现出较好的架构图信息读取能力。 |
| 3 | chart_01 | chart_understanding | 模型正确识别出降雨量最高的月份是 June，数值为 180 mm。该样本说明模型对简单柱状图的最高值读取和坐标轴数值理解较稳定。 |
| 4 | table_02 | table_comparison | 模型正确判断 Clean 数据集上测试准确率最高的模型是 MobileViT-S，准确率为 100.00%。回答能够结合表格中的模型名称和测试准确率列进行比较。 |
| 5 | ui_03 | UI_understanding | 模型正确读取 Hugging Face 页面右侧 Trending 列表第一位模型名称 SulphurAI/Sulphur-2-base，说明其对网页截图中的局部信息定位和 UI 文本识别能力较好。 |

---

## 4. Five Problematic Cases

| Case | image_id | skill_type | Problem Type | Why it is problematic |
|---:|---|---|---|---|
| 1 | chart_04 | chart_comparison | Chart Misinterpretation | expected_answer 是 mobilevit 在 SNR=-4 dB 时准确率最高，但模型回答为 resnet50。该错误说明模型在多曲线图中可能会误判曲线位置或图例对应关系。 |
| 2 | OCR_03 | academic_OCR | OCR Error / Reasoning Error | 问题询问论文标题中提到的 image patch 大小，expected_answer 为 16x16；模型虽然观察到标题 “An Image is Worth 16x16 Words”，但最终却回答“图中无法确定”。这是典型的“看到了关键信息但没有转化为正确答案”的错误。 |
| 3 | scene_02 | scene_OCR | OCR Error | expected_answer 是书法作品“大音希声”，但模型回答“大青师朴”。该样本说明模型对艺术字体、书法字体或低清晰度中文 OCR 的能力较弱。 |
| 4 | table_06 | table_understanding | Table Misreading / Number Error | expected_answer 是 Qwen2.5-VL 72B 在 MathVista mini 上得分 74.8，但模型回答 70.5。该错误说明模型在密集 benchmark 表格中可能会读错行列交叉位置。 |
| 5 | ui_05 | UI_understanding | OCR Error / UI Misreading | expected_answer 是 VS Code 中“打开文件”的快捷键 Ctrl+O，但模型回答 Ctrl+K。该错误说明模型在软件界面截图中对快捷键细节的读取仍不稳定。 |

---

## 5. Error Types Observed

> 说明：下表是基于 40 条结果的第一轮人工观察，不是严格人工评分后的最终统计。后续可以在 `manual_scores.csv` 中进一步精确标注。

| Error Type | Count | Notes |
|---|---:|---|
| OCR Error | 4 | 主要出现在论文标题细节、中文书法、电影海报标题和 VS Code 快捷键读取中；代表样本包括 OCR_03、scene_02、scene_07、ui_05。 |
| Number Error | 2 | 主要出现在精确数值读取或单位细节中；代表样本包括 table_06，chart_03 中也出现了单位拼写不规范。 |
| Chart Misinterpretation | 1 | chart_04 将 SNR=-4 dB 下最高准确率模型从 mobilevit 误判为 resnet50。 |
| Table Misreading | 1 | table_06 在密集表格中读错 MathVista mini 对应数值。 |
| Spatial Error | 0 | 当前空间关系样本较少，已有样本中暂未观察到明显错误。 |
| Counting Error | 0 | 当前计数样本较少，scene_03 正确判断有两块屏幕。 |
| Hallucination | 1 | 本轮明显幻觉较少，模型在 no_answer 类问题上总体较谨慎；但个别回答存在过度解释或给出看似合理但错误的细节。 |
| Over-general Answer | 1 | 少数回答推理部分偏模板化，尤其在图表和表格题中会重复“比较柱子高度/查看表格”等泛化描述，但最终答案多数仍可用。 |
| Format Error | 0 | 在 structured_zh prompt 下，模型基本都能按照 Observation / Reasoning / Final Answer 的格式输出。 |

---

## 6. Notes for Next Step

后续需要重点关注：

1. 哪些任务最容易出错？

   初步来看，最容易出错的不是普通图像描述，而是精确细节读取类任务，包括复杂曲线图对比、密集表格数值读取、中文书法 OCR、海报标题 OCR 和软件快捷键 OCR。

2. 哪些问题的 expected_answer 需要改得更明确？

   部分 expected_answer 可以进一步写得更标准，例如 chart/table 类问题最好明确“只需要回答模型名称和数值”；no_answer 类问题最好明确“图中没有直接证据，不应猜测”。

3. 哪些图片可能不适合作为 benchmark？

   如果图片文字过小、截图分辨率低、书法字体过于艺术化，模型错误可能更多来自图像质量而不是模型能力本身。此类图片可以保留为 hard case，但需要在 notes 中说明其难度来源。

4. 是否需要给部分图片增加第二个问题？

   建议只给高价值图片增加第二个问题，而不是所有图片都加。例如 chart_04、table_06、OCR_03、ui_05 这类出错样本，可以增加一个更简单的问题，用来判断模型到底是“没看清图像”，还是“看到了但推理/定位错了”。

5. 是否需要进一步测试英文 Prompt？

   暂时不建议大规模做中英文 prompt 对比。更高价值的做法是先选 8 个典型样本，比较 direct prompt 和 evidence-aware prompt，观察模型是否会减少幻觉、是否更愿意承认“图中无法确定”。英文 prompt 对比可以作为 optional experiment。

---

## 7. Interim Conclusion

本轮实验说明，Qwen2.5-VL-3B-Instruct 已经能够较稳定地完成多类 VLM 基础任务，包括架构图理解、简单图表读取、表格比较、OCR、UI 截图理解和常见场景识别。模型的主要问题不在于完全看不懂图片，而在于面对复杂图表、密集表格、艺术化中文文字和软件快捷键等细节任务时，容易出现局部误读或错误定位。

因此，下一阶段不应盲目扩大数据量或机械尝试大量 prompt，而应围绕本轮发现的 bad cases，开展更有针对性的人工评分、错误分类和少量 prompt 诊断。
