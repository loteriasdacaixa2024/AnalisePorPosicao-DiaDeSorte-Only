import re

content = open('templates/gerador_especial.html', 'r', encoding='utf-8').read()

# Let's find index of '<!-- Fim Container Geral -->'
end_idx = content.find('<!-- Fim Container Geral -->')
if end_idx == -1:
    print("Could not find end of Container Geral")
    exit()

print(f"End index: {end_idx}")

# Let's trace tags in content[0:end_idx]
sub = content[0:end_idx]

# Let's find all '<div' and '</div>' tags
tags = []
for m in re.finditer(r'</?div\b[^>]*>', sub, re.IGNORECASE):
    tag = m.group(0)
    pos = m.start()
    tags.append((tag, pos))

# Trace stack
stack = []
for tag, pos in tags:
    if tag.lower().startswith('</div'):
        if stack:
            popped = stack.pop()
        else:
            line_num = content[:pos].count('\n') + 1
            print(f"ALERT: Underflow at line {line_num} (pos {pos}): {tag}")
    elif tag.lower().startswith('<div'):
        stack.append((tag, pos))

print("\nRemaining open divs at the very end:")
for tag, pos in stack:
    line_num = content[:pos].count('\n') + 1
    print(f"Line {line_num} (pos {pos}): {tag}")
