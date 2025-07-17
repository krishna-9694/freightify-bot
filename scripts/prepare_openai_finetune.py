import json

input_file = "llm_finetune_data.jsonl"
output_file = "openai_finetune_ready.jsonl"

with open(input_file) as fin, open(output_file, "w") as fout:
    for line in fin:
        entry = json.loads(line)
        user_content = f"Context: {entry['context']}\nQuestion: {entry['question']}"
        assistant_content = entry["comment"] if entry["comment"] else entry["answer"]
        fout.write(json.dumps({
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_content},
                {"role": "assistant", "content": assistant_content}
            ]
        }) + "\n")
print(f"OpenAI fine-tune data written to {output_file}") 