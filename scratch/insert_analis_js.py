content = open('templates/gerador_especial.html', 'r', encoding='utf-8').read()

JS_ANCHOR = "    // (O script gen\u00e9rico de hash foi removido para manter o comportamento original de abrir a Aba 1 por padr\u00e3o)\n</script>"

ANALIS_JS = """
    // ============================================================
    // ABA 10: ANALISADOR DE APOSTAS EM MASSA
    // ============================================================
    const ANALIS_GRUPOS = {
        '0': [10, 20, 30],
        '1': [1, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 21, 31],
        '2': [2, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29],
        '3': [3, 13, 23, 30, 31],
        '4': [4, 14, 24],
        '5': [5, 15, 25],
        '6': [6, 16, 26],
        '7': [7, 17, 27],
        '8': [8, 18, 28],
        '9': [9, 19, 29],
        'gemeas': [11, 22]
    };
    const ANALIS_GRUPOS_KEYS = ['0','1','2','3','4','5','6','7','8','9','gemeas'];

    const ANALIS_MESES = {
        'jan':1,'janeiro':1,'fev':2,'fevereiro':2,
        'mar':3,'março':3,'marco':3,'abr':4,'abril':4,
        'mai':5,'maio':5,'jun':6,'junho':6,'jul':7,'julho':7,
        'ago':8,'agosto':8,'set':9,'setembro':9,
        'out':10,'outubro':10,'nov':11,'novembro':11,
        'dez':12,'dezembro':12
    };
    const ANALIS_MESES_NOMES = ['','Janeiro','Fevereiro','Março','Abril','Maio','Junho','Julho','Agosto','Setembro','Outubro','Novembro','Dezembro'];
    const ANALIS_MESES_COR = {
        1:'#007bff',2:'#6610f2',3:'#28a745',4:'#fd7e14',
        5:'#dc3545',6:'#20c997',7:'#e83e8c',8:'#ff6600',
        9:'#6f42c1',10:'#795548',11:'#607d8b',12:'#d63384'
    };

    let analisData = [];
    let analisCurrentPage = 1;

    function analisContarLinhas() {
        const txt = document.getElementById('analis_textarea').value;
        const linhas = txt.split('\\n').filter(l => l.trim() !== '').length;
        document.getElementById('analis_line_count').textContent = linhas + ' linhas';
    }

    function analisDropOver(e) {
        e.preventDefault();
        document.getElementById('analis_dropzone').style.background = 'linear-gradient(135deg,#ede0ff,#f8f5ff)';
        document.getElementById('analis_dropzone').style.borderColor = '#5a2d9c';
    }
    function analisDropLeave(e) {
        document.getElementById('analis_dropzone').style.background = 'linear-gradient(135deg,#f8f5ff,#fff)';
        document.getElementById('analis_dropzone').style.borderColor = '#6f42c1';
    }
    function analisDropFile(e) {
        e.preventDefault();
        analisDropLeave(e);
        const file = e.dataTransfer.files[0];
        if (file) analisReadFile(file);
    }
    function analisLoadFile(event) {
        const file = event.target.files[0];
        if (file) analisReadFile(file);
    }
    function analisReadFile(file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            document.getElementById('analis_textarea').value = e.target.result;
            analisContarLinhas();
        };
        reader.readAsText(file, 'utf-8');
    }

    function analiserParseLinha(linha) {
        linha = linha.trim();
        if (!linha) return null;
        const partes = linha.split(/\\s+/);
        if (partes.length < 7) return { erro: 'Menos de 7 partes: ' + linha };

        // Last token = month
        const mesStr = partes[partes.length - 1].toLowerCase()
            .normalize('NFD').replace(/[\\u0300-\\u036f]/g, ''); // strip accents
        const mesNum = ANALIS_MESES[mesStr] || null;
        const dezenas = partes.slice(0, partes.length - 1).map(x => parseInt(x));

        if (dezenas.some(isNaN)) return { erro: 'N\u00fameros inv\u00e1lidos: ' + linha };
        if (dezenas.length < 7 || dezenas.length > 9) return { erro: 'Quantidade inv\u00e1lida de dezenas (' + dezenas.length + '): ' + linha };
        const invalidas = dezenas.filter(d => d < 1 || d > 31);
        if (invalidas.length) return { erro: 'Dezenas fora do intervalo (1-31): ' + invalidas.join(', ') };
        const uniq = new Set(dezenas);
        if (uniq.size !== dezenas.length) return { erro: 'Dezenas duplicadas: ' + linha };

        // Compute group counts
        const contagem = {};
        ANALIS_GRUPOS_KEYS.forEach(k => {
            contagem[k] = dezenas.filter(d => ANALIS_GRUPOS[k].includes(d)).length;
        });
        const gruposAtivos = ANALIS_GRUPOS_KEYS.filter(k => contagem[k] > 0);

        return {
            dezenas: dezenas.sort((a,b) => a-b),
            mesNum: mesNum,
            mesNome: mesNum ? ANALIS_MESES_NOMES[mesNum] : (partes[partes.length-1] || '?'),
            mesValido: !!mesNum,
            contagem,
            gruposAtivos,
            erro: null
        };
    }

    function analisProcessar() {
        const textarea = document.getElementById('analis_textarea');
        const linhas = textarea.value.split('\\n');
        const resultado = document.getElementById('analis_resultado');
        const loading = document.getElementById('analis_loading');

        resultado.style.display = 'none';
        loading.style.display = 'block';

        // Use setTimeout to allow UI to update (loading spinner)
        setTimeout(() => {
            analisData = [];
            let erros = 0;
            const mesCount = {};
            const grupoCount = {};
            ANALIS_GRUPOS_KEYS.forEach(k => grupoCount[k] = 0);
            let totalGrupos = 0;

            linhas.forEach((linha, i) => {
                if (!linha.trim()) return;
                const parsed = analiserParseLinha(linha);
                if (!parsed) return;
                if (parsed.erro) {
                    erros++;
                    analisData.push({ idx: analisData.length + 1, erro: parsed.erro, linha });
                } else {
                    // Stats
                    if (parsed.mesNum) mesCount[parsed.mesNum] = (mesCount[parsed.mesNum] || 0) + 1;
                    ANALIS_GRUPOS_KEYS.forEach(k => { grupoCount[k] += parsed.contagem[k]; });
                    totalGrupos += parsed.gruposAtivos.length;
                    analisData.push({ idx: analisData.length + 1, ...parsed });
                }
            });

            const validas = analisData.filter(a => !a.erro);
            const media = validas.length > 0 ? (totalGrupos / validas.length).toFixed(1) : 0;

            // Update stat cards
            document.getElementById('stat_total').textContent = analisData.length;
            document.getElementById('stat_ok').textContent = validas.length;
            document.getElementById('stat_err').textContent = erros;
            document.getElementById('stat_espalhamento').textContent = media;

            // Badge total
            document.getElementById('analis_total_loaded').textContent = analisData.length;
            document.getElementById('analis_counter_badge').style.display = '';

            // Month stats
            const mesHtml = Object.entries(mesCount)
                .sort((a,b) => b[1]-a[1])
                .map(([m, cnt]) => `<span class="badge" style="background:${ANALIS_MESES_COR[m] || '#6f42c1'}; font-size:13px; padding:6px 12px;">${ANALIS_MESES_NOMES[m]}: ${cnt}</span>`)
                .join('');
            document.getElementById('analis_mes_stats').innerHTML = mesHtml || '<span class="text-muted">Nenhum</span>';

            // Group stats
            const grupoHtml = ANALIS_GRUPOS_KEYS.map(k => {
                const nome = k === 'gemeas' ? 'G\u00eam' : 'G' + k;
                const total = grupoCount[k];
                const pct = validas.length > 0 ? Math.round(total / validas.length * 10) / 10 : 0;
                return `<div class="text-center px-2 py-2 rounded" style="background:#f8f5ff; border:1px solid #d0b8f0; min-width:70px;">
                    <div class="fw-bold" style="font-size:16px; color:#6f42c1;">${total}</div>
                    <div style="font-size:11px; color:#555;">${nome}</div>
                    <div style="font-size:10px; color:#999;">~${pct}/ap</div>
                </div>`;
            }).join('');
            document.getElementById('analis_grupo_stats').innerHTML = grupoHtml;

            loading.style.display = 'none';
            resultado.style.display = '';
            analisCurrentPage = 1;
            analisRenderPage(1);
        }, 50);
    }

    function analisRenderPage(page) {
        const perPage = parseInt(document.getElementById('analis_perpage').value);
        const total = analisData.length;
        const totalPages = Math.max(1, Math.ceil(total / perPage));
        page = Math.max(1, Math.min(page, totalPages));
        analisCurrentPage = page;

        document.getElementById('analis_paginfo').textContent = `p\u00e1g. ${page}/${totalPages}`;
        document.getElementById('btn_prev_pag').disabled = page <= 1;
        document.getElementById('btn_next_pag').disabled = page >= totalPages;

        const slice = analisData.slice((page-1)*perPage, page*perPage);
        const tbody = document.getElementById('analis_tbody');

        const MES_COR = ANALIS_MESES_COR;

        tbody.innerHTML = slice.map((ap, i) => {
            const rowIdx = (page-1)*perPage + i + 1;
            const bg = (rowIdx % 2 === 0) ? '#fafafa' : '#fff';
            if (ap.erro) {
                return `<tr style="background:#fff5f5;">
                    <td class="text-center text-muted">${ap.idx}</td>
                    <td colspan="14" class="text-danger text-start px-3"><i class="fas fa-exclamation-triangle me-1"></i>${ap.erro}</td>
                    <td class="text-center"><span class="badge bg-danger">Erro</span></td>
                </tr>`;
            }
            const dezenasStr = ap.dezenas.map(d => d.toString().padStart(2,'0')).join(' &bull; ');
            const mesBadge = `<span class="badge" style="background:${MES_COR[ap.mesNum] || '#6f42c1'}; font-size:11px;">${ap.mesNome}</span>`;
            const grupoCols = ANALIS_GRUPOS_KEYS.map(k => {
                const v = ap.contagem[k];
                return `<td class="text-center fw-bold ${v > 0 ? 'text-success' : 'text-muted'}">${v}</td>`;
            }).join('');
            const ativosCount = ap.gruposAtivos.length;
            let statusBadge;
            if (ativosCount >= 7) statusBadge = '<span class="badge bg-success">Espalhada</span>';
            else if (ativosCount >= 5) statusBadge = '<span class="badge bg-info text-dark">Boa</span>';
            else if (ativosCount >= 3) statusBadge = '<span class="badge bg-warning text-dark">M\u00e9dia</span>';
            else statusBadge = '<span class="badge bg-secondary">Concentrada</span>';

            return `<tr style="background:${bg};" onmouseover="this.style.background='#f0e8ff'" onmouseout="this.style.background='${bg}'">
                <td class="text-center text-muted">${ap.idx}</td>
                <td class="text-center fw-bold" style="font-family:monospace; letter-spacing:1px; white-space:nowrap;">${dezenasStr}</td>
                <td class="text-center">${mesBadge}</td>
                ${grupoCols}
                <td class="text-center">
                    <span class="badge" style="background:#6f42c1; font-size:12px;">${ativosCount} grupo${ativosCount !== 1 ? 's' : ''}</span>
                </td>
                <td class="text-center">${statusBadge}</td>
            </tr>`;
        }).join('');

        // Bottom pagination
        const paginationHtml = Array.from({length: Math.min(totalPages, 10)}, (_, i) => {
            const p = i + 1;
            return `<button class="btn btn-sm ${p === page ? 'btn-primary' : 'btn-outline-secondary'}" onclick="analisRenderPage(${p})" style="${p === page ? 'background:#6f42c1; border-color:#6f42c1;' : ''}">${p}</button>`;
        }).join('');
        document.getElementById('analis_pagination_bottom').innerHTML = paginationHtml;
    }

    function analisLimpar() {
        document.getElementById('analis_textarea').value = '';
        document.getElementById('analis_line_count').textContent = '0 linhas';
        document.getElementById('analis_resultado').style.display = 'none';
        document.getElementById('analis_counter_badge').style.display = 'none';
        analisData = [];
    }
"""

if JS_ANCHOR in content:
    content = content.replace(JS_ANCHOR, ANALIS_JS + "\n" + JS_ANCHOR, 1)
    open('templates/gerador_especial.html', 'w', encoding='utf-8').write(content)
    print("OK - JS inserted")
else:
    print("JS ANCHOR NOT FOUND")
    idx = content.find('hash foi removido')
    print("hash at:", idx)
    print(repr(content[idx:idx+80]))
