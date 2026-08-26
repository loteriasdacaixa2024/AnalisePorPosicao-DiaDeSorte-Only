content = open('templates/gerador_especial.html', 'r', encoding='utf-8').read()

# Replace all purple references with Dia de Sorte gold palette
# Main color: #6f42c1 -> #D4B31A
# Dark variant: #5a2d9c -> #b69816  (darker gold)
# Light bg: #f8f5ff -> #fcf9e8     (lighter gold tint)
# Light bg2: #f0e8ff -> #f9f2d2    (hover gold tint)
# Border: #d0b8f0 -> #e6c533       (medium gold)
# Gradient: linear-gradient(135deg,#6f42c1,#8a63d2) -> linear-gradient(135deg,#D4B31A,#e6c533)
# Gradient hover: linear-gradient(135deg,#ede0ff -> linear-gradient(135deg,#f4e5a4

replacements = [
    ('linear-gradient(135deg,#6f42c1,#8a63d2)', 'linear-gradient(135deg,#D4B31A,#e6c533)'),
    ('linear-gradient(135deg,#f8f5ff,#fff)', 'linear-gradient(135deg,#fcf9e8,#fff)'),
    ('linear-gradient(135deg,#ede0ff,#f8f5ff)', 'linear-gradient(135deg,#f4e5a4,#fcf9e8)'),
    ('border-color:#6f42c1', 'border-color:#D4B31A'),
    ('border:1px solid #d0b8f0', 'border:1px solid #e6c533'),
    ("background:#6f42c1; font-size:12px; padding:6px 16px;", "background:#D4B31A; color:#2d2606; font-size:12px; padding:6px 16px; font-weight:bold;"),
    ("style=\"background:#6f42c1; color:#fff;\" onclick=\"analisProcessar()\"", "style=\"background:#D4B31A; color:#2d2606; font-weight:bold;\" onclick=\"analisProcessar()\""),
    ("style=\"color:#6f42c1;\"", "style=\"color:#D4B31A;\""),
    ("color:#6f42c1", "color:#D4B31A"),
    ("background:#6f42c1; color:#fff; font-size:13px;", "background:#D4B31A; color:#2d2606; font-size:13px; font-weight:bold;"),
    ("background:#6f42c1; color:#fff;\" onclick=\"analisProcessar()\"", "background:#D4B31A; color:#2d2606; font-weight:bold;\" onclick=\"analisProcessar()\""),
    ("background:#6f42c1; color:#fff;", "background:#D4B31A; color:#2d2606; font-weight:bold;"),
    ("background:#6f42c1;", "background:#D4B31A;"),
    ("border-color:#5a2d9c", "border-color:#b69816"),
    ("#6f42c1", "#D4B31A"),
    ("background:#f8f5ff", "background:#fcf9e8"),
    ("border-top:3px solid #6f42c1!important;", "border-top:3px solid #D4B31A!important;"),
    ("border-top: 4px solid #6f42c1 !important;", "border-top: 4px solid #D4B31A !important;"),
    ("color:#6f42c1;", "color:#b69816;"),
    ("style=\"background:#D4B31A;\"", "style=\"background:#D4B31A; color:#2d2606;\""),
]

# Only replace within the analisador section
start_marker = '<!-- ABA 10: ANALISADOR DE APOSTAS EM MASSA'
end_marker = '// ============================================================\n    // ABA 10: ANALISADOR DE APOSTAS EM MASSA'

idx_html_start = content.find(start_marker)
idx_js_start = content.find(end_marker)
idx_js_end = content.find('\n    // (O script gen')

print(f"HTML section: {idx_html_start}")
print(f"JS section: {idx_js_start} to {idx_js_end}")

if idx_html_start < 0 or idx_js_start < 0:
    print("MARKERS NOT FOUND")
else:
    # Replace in HTML section
    html_section = content[idx_html_start:idx_js_start]
    js_section = content[idx_js_start:idx_js_end]
    
    for old, new in replacements:
        html_section = html_section.replace(old, new)
        js_section = js_section.replace(old, new)
    
    content = content[:idx_html_start] + html_section + js_section + content[idx_js_end:]
    open('templates/gerador_especial.html', 'w', encoding='utf-8').write(content)
    print("OK - colors updated to Dia de Sorte gold palette")
    
    # Verify
    remaining = html_section.count('#6f42c1') + js_section.count('#6f42c1')
    print(f"Remaining #6f42c1 references: {remaining}")
