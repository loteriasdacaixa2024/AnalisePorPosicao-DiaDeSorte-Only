/**
 * Aba Ciclo por Posição — /estatisticas
 */
(function () {
    'use strict';

    const API_RESUMO = '/api/estatisticas/ciclo-por-posicao/resumo';
    const API_GERAR = '/api/estatisticas/ciclo-por-posicao/gerar-apostas';

    let resumoCache = null;
    let posicaoSelecionada = 1;
    let apostasCompositor = [];
    let resumoRequestId = 0;
    /** @type {'pendentes'|'posicao'} */
    let ordenacaoModo = 'pendentes';

    const FETCH_TIMEOUT_MS = 90000;

    function pad(n) {
        return String(n).padStart(2, '0');
    }

    function el(id) {
        return document.getElementById(id);
    }

    function pendentesDaPosicao(d) {
        return d?.ciclo_atual?.dezenas_pendentes || [];
    }

    function atrasoMapaPosicao(p) {
        const c = resumoCache[p]?.ciclo_atual || {};
        const map = {};
        (c.pendentes_com_atraso || []).forEach((x) => {
            map[x.dezena] = x.atraso;
        });
        return map;
    }

    function ordenarPosicoes() {
        const pos = [1, 2, 3, 4, 5, 6, 7];
        if (ordenacaoModo === 'posicao') {
            return pos;
        }
        return pos.sort((a, b) => {
            const pa = pendentesDaPosicao(resumoCache[a]).length;
            const pb = pendentesDaPosicao(resumoCache[b]).length;
            return pb - pa || a - b;
        });
    }

    function posicaoComMaisPendentes() {
        return ordenarPosicoes()[0];
    }

    function atualizarBotaoOrdenacao() {
        const btn = el('cicloPosBtnOrdenar');
        if (!btn) return;
        if (ordenacaoModo === 'pendentes') {
            btn.innerHTML = '<i class="fas fa-sort-numeric-down"></i> Ordenar por posição (1→7)';
            btn.title = 'Clique para ordenar cards e tabela na ordem Posição 1, 2, 3…';
        } else {
            btn.innerHTML = '<i class="fas fa-sort-amount-down"></i> Ordenar por pendentes';
            btn.title = 'Clique para ordenar da posição com mais pendentes para a com menos';
        }
    }

    function textoOrdenacaoAtual() {
        return ordenacaoModo === 'pendentes'
            ? 'Ordenado da posição com <strong>mais pendentes</strong> para a com menos.'
            : 'Ordenado por <strong>posição</strong> (1ª bola → 7ª bola).';
    }

    function badgesPendentes(nums, extraClass) {
        if (!nums?.length) return '<span class="text-muted small">—</span>';
        const cls = extraClass ? ` ${extraClass}` : '';
        return nums.map((n) => `<span class="ciclo-pendente-badge${cls}">${pad(n)}</span>`).join('');
    }

    function badgesComAtraso(itens) {
        if (!itens?.length) return '<span class="text-muted small">—</span>';
        return itens
            .map(
                (x) =>
                    `<span class="ciclo-pendente-badge ciclo-pendente-atraso" title="Atraso na posição: ${x.atraso} conc.">${pad(x.dezena)}${x.atraso > 0 ? `<small class="ciclo-atraso-num">${x.atraso}</small>` : ''}</span>`
            )
            .join('');
    }

    function matrizCruzadaPendentes() {
        const porDezena = {};
        for (let n = 1; n <= 31; n++) {
            porDezena[n] = { dezena: n, posicoes: [], maxAtraso: 0 };
        }
        for (let p = 1; p <= 7; p++) {
            const atrasos = atrasoMapaPosicao(p);
            pendentesDaPosicao(resumoCache[p]).forEach((n) => {
                porDezena[n].posicoes.push(p);
                porDezena[n].maxAtraso = Math.max(porDezena[n].maxAtraso, atrasos[n] || 0);
            });
        }
        return porDezena;
    }

    async function fetchComTimeout(url, opcoes = {}) {
        const ctrl = new AbortController();
        const timer = setTimeout(() => ctrl.abort(), FETCH_TIMEOUT_MS);
        try {
            return await fetch(url, { ...opcoes, signal: ctrl.signal });
        } catch (e) {
            if (e.name === 'AbortError') {
                throw new Error(
                    'A consulta demorou demais. Reinicie o servidor (DiaDeSorte_POSICAO.bat) e clique em Atualizar análise.'
                );
            }
            throw e;
        } finally {
            clearTimeout(timer);
        }
    }

    async function parseJsonResponse(r) {
        const text = await r.text();
        const ct = (r.headers.get('content-type') || '').toLowerCase();
        if (!ct.includes('application/json')) {
            if (text.trim().startsWith('<')) {
                if (r.status === 404) {
                    throw new Error(
                        'API não encontrada (404). Reinicie o servidor (DiaDeSorte_POSICAO.bat ou python app.py).'
                    );
                }
                throw new Error(`Servidor retornou HTML (HTTP ${r.status}). Reinicie o Flask.`);
            }
            throw new Error(`Resposta inválida (HTTP ${r.status}).`);
        }
        try {
            return JSON.parse(text);
        } catch (e) {
            throw new Error(`JSON inválido: ${e.message}`);
        }
    }

    function normalizarPosicoes(posicoes) {
        const out = {};
        if (!posicoes || typeof posicoes !== 'object') return out;
        for (let p = 1; p <= 7; p++) {
            const d = posicoes[p] || posicoes[String(p)];
            if (d) out[p] = d;
        }
        return out;
    }

    function copiarTexto(texto) {
        if (navigator.clipboard?.writeText) {
            navigator.clipboard.writeText(texto).then(
                () => alert('Copiado!'),
                () => fallbackCopy(texto)
            );
        } else {
            fallbackCopy(texto);
        }
    }

    function fallbackCopy(texto) {
        const ta = document.createElement('textarea');
        ta.value = texto;
        document.body.appendChild(ta);
        ta.select();
        document.execCommand('copy');
        document.body.removeChild(ta);
        alert('Copiado!');
    }

    function renderTudo() {
        renderResumoGrid();
        renderMapaPendentes();
        renderCruzamento();
        renderDetalhePosicao(posicaoSelecionada);
        atualizarBotaoOrdenacao();
        const hint = el('cicloPosOrdenacaoHint');
        if (hint) hint.innerHTML = textoOrdenacaoAtual();
    }

    function abaCicloPosicaoVisivel() {
        const pane = document.getElementById('ciclo-por-posicao');
        return pane && (pane.classList.contains('active') || pane.classList.contains('show'));
    }

    async function carregarResumo() {
        const box = el('cicloPosResumoGrid');
        if (!box) return;
        const reqId = ++resumoRequestId;

        const ts = el('cicloPosUltimaAtualizacao');
        if (ts) ts.textContent = 'Atualizando dados do banco…';

        if (!resumoCache) {
            box.innerHTML =
                '<div class="text-center py-4"><div class="spinner-border text-warning"></div><p class="small text-muted mt-2 mb-0">Carregando análise…</p></div>';
            const mapa = el('cicloPosMapaPendentes');
            if (mapa) mapa.innerHTML = '';
            const cruz = el('cicloPosCruzamento');
            if (cruz) cruz.innerHTML = '';
        }

        try {
            const r = await fetchComTimeout(API_RESUMO);
            if (reqId !== resumoRequestId) return;
            const j = await parseJsonResponse(r);
            if (!r.ok) throw new Error(j.erro || `Erro HTTP ${r.status}`);
            if (!j.sucesso || !j.posicoes) throw new Error(j.erro || 'Resposta inválida da API');

            resumoCache = normalizarPosicoes(j.posicoes);
            if (Object.keys(resumoCache).length < 7) throw new Error('Dados incompletos das 7 posições');

            if (!resumoCache[posicaoSelecionada]) {
                posicaoSelecionada = posicaoComMaisPendentes();
            }
            if (ts) {
                ts.textContent = `Atualizado: ${new Date().toLocaleString('pt-BR')}`;
            }
            apostasCompositor = [];
            try {
                renderTudo();
            } catch (renderErr) {
                console.error(renderErr);
                box.innerHTML = `<div class="alert alert-danger mb-0"><strong>Erro ao exibir:</strong> ${renderErr.message}</div>`;
            }
        } catch (e) {
            if (reqId !== resumoRequestId) return;
            box.innerHTML = `<div class="alert alert-danger mb-0"><strong>Erro ao carregar:</strong> ${e.message}</div>`;
            if (ts) ts.textContent = 'Falha na atualização.';
        }

        if (reqId === resumoRequestId) {
            setTimeout(carregarImpressaoSegundoPlano, 50);
        }
    }

    async function carregarImpressaoSegundoPlano() {
        const ult = el('cicloImpUltimo');
        const qtdImp = parseInt(el('cicloImpQtdApostas')?.value, 10) || 30;
        const dezImp = parseInt(el('cicloImpDezenas')?.value, 10) || 7;
        if (ult) {
            ult.innerHTML =
                '<span class="text-muted"><span class="spinner-border spinner-border-sm me-1"></span> Carregando impressão e apostas…</span>';
        }
        try {
            const r = await fetchComTimeout(
                `${API_RESUMO}?impressao=1&apostas=${qtdImp}&dezenas=${dezImp}`
            );
            const j = await parseJsonResponse(r);
            if (!r.ok) throw new Error(j.erro || `HTTP ${r.status}`);
            const pacote = j.impressao;
            if (!pacote?.sucesso) throw new Error(pacote?.erro || 'Falha na impressão');
            if (typeof window.cicloImpressao30AplicarPacote === 'function') {
                window.cicloImpressao30AplicarPacote(pacote);
            }
        } catch (e) {
            if (ult) {
                ult.innerHTML = `<span class="text-warning">Impressão: ${e.message}</span>`;
            }
        }
    }

    function aoAbrirAbaCicloPosicao() {
        carregarResumo();
    }

    function renderResumoGrid() {
        const box = el('cicloPosResumoGrid');
        if (!box || !resumoCache) return;

        const ordenadas = ordenarPosicoes();
        const topP = posicaoComMaisPendentes();
        const maxPend = pendentesDaPosicao(resumoCache[topP]).length;

        let html = '';
        ordenadas.forEach((p) => {
            const d = resumoCache[p];
            const ciclo = d.ciclo_atual || {};
            const prog = ciclo.progresso_pct || 0;
            const lista = pendentesDaPosicao(d);
            const pend = lista.length;
            const ativo = p === posicaoSelecionada ? ' ativo' : '';
            const destaque =
                ordenacaoModo === 'pendentes' && pend === maxPend && pend > 0 ? ' mais-pendentes' : '';
            const preview =
                pend > 8
                    ? `${lista.slice(0, 8).map(pad).join(' ')} … +${pend - 8}`
                    : lista.map(pad).join(' ') || '—';

            html += `
            <div class="ciclo-pos-card-pos${ativo}${destaque}" data-pos="${p}" role="button" tabindex="0"
                title="Ver ${pend} pendentes — ${lista.map(pad).join(' ')}">
                <div class="d-flex justify-content-between align-items-start">
                    <div class="fw-bold">Posição ${p}</div>
                    ${destaque ? '<span class="badge bg-warning text-dark">mais pend.</span>' : ''}
                </div>
                <div class="small text-muted mb-1">${prog}% do ciclo · <strong>${pend} pendentes</strong></div>
                <div class="prog mb-1"><div class="prog-bar" style="width:${prog}%"></div></div>
                <div class="small mb-1">Ciclo atual: <strong>${ciclo.concursos_no_ciclo || 0}</strong> conc.</div>
                <div class="ciclo-pos-card-pendentes small">${preview}</div>
            </div>`;
        });

        box.innerHTML = html;
        box.querySelectorAll('.ciclo-pos-card-pos').forEach((card) => {
            card.addEventListener('click', () => {
                posicaoSelecionada = parseInt(card.getAttribute('data-pos'), 10);
                renderTudo();
                document.getElementById(`ciclo-mapa-row-${posicaoSelecionada}`)?.scrollIntoView({
                    behavior: 'smooth',
                    block: 'nearest',
                });
            });
        });
    }

    function renderMapaPendentes() {
        const mapa = el('cicloPosMapaPendentes');
        if (!mapa || !resumoCache) return;

        const ordenadas = ordenarPosicoes();
        const topP = posicaoComMaisPendentes();
        const maxPend = pendentesDaPosicao(resumoCache[topP]).length;

        let rows = '';
        ordenadas.forEach((p) => {
            const d = resumoCache[p];
            const c = d.ciclo_atual || {};
            const lista = pendentesDaPosicao(d);
            const atrasos = atrasoMapaPosicao(p);
            const comAtraso =
                c.pendentes_com_atraso || lista.map((n) => ({ dezena: n, atraso: atrasos[n] || 0 }));
            const ativo = p === posicaoSelecionada ? ' ciclo-mapa-row-ativo' : '';
            const destaque =
                ordenacaoModo === 'pendentes' && lista.length === maxPend && maxPend > 0
                    ? ' ciclo-mapa-row-top'
                    : '';

            rows += `
            <tr class="ciclo-mapa-row${ativo}${destaque}" id="ciclo-mapa-row-${p}" data-pos="${p}">
                <td class="fw-bold text-nowrap">Posição ${p}</td>
                <td class="text-nowrap small">${c.progresso_pct ?? 0}%</td>
                <td class="text-nowrap small">${c.concursos_no_ciclo ?? 0}</td>
                <td class="text-center fw-bold">${lista.length}</td>
                <td class="ciclo-mapa-dezenas">${badgesComAtraso(comAtraso)}</td>
                <td class="text-nowrap">
                    <button type="button" class="btn btn-sm btn-outline-secondary py-0 px-1 ciclo-btn-copiar-linha" title="Copiar">
                        <i class="fas fa-copy"></i>
                    </button>
                </td>
            </tr>`;
        });

        mapa.innerHTML = `
            <table class="table table-sm table-hover mb-0 ciclo-pos-mapa">
                <thead class="table-light">
                    <tr>
                        <th>Posição</th><th>% ciclo</th><th>Conc.</th>
                        <th class="text-center">Qtd</th>
                        <th>Dezenas pendentes (nº pequeno = atraso)</th><th></th>
                    </tr>
                </thead>
                <tbody>${rows}</tbody>
            </table>`;

        mapa.querySelectorAll('.ciclo-mapa-row').forEach((row) => {
            row.addEventListener('click', (ev) => {
                if (ev.target.closest('.ciclo-btn-copiar-linha')) return;
                posicaoSelecionada = parseInt(row.getAttribute('data-pos'), 10);
                renderTudo();
            });
        });

        mapa.querySelectorAll('.ciclo-btn-copiar-linha').forEach((btn) => {
            btn.addEventListener('click', (ev) => {
                ev.stopPropagation();
                const pos = parseInt(btn.closest('.ciclo-mapa-row')?.getAttribute('data-pos'), 10);
                const lista = pendentesDaPosicao(resumoCache[pos]);
                copiarTexto(`P${pos} (${lista.length}): ${lista.map(pad).join(' ')}`);
            });
        });
    }

    function renderCruzamento() {
        const box = el('cicloPosCruzamento');
        if (!box || !resumoCache) return;

        const matriz = matrizCruzadaPendentes();
        const multi = Object.values(matriz)
            .filter((x) => x.posicoes.length >= 2)
            .sort(
                (a, b) =>
                    b.posicoes.length - a.posicoes.length ||
                    b.maxAtraso - a.maxAtraso ||
                    a.dezena - b.dezena
            );

        const linhasMulti = multi
            .map((x) => {
                const posTxt = x.posicoes.map((p) => `P${p}`).join(', ');
                return `<tr>
                <td class="fw-bold text-nowrap">${pad(x.dezena)}</td>
                <td class="text-center text-nowrap"><span class="badge bg-warning text-dark">${x.posicoes.length}</span></td>
                <td class="small">falta em <strong>${posTxt}</strong></td>
            </tr>`;
            })
            .join('');

        box.innerHTML = multi.length
            ? `<table class="table table-sm table-bordered mb-0 ciclo-pos-mapa">
                <thead class="table-light">
                    <tr><th>Dez.</th><th>Qtd pos.</th><th>Onde ainda não saiu neste ciclo</th></tr>
                </thead>
                <tbody>${linhasMulti}</tbody>
            </table>`
            : '<p class="small text-muted mb-0 p-2">Nenhuma dezena pendente em 2+ posições.</p>';
    }

    function scoreCandidata(item, variacao) {
        return (
            item.posicoes.length * 1000 +
            item.maxAtraso * 10 +
            ((item.dezena + variacao * 7) % 31)
        );
    }

    function montarUmaAposta(qtdDez, maxPorPos, variacao, jaUsadas) {
        const matriz = matrizCruzadaPendentes();
        let candidatas = Object.values(matriz).filter((x) => x.posicoes.length > 0);
        candidatas.sort((a, b) => scoreCandidata(b, variacao) - scoreCandidata(a, variacao));

        const usoPos = { 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0 };
        const escolhidas = [];

        function tentarIncluir(relaxar) {
            for (const item of candidatas) {
                if (escolhidas.length >= qtdDez) break;
                if (escolhidas.some((e) => e.dezena === item.dezena)) continue;
                const chave = escolhidas
                    .map((e) => e.dezena)
                    .concat(item.dezena)
                    .sort((a, b) => a - b)
                    .join('-');
                if (jaUsadas.has(chave)) continue;

                const limite = relaxar ? qtdDez : maxPorPos;
                if (!item.posicoes.every((p) => usoPos[p] < limite)) continue;

                escolhidas.push(item);
                item.posicoes.forEach((p) => {
                    usoPos[p]++;
                });
            }
        }

        tentarIncluir(false);
        if (escolhidas.length < qtdDez) tentarIncluir(true);

        if (!escolhidas.length) return null;

        const numeros = escolhidas.map((x) => x.dezena).sort((a, b) => a - b);
        return {
            numeros,
            escolhidas,
            usoPos,
            chave: numeros.join('-'),
        };
    }

    function renderResultadoCompositor() {
        const out = el('cicloPosCompResultado');
        if (!out) return;

        if (!apostasCompositor.length) {
            out.innerHTML =
                '<p class="text-muted mb-0">Clique em <strong>Gerar jogos</strong>. Cada linha = um volante para apostar.</p>';
            return;
        }

        const maxPorPos = parseInt(el('cicloPosCompMaxPos')?.value, 10) || 2;
        let html = `<p class="mb-2"><strong>${apostasCompositor.length} jogo(s)</strong> · máx. ${maxPorPos} dez./posição</p>`;
        apostasCompositor.forEach((j, i) => {
            const cov = j.escolhidas
                .map((x) => `${pad(x.dezena)}→P${x.posicoes.join('/')}`)
                .join(' ');
            html += `<div class="ciclo-comp-jogo-linha">
                <strong>${i + 1}.</strong> <span class="fw-bold">${j.numeros.map(pad).join(' ')}</span>
                <div class="text-muted" style="font-size:11px">${cov}</div>
            </div>`;
        });
        out.innerHTML = html;
    }

    function montarJogoCompositor() {
        const out = el('cicloPosCompResultado');
        if (!resumoCache || !out) return;

        const qtdDez = parseInt(el('cicloPosCompQtd')?.value, 10) || 7;
        const maxPorPos = parseInt(el('cicloPosCompMaxPos')?.value, 10) || 2;
        const qtdJogos = parseInt(el('cicloPosCompQtdJogos')?.value, 10) || 5;

        out.innerHTML = '<p class="text-muted mb-0">Gerando…</p>';
        apostasCompositor = [];
        const jaUsadas = new Set();

        for (let v = 0; v < qtdJogos; v++) {
            const j = montarUmaAposta(qtdDez, maxPorPos, v, jaUsadas);
            if (j && j.numeros.length >= qtdDez) {
                jaUsadas.add(j.chave);
                apostasCompositor.push(j);
            }
        }

        if (!apostasCompositor.length) {
            out.innerHTML =
                '<div class="alert alert-warning small mb-0">Não foi possível montar. Clique em <strong>Atualizar análise</strong> e tente de novo.</div>';
            return;
        }

        renderResultadoCompositor();
    }

    function exportarCompositorTxt() {
        if (!apostasCompositor.length) {
            alert('Clique em Gerar jogos antes de exportar.');
            return;
        }
        const linhas = apostasCompositor.map((j) => j.numeros.map(pad).join(' '));
        const blob = new Blob([linhas.join('\n')], { type: 'text/plain;charset=utf-8' });
        const a = document.createElement('a');
        const data = new Date().toISOString().slice(0, 10);
        a.href = URL.createObjectURL(blob);
        a.download = `ciclo_posicao_jogos_${data}.txt`;
        a.click();
        URL.revokeObjectURL(a.href);
    }

    function copiarTodasPendentes() {
        if (!resumoCache) return;
        const linhas = ordenarPosicoes().map((p) => {
            const lista = pendentesDaPosicao(resumoCache[p]);
            return `P${p} (${lista.length}): ${lista.map(pad).join(' ')}`;
        });
        copiarTexto(linhas.join('\n'));
    }

    function renderDetalhePosicao(p) {
        const det = el('cicloPosDetalhe');
        if (!det || !resumoCache?.[p]) return;

        const d = resumoCache[p];
        const c = d.ciclo_atual || {};
        const m = d.metricas_fechados || {};
        const todasPendentes = pendentesDaPosicao(d);
        const comAtraso = c.pendentes_com_atraso || todasPendentes.map((n) => ({ dezena: n, atraso: 0 }));
        const saidas = (c.dezenas_saidas || []).slice().sort((a, b) => a - b);
        const ult = c.ultimo;
        const textoCopia = `P${p} (${todasPendentes.length}): ${todasPendentes.map(pad).join(' ')}`;

        det.innerHTML = `
            <div class="row g-3">
                <div class="col-lg-7">
                    <div class="d-flex flex-wrap justify-content-between align-items-center gap-2 mb-2">
                        <h6 class="fw-bold mb-0"><i class="fas fa-sync-alt text-warning"></i> Detalhe — Posição ${p}</h6>
                        <button type="button" class="btn btn-sm btn-outline-warning" id="cicloPosBtnCopiarPos">
                            <i class="fas fa-copy"></i> Copiar ${todasPendentes.length} pendentes
                        </button>
                    </div>
                    <ul class="small mb-2">
                        <li>Concursos no ciclo: <strong>${c.concursos_no_ciclo || 0}</strong></li>
                        <li>Progresso: <strong>${c.progresso_pct || 0}%</strong> (${saidas.length}/31 saíram)</li>
                        <li>Último: conc. <strong>${ult ? ult.concurso : '—'}</strong> → <strong>${ult ? pad(ult.dezena) : '—'}</strong></li>
                    </ul>
                    <p class="fw-bold small mb-1">Todas as pendentes (${todasPendentes.length}):</p>
                    <div class="ciclo-pos-lista-completa mb-3">${badgesComAtraso(comAtraso)}</div>
                    <p class="fw-bold small mb-1 text-muted">Já saíram (${saidas.length}):</p>
                    <div class="ciclo-pos-lista-saidas">${badgesPendentes(saidas, ' ciclo-saida-badge')}</div>
                </div>
                <div class="col-lg-5">
                    <h6 class="fw-bold"><i class="fas fa-chart-line"></i> Histórico fechados</h6>
                    <ul class="small">
                        <li>Média: <strong>${m.media_concursos ?? '—'}</strong> · Mín: <strong>${m.minimo ?? '—'}</strong> · Máx: <strong>${m.maximo ?? '—'}</strong></li>
                    </ul>
                    <table class="table table-sm table-bordered mb-0">
                        <thead><tr><th>#</th><th>Início</th><th>Fim</th><th>Conc.</th></tr></thead>
                        <tbody>${(d.historico_ciclos || [])
                            .map(
                                (h) => `<tr>
                            <td>${h.numero}${h.em_aberto ? ' <span class="badge bg-warning text-dark">aberto</span>' : ''}</td>
                            <td>${h.concurso_inicio}</td><td>${h.concurso_fim || '—'}</td><td>${h.concursos}</td>
                        </tr>`
                            )
                            .join('')}</tbody>
                    </table>
                </div>
            </div>`;

        el('cicloPosBtnCopiarPos')?.addEventListener('click', () => copiarTexto(textoCopia));
    }

    function alternarOrdenacao() {
        ordenacaoModo = ordenacaoModo === 'pendentes' ? 'posicao' : 'pendentes';
        renderTudo();
    }

    async function gerarApostas() {
        const status = el('cicloPosGeradorStatus');
        const lista = el('cicloPosApostasLista');
        const qtd = parseInt(el('cicloPosQtdApostas')?.value, 10) || 10;
        const dez = parseInt(el('cicloPosQtdDezenas')?.value, 10) || 7;
        const focoVal = el('cicloPosFoco')?.value;
        const foco = focoVal === 'todas' ? null : parseInt(focoVal, 10);

        if (status) {
            status.className = 'alert alert-secondary py-2 small';
            status.textContent = 'Gerando apostas…';
        }
        if (lista) lista.innerHTML = '';

        try {
            const r = await fetch(API_GERAR, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ quantidade: qtd, dezenas_por_aposta: dez, posicao_foco: foco }),
            });
            const j = await parseJsonResponse(r);
            if (!r.ok) throw new Error(j.erro || `Erro HTTP ${r.status}`);
            if (!j.sucesso) throw new Error(j.erro || 'Falha na geração');

            if (status) {
                status.className = 'alert alert-success py-2 small';
                status.innerHTML = `<strong>${j.quantidade} apostas</strong> · ${j.dezenas_por_aposta} dez.<br><span class="text-muted">${j.estrategia}</span>`;
            }

            let html = '';
            j.apostas.forEach((ap, i) => {
                const nums = ap.numeros.map(pad).join(' ');
                const cov = ap.cobertura_pendentes
                    .map((x) => `P${x.posicao}: ${x.pendentes_cobertas.map(pad).join(',')}`)
                    .join(' · ');
                html += `<div class="ciclo-aposta-linha"><strong>${i + 1}.</strong> ${nums}
                    <span class="text-muted small"> — ${ap.qtd_pendentes_no_jogo} pend. (${cov || '—'})</span></div>`;
            });
            if (lista) lista.innerHTML = html || '<p class="small text-muted mb-0">Nenhuma aposta.</p>';

            const sim = el('cicloPosSimOrcamento');
            if (sim && j.simulacao_orcamento) {
                sim.innerHTML = `<ul class="small mb-0">${Object.entries(j.simulacao_orcamento)
                    .map(
                        ([pos, s]) =>
                            `<li>P${pos}: ${s.percentual_fecharia ?? '—'}% com ${s.n} conc.</li>`
                    )
                    .join('')}</ul>`;
            }
        } catch (e) {
            if (status) {
                status.className = 'alert alert-danger py-2 small';
                status.textContent = e.message;
            }
        }
    }

    function exportarTxt() {
        const linhas = [];
        document.querySelectorAll('#cicloPosApostasLista .ciclo-aposta-linha').forEach((row) => {
            const t = row.textContent.replace(/^\d+\.\s*/, '').split('—')[0].trim();
            if (t) linhas.push(t.replace(/\s+/g, ' '));
        });
        if (!linhas.length) {
            alert('Gere as apostas antes.');
            return;
        }
        const blob = new Blob([linhas.join('\n')], { type: 'text/plain;charset=utf-8' });
        const a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = 'ciclo_por_posicao_apostas.txt';
        a.click();
        URL.revokeObjectURL(a.href);
    }

    function init() {
        el('cicloPosBtnAtualizar')?.addEventListener('click', carregarResumo);
        el('cicloPosBtnOrdenar')?.addEventListener('click', alternarOrdenacao);
        el('cicloPosBtnGerar')?.addEventListener('click', gerarApostas);
        el('cicloPosBtnExportar')?.addEventListener('click', exportarTxt);
        el('cicloPosBtnCopiarTodas')?.addEventListener('click', copiarTodasPendentes);
        el('cicloPosBtnMontarJogo')?.addEventListener('click', montarJogoCompositor);
        el('cicloPosCompExportar')?.addEventListener('click', exportarCompositorTxt);

        const tabCiclo = document.getElementById('ciclo-por-posicao-tab');
        tabCiclo?.addEventListener('shown.bs.tab', aoAbrirAbaCicloPosicao);

        atualizarBotaoOrdenacao();
        renderResultadoCompositor();

        if (abaCicloPosicaoVisivel()) {
            aoAbrirAbaCicloPosicao();
        }

        window.addEventListener('hashchange', () => {
            if (window.location.hash === '#ciclo-por-posicao' && abaCicloPosicaoVisivel()) {
                aoAbrirAbaCicloPosicao();
            }
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
