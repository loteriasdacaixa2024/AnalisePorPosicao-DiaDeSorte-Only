/**
 * Relatório Locais da Sorte — Dia de Sorte (Central de Conferências)
 */
(function () {
    'use strict';

    const API = {
        importar: '/api/locais-sorte-dia/importar',
        resumo: '/api/locais-sorte-dia/resumo',
        relatorio: '/api/locais-sorte-dia/relatorio',
        comparativo: '/api/locais-sorte-dia/comparativo',
        padroes: '/api/locais-sorte-dia/padroes-acertos',
    };

    let paginaAtual = 1;
    let porPagina = 50;
    let debounceTimer = null;
    let abaInicializada = false;
    let ordenacaoAtual = 'concurso';
    let ordemAtual = 'desc';

    function el(id) {
        return document.getElementById(id);
    }

    function fmtMoeda(v) {
        const n = Number(v) || 0;
        return n.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
    }

    function coletarFiltros() {
        const mapa = {
            'ls-filtro-concurso': 'concurso',
            'ls-filtro-local': 'local',
            'ls-filtro-acertos': 'acertos',
            'ls-filtro-estrategia': 'estrategia',
            'ls-filtro-tipo': 'tipo_aposta',
            'ls-filtro-canal': 'canal_vendas',
            'ls-filtro-cidade': 'cidade',
            'ls-filtro-loterica': 'unidade_loterica',
            'ls-filtro-valor': 'valor_premio',
            'ls-filtro-cotas': 'cotas',
            'ls-filtro-numeros': 'qtd_numeros_apostados',
            'ls-filtro-busca': 'busca_global',
        };
        const params = new URLSearchParams();
        Object.entries(mapa).forEach(([id, chave]) => {
            const campo = el(id);
            if (campo && campo.value.trim()) {
                params.set(chave, campo.value.trim());
            }
        });
        return params;
    }

    function badgeTipo(tipo) {
        const t = (tipo || 'Simples').toLowerCase();
        if (t.includes('bol')) {
            return '<span class="badge badge-bolao">Bolão</span>';
        }
        return '<span class="badge badge-simples">Simples</span>';
    }

    function badgeAcertos(faixa) {
        const f = (faixa || '').toLowerCase();
        const alto = f.includes('6') || f.includes('7');
        const cls = alto ? 'badge-acerto-alto' : 'badge-acerto-baixo';
        return `<span class="badge ${cls}">${faixa || '—'}</span>`;
    }

    async function fetchJson(url, opts) {
        const r = await fetch(url, opts);
        return r.json();
    }

    window.lsSincronizarJson = async function () {
        const btn = el('ls-btn-sync');
        const status = el('ls-status-sync');
        if (!btn) return;
        btn.disabled = true;
        status.textContent = 'Importando JSON → SQL...';
        status.className = 'small text-muted';
        try {
            const data = await fetchJson(API.importar, { method: 'POST' });
            if (data.sucesso !== false) {
                status.innerHTML = `<span class="text-success"><i class="fas fa-check"></i> ${data.registros_inseridos || 0} novos, ${data.registros_pulados || 0} já existentes, ${data.arquivos_processados || 0} arquivo(s)</span>`;
                if (data.erros && data.erros.length) {
                    status.innerHTML += `<br><span class="text-warning">${data.erros.join('; ')}</span>`;
                }
                await lsCarregarPainel();
            } else {
                status.innerHTML = `<span class="text-danger">${data.erro || 'Falha na importação'}</span>`;
            }
        } catch (e) {
            status.innerHTML = `<span class="text-danger">Erro: ${e.message}</span>`;
        } finally {
            btn.disabled = false;
        }
    };

    async function carregarResumo() {
        const data = await fetchJson(API.resumo);
        if (!data.sucesso) return;
        if (el('ls-kpi-registros')) el('ls-kpi-registros').textContent = data.total_registros.toLocaleString('pt-BR');
        if (el('ls-kpi-concursos')) el('ls-kpi-concursos').textContent = data.total_concursos;
        if (el('ls-kpi-premios')) el('ls-kpi-premios').textContent = fmtMoeda(data.soma_premios);
        if (el('ls-kpi-json')) el('ls-kpi-json').textContent = data.arquivos_json_pasta;
        if (el('ls-kpi-ultima')) el('ls-kpi-ultima').textContent = data.ultima_importacao || '—';
        if (el('ls-pasta-info')) el('ls-pasta-info').textContent = data.pasta_dados || '';
    }

    async function carregarTabela(pagina) {
        paginaAtual = pagina || 1;
        const tbody = el('ls-tbody-relatorio');
        if (!tbody) return;
        tbody.innerHTML = '<tr><td colspan="12" class="text-center py-4"><span class="spinner-border spinner-border-sm"></span> Carregando...</td></tr>';

        const params = coletarFiltros();
        params.set('pagina', String(paginaAtual));
        params.set('por_pagina', String(porPagina));
        params.set('ordenacao', ordenacaoAtual);
        params.set('ord_dir', ordemAtual);

        const data = await fetchJson(`${API.relatorio}?${params}`);
        if (!data.sucesso) {
            tbody.innerHTML = `<tr><td colspan="12" class="text-danger text-center">${data.erro || 'Erro'}</td></tr>`;
            return;
        }

        if (!data.dados.length) {
            tbody.innerHTML = '<tr><td colspan="12" class="text-center text-muted py-4">Nenhum registro. Clique em <strong>Sincronizar JSON</strong> para importar da pasta Dia-de-Sorte.</td></tr>';
        } else {
            tbody.innerHTML = data.dados.map((r) => `
                <tr>
                    <td><strong>${r.concurso}</strong></td>
                    <td class="small" style="white-space: nowrap;">${r.cidade || '—'}</td>
                    <td class="small" style="white-space: nowrap;" title="${r.razao_social || ''}${(r.unidade_loterica || '').toLowerCase().includes('canais eletronicos') ? ' — Apostas feitas online (aplicativo/site da Caixa) — não tem lotérica física associada!' : ''}">${r.unidade_loterica || '—'}</td>
                    <td>${badgeTipo(r.tipo_aposta)}</td>
                    <td>${badgeAcertos(r.faixa_acertos)}</td>
                    <td class="text-center">${r.qtd_numeros_apostados ?? '—'}</td>
                    <td>${r.canal_vendas || '—'}</td>
                    <td class="text-center">${r.cotas ?? '—'}</td>
                    <td class="premio-valor">${fmtMoeda(r.valor_premio)}</td>
                    <td><small>${r.premio || ''}</small></td>
                    <td><small class="text-muted">${r.data_importacao || '—'}</small></td>
                    <td><small class="text-muted" title="${r.arquivo_origem || ''}">${(r.arquivo_origem || '').slice(0, 18)}</small></td>
                </tr>
            `).join('');
        }

        if (el('ls-info-paginacao')) {
            const totalText = `${data.total} registro(s) filtrado(s)`;
            el('ls-info-paginacao').innerHTML = `<strong class="text-primary">${totalText}</strong> — Página ${data.pagina_atual} de ${data.paginas || 1}`;
        }
        if (el('ls-btn-pag-ant')) el('ls-btn-pag-ant').disabled = paginaAtual <= 1;
        if (el('ls-btn-pag-prox')) el('ls-btn-pag-prox').disabled = paginaAtual >= (data.paginas || 1);
    }

    function renderComparativo(data) {
        const tbodyBolao = el('ls-tbody-bolao-vs');
        if (tbodyBolao && data.comparador_aposta) {
            tbodyBolao.innerHTML = data.comparador_aposta.map((row) => `
                <tr>
                    <td>${badgeTipo(row.tipo_aposta)}</td>
                    <td class="text-end">${row.total_apostas}</td>
                    <td class="text-end premio-valor">${fmtMoeda(row.total_premios)}</td>
                    <td class="text-end">${fmtMoeda(row.premio_medio)}</td>
                </tr>
            `).join('');
        }

        const renderTop = (id, rows, cols) => {
            const tb = el(id);
            if (!tb || !rows) return;
            tb.innerHTML = rows.map((r) => `
                <tr>${cols.map((c) => `<td>${c(r)}</td>`).join('')}</tr>
            `).join('');
        };

        renderTop('ls-tbody-top-cidades', data.top_cidades, [
            (r) => r.cidade || '—',
            (r) => r.total_apostas,
            (r) => `<span class="premio-valor">${fmtMoeda(r.total_premios)}</span>`,
        ]);
        renderTop('ls-tbody-top-lotericas', data.top_lotericas, [
            (r) => {
                const lotericaText = r.loterica || '—';
                const isCanaisEletronicos = lotericaText.toLowerCase().includes('canais eletronicos');
                const tooltip = isCanaisEletronicos ? ' title="Apostas feitas online (aplicativo/site da Caixa) — não tem lotérica física associada!"' : '';
                return `<span${tooltip}>${lotericaText}</span> <small class="text-muted">(${r.cidade || ''})</small>`;
            },
            (r) => r.total_apostas,
            (r) => `<span class="premio-valor">${fmtMoeda(r.total_premios)}</span>`,
        ]);
        renderTop('ls-tbody-top-concursos', data.top_concursos, [
            (r) => `<strong>${r.concurso}</strong>`,
            (r) => r.total_apostas,
            (r) => `<span class="premio-valor">${fmtMoeda(r.total_premios)}</span>`,
        ]);
    }

    async function carregarComparativo() {
        const data = await fetchJson(API.comparativo);
        if (data.sucesso) renderComparativo(data);
    }

    async function carregarPadroes() {
        const data = await fetchJson(API.padroes);
        const tb = el('ls-tbody-padroes');
        if (!tb || !data.sucesso) return;
        tb.innerHTML = data.padroes.map((p) => `
            <tr>
                <td>${badgeAcertos(p.faixa_acertos)}</td>
                <td>${badgeTipo(p.tipo_aposta)}</td>
                <td class="text-end">${p.total}</td>
                <td class="text-end premio-valor">${fmtMoeda(p.soma_premios)}</td>
                <td class="text-end">${fmtMoeda(p.media_premio)}</td>
            </tr>
        `).join('');
    }

    window.lsCarregarPainel = async function () {
        await Promise.all([
            carregarResumo(),
            carregarTabela(paginaAtual),
            carregarComparativo(),
            carregarPadroes(),
        ]);
        atualizarIconesOrdenacao();
    };

    window.lsLimparFiltros = function () {
        document.querySelectorAll('.ls-filtro-input').forEach((inp) => { inp.value = ''; });
        paginaAtual = 1;
        lsCarregarPainel();
    };

    window.lsAplicarFiltros = function () {
        paginaAtual = 1;
        carregarTabela(1);
    };

    window.lsPaginaAnterior = function () {
        if (paginaAtual > 1) carregarTabela(paginaAtual - 1);
    };

    window.lsPaginaProxima = function () {
        carregarTabela(paginaAtual + 1);
    };

    function atualizarIconesOrdenacao() {
        // Update all sortable headers
        document.querySelectorAll('th.sortable').forEach(th => {
            const coluna = th.getAttribute('data-coluna');
            const icone = th.querySelector('i');
            if (coluna === ordenacaoAtual) {
                if (ordemAtual === 'desc') {
                    icone.className = 'fas fa-sort-down ms-1';
                } else {
                    icone.className = 'fas fa-sort-up ms-1';
                }
            } else {
                icone.className = 'fas fa-sort ms-1';
            }
        });
    }

    function bindEventos() {
        // Bind filter inputs
        document.querySelectorAll('.ls-filtro-input').forEach((inp) => {
            inp.addEventListener('input', () => {
                clearTimeout(debounceTimer);
                debounceTimer = setTimeout(() => {
                    paginaAtual = 1;
                    carregarTabela(1);
                }, 400);
            });
        });

        // Bind sortable headers
        document.querySelectorAll('th.sortable').forEach(th => {
            th.style.cursor = 'pointer';
            th.addEventListener('click', () => {
                const coluna = th.getAttribute('data-coluna');
                if (coluna === ordenacaoAtual) {
                    // Toggle direction
                    ordemAtual = ordemAtual === 'desc' ? 'asc' : 'desc';
                } else {
                    // New column, default to desc
                    ordenacaoAtual = coluna;
                    ordemAtual = 'desc';
                }
                atualizarIconesOrdenacao();
                paginaAtual = 1;
                carregarTabela(1);
            });
        });

        // Bind por página
        const pp = el('ls-por-pagina');
        if (pp) {
            pp.addEventListener('change', () => {
                porPagina = parseInt(pp.value, 10) || 50;
                carregarTabela(1);
            });
        }
    }

    window.lsInicializarAba = function () {
        if (abaInicializada) {
            lsCarregarPainel();
            return;
        }
        abaInicializada = true;
        bindEventos();
        lsSincronizarJson();
    };

    document.addEventListener('DOMContentLoaded', function () {
        const tabBtn = document.getElementById('tab-locais-sorte-dia');
        if (!tabBtn) return;
        tabBtn.addEventListener('shown.bs.tab', lsInicializarAba);
        if (window.location.hash === '#pane-locais-sorte-dia' || window.location.hash === '#locais-sorte-dia') {
            const tab = new bootstrap.Tab(tabBtn);
            tab.show();
            lsInicializarAba();
        }
    });
})();
