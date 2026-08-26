import re
content = open('templates/gerador_especial.html', 'r', encoding='utf-8').read()

idx_start = content.find('id="fatiamento"')
# Get the fatiamento section up to analisador or style tag
idx_end = content.find('<!-- ABA 10:', idx_start)

section = content[idx_start:idx_end]

# Find all color references
colors = re.findall(r'(?:background|color|border)[^;"\n]{0,40}(?:#[0-9a-fA-F]{3,6})', section)
print("=== Colors in Aba 9 (fatiamento section) ===")
for col in sorted(set(colors)):
    print(" ", col)

# Also find Bootstrap color classes used
bs_colors = re.findall(r'(?:bg|text|border)-(?:primary|secondary|success|danger|warning|info|dark|light)', section)
print("\n=== Bootstrap color classes ===")
for col in sorted(set(bs_colors)):
    print(f"  {col} ({section.count(col)}x)")

# Show first 2000 chars of section
print("\n=== First section HTML snippet ===")
print(section[:1500])
