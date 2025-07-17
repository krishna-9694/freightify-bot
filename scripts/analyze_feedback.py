import json
from collections import Counter, defaultdict

FEEDBACK_FILE = "feedback_log.jsonl"

# Data structures to collect stats
downvoted = []
comments = []
source_counter = Counter()
question_counter = Counter()
comment_map = defaultdict(list)

# Read feedback log
with open(FEEDBACK_FILE) as f:
    for line in f:
        entry = json.loads(line)
        if entry["feedback"] == "thumbs_down":
            downvoted.append(entry)
            question_counter[entry["query"]] += 1
            for src in entry["sources"]:
                source_counter[src] += 1
            if entry.get("comment"):
                comments.append(entry["comment"])
                comment_map[entry["query"]].append(entry["comment"])

print("Most downvoted questions:")
for q, count in question_counter.most_common(5):
    print(f"- {q} ({count} downvotes)")

print("\nSources most associated with bad answers:")
for src, count in source_counter.most_common(5):
    print(f"- {src} ({count} times)")

print("\nSample user comments on bad answers:")
for q, comms in comment_map.items():
    print(f"Q: {q}")
    for c in comms:
        print(f"  - {c}") 

REVIEW_THRESHOLD = 3  # Number of downvotes to flag a source

problematic_sources = [src for src, count in source_counter.items() if count >= REVIEW_THRESHOLD]

with open("sources_to_review.txt", "w") as f:
    for src in problematic_sources:
        f.write(f"{src}\n")

print(f"\nFlagged {len(problematic_sources)} sources for review (see sources_to_review.txt)") 

input_file = "feedback_log.jsonl"
output_file = "llm_finetune_data.jsonl"

with open(input_file) as fin, open(output_file, "w") as fout:
    for line in fin:
        entry = json.loads(line)
        # Only use entries with comments or thumbs down
        if entry["feedback"] == "thumbs_down" or entry.get("comment"):
            # You can customize the context as needed
            context = " ".join(entry.get("sources", []))
            fout.write(json.dumps({
                "question": entry["query"],
                "context": context,
                "answer": entry["response"],
                "feedback": entry["feedback"],
                "comment": entry.get("comment", "")
            }) + "\n")

print(f"Fine-tuning data written to {output_file}") 