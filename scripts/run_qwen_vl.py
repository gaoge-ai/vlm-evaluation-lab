#这份脚本采用的是 Hugging Face 官方推荐的
#Qwen2_5_VLForConditionalGeneration、AutoProcessor 和 qwen_vl_utils.process_vision_info 这一套使用方式；
#官方示例里也是用 chat template 组织图像和文本输入，再进行生成
#pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128
#pip install -U pandas pillow tqdm accelerate qwen-vl-utils
#ip install git+https://github.com/huggingface/transformers
import argparse
import time
import traceback
from pathlib import Path

import pandas as pd
import torch
from tqdm import tqdm
from transformers import Qwen2_5_VLForConditionalGeneration, AutoProcessor
from qwen_vl_utils import process_vision_info


def build_prompt(question: str, prompt_mode: str = "structured_zh") -> str:
    """
    Build the prompt used for VLM evaluation.
    The expected answer is intentionally not included.
    """
    question = str(question).strip()

    if prompt_mode == "direct":
        return question

    if prompt_mode == "structured_zh":
        return f"""请严格基于图像内容回答问题。不要猜测图中看不到的信息。
如果图中无法判断，请明确回答“图中无法确定”。

问题：{question}

请用以下格式回答：
Observation:
Reasoning:
Final Answer:"""

    if prompt_mode == "concise_zh":
        return f"""请只基于图像内容，简洁回答下面的问题。不要编造图中不存在的信息。

问题：{question}"""

    raise ValueError(f"Unknown prompt_mode: {prompt_mode}")


def run_one_sample(model, processor, image_path: Path, prompt: str, max_new_tokens: int):
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "image": str(image_path),
                },
                {
                    "type": "text",
                    "text": prompt,
                },
            ],
        }
    ]

    text = processor.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
    )

    image_inputs, video_inputs = process_vision_info(messages)

    inputs = processor(
        text=[text],
        images=image_inputs,
        videos=video_inputs,
        padding=True,
        return_tensors="pt",
    )

    if torch.cuda.is_available():
        inputs = inputs.to("cuda")

    with torch.inference_mode():
        generated_ids = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
        )

    generated_ids_trimmed = [
        output_ids[len(input_ids):]
        for input_ids, output_ids in zip(inputs.input_ids, generated_ids)
    ]

    output_text = processor.batch_decode(
        generated_ids_trimmed,
        skip_special_tokens=True,
        clean_up_tokenization_spaces=False,
    )[0]

    return output_text.strip()


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--questions",
        type=str,
        default="data/questions.csv",
        help="Path to questions.csv",
    )

    parser.add_argument(
        "--output",
        type=str,
        default="results/qwen_vl_40_images.csv",
        help="Path to output CSV",
    )

    parser.add_argument(
        "--model_name",
        type=str,
        default="Qwen/Qwen2.5-VL-3B-Instruct",
        help="Qwen2.5-VL model name",
    )

    parser.add_argument(
        "--prompt_mode",
        type=str,
        default="structured_zh",
        choices=["direct", "structured_zh", "concise_zh"],
        help="Prompt template mode",
    )

    parser.add_argument(
        "--max_new_tokens",
        type=int,
        default=256,
        help="Maximum number of generated tokens",
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Only run the first N samples for debugging",
    )

    parser.add_argument(
        "--min_pixels",
        type=int,
        default=256 * 28 * 28,
        help="Minimum visual pixels for processor",
    )

    parser.add_argument(
        "--max_pixels",
        type=int,
        default=1024 * 28 * 28,
        help="Maximum visual pixels for processor. Reduce this if CUDA OOM happens.",
    )

    args = parser.parse_args()

    project_root = Path(".").resolve()
    questions_path = project_root / args.questions
    output_path = project_root / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print("Qwen2.5-VL Inference")
    print("=" * 80)
    print(f"Questions file: {questions_path}")
    print(f"Output file:    {output_path}")
    print(f"Model:          {args.model_name}")
    print(f"Prompt mode:    {args.prompt_mode}")
    print("=" * 80)

    df = pd.read_csv(questions_path, encoding="utf-8-sig")

    if args.limit is not None:
        df = df.head(args.limit).copy()

    required_columns = [
        "image_id",
        "question_id",
        "image_path",
        "image_type",
        "skill_type",
        "difficulty",
        "question",
        "expected_answer",
        "answer_type",
    ]

    missing_columns = [c for c in required_columns if c not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns in questions.csv: {missing_columns}")

    print("Loading model and processor...")

    model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
        args.model_name,
        torch_dtype="auto",
        device_map="auto",
    )

    processor = AutoProcessor.from_pretrained(
        args.model_name,
        min_pixels=args.min_pixels,
        max_pixels=args.max_pixels,
    )

    results = []

    for _, row in tqdm(df.iterrows(), total=len(df)):
        image_rel_path = str(row["image_path"])
        image_path = project_root / image_rel_path

        prompt = build_prompt(row["question"], args.prompt_mode)

        result_row = row.to_dict()
        result_row.update(
            {
                "model_name": args.model_name,
                "prompt_mode": args.prompt_mode,
                "prompt": prompt,
                "model_answer": "",
                "inference_time": None,
                "error_note": "",
                "whether_answer_is_usable": False,
            }
        )

        if not image_path.exists():
            result_row["error_note"] = f"Image not found: {image_path}"
            results.append(result_row)
            continue

        start_time = time.time()

        try:
            answer = run_one_sample(
                model=model,
                processor=processor,
                image_path=image_path,
                prompt=prompt,
                max_new_tokens=args.max_new_tokens,
            )

            elapsed = time.time() - start_time

            result_row["model_answer"] = answer
            result_row["inference_time"] = round(elapsed, 4)
            result_row["whether_answer_is_usable"] = True

        except Exception as e:
            elapsed = time.time() - start_time
            result_row["inference_time"] = round(elapsed, 4)
            result_row["error_note"] = repr(e)
            result_row["whether_answer_is_usable"] = False

            print("\nError occurred:")
            print(f"image_id: {row['image_id']}")
            print(f"image_path: {image_path}")
            print(traceback.format_exc())

        results.append(result_row)

        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    out_df = pd.DataFrame(results)
    out_df.to_csv(output_path, index=False, encoding="utf-8-sig")

    print("=" * 80)
    print("Inference finished.")
    print(f"Saved to: {output_path}")
    print("=" * 80)

    usable_count = out_df["whether_answer_is_usable"].sum()
    print(f"Usable answers: {usable_count} / {len(out_df)}")

    if out_df["error_note"].astype(str).str.len().sum() > 0:
        print("Some samples have errors. Please check the error_note column.")


if __name__ == "__main__":
    main()