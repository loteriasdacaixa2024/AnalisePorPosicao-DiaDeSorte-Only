import os

root_dir = r"D:\Loterias"
for root, dirs, files in os.walk(root_dir):
    # Skip virtual environments
    if any(p in root.lower() for p in ['venv', '.git', 'node_modules']):
        continue
    for f in files:
        if f.lower().endswith(('.jpg', '.jpeg', '.png')):
            print(os.path.join(root, f))
