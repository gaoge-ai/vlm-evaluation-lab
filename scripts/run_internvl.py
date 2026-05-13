import argparse
import time
import traceback
from pathlib import Path
from PIL import Image
import pandas as pd
import torch
from tqdm import tqdm
from transformers import AutoProcessor, AutoModelForImageTextToText


def build_prompt(question: str, prompt_mode: str = "structured_zh") -> str:
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
    """
    Use PIL to load local image directly.
    This avoids Windows file URI issues such as file:///C:/...
    """

    image = Image.open(image_path).convert("RGB")

    messages = [
        {
            "role": "user",
            "content": [
                {"type": "image"},
                {"type": "text", "text": prompt},
            ],
        }
    ]

    text = processor.apply_chat_template(
        messages,
        add_generation_prompt=True,
        tokenize=False,
    )

    inputs = processor(
        text=[text],
        images=[image],
        return_tensors="pt",
    )

    if torch.cuda.is_available():
        inputs = inputs.to("cuda")

    with torch.inference_mode():
        generated_ids = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
        )

    input_len = inputs["input_ids"].shape[1]

    output_text = processor.decode(
        generated_ids[0, input_len:],
        skip_special_tokens=True,
    )

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
        default="results/internvl3_2b.csv",
        help="Path to output CSV",
    )

    parser.add_argument(
        "--model_name",
        type=str,
        default="OpenGVLab/InternVL3-2B-hf",
        help="InternVL model name",
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

    args = parser.parse_args()

    project_root = Path(".").resolve()
    questions_path = project_root / args.questions
    output_path = project_root / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print("InternVL Inference")
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

    processor = AutoProcessor.from_pretrained(args.model_name)

    model = AutoModelForImageTextToText.from_pretrained(
        args.model_name,
        torch_dtype="auto",
        device_map="auto",
    )

    results = []

    for _, row in tqdm(df.iterrows(), total=len(df)):
        image_path = project_root / str(row["image_path"])
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