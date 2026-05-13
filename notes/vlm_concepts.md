# VLM 核心概念笔记

## 1. 文件目的

本文件用于整理 `vlm-evaluation-lab` 项目中需要掌握的 VLM 基础概念。

这份笔记不是系统课程笔记，而是围绕本项目中真实遇到的问题来理解 VLM：

```text
为什么模型能看图？
为什么它能读文字、看表格、看图表？
为什么它有时候会幻觉？
为什么 Qwen 和 InternVL 总分一样，但错误类型不同？
为什么 OCR、表格、图表、空间关系难度不一样？
```

本文件的目标是帮助我从“会跑模型”进一步过渡到“知道模型为什么会这样表现”。

---

## 2. VLM 的基本结构

一个典型 VLM 可以简化理解为：

```text
Image → Vision Encoder → Projector / Adapter → LLM → Answer
```

更具体一点：

```text
图像
  ↓
视觉编码器 Vision Encoder
  ↓
视觉特征 Visual Features
  ↓
投影层 / 适配器 Projector / Adapter
  ↓
图像 token / visual tokens
  ↓
大语言模型 LLM
  ↓
文本回答 Answer
```

可以画成：

```text
            ┌────────────────────┐
            │       Image         │
            └─────────┬──────────┘
                      ↓
            ┌────────────────────┐
            │   Vision Encoder    │
            │  ViT / CLIP / etc.  │
            └─────────┬──────────┘
                      ↓
            ┌────────────────────┐
            │ Visual Features     │
            └─────────┬──────────┘
                      ↓
            ┌────────────────────┐
            │ Projector / Adapter │
            └─────────┬──────────┘
                      ↓
            ┌────────────────────┐
            │   Image Tokens      │
            └─────────┬──────────┘
                      ↓
Text Prompt ───────→  LLM  ───────→ Answer
```

核心理解：

```text
VLM 并不是让 LLM 直接看图片，而是先把图像转成 LLM 能处理的 token / embedding。
```

---

## 3. 为什么 VLM 需要 Vision Encoder？

LLM 本质上只能处理文本 token。  
图片不是文本，所以不能直接输入 LLM。

Vision Encoder 的作用是：

```text
把图像转换成一组视觉特征。
```

这些视觉特征会包含：

```text
物体信息
纹理信息
空间布局
局部区域特征
文字区域特征
图表结构信息
```

常见 Vision Encoder 包括：

```text
ViT
CLIP Vision Encoder
ConvNeXt
Swin Transformer
InternViT
```

在本项目中，模型能回答“图中有什么”“表格里哪个值最大”“截图中是什么快捷键”，前提都是 Vision Encoder 先把图像变成可供后续模型理解的视觉表示。

---

## 4. ViT 和 CNN 的核心差异

### CNN

CNN 更强调局部卷积和局部模式提取。

特点：

```text
天然适合提取边缘、纹理、局部形状
具有局部归纳偏置
计算方式偏局部
```

### ViT

ViT 会把图像切成 patch，然后把 patch 当作 token 输入 Transformer。

特点：

```text
把图片变成 patch tokens
通过 self-attention 建模全局关系
更适合和 LLM 的 token 思路对接
```

简化理解：

```text
CNN 更像“局部扫描图片”
ViT 更像“把图片切成很多视觉词，然后做全局关系建模”
```

这也是为什么现代 VLM 中经常使用 ViT / CLIP / InternViT 作为视觉编码器。

---

## 5. CLIP 为什么重要？

CLIP 的核心思想是：

```text
让图像和文本在同一个语义空间中对齐。
```

它通过大量图文对进行 contrastive learning，让模型学会：

```text
这张图和这句话应该接近
这张图和无关句子应该远离
```

CLIP 对 VLM 的意义在于：

```text
它让图像特征具备了语言语义。
```

早期很多 VLM 都会使用 CLIP Vision Encoder，因为它已经学到了图像和文本之间的基础对应关系。

可以简单理解：

```text
CLIP 是 VLM 图文对齐能力的重要基础。
```

---

## 6. Projector / Adapter 是什么？

Vision Encoder 输出的是视觉特征，但 LLM 不能直接理解这些视觉特征。

Projector / Adapter 的作用是：

```text
把视觉特征映射到 LLM 能理解的 embedding 空间。
```

也就是说，它是图像和语言之间的“翻译器”。

可以类比为：

```text
Vision Encoder：负责看图
Projector / Adapter：负责把视觉信息翻译成 LLM 能读的形式
LLM：负责结合问题生成答案
```

如果没有 Projector / Adapter，视觉特征和语言模型之间就无法顺利对接。

---

## 7. Image Token 是什么？

Image Token / Visual Token 可以理解为：

```text
图像被编码后形成的一组“视觉 token”。
```

在 LLM 看来，这些 image tokens 和文本 tokens 会被放在一起处理。

例如：

```text
[image tokens] + [text prompt tokens] → LLM → answer
```

这就解释了为什么高分辨率图片、长文档截图、密集表格会更难：

```text
图像越复杂，需要表达的信息越多；
视觉 token 数量有限；
如果重要细节没有被充分保留，模型就可能看错。
```

---

## 8. Visual Token Budget 是什么？

Visual Token Budget 指的是：

```text
模型能够用于表示一张图片的视觉 token 数量。
```

这个概念非常重要。

如果一张图片很简单，比如一个苹果，少量 visual tokens 就够了。

但如果图片是：

```text
高分辨率论文截图
密集表格
复杂图表
多行代码
UI 界面
文档扫描件
```

那么模型需要保留很多细节。

如果 visual token budget 不够，可能出现：

```text
小字看不清
表格行列错位
图例对应错误
快捷键读错
标题细节遗漏
```

这也能解释本项目中的一些错误：

```text
table_06：密集表格数值读错
ui_05：快捷键误读
OCR_03：论文标题细节没有转化为答案
chart_04：复杂曲线图判断错误
```

---

## 9. Visual Instruction Tuning 是什么？

Visual Instruction Tuning 可以理解为：

```text
教模型根据图像和人类指令完成任务。
```

仅有图文对齐还不够，因为模型不仅要“知道图里有什么”，还要会回答人的问题。

Visual Instruction Tuning 通常会训练模型完成：

```text
图像问答
图像描述
OCR 问答
图表问答
多轮对话
复杂推理
拒绝无法判断的问题
```

这就是为什么现代 VLM 能听懂类似下面的问题：

```text
请比较这张图中哪个模型准确率最高
请读取表格中某一行某一列的数值
请判断图中是否能确定城市名称
```

简单说：

```text
CLIP-style learning 让模型学会图文对齐；
Visual Instruction Tuning 让模型学会听人话、按指令回答。
```

---

## 10. Grounding、Recognition、Reasoning 的区别

这三个概念很容易混在一起，但对 VLM 评估非常重要。

### 10.1 Recognition：识别

指模型能不能看出图中有什么。

例子：

```text
图中有两块屏幕
图中是 GitHub 页面
图中有一个表格
```

### 10.2 Grounding：定位 / 依据

指模型的回答是否能在图像中找到明确依据。

例子：

```text
模型说快捷键是 Ctrl+O，那么图中对应位置是否真的写着 Ctrl+O？
模型说最高值是 June，那么图表中 June 的柱子是否最高？
```

### 10.3 Reasoning：推理

指模型是否能基于图像信息进一步比较、判断或归纳。

例子：

```text
比较多条曲线在 SNR=-4 dB 时谁最高
根据表格判断 HumanEval 最高分模型是谁
根据架构图判断某个模块前后关系
```

重要理解：

```text
看见了 ≠ 定位对了 ≠ 推理对了
```

本项目中很多错误不是模型完全没看见，而是：

```text
看到了图，但定位错了；
读到了文字，但没有抽取为答案；
识别了表格，但行列对应错了。
```

---

## 11. 为什么 VLM 会幻觉？

VLM hallucination 指模型生成了图中没有的信息。

可能原因包括：

### 11.1 LLM 的语言先验太强

LLM 本身很擅长根据上下文补全合理答案。  
但视觉信息不足时，它可能会根据常识猜。

例如：

```text
看到一栋建筑，就猜城市名称
看到论文图，就猜数据集名称
```

### 11.2 视觉信息没有被充分编码

如果图片中细节太小、太密集或太模糊，视觉编码器可能没有保留足够信息。

于是 LLM 只能根据语言先验补全。

### 11.3 Prompt 没有约束模型

如果 prompt 没有明确要求“不要猜测图中看不到的信息”，模型更容易给出看似合理但无依据的回答。

### 11.4 训练数据中的回答习惯

很多训练样本鼓励模型积极回答，而不是承认不知道。  
所以模型可能更倾向于输出一个答案，而不是说“无法确定”。

在本项目中，structured_zh prompt 加入了：

```text
如果图中无法判断，请明确回答“图中无法确定”。
```

这对 no-answer 类问题有帮助。

---

## 12. 为什么 OCR 难？

OCR 对 VLM 来说不只是“看见文字”。

它还涉及：

```text
定位文字区域
识别字符
保持字符顺序
理解上下文
把文字转化成答案
```

不同 OCR 难度差异很大：

| OCR 类型 | 难度 | 原因 |
|---|---|---|
| 普通文档 OCR | 较低 | 字体清晰、排版规整 |
| 代码截图 OCR | 中等 | 符号、下划线、大小写容易错 |
| UI 小字号 OCR | 中等偏高 | 字体小、局部区域复杂 |
| 论文标题 OCR | 中等 | 需要抓住关键短语 |
| 海报 OCR | 高 | 字体艺术化、背景复杂 |
| 中文书法 OCR | 很高 | 字形变形大，不符合标准字体 |

本项目中的典型错误：

```text
scene_02：中文书法“大音希声”识别错误
scene_07：电影海报标题只识别出 The Movie，遗漏 F1
ui_05：Qwen 将 Ctrl+O 误读为 Ctrl+K
OCR_03：Qwen 没有提取出标题中的 16x16
```

---

## 13. 为什么图表理解难？

图表理解不是简单 OCR。

它通常需要同时完成：

```text
读取坐标轴
理解单位
识别图例
定位曲线或柱子
比较数值大小
理解趋势
```

例如：

```text
哪个月份最高？
哪条曲线在 SNR=-4 dB 时最高？
哪个模型平均准确率最高？
```

图表错误常见原因：

```text
图例和曲线对应错
横坐标位置定位错
纵坐标数值估计错
单位读错
趋势理解过于粗略
```

本项目中的典型错误：

```text
chart_04：Qwen 在多曲线图中误判 SNR=-4 dB 下最高模型
chart_06：InternVL 在散点图中误判参数量最大的模型
chart_03：Qwen 单位写错为 kvWh
```

---

## 14. 为什么表格理解难？

表格理解的难点在于：

```text
不仅要读文字，还要定位行列关系。
```

模型需要知道：

```text
目标行是哪一行
目标列是哪一列
交叉单元格是什么值
是否需要比较多个单元格
```

密集表格尤其难，因为：

```text
行列多
数字密集
字号小
相邻单元格很接近
模型容易错位读取
```

本项目中的典型错误：

```text
table_06：Qwen 和 InternVL 都读错 MathVista mini 数值
table_05：InternVL 误判 HumanEval 最高分模型
table_04：InternVL 读错 Vision Encoder
```

这说明表格理解比普通 OCR 更复杂：

```text
OCR 只需要读出文字；
Table Understanding 还需要理解二维结构。
```

---

## 15. 为什么 UI 截图理解难？

UI 截图通常包含：

```text
按钮
菜单
快捷键
图标
多个区域
小字号文字
层级结构
```

模型需要先理解界面布局，再定位具体问题要求的区域。

常见错误：

```text
读错快捷键
读错按钮名称
混淆不同区域的文本
忽略局部小字
```

本项目中：

```text
Qwen 在 ui_05 中把 Ctrl+O 误读为 Ctrl+K
InternVL 在 ui_05 中正确读出 Ctrl+O
```

这说明 UI 任务往往很依赖细节 OCR 和局部定位能力。

---

## 16. 为什么空间关系和计数难？

空间关系和计数看似简单，但对 VLM 并不总是容易。

### 16.1 空间关系

需要判断：

```text
左 / 右
上 / 下
前 / 后
旁边
里面 / 外面
遮挡关系
```

如果图片中物体重叠、视角复杂或局部模糊，模型容易判断错。

### 16.2 计数

需要完成：

```text
检测所有目标
避免重复计数
避免漏掉被遮挡目标
区分相似物体
```

本项目中的计数样本较少，例如：

```text
scene_03：两块屏幕
```

模型表现较好，但样本量不足，不能说明模型计数能力整体很强。

后续如果扩展数据集，可以增加更多 counting / spatial reasoning 样本。

---

## 17. 为什么 Qwen 和 InternVL 总分相同，但错误不同？

在本项目中：

```text
Qwen2.5-VL 平均分：1.65 / 2
InternVL3-2B 平均分：1.65 / 2
```

总分相同，但错误分布不同。

这说明：

```text
模型总分不能完全代表能力结构。
```

Qwen 相对更稳的地方：

```text
表格理解
部分架构图理解
散点图参数量判断
```

InternVL 相对更稳的地方：

```text
部分 OCR 细节
UI 快捷键读取
论文标题中的 16x16 提取
```

共同难点：

```text
中文书法 OCR
海报标题 OCR
密集表格数值读取
复杂图表定位
```

这就是为什么模型评估不能只看平均分，而要按任务类型和错误类型分析。

---

## 18. Prompt Sensitivity 是什么？

Prompt Sensitivity 指：

```text
同一个模型、同一张图、同一个问题，在不同 prompt 下可能输出不同答案。
```

例如：

```text
直接问：这张图中哪个模型最高？
约束问：请只基于图像可见信息回答，如果无法判断请说无法确定。
结构化问：Observation / Reasoning / Final Answer。
```

Prompt 可能影响：

```text
回答格式
回答长度
是否承认不确定
是否减少幻觉
是否更认真做推理
```

但要注意：

```text
结构化 prompt 不一定提高事实正确性。
```

它可能只是让回答更长、更像推理，但最终答案仍然可能错误。

本项目没有系统做 prompt 对比实验，但 structured_zh prompt 对 no-answer 问题有帮助，因为它明确要求不要猜测图中看不到的信息。

---

## 19. Generation-based Evaluation 是什么？

VLM 通常输出自然语言，而不是固定类别。

这就带来评估问题：

```text
模型回答很长，怎么判断它对不对？
Final Answer 在哪里？
同义表达算不算正确？
数字单位错误算几分？
```

这就是 generation-based evaluation 的难点。

正式工具如 VLMEvalKit 通常需要：

```text
答案抽取
后处理
规则匹配
LLM judge
指标计算
```

而本项目使用人工 0–2 分评分，是一种小规模但更细致的方式。

---

## 20. VLM 常见能力 vs 常见错误

| 能力类型 | 任务例子 | 常见错误 |
|---|---|---|
| OCR | 读取标题、代码、文档、UI 文本 | 读错字、漏字、小字号识别失败 |
| Chart Understanding | 判断最高值、趋势、曲线比较 | 图例错配、坐标读错、趋势误判 |
| Table Understanding | 读取某行某列、比较指标 | 行列错位、相邻单元格误读 |
| Scientific Figure | 理解模型架构图、流程图 | 模块关系误判、过度解释 |
| UI Understanding | 读取按钮、快捷键、网页信息 | 局部文字误读、界面区域混淆 |
| Object Recognition | 识别物体和场景 | 物体误识别、加入无关细节 |
| Counting | 数屏幕、物体数量 | 漏数、重复计数 |
| Spatial Reasoning | 判断左右、旁边、包含关系 | 方向错误、遮挡关系错误 |
| Hallucination Control | 判断图中无法确定的问题 | 编造城市、数据集、背景信息 |
| Reasoning | 基于图像做比较和归纳 | 看见了但推理错、结论不支持 |

---

## 21. 项目中最重要的概念收获

通过这两周项目，我对 VLM 有几个关键理解：

### 21.1 VLM 评估不是只看“回答像不像”

模型回答很流畅，不代表它看对了图。

必须检查：

```text
答案是否来自图像
数字是否正确
行列是否对应
曲线是否对应
是否有幻觉
```

---

### 21.2 不同视觉任务不是同一种能力

OCR、图表、表格、UI、场景、空间关系并不是同一个难度。

模型可能：

```text
OCR 很强，但表格弱
表格不错，但图表曲线判断弱
普通文本能读，但书法 OCR 很差
UI 大体能看懂，但快捷键会错
```

所以 benchmark 要按能力维度设计。

---

### 21.3 总分相同不代表模型能力相同

Qwen 和 InternVL 总分相同，但错误类型不同。

这说明模型对比应该看：

```text
任务类型
错误类型
代表性 case
共性错误
独有错误
```

而不是只看一个平均分。

---

### 21.4 人工错误分析对入门很重要

正式 benchmark 可以给出分数，但刚入门时更重要的是：

```text
看模型怎么错
为什么错
错在 OCR 还是表格
错在视觉还是推理
错在幻觉还是定位
```

这也是本项目最核心的学习价值。

---

## 22. 后续需要继续补的方向

如果后续继续深入 VLM，可以重点补：

```text
CLIP 与图文对齐
ViT / Swin / InternViT 视觉编码器
LLaVA 的 visual instruction tuning
Qwen-VL 的动态分辨率和视觉 token 机制
InternVL 的模型架构设计
VLM fine-tuning / LoRA
文档图像理解 Document VQA
图表理解 ChartQA
多图理解和视频理解
VLMEvalKit 正式评估流程
```

下一步如果要做更接近算法岗的项目，可以从：

```text
VLM Evaluation → VLM Fine-tuning → Domain-specific VLM
```

逐步推进。

---

## 23. 一句话总结

VLM 的核心不是“让模型看图然后聊天”，而是：

```text
把图像转成语言模型能理解的视觉 token，
再通过指令微调让模型学会基于图像回答问题。
```

而 VLM 评估的核心也不是“模型说得像不像”，而是：

```text
它是否真正基于图像证据，正确完成 OCR、图表、表格、UI、场景和推理任务。
```
