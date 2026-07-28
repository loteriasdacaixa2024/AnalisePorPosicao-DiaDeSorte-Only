content = open('templates/gerador_especial.html', 'r', encoding='utf-8').read()

idx_start = content.find('id="fatiamento"')
idx_end = content.find('<!-- ABA 10:', idx_start)

section = content[idx_start:idx_end]
original_section = section

# === SUBSTITUIÇÕES CIRÚRGICAS NA ABA 9 ===

# 1. Título h2 - #0dcaf0 (cyan/info) -> dourado
section = section.replace('color: #0dcaf0;', 'color: #D4B31A;')
section = section.replace('color: #0dcaf0', 'color: #D4B31A')

# 2. alert-info -> alert personalizado dourado
section = section.replace(
    '<div class="alert alert-info shadow-sm mb-4">',
    '<div class="alert shadow-sm mb-4" style="background:#fcf9e8; border-left: 5px solid #D4B31A; border-color:#e6c533;">'
)

# 3. badge bg-primary -> badge dourado
section = section.replace(
    '<span class="badge bg-primary"><i class="fas fa-magic"></i> Configurar Filtros</span>',
    '<span class="badge" style="background:#D4B31A; color:#2d2606;"><i class="fas fa-magic"></i> Configurar Filtros</span>'
)

# 4. Raio-X header - bg-primary -> dourado
section = section.replace('bg-primary text-white', 'text-dark" style="background:#D4B31A;')

# 5. border-top: 5px solid #6f42c1 -> dourado
section = section.replace('border-top: 5px solid #6f42c1', 'border-top: 5px solid #D4B31A')

# 6. background-color: #6f42c1 (placard recordes header) -> dourado  
section = section.replace('background-color: #6f42c1', 'background-color: #D4B31A; color: #2d2606;')

# 7. text-primary -> cor dourada inline
# Be careful here - only specific key headings, not all
section = section.replace(
    '<h6 class="fw-bold text-primary text-center mb-2">',
    '<h6 class="fw-bold text-center mb-2" style="color:#D4B31A;">'
)
section = section.replace(
    '<h6 class="fw-bold text-primary text-center mb-1">',
    '<h6 class="fw-bold text-center mb-1" style="color:#D4B31A;">'
)
section = section.replace(
    '<h6 class="fw-bold text-primary mb-3">',
    '<h6 class="fw-bold mb-3" style="color:#D4B31A;">'
)
section = section.replace(
    '<h6 class="fw-bold text-primary mb-1">',
    '<h6 class="fw-bold mb-1" style="color:#D4B31A;">'
)

# 8. Raio-X card header background color
section = section.replace(
    'class="card-header" style="background: linear-gradient(135deg, #6610f2, #0dcaf0)',
    'class="card-header" style="background: linear-gradient(135deg, #b69816, #D4B31A)'
)

# 9. Raio-X header purple-to-cyan gradient -> gold gradient
section = section.replace(
    'background: linear-gradient(135deg, #6610f2,',
    'background: linear-gradient(135deg, #b69816,'
)
section = section.replace('#0dcaf0)', '#D4B31A)')
section = section.replace('#0dcaf0 ', '#D4B31A ')

# 10. btn-info -> styled button with gold
section = section.replace(
    'class="btn btn-info fw-bold',
    'class="btn fw-bold" style="background:#D4B31A; color:#2d2606; border:none;" onmouseover="this.style.background=\'#b69816\'" onmouseout="this.style.background=\'#D4B31A\'"'
)

# 11. bg-info (badge) -> gold badge
section = section.replace('class="badge bg-info', 'class="badge" style="background:#D4B31A; color:#2d2606;"')

# 12. border-top: 5px solid #0dcaf0
section = section.replace('border-top: 5px solid #0dcaf0', 'border-top: 5px solid #D4B31A')

# 13. text-info -> gold
section = section.replace('class="fw-bold text-info', 'class="fw-bold" style="color:#D4B31A;"')

# 14. CONFIGURAR FILTROS button
section = section.replace(
    'class="btn btn-warning btn-sm fw-bold',
    'class="btn btn-sm fw-bold" style="background:#D4B31A; color:#2d2606; border:none;"'
)

# 15. span text-primary fw-bold (total values in placards)
section = section.replace(
    '<span class="text-primary fw-bold"',
    '<span class="fw-bold" style="color:#b69816;"'
)

# 16. bg-success in espalhados cards -> mantém verde (é semântico)
# bg-success kept as-is (green is for "groups activated" - semantic)

# Count replacements
changed = sum(1 for a, b in zip(original_section, section) if a != b)
print(f"Section changed: {len(section) != len(original_section) or section != original_section}")
print(f"Remaining #0dcaf0: {section.count('#0dcaf0')}")
print(f"Remaining #6f42c1: {section.count('#6f42c1')}")
print(f"Remaining alert-info: {section.count('alert-info')}")
print(f"Remaining bg-primary (non-semantic): {section.count('bg-primary')}")

content = content[:idx_start] + section + content[idx_end:]
open('templates/gerador_especial.html', 'w', encoding='utf-8').write(content)
print("OK - Aba 9 colors updated to Dia de Sorte palette")
