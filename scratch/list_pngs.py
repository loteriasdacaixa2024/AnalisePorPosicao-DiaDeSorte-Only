import os
import glob

brain_dir = r"C:\Users\Marcio Fernando Maia\.gemini\antigravity\brain\32e834c5-68a5-481d-9cb6-e1c1c77a44a7"
temp_media_dir = os.path.join(brain_dir, ".tempmediaStorage")

print("Files in .tempmediaStorage:")
for path in glob.glob(os.path.join(temp_media_dir, "*")):
    print(f" - {os.path.basename(path)}: {os.path.getsize(path)} bytes")

click_feedback_dir = os.path.join(brain_dir, ".system_generated", "click_feedback")
if os.path.exists(click_feedback_dir):
    print("\nFiles in click_feedback:")
    for path in glob.glob(os.path.join(click_feedback_dir, "*")):
        print(f" - {os.path.basename(path)}: {os.path.getsize(path)} bytes")
