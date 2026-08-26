content = open('templates/gerador_especial.html', 'r', encoding='utf-8').read()

grupos = [
    ('0', '3', '', '10, 20, 30'),
    ('1', '4', 'border-primary fw-bold', '1, 10, 11... 31 (13 dezenas)'),
    ('2', '3', 'border-primary fw-bold', '2, 20... 29 (11 dezenas)'),
    ('3', '2', '', '3, 13, 23, 30, 31'),
    ('4', '2', 'border-warning', '4, 14, 24'),
    ('5', '2', 'border-warning', '5, 15, 25'),
    ('6', '2', '', '6, 16, 26'),
    ('7', '2', 'border-warning', '7, 17, 27'),
    ('8', '2', 'border-warning', '8, 18, 28'),
    ('9', '2', '', '9, 19, 29'),
]

# Build old section
old_section = '<div class="row g-1">\n'
for g, val, cls, title in grupos:
    extra_cls = f' {cls}' if cls else ''
    old_section += f'                                    <div class="col-6"><label>Grupo {g}:</label><input type="number" id="fat_dig_{g}" class="form-control form-control-sm{extra_cls}" value="{val}" min="0" max="7" title="{title}"></div>\n'
old_section += '                                    <div class="col-12 mt-2"><label>G\u00eameas:</label><input type="number" id="fat_gemeas" class="form-control form-control-sm border-danger fw-bold" value="1" min="0" max="7" title="11, 22"></div>'

# Build new section with toggle buttons
def build_group_cell(g_id, label, val, cls, title, col='col-6'):
    extra_cls = f' {cls}' if cls else ''
    return (
        f'<div class="{col}">\n'
        f'                                        <label class="form-label mb-0" style="font-size:11px;"><strong>{label}</strong> <small class="text-muted">({title})</small></label>\n'
        f'                                        <div class="input-group input-group-sm">\n'
        f'                                            <button type="button" id="fat_modo_{g_id}" class="btn btn-sm btn-outline-danger fat-modo-toggle" data-modo="max" onclick="toggleFatModo(\'{g_id}\')" title="Clique para alternar entre Máximo e Mínimo" style="font-size:11px; font-weight:bold; min-width:32px;">\u2264</button>\n'
        f'                                            <input type="number" id="fat_dig_{g_id}" class="form-control form-control-sm{extra_cls}" value="{val}" min="0" max="7" title="{title}">\n'
        f'                                        </div>\n'
        f'                                    </div>'
    )

new_section = '<div class="row g-2">\n'
for g, val, cls, title in grupos:
    new_section += '                                    ' + build_group_cell(g, f'Grupo {g}', val, cls, title) + '\n'
# Gemeas full width
new_section += '                                    ' + build_group_cell('gemeas', 'G\u00eameas', '1', 'border-danger fw-bold', '11, 22', 'col-12 mt-1') + ''

if old_section in content:
    content = content.replace(old_section, new_section, 1)
    open('templates/gerador_especial.html', 'w', encoding='utf-8').write(content)
    print("OK - form updated")
else:
    print("NOT FOUND")
    # show what we're looking for vs what's there
    idx = content.find('fat_dig_0')
    print(repr(content[idx-100:idx+200]))
