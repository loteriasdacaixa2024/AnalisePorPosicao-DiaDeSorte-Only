/**
 * Aba 6A — Gerador Atraso Posicional Experimental (saltos configuráveis).
 * Independente da Aba 6 original.
 */
(function () {
    const API = '/gerador-especial/api/gerar_atraso_posicao_experimental';
    let cache = null;
    let carregando = false;
    let jaAberta = false;
    let gabarito = null;
    let gabaritoMes = null;
    let concursoConf = null;
    let mostrarPreenchimento = false;
    let mostrarAjuste = false;
    let mostrarColFaltantes = false;
    let concursosCarregados = false;
    let subAbaAtiva = 'original';

    const TABELA_PRECO = { 7: 2.5, 8: 20, 9: 90, 10: 300, 11: 825, 12: 1980, 13: 4290, 14: 8580, 15: 16087.5 };
    const ORDEM_LABELS = ['1º<br>SORTEIO', '2º<br>SORTEIO', '3º<br>SORTEIO', '4º<br>SORTEIO', '5º<br>SORTEIO', '6º<br>SORTEIO', '7º<br>SORTEIO'];

    function el(id) { return document.getElementById(id); }

    function limiteSaltoMax() {
        const r = document.querySelector('input[name="atraso6a_limite"]:checked');
        return r ? parseInt(r.value, 10) : 30;
    }

    const saltosStore = {
        global: { mais: 1, menos: 1 },
        col: {
            mais: [1, 1, 1, 1, 1, 1, 1],
            menos: [1, 1, 1, 1, 1, 1, 1]
        }
    };

    function modoSaltoColuna() {
        const m = el('atraso6a_salto_modo');
        return m && m.value === 'por_coluna';
    }

    function persistirSaltosUi() {
        if (modoSaltoColuna()) {
            for (let p = 1; p <= 7; p++) {
                const sm = el('atraso6a_salto_col_' + p);
                const sn = el('atraso6a_salto_col_menos_' + p);
                if (sm) saltosStore.col.mais[p - 1] = parseInt(sm.value, 10) || 1;
                if (sn) saltosStore.col.menos[p - 1] = parseInt(sn.value, 10) || 1;
            }
        } else {
            const gm = el('atraso6a_salto_global');
            const gn = el('atraso6a_salto_global_menos');
            if (gm) saltosStore.global.mais = parseInt(gm.value, 10) || 1;
            if (gn) saltosStore.global.menos = parseInt(gn.value, 10) || 1;
        }
    }

    function sincronizarSaltosUi() {
        if (modoSaltoColuna()) {
            for (let p = 1; p <= 7; p++) {
                const sm = el('atraso6a_salto_col_' + p);
                const sn = el('atraso6a_salto_col_menos_' + p);
                if (sm) sm.value = String(saltosStore.col.mais[p - 1]);
                if (sn) sn.value = String(saltosStore.col.menos[p - 1]);
            }
        } else {
            const gm = el('atraso6a_salto_global');
            const gn = el('atraso6a_salto_global_menos');
            if (gm) gm.value = String(saltosStore.global.mais);
            if (gn) gn.value = String(saltosStore.global.menos);
        }
        atualizarResumoSaltos();
    }

    function atualizarResumoSaltos() {
        const box = el('atraso6a-resumo-saltos');
        if (!box) return;
        const fmtPar = (mais, menos) => mais.map((v, i) =>
            `<span class="badge bg-light text-dark border me-1 mb-1">${i + 1}º: <span class="text-success">+${v}</span>/<span class="text-danger">−${menos[i]}</span></span>`
        ).join('');
        if (modoSaltoColuna()) {
            box.innerHTML = `<div><strong>Por coluna</strong> — saltos do azul (esquerda <span class="text-success">+</span> / direita <span class="text-danger">−</span>)</div>
                <div class="mt-1">${fmtPar(saltosStore.col.mais, saltosStore.col.menos)}</div>`;
        } else {
            box.innerHTML = `<div><strong>Global</strong> — azul linhas + e − iguais em todas as colunas</div>
                <div class="mt-1"><span class="text-success fw-bold">+</span> <span class="badge bg-light text-dark border">${saltosStore.global.mais}</span>
                &nbsp; <span class="text-danger fw-bold">−</span> <span class="badge bg-light text-dark border">${saltosStore.global.menos}</span></div>`;
        }
    }

    function preencherSelectsSalto() {
        const max = limiteSaltoMax();
        const opts = Array.from({ length: max }, (_, i) => {
            const v = i + 1;
            return `<option value="${v}">${v}</option>`;
        }).join('');
        ['atraso6a_salto_global', 'atraso6a_salto_global_menos'].forEach(id => {
            const s = el(id);
            if (!s) return;
            const cur = s.value || '1';
            s.innerHTML = opts;
            s.value = String(Math.min(parseInt(cur, 10) || 1, max));
        });
        document.querySelectorAll('.atraso6a-salto-col-mais, .atraso6a-salto-col-menos').forEach(sel => {
            const cur = sel.value || '1';
            sel.innerHTML = opts;
            sel.value = String(Math.min(parseInt(cur, 10) || 1, max));
        });
        ['mais', 'menos'].forEach(dir => {
            saltosStore.global[dir] = Math.min(saltosStore.global[dir] || 1, max);
            saltosStore.col[dir] = saltosStore.col[dir].map(v => Math.min(v || 1, max));
        });
        sincronizarSaltosUi();
    }

    function saltosPayload() {
        persistirSaltosUi();
        const modoEl = el('atraso6a_salto_modo');
        const modo = modoEl ? modoEl.value : 'global';
        return {
            salto_modo: modo,
            salto_global: saltosStore.global.mais,
            salto_global_menos: saltosStore.global.menos,
            salto_simetrico: false,
            limite_salto_max: limiteSaltoMax(),
            saltos_coluna: saltosStore.col.mais.slice(),
            saltos_coluna_menos: saltosStore.col.menos.slice()
        };
    }

    function textoSaltosInfo(data) {
        const mais = data.saltos_coluna || [];
        const menos = data.saltos_coluna_menos || mais;
        const iguais = mais.length === menos.length && mais.every((v, i) => v === menos[i]);
        if (iguais) return mais.map(s => '±' + s).join(', ');
        return '+' + mais.join(', ') + ' / −' + menos.join(', ');
    }

    function obterFaltantes(ap) {
        const direct = ap.preenchimento || ap.faltantes_atrasadas || [];
        if (direct.length) return direct;
        const gridSet = new Set((ap.grid || []).filter(n => n != null));
        return (ap.aposta_final_numeros || []).filter(n => !gridSet.has(n));
    }

    function matrizTemFaltantes(data) {
        return (data.apostas || []).some(ap => obterFaltantes(ap).length > 0);
    }

    function colunasExtras(mostrarAj) {
        let n = 2;
        if (mostrarColFaltantes) n++;
        if (mostrarAj) n++;
        return n;
    }

    function dezenasCicloGrid(ap) {
        const nums = new Set();
        (ap.grid || []).forEach((n, i) => {
            if (n != null && ap.grid_wrap && ap.grid_wrap[i]) nums.add(n);
        });
        return nums;
    }

    function repsNaAposta(nums) {
        const vistos = new Set();
        const reps = new Set();
        (nums || []).forEach(n => {
            if (vistos.has(n)) reps.add(n);
            vistos.add(n);
        });
        return reps;
    }

    function renderizarTabela6a(mostrarPre, mostrarAj) {
        if (!cache) return;
        mostrarPreenchimento = mostrarPre;
        mostrarAjuste = mostrarAj;
        mostrarColFaltantes = matrizTemFaltantes(cache);
        const data = cache;
        let tbody = '';
        let baseOk = false;
        const saltosTxt = textoSaltosInfo(data);

        data.apostas.forEach(ap => {
            if (ap.linha_offset > 0 && !baseOk) {
                tbody += `<tr style="background-color:#fff3cd;border:2px solid #333;">
                    <td class="fw-bold px-1 py-1">0</td>
                    ${data.dezenas_base.map(n => `<td class="fw-bold px-1 py-1" style="background-color:#ffc107;color:#000;">${("0"+n).slice(-2)}</td>`).join('')}
                    ${mostrarPre ? `<td colspan="${colunasExtras(mostrarAj)}" class="text-muted fw-bold py-1">SORTEIO BASE</td>` : ''}
                </tr>`;
                baseOk = true;
            }
            const cols = ap.grid.map((n, i) => {
                if (n === null) return `<td style="background-color:#f8f9fa;" class="px-1 py-1"></td>`;
                const wrap = ap.grid_wrap && ap.grid_wrap[i];
                const saltoLinha = ap.linha_offset >= 0
                    ? (data.saltos_coluna || [])[i]
                    : (data.saltos_coluna_menos || data.saltos_coluna || [])[i];
                if (wrap) {
                    return `<td style="background-color:#9EC5E8;color:#000;" class="fw-bold px-1 py-1" title="Azul — ciclo 31↔1 (salto ${saltoLinha})">${("0"+n).slice(-2)}</td>`;
                }
                return `<td style="background-color:#fff;color:#000;border:1px solid #dee2e6;" class="fw-bold px-1 py-1">${("0"+n).slice(-2)}</td>`;
            }).join('');
            let row = `<tr><td class="fw-bold px-1 py-1 ${ap.linha_offset < 0 ? 'text-danger' : 'text-success'}" style="cursor:pointer;" title="Linha ${ap.linha_offset}: azul usa salto ${ap.linha_offset < 0 ? '−' : '+'} — clique para ir aos controles" onclick="atraso6aEditarLinha(${ap.linha_offset})">${ap.linha_offset}</td>${cols}`;
            if (mostrarPre) {
                const falt = obterFaltantes(ap);
                const faltSet = new Set(falt);
                const cicloSet = dezenasCicloGrid(ap);
                const ac = typeof contarAcertos === 'function' ? contarAcertos(ap.aposta_final_numeros, gabarito) : 0;
                let finalHtml = ap.aposta_final_numeros.map(n => {
                    if (typeof badgeDezenaFinal === 'function') {
                        return badgeDezenaFinal(n, { gabarito, isCiclo: cicloSet.has(n) && !faltSet.has(n) });
                    }
                    return `<span class="badge bg-dark">${("0"+n).slice(-2)}</span>`;
                }).join('');
                if (gabarito && typeof badgeClassAcertosAtraso === 'function') {
                    finalHtml += `<span class="badge ${badgeClassAcertosAtraso(ac)} ms-1 px-2" style="font-size:10px;">${ac}/7</span>`;
                }
                if (mostrarColFaltantes) {
                    const fh = falt.map(n => `<span class="badge bg-danger mx-0" style="width:25px;height:25px;font-size:13px;display:inline-flex;justify-content:center;align-items:center;border-radius:8px;">${("0"+n).slice(-2)}</span>`).join('');
                    row += `<td class="py-1 col-faltantes-6a"><div class="d-flex justify-content-center gap-1">${fh}</div></td>`;
                }
                row += `<td class="py-1"><div class="d-flex justify-content-center gap-1">${finalHtml}</div></td>`;
                if (mostrarAj) {
                    const numsA = ap.aposta_ajustada_numeros || ap.aposta_final_numeros;
                    const reps = repsNaAposta(numsA);
                    const acA = typeof contarAcertos === 'function' ? contarAcertos(numsA, gabarito) : 0;
                    let ajHtml = numsA.map(n => {
                        if (typeof badgeDezenaAtraso === 'function') {
                            return badgeDezenaAtraso(n, {
                                gabarito,
                                isFalta: faltSet.has(n),
                                isExtraAjuste: !ap.aposta_final_numeros.includes(n),
                                isRepetido: reps.has(n)
                            });
                        }
                        return `<span class="badge bg-dark">${("0"+n).slice(-2)}</span>`;
                    }).join('');
                    if (gabarito && typeof badgeClassAcertosAtraso === 'function') {
                        ajHtml += `<span class="badge ${badgeClassAcertosAtraso(acA)} ms-1 px-2" style="font-size:10px;">${acA}/7</span>`;
                    }
                    row += `<td class="py-1"><div class="d-flex justify-content-center gap-1">${ajHtml}</div></td>`;
                }
                const mesOk = gabaritoMes && ap.mes_num === gabaritoMes.num;
                row += `<td class="py-1">${badgeMes6a(ap.mes_num, ap.mes_nome, mesOk)}</td>`;
            }
            row += '</tr>';
            tbody += row;
        });
        el('lista-apostas-atraso-6a').innerHTML = tbody;
        document.querySelectorAll('#painel-resultados-atraso-6a .col-preenchimento-6a').forEach(e => e.style.display = mostrarPre ? 'table-cell' : 'none');
        document.querySelectorAll('#painel-resultados-atraso-6a .col-faltantes-6a').forEach(e => {
            e.style.display = (mostrarPre && mostrarColFaltantes) ? 'table-cell' : 'none';
        });
        document.querySelectorAll('#painel-resultados-atraso-6a .col-ajuste-6a').forEach(e => e.style.display = mostrarAj ? 'table-cell' : 'none');
        document.querySelectorAll('#painel-resultados-atraso-6a .btn-export-ajuste-6a').forEach(e => e.style.display = mostrarAj ? 'inline-block' : 'none');
        const badgeInfo = el('atraso6a-info-saltos');
        if (badgeInfo) badgeInfo.textContent = 'Saltos: ' + saltosTxt;
    }

    function montarPainel(data) {
        mostrarColFaltantes = matrizTemFaltantes(data);
        const padF = mostrarColFaltantes ? 1 : 0;
        const thF = mostrarColFaltantes ? '<th class="col-preenchimento-6a col-faltantes-6a" style="display:none;">Faltantes</th>' : '';
        const thead = `<tr>
            <th class="px-1" style="width:40px;font-size:11px;">Linha</th>
            ${data.dezenas_base.map((n, i) => `<th class="px-1" style="font-size:10px;">${ORDEM_LABELS[i]}</th>`).join('')}
            ${thF}
            <th class="col-preenchimento-6a" style="display:none;">FINAL</th>
            <th class="col-ajuste-6a col-preenchimento-6a" style="display:none;background:#0d6efd;color:#fff;">Ajustada</th>
            <th class="col-preenchimento-6a" style="display:none;">Mês</th>
        </tr>`;
        const tfoot = `<tfoot id="tfoot-conferencia-6a" style="display:none;background:#f8f9fa;">
            <tr><td colspan="${data.dezenas_base.length + 2 + padF}" style="border:none;"></td>
            <td style="border:none;text-align:center;padding-top:10px;">
                <button class="btn btn-sm btn-outline-dark fw-bold bg-white" style="font-size:11px;" onclick="enviarParaVisualizador6a('original')"><i class="fas fa-eye text-warning"></i> SIMULADOR</button>
            </td>
            <td style="border:none;text-align:center;padding-top:10px;">
                <button class="btn btn-sm btn-outline-dark fw-bold bg-white" style="font-size:11px;" onclick="enviarParaVisualizador6a('ajustada')"><i class="fas fa-eye text-success"></i> SIMULADOR</button>
            </td><td style="border:none;"></td></tr>
            <tr><td colspan="${data.dezenas_base.length + 4 + padF}" style="border:none;text-align:center;padding:15px 0;">
                <button class="btn btn-sm btn-success fw-bold" onclick="enviarConferencia6a(event)"><i class="fas fa-check-double"></i> ENVIAR PARA CONFERÊNCIA</button>
            </td></tr>
        </tfoot>`;

        el('painel-resultados-atraso-6a').innerHTML = `
            <div class="card shadow border-info mt-3">
                <div class="card-header bg-dark text-white fw-bold d-flex justify-content-between align-items-center flex-wrap gap-2">
                    <span><i class="fas fa-flask text-info"></i> Matriz 6A (Concurso ${data.concurso_base})
                        <span id="atraso6a-info-saltos" class="badge bg-info text-dark ms-2"></span>
                        <span id="atraso6a-badge-conf" class="badge bg-success ms-2" style="display:none;"></span>
                    </span>
                    <div class="d-flex align-items-center gap-2 flex-wrap">
                        <span class="badge" style="background:#ffc107;color:#000;">Linha 0</span>
                        <span class="badge" style="background:#fff;color:#000;border:1px solid #ccc;">Linear</span>
                        <span class="badge" style="background:#9EC5E8;color:#000;">Ciclo 31↔1</span>
                        <button class="btn btn-sm btn-outline-light fw-bold" onclick="exportarAtrasoTXT6a(false)"><i class="fas fa-download"></i> Exportar</button>
                        <button class="btn btn-sm btn-outline-primary fw-bold btn-export-ajuste-6a" style="display:none;" onclick="exportarAtrasoTXT6a(true)"><i class="fas fa-download"></i> Exportar Ajuste</button>
                    </div>
                </div>
                <div id="painel-conferencia-atraso-6a" class="border-bottom bg-white px-3 py-2">
                    <div class="row align-items-end g-2">
                        <div class="col-md-3">
                            <label class="fw-bold text-secondary mb-1" style="font-size:12px;">Concurso alvo:</label>
                            <select id="atraso6a-select-concurso" class="form-select form-select-sm" onchange="preencherDezenasConf6a()"></select>
                        </div>
                        <div class="col-md-1 text-center text-muted fw-bold pb-2" style="font-size:11px;">OU</div>
                        <div class="col-md-4">
                            <label class="fw-bold text-secondary mb-1" style="font-size:12px;">Dezenas manuais:</label>
                            <input type="text" id="atraso6a-input-dezenas" class="form-control form-control-sm" placeholder="02, 09, 10, 13, 19, 26, 27">
                        </div>
                        <div class="col-md-2">
                            <button class="btn btn-success btn-sm w-100 fw-bold" onclick="conferirMatriz6a()"><i class="fas fa-check-double"></i> CONFERIR</button>
                        </div>
                        <div class="col-md-2">
                            <button class="btn btn-outline-secondary btn-sm w-100 fw-bold" onclick="limparConferencia6a()"><i class="fas fa-eraser"></i> LIMPAR</button>
                        </div>
                    </div>
                    <div id="resumo-conferencia-atraso-6a" class="mt-2"></div>
                </div>
                <div class="card-body bg-light p-1">
                    <div class="table-responsive">
                        <table class="table table-bordered table-sm mb-0 text-center">
                            <thead class="table-dark" style="font-size:13px;">${thead}</thead>
                            <tbody id="lista-apostas-atraso-6a"></tbody>
                            ${tfoot}
                        </table>
                    </div>
                </div>
            </div>`;
        concursosCarregados = false;
        carregarConcursosConf6a();
    }

    function alternarSubAbaAtraso(modo) {
        subAbaAtiva = modo;
        const orig = el('atraso-panel-original');
        const exp = el('atraso-panel-6a');
        const btnO = el('subaba-atraso-original');
        const btnE = el('subaba-atraso-6a');
        if (orig) orig.style.display = modo === 'original' ? 'block' : 'none';
        if (exp) exp.style.display = modo === 'experimental' ? 'block' : 'none';
        if (btnO) btnO.classList.toggle('active', modo === 'original');
        if (btnE) btnE.classList.toggle('active', modo === 'experimental');
    }

    window._initAtraso6aExperimental = function () {
        preencherSelectsSalto();
        atraso6aToggleModoSalto();
        if (!jaAberta) {
            jaAberta = true;
            const sel = el('atraso6a_concurso_base');
            if (sel) sel.value = 'ultimo';
            carregarMatriz6a({ autoPreencher: true });
        }
    };

    window.mostrarSubAbaAtraso = function (modo) {
        alternarSubAbaAtraso(modo);
        if (modo === 'experimental') {
            window._initAtraso6aExperimental();
        }
    };

    window.atraso6aAtualizarLimiteSalto = function () {
        preencherSelectsSalto();
    };

    window.atraso6aSalvarSaltos = function () {
        persistirSaltosUi();
        atualizarResumoSaltos();
    };

    window.atraso6aEditarLinha = function (linha) {
        if (linha === 0) return;
        persistirSaltosUi();
        const alvo = el('atraso6a-resumo-saltos');
        if (alvo) alvo.scrollIntoView({ behavior: 'smooth', block: 'center' });
        atualizarResumoSaltos();
        const box = el('atraso6a-resumo-saltos');
        if (box) {
            const lado = linha > 0 ? '+' : '−';
            const hint = `<div class="fw-bold text-warning mb-1"><i class="fas fa-hand-point-up"></i> Linha ${linha} → salto <span class="${linha > 0 ? 'text-success' : 'text-danger'}">${lado}</span> (células azuis)</div>`;
            box.innerHTML = hint + box.innerHTML;
            box.classList.add('border-warning');
            setTimeout(() => box.classList.remove('border-warning'), 2000);
        }
    };

    window.atraso6aToggleModoSalto = function () {
        persistirSaltosUi();
        const modoEl = el('atraso6a_salto_modo');
        const modo = modoEl ? modoEl.value : 'global';
        const wrapG = el('atraso6a-wrap-global');
        const wrapC = el('atraso6a-wrap-colunas');
        if (wrapG) wrapG.style.display = modo === 'global' ? 'flex' : 'none';
        if (wrapC) wrapC.style.display = modo === 'por_coluna' ? 'flex' : 'none';
        sincronizarSaltosUi();
    };

    window.atraso6aPresetSalto = function (v) {
        const max = limiteSaltoMax();
        v = Math.min(v, max);
        saltosStore.global.mais = v;
        saltosStore.global.menos = v;
        saltosStore.col.mais = [v, v, v, v, v, v, v];
        saltosStore.col.menos = [v, v, v, v, v, v, v];
        sincronizarSaltosUi();
    };

    /** Aplica saltos por coluna vindos da Busca Automática (não altera presets manuais). */
    window.atraso6aAplicarSaltosColuna = function (mais, menos, opts) {
        opts = opts || {};
        const max = limiteSaltoMax();
        const norm = (arr, fb) => {
            const a = (arr || []).slice(0, 7);
            while (a.length < 7) a.push(fb);
            return a.map(v => Math.max(1, Math.min(parseInt(v, 10) || fb, max)));
        };
        saltosStore.col.mais = norm(mais, 1);
        saltosStore.col.menos = norm(menos != null ? menos : mais, 1);
        saltosStore.global.mais = saltosStore.col.mais[0];
        saltosStore.global.menos = saltosStore.col.menos[0];
        const modoEl = el('atraso6a_salto_modo');
        if (modoEl) modoEl.value = 'por_coluna';
        atraso6aToggleModoSalto();
        sincronizarSaltosUi();
        if (opts.recarregar !== false) {
            carregarMatriz6a({ autoPreencher: true });
        }
    };

    window.carregarMatriz6a = function (opcoes) {
        opcoes = opcoes || {};
        if (carregando) return;
        const btnLoad = el('btn-carregar-matriz-6a');
        const btnFill = el('btn-preencher-matriz-6a');
        const btnEq = el('btn-equilibrar-matriz-6a');
        const loading = el('loading-atraso-6a');
        const painel = el('painel-resultados-atraso-6a');
        const selBase = el('atraso6a_concurso_base');
        const selDezenas = el('atraso6a_dezenas');
        const selMes = el('atraso6a_mes');
        if (!btnLoad || !selBase) {
            alert('Painel 6A ainda não carregou. Aguarde e tente novamente.');
            return;
        }
        carregando = true;
        btnLoad.disabled = true;
        if (btnFill) btnFill.style.display = 'none';
        if (btnEq) btnEq.style.display = 'none';
        if (loading) loading.style.display = 'block';
        if (painel) painel.innerHTML = '';
        cache = null;
        gabarito = null;

        const sp = saltosPayload();
        const payload = Object.assign({
            concurso_base_id: selBase.value,
            quantidade: 0,
            dezenas_por_jogo: selDezenas ? parseInt(selDezenas.value, 10) : 7,
            mes_tipo: selMes ? selMes.value : 'sequencial'
        }, sp);

        fetch(API, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) })
            .then(r => r.json())
            .then(data => {
                carregando = false;
                el('btn-carregar-matriz-6a').disabled = false;
                el('loading-atraso-6a').style.display = 'none';
                if (!data.sucesso) {
                    alert('Erro: ' + (data.mensagem || 'Falha na geração'));
                    return;
                }
                cache = data;
                el('atraso6a_quantidade').value = data.quantidade + ' apostas';
                const dz = parseInt(el('atraso6a_dezenas').value, 10) || 7;
                const total = data.quantidade * (TABELA_PRECO[dz] || 2.5);
                el('atraso6a_investimento').innerText = 'R$ ' + total.toLocaleString('pt-BR', { minimumFractionDigits: 2 });
                montarPainel(data);
                renderizarTabela6a(true, false);
                el('btn-preencher-matriz-6a').style.display = 'inline-block';
                if (opcoes.autoPreencher !== false) preencherMatriz6a();
            })
            .catch(err => {
                carregando = false;
                el('btn-carregar-matriz-6a').disabled = false;
                el('loading-atraso-6a').style.display = 'none';
                alert('Erro de conexão: ' + err);
            });
    };

    window.preencherMatriz6a = function () {
        renderizarTabela6a(true, false);
        el('btn-preencher-matriz-6a').style.display = 'none';
        el('btn-equilibrar-matriz-6a').style.display = 'inline-block';
        el('btn-carregar-matriz-6a').innerHTML = '<i class="fas fa-redo"></i> 1. RECARREGAR MATRIZ';
    };

    window.equilibrarMatriz6a = function () {
        renderizarTabela6a(true, true);
        el('btn-equilibrar-matriz-6a').style.display = 'none';
        const tf = el('tfoot-conferencia-6a');
        if (tf) tf.style.display = 'table-footer-group';
        if (gabarito) atualizarResumoConf6a();
    };

    function parseGabarito(val) {
        return val.split(/[,;\s]+/).map(x => parseInt(x.trim(), 10)).filter(x => !isNaN(x) && x > 0 && x <= 31);
    }

    function parseSelectConf6a(val) {
        if (!val) return null;
        const parts = val.split('|');
        return {
            dezenas: parts[0] || '',
            concurso: parts[1] || 'Manual',
            mesNum: parts[2] ? parseInt(parts[2], 10) : null,
            mesNome: parts[3] || null
        };
    }

    function badgeMes6a(mesNum, mesNome, acertou) {
        const star = acertou ? '⭐ ' : '';
        const ring = acertou ? ' box-shadow:0 0 0 2px #198754;' : '';
        return `<span class="badge mes-badge mes-cor-${mesNum} shadow-sm px-2 py-1${acertou ? '' : ' ms-2'}" style="font-size:12px;${ring}">${star}${mesNome}</span>`;
    }

    window.carregarConcursosConf6a = function () {
        const sel = el('atraso6a-select-concurso');
        if (!sel) return;
        fetch('/gerador-especial/api/ultimos-resultados')
            .then(r => r.json())
            .then(data => {
                if (!data.sucesso) return;
                sel.innerHTML = '<option value="">-- Selecione --</option>';
                data.sorteios.forEach(s => {
                    const dz = s.dezenas.map(n => ('0' + n).slice(-2)).join(', ');
                    sel.innerHTML += `<option value="${s.dezenas.join(',')}|${s.concurso}|${s.mes_num}|${s.mes_nome}">Concurso ${s.concurso} (${s.mes_nome}) — ${dz}</option>`;
                });
                concursosCarregados = true;
                if (cache && cache.concurso_base) {
                    const alvo = parseInt(cache.concurso_base, 10) + 1;
                    for (let i = 0; i < sel.options.length; i++) {
                        if (sel.options[i].value.endsWith('|' + alvo)) {
                            sel.selectedIndex = i;
                            preencherDezenasConf6a();
                            break;
                        }
                    }
                }
            });
    };

    window.preencherDezenasConf6a = function () {
        const sel = el('atraso6a-select-concurso');
        const input = el('atraso6a-input-dezenas');
        if (!sel || !input || !sel.value) return;
        const parts = sel.value.split('|');
        input.value = parts[0].split(',').map(n => ('0' + parseInt(n, 10)).slice(-2)).join(', ');
    };

    window.conferirMatriz6a = function () {
        if (!cache) return alert('Carregue a matriz primeiro!');
        const input = el('atraso6a-input-dezenas');
        const sel = el('atraso6a-select-concurso');
        if (!input.value.trim()) return alert('Informe o concurso alvo ou dezenas!');
        const g = parseGabarito(input.value);
        if (g.length < 7) return alert('Informe 7 dezenas válidas!');
        gabarito = new Set(g.slice(0, 7));
        if (sel && sel.value) {
            const info = parseSelectConf6a(sel.value);
            concursoConf = info.concurso;
            gabaritoMes = (info.mesNum && info.mesNome)
                ? { num: info.mesNum, nome: info.mesNome }
                : null;
        } else {
            concursoConf = 'Manual';
            gabaritoMes = null;
        }
        const b = el('atraso6a-badge-conf');
        if (b) { b.style.display = 'inline-block'; b.textContent = 'Conferindo: ' + concursoConf; }
        renderizarTabela6a(mostrarPreenchimento, mostrarAjuste);
        atualizarResumoConf6a();
    };

    window.limparConferencia6a = function () {
        gabarito = null;
        gabaritoMes = null;
        concursoConf = null;
        const b = el('atraso6a-badge-conf');
        if (b) b.style.display = 'none';
        el('resumo-conferencia-atraso-6a').innerHTML = '';
        if (cache) renderizarTabela6a(mostrarPreenchimento, mostrarAjuste);
    };

    function atualizarResumoConf6a() {
        const painel = el('resumo-conferencia-atraso-6a');
        if (!painel || !gabarito || !cache) return;
        const cont = (campo) => {
            const c = { 4: 0, 5: 0, 6: 0, 7: 0 };
            cache.apostas.forEach(ap => {
                const nums = campo === 'ajustada' ? (ap.aposta_ajustada_numeros || ap.aposta_final_numeros) : ap.aposta_final_numeros;
                const ac = typeof contarAcertos === 'function' ? contarAcertos(nums, gabarito) : 0;
                if (ac >= 4 && ac <= 7) c[ac]++;
            });
            return c;
        };
        const o = cont('final');
        const a = cont('ajustada');
        const dz = Array.from(gabarito).sort((x, y) => x - y).map(n => ('0' + n).slice(-2)).join(', ');
        const mesResumo = gabaritoMes ? badgeMes6a(gabaritoMes.num, gabaritoMes.nome, false) : '';
        painel.innerHTML = `<div class="alert alert-success py-2 mb-0 shadow-sm text-center">
            <div class="fw-bold d-flex flex-wrap align-items-center justify-content-center gap-2" style="font-size:13px;">
                <span>Concurso ${concursoConf}: ${dz}${mesResumo}</span>
                <span><strong>FINAL:</strong>
                    <span class="badge bg-secondary ms-1">4: ${o[4]}</span>
                    <span class="badge bg-success ms-1">5: ${o[5]}</span>
                    <span class="badge bg-primary ms-1">6: ${o[6]}</span>
                    <span class="badge bg-danger ms-1">7: ${o[7]}</span>
                </span>
                ${mostrarAjuste ? `<span><strong>Ajustada:</strong>
                    <span class="badge bg-secondary ms-1">4: ${a[4]}</span>
                    <span class="badge bg-success ms-1">5: ${a[5]}</span>
                    <span class="badge bg-primary ms-1">6: ${a[6]}</span>
                    <span class="badge bg-danger ms-1">7: ${a[7]}</span></span>` : ''}
            </div>
        </div>`;
    }

    window.exportarAtrasoTXT6a = function (ajuste) {
        if (!cache || !cache.apostas.length) return;
        let txt = '';
        cache.apostas.forEach(ap => {
            const nums = (ajuste ? ap.aposta_ajustada_numeros : ap.aposta_final_numeros).map(n => ('0' + n).slice(-2)).join(' ');
            const m = (typeof mesAbbr !== 'undefined' && mesAbbr[ap.mes_nome]) ? mesAbbr[ap.mes_nome] : ap.mes_nome;
            txt += nums + ' ' + m + '\r\n';
        });
        const blob = new Blob([txt], { type: 'text/plain;charset=utf-8' });
        const a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = (ajuste ? 'Gerador_6A_Ajustado_' : 'Gerador_6A_Salto_') + cache.concurso_base + '.txt';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    };

    window.enviarParaVisualizador6a = function (tipo) {
        if (!cache) return;
        let arr = [];
        if (tipo === 'original') arr = cache.apostas.map(ap => ap.aposta_final_numeros);
        else if (tipo === 'ajustada') arr = cache.apostas.map(ap => ap.aposta_ajustada_numeros || ap.aposta_final_numeros);
        localStorage.setItem('simuladorJogosTransfer', JSON.stringify(arr));
        window.open('/analise-visual/#pane-simulador-filtros', '_blank');
    };

    window.enviarConferencia6a = function (event) {
        if (!cache) return;
        const btn = event.currentTarget;
        const orig = btn.innerHTML;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Enviando...';
        btn.disabled = true;
        let matO = '', matA = '';
        cache.apostas.forEach(ap => {
            const m = (typeof mesAbbr !== 'undefined' && mesAbbr[ap.mes_nome]) ? mesAbbr[ap.mes_nome] : ap.mes_nome;
            matO += ap.aposta_final_numeros.map(n => ('0' + n).slice(-2)).join(' ') + ' ' + m + '\r\n';
            matA += (ap.aposta_ajustada_numeros || ap.aposta_final_numeros).map(n => ('0' + n).slice(-2)).join(' ') + ' ' + m + '\r\n';
        });
        fetch('/gerador-especial/api/enviar-conferencia', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ concurso_base: cache.concurso_base, matriz_original: matO, matriz_ajustada: matA })
        }).then(r => r.json()).then(data => {
            btn.innerHTML = orig;
            btn.disabled = false;
            if (data.sucesso) {
                alert('Enviado! ' + data.mensagem);
                window.location.href = '/central-conferencias#pane-conferencia-historica';
            } else alert(data.mensagem || 'Erro ao enviar');
        }).catch(() => { btn.innerHTML = orig; btn.disabled = false; });
    };

    el('atraso6a_concurso_base') && el('atraso6a_concurso_base').addEventListener('change', () => carregarMatriz6a({ autoPreencher: true }));
    el('atraso6a_dezenas') && el('atraso6a_dezenas').addEventListener('change', () => { if (cache) carregarMatriz6a({ autoPreencher: true }); });
    el('atraso6a_mes') && el('atraso6a_mes').addEventListener('change', () => { if (cache) carregarMatriz6a({ autoPreencher: true }); });

    preencherSelectsSalto();
    atraso6aToggleModoSalto();
})();
