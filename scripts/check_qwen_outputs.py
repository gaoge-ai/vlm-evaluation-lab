import pandas as pd

path = "results/qwen_vl_40_images.csv"
df = pd.read_csv(path, encoding="utf-8-sig")

print("Total rows:", len(df))
print("Usable:", df["whether_answer_is_usable"].sum())
print("Failed:", (~df["whether_answer_is_usable"]).sum())

print("\nImage type counts:")
print(df["image_type"].value_counts())

print("\nSkill type counts:")
print(df["skill_type"].value_counts())

print("\nFailed samples:")
print(df[df["whether_answer_is_usable"] == False][["image_id", "image_path", "error_note"]])

print("\nFirst 3 answers:")
for _, row in df.head(3).iterrows():
    print("=" * 80)
    print("image_id:", row["image_id"])
    print("question:", row["question"])
    print("expected_answer:", row["expected_answer"])
    print("model_answer:", row["model_answer"])