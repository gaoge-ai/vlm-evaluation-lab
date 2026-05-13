(vlm_eval) PS C:\Users\15255\Desktop\vlm-evaluation-lab> python scripts/check_qwen_outputs.py
Total rows: 40
Usable: 40
Failed: 0

Image type counts:
image_type
academic_figure           8
scene_photo               8
chart                     6
table                     6
ui_screenshot             5
ocr_document              2
ocr_paper                 2
ocr_code_screenshot       1
ocr_bilingual_document    1
poster_photo              1
Name: count, dtype: int64

Skill type counts:
skill_type
UI_understanding               5
table_understanding            4
scene_OCR                      3
architecture_understanding     2
chart_comparison               2
hallucination_risk             2
chart_understanding            2
object_recognition             2
table_comparison               2
academic_OCR                   2
architecture_comparison        1
visual_reasoning               1
scientific_figure              1
multimodal_architecture        1
zero_shot_reasoning            1
scatter_plot_understanding     1
bilingual_OCR                  1
Chinese_OCR                    1
code_OCR                       1
OCR                            1
stacked_chart_understanding    1
counting                       1
spatial_reasoning              1
handwritten_OCR                1
Name: count, dtype: int64

Failed samples:
Empty DataFrame
Columns: [image_id, image_path, error_note]
Index: []

First 3 answers:
================================================================================
image_id: architecture_01
question: 图中 BERT 的预训练部分包含哪两个顶部任务标签？
expected_answer: 包含 NSP 和 Mask LM 两个任务标签。
model_answer: Observation: 图中 BERT 的预训练部分有两个顶部任务标签，分别是 NSP 和 Mask LM。

Reasoning: 根据图中的标注，NSP 和 Mask LM 是预训练阶段的两个主要任务标签。

Final Answer: 图中 BERT 的预训练部分包含 NSP 和 Mask LM 两个顶部任务标签。
================================================================================
image_id: architecture_02
question: 在右侧 zero-shot prediction 部分，图像特征最终匹配到的文本类别是什么？
expected_answer: 匹配到 dog，对应输出是“A photo of a dog.”。
model_answer: Observation: 在右侧 zero-shot prediction 部分，图像特征最终匹配到的文本类别是 "dog"。

Reasoning: 根据图中的描述和流程图，当输入一张图片时，首先通过图像编码器提取图像特征 I1, I2, ..., IN。然后将这些特征与文本 T1, T2, ..., TN 进行对比，找出最相似的 文本类别。在这个例子中，图像特征最终匹配到了文本类别 "dog"。

Final Answer: dog
================================================================================
image_id: architecture_03
question: 图中 Noised Latent 在进入 DiT Block 之前经过了哪一步处理？
expected_answer: Noised Latent 先经过 Patchify 处理；timestep 和 label 也通过 Embed 输入到 DiT Block。
model_answer: Observation: 图中 Noised Latent 在进入 DiT Block 之前，经过了 Patchify 和 Embed 的处理。

Reasoning: 根据图中的流程图，Noised Latent 首先被 Patchify 处理，然后被 Embed 处理，这两个步骤在 Noised Latent 进入 DiT Block 之前进行。

Final Answer: Noised Latent 在进入 DiT Block 之前经过了 Patchify 和 Embed 的处理。