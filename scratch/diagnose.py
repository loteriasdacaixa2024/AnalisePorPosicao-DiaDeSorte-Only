content = open('templates/gerador_especial.html', 'r', encoding='utf-8').read()

# Check for broken HTML patterns from the replacements
problems = []

# 1. Check for broken class attribute - the bg-primary text-white replacement was dangerous
idx = content.find('text-dark" style="background:#D4B31A;')
if idx > 0:
    problems.append(f"Broken class attr at {idx}: {repr(content[idx-50:idx+80])}")

# 2. Check for unclosed quotes near the btn replacement
import re
# Look for onmouseover with escaped quotes that might have broken things
broken_btn = content.find("class=\"btn fw-bold\" style=\"background:#D4B31A; color:#2d2606; border:none;\" onmouseover=")
print(f"btn replacement found at: {broken_btn}")
if broken_btn > 0:
    print(repr(content[broken_btn-20:broken_btn+200]))

# 3. Check for JS errors - look for unterminated strings
# Find the script section
idx_script = content.find('function mostrarAba')
print(f"\nmostrarAba found at: {idx_script}")

# 4. Look for HTML validation issues around fatiamento
idx_fat = content.find('id="fatiamento"')
chunk = content[idx_fat:idx_fat+500]
print(f"\nFatiamento section start:")
print(chunk)

for p in problems:
    print("PROBLEM:", p)
