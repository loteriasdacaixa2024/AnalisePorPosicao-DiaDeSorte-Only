content = open('templates/gerador_especial.html', 'r', encoding='utf-8').read()

old = """                    const medalhasEsp = ['\U0001f947', '\U0001f948', '\U0001f949'];
                    let espHtml = '';
                    sorteiosEspalhamento.slice(0, 3).forEach((s, i) => {
                        let dezenasStr = s.dezenas.map(d => ('0'+d).slice(-2)).join(' ');
                        let gruposBadges = s.gruposNomes.map(g =>
                            `<span class="badge bg-success" style="font-size: 10px;">${g}</span>`
                        ).join(' ');
                        espHtml += `
                        <div class="card border-success shadow-sm" style="min-width: 260px; max-width: 300px;">
                            <div class="card-body p-2 text-center">
                                <div class="fw-bold" style="font-size: 15px;">${medalhasEsp[i]} Concurso <span class="text-success">${s.concurso}</span></div>
                                <div class="text-muted" style="font-size: 11px;">${s.data}</div>
                                <div class="my-1" style="font-size: 11px; letter-spacing: 1px;">${dezenasStr}</div>
                                <div class="mb-1">${gruposBadges}</div>
                                <span class="badge bg-success px-3 py-1" style="font-size: 12px;">
                                    <i class="fas fa-project-diagram"></i> ${s.gruposAtivados} grupos ativados
                                </span>
                            </div>
                        </div>`;
                    });"""

new = """                    const medalhasEsp = ['1\u00ba', '2\u00ba', '3\u00ba'];
                    const coresEsp = ['#ffd700', '#c0c0c0', '#cd7f32'];
                    let espHtml = '';
                    sorteiosEspalhamento.slice(0, 3).forEach((s, i) => {
                        let dezenasStr = s.dezenas.map(d => ('0'+d).slice(-2)).join(' ');
                        let gruposBadges = s.gruposNomes.map(g =>
                            `<span class="badge bg-success" style="font-size: 9px; padding: 2px 5px;">${g}</span>`
                        ).join(' ');
                        espHtml += `
                        <div class="card shadow-sm flex-fill" style="border: 2px solid ${coresEsp[i]}; min-width: 0;">
                            <div class="card-body p-2 text-center">
                                <div class="fw-bold mb-1" style="font-size: 13px; color: ${coresEsp[i]};">
                                    ${medalhasEsp[i]} &nbsp; Concurso <span style="color:#198754">${s.concurso}</span>
                                </div>
                                <div class="text-muted mb-1" style="font-size: 10px;">${s.data}</div>
                                <div class="mb-1 fw-bold" style="font-size: 11px; letter-spacing: 1px; font-family: monospace;">${dezenasStr}</div>
                                <div class="mb-2 d-flex flex-wrap justify-content-center gap-1">${gruposBadges}</div>
                                <span class="badge bg-success w-100" style="font-size: 11px;">
                                    <i class="fas fa-project-diagram"></i> ${s.gruposAtivados} grupos ativados
                                </span>
                            </div>
                        </div>`;
                    });"""

if old in content:
    content = content.replace(old, new, 1)
    open('templates/gerador_especial.html', 'w', encoding='utf-8').write(content)
    print("OK")
else:
    print("NOT FOUND - checking fragment...")
    idx = content.find('const medalhasEsp')
    print(repr(content[idx:idx+100]))
