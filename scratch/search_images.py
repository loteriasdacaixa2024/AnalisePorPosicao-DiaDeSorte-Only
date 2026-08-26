import json

transcript_path = r"C:\Users\Marcio Fernando Maia\.gemini\antigravity\brain\dea24b1c-795d-446e-998b-c93e8d65d667\.system_generated\logs\transcript.jsonl"

with open(transcript_path, 'r', encoding='utf-8') as f:
    for line in f:
        if "media_dea24b1c" in line:
            try:
                data = json.loads(line)
                print(f"--- Step {data.get('step_index')} type={data.get('type')} ---")
                # Look for image details
                content = str(data)
                # print some context around media_dea24b1c
                idx = content.find("media_dea24b1c")
                print(content[max(0, idx-100):min(len(content), idx+200)])
            except Exception as e:
                pass
