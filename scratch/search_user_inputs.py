import json

transcript_path = r"C:\Users\Marcio Fernando Maia\.gemini\antigravity\brain\dea24b1c-795d-446e-998b-c93e8d65d667\.system_generated\logs\transcript.jsonl"

with open(transcript_path, 'r', encoding='utf-8') as f:
    for line in f:
        try:
            data = json.loads(line)
            if data.get('type') == 'USER_INPUT':
                print(f"=== Step {data.get('step_index')} ===")
                print(data.get('content'))
        except Exception as e:
            pass
