/**
 * Análise Visual de Colunas do volante — Dia de Sorte
 * Grade 10 colunas × 4 linhas (31 na coluna 1, linha 4).
 */
(function () {
    'use strict';

    const MAX_EXEMPLOS = 12;
    const MAX_EXEMPLOS_HOVER = 4;
    const MAX_EXEMPLOS_MODAL = 15;

    const VolanteColunasGeo = {
        colunas: [],

        init() {
            this.colunas = [];
            for (let c = 0; c < 10; c++) this.colunas[c] = [];
            for (let n = 1; n <= 31; n++) {
                let col;
                if (n === 31) col = 0;
                else col = (n - 1) % 10;
                this.colunas[col].push(n);
            }
        },

        getColuna(numero) {
            const n = parseInt(numero, 10);
            if (n === 31) return 0;
            if (n >= 1 && n <= 30) return (n - 1) % 10;
            return null;
        },
    };

    VolanteColunasGeo.init();

    function analiseColunasThresholdZerada(col) {
        return col.concursosZerada > 400;
    }

    function padDezena(n) {
        return String(n).padStart(2, '0');
    }

    function formatDezenasLista(nums) {
        return nums.map(padDezena).join(', ');
    }

    function formatDezenasET(nums) {
        if (nums.length <= 1) return formatDezenasLista(nums);
        const last = padDezena(nums[nums.length - 1]);
        return `${nums.slice(0, -1).map(padDezena).join(', ')} e ${last}`;
    }

    class AnaliseColunasAnalyzer {
        constructor() {
            this.colunasMeta = VolanteColunasGeo.colunas.map((dezenas, idx) => ({
                id: idx + 1,
                colIndex: idx,
                dezenas,
                dezenasTxt: dezenas.map((d) => padDezena(d)).join(', '),
                nome: `Coluna ${idx + 1}`,
                nomeCompleto: `Coluna ${idx + 1} (${dezenas.map((d) => padDezena(d)).join(' · ')})`,
                nomeInline: `Coluna ${idx + 1} → ${dezenas.map((d) => padDezena(d)).join(', ')}`,
                totalNumeros: dezenas.length,
            }));
            this._ultimaAnalise = null;
            this._tabelaState = { sortKey: 'id', sortDir: 'asc', filters: {} };
            this._tooltipEl = null;
        }

        _numsConcurso(conc) {
            const raw = conc.numeros_ordenados || conc.numeros || conc.dezenas || [];
            return [...raw].map(Number).filter((n) => n >= 1 && n <= 31);
        }

        _normalizarOrdem(concursos) {
            const arr = concursos.slice();
            if (arr.length >= 2 && arr[0].concurso < arr[arr.length - 1].concurso) {
                arr.reverse();
            }
            return arr;
        }

        _pushExemplo(lista, item) {
            if (lista.length < MAX_EXEMPLOS) lista.push(item);
        }

        calcularEstatisticas(concursos) {
            if (!concursos || !concursos.length) return null;

            const concursosAnalisar = this._normalizarOrdem(concursos);
            const totalConcursos = concursosAnalisar.length;

            const stats = this.colunasMeta.map((m) => ({
                ...m,
                frequenciaBolas: 0,
                concursosPresente: 0,
                concursosZerada: 0,
                frequenciaRecente: 0,
                atrasoAtual: 0,
                ocorreuNoUltimo: false,
                vezes1: 0,
                vezes2: 0,
                vezes3: 0,
                vezes4: 0,
                concursosComDupla: 0,
                concursosComTrinca: 0,
                concursosComQuadra: 0,
                exemplosDupla: [],
                exemplosTrinca: [],
                exemplosQuadra: [],
                exemplosZerada: [],
                exemplosPresenca: [],
            }));

            let concursosComDuplaGlobal = 0;
            let concursosComTrincaGlobal = 0;

            concursosAnalisar.forEach((conc, index) => {
                const numeros = this._numsConcurso(conc);
                const contagemPorCol = Array(10).fill(0);
                const numsPorCol = Array.from({ length: 10 }, () => []);

                numeros.forEach((num) => {
                    const col = VolanteColunasGeo.getColuna(num);
                    if (col === null) return;
                    contagemPorCol[col]++;
                    numsPorCol[col].push(num);
                    stats[col].frequenciaBolas++;
                });

                let duplaNoConcurso = false;
                let trincaNoConcurso = false;

                stats.forEach((stat) => {
                    const qtd = contagemPorCol[stat.colIndex];
                    const dezenasCol = [...numsPorCol[stat.colIndex]].sort((a, b) => a - b);
                    const concursoNum = conc.concurso;

                    if (qtd >= 1) {
                        stat.concursosPresente++;
                        if (index < 10) stat.frequenciaRecente++;
                        if (index === 0) stat.ocorreuNoUltimo = true;
                        this._pushExemplo(stat.exemplosPresenca, {
                            concurso: concursoNum,
                            dezenas: dezenasCol,
                        });
                    } else {
                        stat.concursosZerada++;
                        this._pushExemplo(stat.exemplosZerada, { concurso: concursoNum });
                    }

                    if (qtd === 1) stat.vezes1++;
                    else if (qtd === 2) {
                        stat.vezes2++;
                        stat.concursosComDupla++;
                        this._pushExemplo(stat.exemplosDupla, {
                            concurso: concursoNum,
                            dezenas: dezenasCol,
                        });
                    } else if (qtd === 3) {
                        stat.vezes3++;
                        stat.concursosComDupla++;
                        stat.concursosComTrinca++;
                        this._pushExemplo(stat.exemplosDupla, {
                            concurso: concursoNum,
                            dezenas: dezenasCol,
                        });
                        this._pushExemplo(stat.exemplosTrinca, {
                            concurso: concursoNum,
                            dezenas: dezenasCol,
                        });
                    } else if (qtd >= 4) {
                        stat.vezes4++;
                        stat.concursosComDupla++;
                        stat.concursosComTrinca++;
                        stat.concursosComQuadra++;
                        this._pushExemplo(stat.exemplosDupla, {
                            concurso: concursoNum,
                            dezenas: dezenasCol,
                        });
                        this._pushExemplo(stat.exemplosTrinca, {
                            concurso: concursoNum,
                            dezenas: dezenasCol,
                        });
                        this._pushExemplo(stat.exemplosQuadra, {
                            concurso: concursoNum,
                            dezenas: dezenasCol,
                        });
                    }

                    if (qtd >= 2) duplaNoConcurso = true;
                    if (qtd >= 3) trincaNoConcurso = true;
                });

                if (duplaNoConcurso) concursosComDuplaGlobal++;
                if (trincaNoConcurso) concursosComTrincaGlobal++;
            });

            stats.forEach((stat) => {
                let atraso = 0;
                for (let i = 0; i < concursosAnalisar.length; i++) {
                    const nums = this._numsConcurso(concursosAnalisar[i]);
                    const tem = nums.some((n) => VolanteColunasGeo.getColuna(n) === stat.colIndex);
                    if (tem) break;
                    atraso++;
                }
                stat.atrasoAtual = atraso;

                stat.percentual =
                    totalConcursos > 0
                        ? ((stat.concursosPresente / totalConcursos) * 100).toFixed(1)
                        : '0.0';
                stat.percentualNum = parseFloat(stat.percentual);
                stat.percentualZerada =
                    totalConcursos > 0
                        ? ((stat.concursosZerada / totalConcursos) * 100).toFixed(1)
                        : '0.0';
                stat.pctDupla =
                    totalConcursos > 0
                        ? ((stat.concursosComDupla / totalConcursos) * 100).toFixed(1)
                        : '0.0';
                stat.pctTrinca =
                    totalConcursos > 0
                        ? ((stat.concursosComTrinca / totalConcursos) * 100).toFixed(1)
                        : '0.0';
                stat.pctQuadra =
                    totalConcursos > 0
                        ? ((stat.concursosComQuadra / totalConcursos) * 100).toFixed(1)
                        : '0.0';
                stat.mediaBolasPorConcurso =
                    totalConcursos > 0
                        ? (stat.frequenciaBolas / totalConcursos).toFixed(2)
                        : '0.00';

                const prob = 1 - this._probZeroNaColuna(stat.totalNumeros);
                stat.esperado = prob * 100;
                stat.diferencaEsperado = parseFloat(stat.percentual) - stat.esperado;

                const esperadoRecente = prob * Math.min(10, totalConcursos);
                if (stat.frequenciaRecente > esperadoRecente * 1.15) {
                    stat.status = 'QUENTE';
                    stat.statusClass = 'status-quente';
                } else if (stat.frequenciaRecente < esperadoRecente * 0.85 || stat.atrasoAtual > 3) {
                    stat.status = 'FRIA';
                    stat.statusClass = 'status-fria';
                } else {
                    stat.status = 'NORMAL';
                    stat.statusClass = 'status-normal';
                }

                stat.rankVolume =
                    [...stats].sort((a, b) => b.frequenciaBolas - a.frequenciaBolas).findIndex((c) => c.id === stat.id) +
                    1;
            });

            const ranking = [...stats].sort((a, b) => b.frequenciaBolas - a.frequenciaBolas);
            const rankingDupla = [...stats].sort((a, b) => b.concursosComDupla - a.concursosComDupla);
            const rankingTrinca = [...stats].sort((a, b) => b.concursosComTrinca - a.concursosComTrinca);
            const porOrdemNumerica = [...stats].sort((a, b) => a.id - b.id);

            return {
                totalConcursos,
                ranking,
                colunas: stats,
                colunasOrdenadas: porOrdemNumerica,
                concursosComDuplaGlobal,
                concursosComTrincaGlobal,
                pctDuplaGlobal: totalConcursos
                    ? ((concursosComDuplaGlobal / totalConcursos) * 100).toFixed(1)
                    : '0.0',
                pctTrincaGlobal: totalConcursos
                    ? ((concursosComTrincaGlobal / totalConcursos) * 100).toFixed(1)
                    : '0.0',
                colMaisBolas: ranking[0],
                colMenosBolas: ranking[ranking.length - 1],
                colMaisDupla: rankingDupla[0],
                colMaisTrinca: rankingTrinca[0],
            };
        }

        _probZeroNaColuna(k) {
            if (k <= 0 || k > 31) return 1;
            let p = 1;
            for (let i = 0; i < 7; i++) {
                p *= (31 - k - i) / (31 - i);
            }
            return p;
        }

        _badgeRank(index) {
            if (index === 0) return '🏆';
            if (index === 1) return '🥈';
            if (index === 2) return '🥉';
            return '📊';
        }

        _barClass(index) {
            if (index === 0) return 'bar-top1';
            if (index === 1) return 'bar-top2';
            if (index === 2) return 'bar-top3';
            return 'bar-other';
        }

        _htmlListaExemplos(exemplos, formatFn, limite) {
            if (!exemplos || !exemplos.length) {
                return '<p class="col-tip-vazio mb-0">Nenhum registro no histórico.</p>';
            }
            const max = limite || MAX_EXEMPLOS_HOVER;
            const itens = exemplos
                .slice(0, max)
                .map((ex) => {
                    if (!ex.dezenas || !ex.dezenas.length) {
                        return `<li><b>${ex.concurso}</b> — zerada</li>`;
                    }
                    const dez = formatFn ? formatFn(ex.dezenas) : formatDezenasET(ex.dezenas);
                    return `<li><b>${ex.concurso}</b> → ${dez}</li>`;
                })
                .join('');
            const mais =
                exemplos.length > max
                    ? `<li class="col-tip-mais">+ ${exemplos.length - max} no histórico (use Detalhes)</li>`
                    : '';
            return `<ul class="col-tip-list-compact">${itens}${mais}</ul>`;
        }

        _htmlTooltipCelula(titulo, exemplos, formatFn) {
            return `
                <div class="col-mini-tip">
                    <div class="col-mini-tip-titulo">${titulo}</div>
                    ${this._htmlListaExemplos(exemplos, formatFn, MAX_EXEMPLOS_HOVER)}
                </div>`;
        }

        _tooltipHtmlCelula(tipo, col) {
            const map = {
                presenca: ['Presença', col.exemplosPresenca, formatDezenasLista],
                zerada: ['Zerada', col.exemplosZerada, null],
                dupla: ['Dupla (2×)', col.exemplosDupla, formatDezenasET],
                trinca: ['Trinca (3×)', col.exemplosTrinca, formatDezenasET],
                quadra: ['Quadra (4×)', col.exemplosQuadra, formatDezenasLista],
            };
            const cfg = map[tipo];
            if (!cfg) return '';
            return this._htmlTooltipCelula(cfg[0], cfg[1], cfg[2]);
        }

        _htmlModalColuna(col) {
            const tabs = [
                { id: 'pres', label: 'Presença', active: true },
                { id: 'dup', label: 'Dupla' },
                { id: 'tri', label: 'Trinca' },
            ];
            if (col.totalNumeros >= 4) tabs.push({ id: 'qua', label: 'Quadra' });
            tabs.push({ id: 'zer', label: 'Zerada' });

            const nav = tabs
                .map(
                    (t, i) => `
                <li class="nav-item" role="presentation">
                    <button class="nav-link${i === 0 ? ' active' : ''}" data-bs-toggle="tab"
                        data-bs-target="#colTab-${t.id}-${col.id}" type="button">${t.label}</button>
                </li>`
                )
                .join('');

            const panes = `
                <div class="tab-pane fade show active" id="colTab-pres-${col.id}" role="tabpanel">
                    ${this._htmlListaExemplos(col.exemplosPresenca, formatDezenasLista, MAX_EXEMPLOS_MODAL)}
                </div>
                <div class="tab-pane fade" id="colTab-dup-${col.id}" role="tabpanel">
                    ${this._htmlListaExemplos(col.exemplosDupla, formatDezenasET, MAX_EXEMPLOS_MODAL)}
                </div>
                <div class="tab-pane fade" id="colTab-tri-${col.id}" role="tabpanel">
                    ${this._htmlListaExemplos(col.exemplosTrinca, formatDezenasET, MAX_EXEMPLOS_MODAL)}
                </div>
                ${
                    col.totalNumeros >= 4
                        ? `<div class="tab-pane fade" id="colTab-qua-${col.id}" role="tabpanel">
                    ${this._htmlListaExemplos(col.exemplosQuadra, formatDezenasLista, MAX_EXEMPLOS_MODAL)}
                </div>`
                        : ''
                }
                <div class="tab-pane fade" id="colTab-zer-${col.id}" role="tabpanel">
                    ${this._htmlListaExemplos(col.exemplosZerada, null, MAX_EXEMPLOS_MODAL)}
                </div>`;

            return { nav, panes };
        }

        _ensureModal() {
            if (document.getElementById('modalDetalhesColunaVolante')) return;
            const wrap = document.createElement('div');
            wrap.innerHTML = `
            <div class="modal fade" id="modalDetalhesColunaVolante" tabindex="-1" aria-hidden="true">
                <div class="modal-dialog modal-dialog-centered modal-dialog-scrollable modal-md">
                    <div class="modal-content">
                        <div class="modal-header py-2" style="border-bottom:2px solid #D4B31A">
                            <h5 class="modal-title fw-bold" id="modalDetalhesColunaTitulo" style="font-size:1rem;color:#5b4c0b">
                                Detalhes da coluna
                            </h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Fechar"></button>
                        </div>
                        <div class="modal-body py-2">
                            <p id="modalDetalhesColunaResumo" class="small mb-2"></p>
                            <ul class="nav nav-tabs nav-tabs-sm mb-2" id="modalDetalhesColunaTabs" role="tablist"></ul>
                            <div class="tab-content col-modal-tab-body" id="modalDetalhesColunaConteudo"></div>
                        </div>
                    </div>
                </div>
            </div>`;
            document.body.appendChild(wrap.firstElementChild);
        }

        _abrirModalColuna(colId) {
            const col = this._ultimaAnalise?.colunas.find((c) => c.id === colId);
            if (!col) return;
            this._ensureModal();
            const titulo = document.getElementById('modalDetalhesColunaTitulo');
            const resumo = document.getElementById('modalDetalhesColunaResumo');
            const tabsEl = document.getElementById('modalDetalhesColunaTabs');
            const conteudo = document.getElementById('modalDetalhesColunaConteudo');
            if (!titulo || !tabsEl || !conteudo) return;

            titulo.textContent = col.nomeInline;
            resumo.innerHTML =
                `Total <strong>${col.frequenciaBolas}</strong> dezenas · Presença <strong>${col.percentual}%</strong> · ` +
                `Dupla <strong>${col.concursosComDupla}x</strong> · Trinca <strong>${col.concursosComTrinca}x</strong> · ` +
                `Status <span class="status-badge ${col.statusClass}">${col.status}</span>`;

            const { nav, panes } = this._htmlModalColuna(col);
            tabsEl.innerHTML = nav;
            conteudo.innerHTML = panes;

            const modalEl = document.getElementById('modalDetalhesColunaVolante');
            if (typeof bootstrap !== 'undefined' && modalEl) {
                bootstrap.Modal.getOrCreateInstance(modalEl).show();
            }
        }

        _ensureMiniTip() {
            if (this._tooltipEl) return this._tooltipEl;
            const el = document.createElement('div');
            el.className = 'col-analise-tooltip col-mini-tip-float';
            el.setAttribute('role', 'tooltip');
            document.body.appendChild(el);
            this._tooltipEl = el;
            return el;
        }

        _posicionarMiniTip(tip, anchorEl) {
            const ar = anchorEl.getBoundingClientRect();
            const margin = 10;
            let left = ar.right + margin;
            let top = ar.top;
            tip.style.left = `${left}px`;
            tip.style.top = `${top}px`;
            tip.classList.add('visible');
            const tr = tip.getBoundingClientRect();
            if (tr.right > window.innerWidth - 12) {
                left = Math.max(8, ar.left - tr.width - margin);
                tip.style.left = `${left}px`;
            }
            if (tr.bottom > window.innerHeight - 12) {
                top = Math.max(8, window.innerHeight - tr.height - 12);
                tip.style.top = `${top}px`;
            }
        }

        _bindInteracoesTabela(root) {
            const tip = this._ensureMiniTip();
            let hideTimer = null;
            let anchorAtual = null;

            const hide = () => {
                hideTimer = setTimeout(() => {
                    tip.classList.remove('visible');
                    anchorAtual = null;
                }, 150);
            };

            const show = (el) => {
                clearTimeout(hideTimer);
                const colId = parseInt(el.getAttribute('data-col-id'), 10);
                const tipo = el.getAttribute('data-col-tip');
                const col = this._ultimaAnalise?.colunas.find((c) => c.id === colId);
                if (!col || !tipo) return;
                tip.innerHTML = this._tooltipHtmlCelula(tipo, col);
                anchorAtual = el;
                this._posicionarMiniTip(tip, el);
            };

            root.querySelectorAll('[data-col-tip]').forEach((el) => {
                el.addEventListener('mouseenter', () => show(el));
                el.addEventListener('mouseleave', hide);
            });

            tip.addEventListener('mouseenter', () => clearTimeout(hideTimer));
            tip.addEventListener('mouseleave', hide);

            root.querySelectorAll('.col-btn-detalhes').forEach((btn) => {
                btn.addEventListener('click', (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    tip.classList.remove('visible');
                    const colId = parseInt(btn.getAttribute('data-col-id'), 10);
                    this._abrirModalColuna(colId);
                });
            });
        }

        _thSort(label, key, extraFilterHtml) {
            const st = this._tabelaState;
            const active = st.sortKey === key;
            const icon = active ? (st.sortDir === 'asc' ? 'fa-sort-up' : 'fa-sort-down') : 'fa-sort';
            return `
                <th class="col-th-interactive" data-sort-key="${key}">
                    <div class="col-th-wrap">
                        <span class="col-th-label">${label}</span>
                        <button type="button" class="col-th-sort-btn" data-sort-btn="${key}" title="Ordenar">
                            <i class="fas ${icon}"></i>
                        </button>
                        ${extraFilterHtml || ''}
                    </div>
                </th>`;
        }

        _renderLinhaTabela(col) {
            const quadraCell =
                col.totalNumeros >= 4
                    ? `<td class="text-end col-cell-compact col-has-quadra" data-col-id="${col.id}" data-col-tip="quadra">
                        <span class="col-val-main">${col.vezes4}</span><span class="col-val-pct">(${col.pctQuadra}%)</span>
                       </td>`
                    : `<td class="text-end text-muted col-cell-compact">—</td>`;

            const trClass = [
                col.concursosComTrinca > 0 ? 'col-row-trinca' : '',
                col.concursosComQuadra > 0 ? 'col-row-quadra' : '',
                col.concursosZerada > analiseColunasThresholdZerada(col) ? 'col-row-alta-zerada' : '',
            ]
                .filter(Boolean)
                .join(' ');

            return `
                <tr class="col-tabela-row ${trClass}"
                    data-col-id="${col.id}"
                    data-rank="${col.rankVolume}"
                    data-total="${col.frequenciaBolas}"
                    data-presenca="${col.percentualNum}"
                    data-zerada="${col.concursosZerada}"
                    data-vezes1="${col.vezes1}"
                    data-dupla="${col.concursosComDupla}"
                    data-trinca="${col.concursosComTrinca}"
                    data-quadra="${col.concursosComQuadra}"
                    data-status="${col.status}"
                    data-has-dupla="${col.concursosComDupla > 0 ? '1' : '0'}"
                    data-has-trinca="${col.concursosComTrinca > 0 ? '1' : '0'}"
                    data-has-quadra="${col.concursosComQuadra > 0 ? '1' : '0'}"
                    data-search="${col.nome} ${col.dezenasTxt}">
                    <td class="text-center col-cell-compact"><span class="col-rank-vol" title="Ranking por volume">${col.rankVolume}º</span></td>
                    <td class="col-cell-nome col-cell-compact">
                        <span class="col-nome-compact">${col.nomeInline}</span>
                        <button type="button" class="col-btn-detalhes" data-col-id="${col.id}"
                            title="Ver concursos (dupla, trinca, presença…)">
                            <i class="fas fa-list-alt"></i>
                        </button>
                    </td>
                    <td class="text-end col-cell-compact">${col.frequenciaBolas}</td>
                    <td class="text-end col-cell-compact" data-col-id="${col.id}" data-col-tip="presenca">${col.percentual}%</td>
                    <td class="text-end col-cell-compact text-danger" data-col-id="${col.id}" data-col-tip="zerada">${col.concursosZerada}</td>
                    <td class="text-end col-cell-compact">${col.vezes1}</td>
                    <td class="text-end col-cell-compact ${col.concursosComDupla > 0 ? 'col-highlight-dupla' : ''}" data-col-id="${col.id}" data-col-tip="dupla">
                        <span class="col-val-main">${col.vezes2}</span><span class="col-val-pct">(${col.pctDupla}%)</span>
                    </td>
                    <td class="text-end col-cell-compact ${col.concursosComTrinca > 0 ? 'col-highlight-trinca' : ''}" data-col-id="${col.id}" data-col-tip="trinca">
                        <span class="col-val-main">${col.vezes3}</span><span class="col-val-pct">(${col.pctTrinca}%)</span>
                    </td>
                    ${quadraCell}
                    <td class="col-cell-compact"><span class="status-badge ${col.statusClass}">${col.status}</span></td>
                </tr>`;
        }

        _aplicarFiltrosETabela(container) {
            const tbody = container.querySelector('#colunasTabelaBody');
            if (!tbody || !this._ultimaAnalise) return;

            const st = this._tabelaState;
            const busca = (st.filters.busca || '').toLowerCase().trim();
            const rows = [...tbody.querySelectorAll('.col-tabela-row')];

            rows.forEach((row) => {
                let vis = true;
                const search = (row.getAttribute('data-search') || '').toLowerCase();
                if (busca && !search.includes(busca)) vis = false;

                if (vis && st.filters.status) {
                    vis = row.getAttribute('data-status') === st.filters.status;
                }
                if (vis && st.filters.dupla === 'com') vis = row.getAttribute('data-has-dupla') === '1';
                if (vis && st.filters.dupla === 'sem') vis = row.getAttribute('data-has-dupla') === '0';
                if (vis && st.filters.trinca === 'com') vis = row.getAttribute('data-has-trinca') === '1';
                if (vis && st.filters.trinca === 'sem') vis = row.getAttribute('data-has-trinca') === '0';
                if (vis && st.filters.quadra === 'com') vis = row.getAttribute('data-has-quadra') === '1';
                if (vis && st.filters.presencaMin) {
                    vis = parseFloat(row.getAttribute('data-presenca')) >= parseFloat(st.filters.presencaMin);
                }
                if (vis && st.filters.zeradaMin) {
                    vis = parseInt(row.getAttribute('data-zerada'), 10) >= parseInt(st.filters.zeradaMin, 10);
                }

                row.style.display = vis ? '' : 'none';
            });

            const visiveis = rows.filter((r) => r.style.display !== 'none');
            const sorted = visiveis.sort((a, b) => {
                const key = st.sortKey;
                let va;
                let vb;
                if (key === 'id') {
                    va = parseInt(a.getAttribute('data-col-id'), 10);
                    vb = parseInt(b.getAttribute('data-col-id'), 10);
                } else if (key === 'nome') {
                    va = parseInt(a.getAttribute('data-col-id'), 10);
                    vb = parseInt(b.getAttribute('data-col-id'), 10);
                } else {
                    va = parseFloat(a.getAttribute(`data-${key}`)) || 0;
                    vb = parseFloat(b.getAttribute(`data-${key}`)) || 0;
                }
                if (va < vb) return st.sortDir === 'asc' ? -1 : 1;
                if (va > vb) return st.sortDir === 'asc' ? 1 : -1;
                return parseInt(a.getAttribute('data-col-id'), 10) - parseInt(b.getAttribute('data-col-id'), 10);
            });

            sorted.forEach((row) => tbody.appendChild(row));

            const contador = container.querySelector('#colunasTabelaContador');
            if (contador) {
                contador.textContent = `Exibindo ${visiveis.length} de ${rows.length} colunas`;
            }
        }

        _bindTabelaInterativa(container) {
            const self = this;

            container.querySelectorAll('[data-sort-btn]').forEach((btn) => {
                btn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    const key = btn.getAttribute('data-sort-btn');
                    if (self._tabelaState.sortKey === key) {
                        self._tabelaState.sortDir = self._tabelaState.sortDir === 'asc' ? 'desc' : 'asc';
                    } else {
                        self._tabelaState.sortKey = key;
                        self._tabelaState.sortDir = key === 'id' || key === 'nome' ? 'asc' : 'desc';
                    }
                    self._aplicarFiltrosETabela(container);
                    self._atualizarIconesSort(container);
                });
            });

            container.querySelectorAll('.col-th-filter').forEach((sel) => {
                sel.addEventListener('change', () => {
                    const f = sel.getAttribute('data-filter');
                    const v = sel.value;
                    if (v === '') delete self._tabelaState.filters[f];
                    else self._tabelaState.filters[f] = v;
                    self._aplicarFiltrosETabela(container);
                });
            });

            const buscaInput = container.querySelector('#colunasFiltroBusca');
            if (buscaInput) {
                buscaInput.addEventListener('input', () => {
                    self._tabelaState.filters.busca = buscaInput.value;
                    self._aplicarFiltrosETabela(container);
                });
            }

            const btnReset = container.querySelector('#colunasFiltroReset');
            if (btnReset) {
                btnReset.addEventListener('click', () => {
                    self._tabelaState = { sortKey: 'id', sortDir: 'asc', filters: {} };
                    container.querySelectorAll('.col-th-filter').forEach((s) => {
                        s.value = '';
                    });
                    if (buscaInput) buscaInput.value = '';
                    self._aplicarFiltrosETabela(container);
                    self._atualizarIconesSort(container);
                });
            }

            this._bindInteracoesTabela(container);
            this._aplicarFiltrosETabela(container);
        }

        _atualizarIconesSort(container) {
            const st = this._tabelaState;
            container.querySelectorAll('[data-sort-btn]').forEach((btn) => {
                const key = btn.getAttribute('data-sort-btn');
                const icon = btn.querySelector('i');
                if (!icon) return;
                icon.className =
                    'fas ' + (st.sortKey === key ? (st.sortDir === 'asc' ? 'fa-sort-up' : 'fa-sort-down') : 'fa-sort');
            });
        }

        renderizar(containerId, dadosConcursos) {
            const container = document.getElementById(containerId);
            if (!container) return;

            const analise = this.calcularEstatisticas(dadosConcursos);
            if (!analise || !analise.ranking.length) {
                container.innerHTML =
                    '<div class="alert alert-warning">Não foi possível calcular a análise de colunas.</div>';
                return;
            }

            this._ultimaAnalise = analise;
            this._tabelaState = { sortKey: 'id', sortDir: 'asc', filters: {} };

            const top3 = analise.ranking.slice(0, 3);
            const colMaisAtrasada = [...analise.colunas].sort((a, b) => b.atrasoAtual - a.atrasoAtual)[0];
            const colMaisQuente = [...analise.colunas].sort(
                (a, b) => b.diferencaEsperado - a.diferencaEsperado
            )[0];
            const colMaiorCrescimento = [...analise.colunas].sort(
                (a, b) => b.frequenciaRecente - a.frequenciaRecente
            )[0];

            const cardsTop3 = top3
                .map((col, index) => {
                    const rankGeral = col.rankVolume;
                    return `
                <div class="ranking-card top-${index + 1}">
                    <div class="ranking-badge">${this._badgeRank(index)}</div>
                    <div class="ranking-title">${index + 1}º Lugar &rarr; ${col.nomeCompleto}</div>
                    <div class="ranking-stats">
                        <div class="stat-item">
                            <span class="stat-label">Dezenas sorteadas</span>
                            <span class="stat-value">${col.frequenciaBolas} <small class="text-muted">(${col.mediaBolasPorConcurso}/conc.)</small></span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">Presença</span>
                            <span class="stat-value">${col.concursosPresente} concursos</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">Zerada</span>
                            <span class="stat-value text-danger">${col.concursosZerada} vezes</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">Dupla na coluna</span>
                            <span class="stat-value">${col.concursosComDupla}x <small class="text-muted">(${col.pctDupla}%)</small></span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">Trinca na coluna</span>
                            <span class="stat-value">${col.concursosComTrinca}x <small class="text-muted">(${col.pctTrinca}%)</small></span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">Tendência (10 conc.)</span>
                            <span class="stat-value">${col.frequenciaRecente} presenças</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">Status</span>
                            <span class="status-badge ${col.statusClass}">${col.status}</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">Ranking geral</span>
                            <span class="stat-value">${rankGeral}º de 10</span>
                        </div>
                    </div>
                </div>`;
                })
                .join('');

            const linhasTabela = analise.colunasOrdenadas.map((col) => this._renderLinhaTabela(col)).join('');

            const barras = analise.colunasOrdenadas
                .map((col) => {
                    const rankIdx = analise.ranking.findIndex((c) => c.id === col.id);
                    const pctBar = Math.min(
                        100,
                        (col.frequenciaBolas / analise.colMaisBolas.frequenciaBolas) * 100
                    ).toFixed(1);
                    return `
                <div class="linha-bar-container">
                    <div class="linha-label" title="${col.dezenasTxt}">Col ${col.id}</div>
                    <div class="linha-progress-wrap">
                        <div class="linha-progress ${this._barClass(rankIdx)}" style="width:${pctBar}%;"></div>
                    </div>
                    <div class="linha-percent">${col.frequenciaBolas}</div>
                </div>`;
                })
                .join('');

            container.innerHTML = `
            <div class="analise-linhas-container analise-colunas-container">
                <div class="analise-linhas-header">
                    <h3 class="analise-linhas-title">
                        <i class="fas fa-columns"></i> ANÁLISE DE COLUNAS (VOLANTE)
                    </h3>
                    <span class="badge bg-secondary">${analise.totalConcursos} concursos</span>
                </div>

                <div class="alert alert-light border py-2 px-3 small mb-3" style="border-left:4px solid #D4B31A!important;">
                    <strong>Coluna</strong> = mesma vertical do volante (ex.: Col 1 → 01, 11, 21, 31).
                    <strong>Dupla</strong> = 2 dezenas da mesma coluna no mesmo concurso;
                    <strong>trinca</strong> = 3; <strong>quadra</strong> = 4 (só Col 1).
                    Passe o mouse em <strong>Presença / Zerada / Dupla / Trinca</strong> para ver até 4 concursos.
                    Clique no ícone <i class="fas fa-list-alt"></i> na coluna para abrir o painel completo com abas.
                </div>

                <div class="ranking-grid colunas-top3-grid">${cardsTop3}</div>

                <div class="tendencia-section">
                    <h4 class="section-title"><i class="fas fa-chart-bar"></i> Volume por coluna (ordem 1 → 10)</h4>
                    ${barras}
                </div>

                <div class="table-responsive mb-3 colunas-tabela-wrap">
                    <div class="d-flex flex-wrap justify-content-between align-items-center gap-2 mb-2">
                        <h4 class="section-title mb-0"><i class="fas fa-table"></i> Todas as 10 colunas</h4>
                        <div class="colunas-filtro-busca-wrap">
                            <i class="fas fa-search text-muted"></i>
                            <input type="search" id="colunasFiltroBusca" class="form-control form-control-sm"
                                placeholder="Buscar coluna ou dezena…" autocomplete="off">
                            <button type="button" class="btn btn-outline-secondary btn-sm" id="colunasFiltroReset" title="Limpar filtros">
                                <i class="fas fa-undo"></i>
                            </button>
                        </div>
                    </div>
                    <p id="colunasTabelaContador" class="small text-muted mb-1">Exibindo 10 de 10 colunas</p>
                    <table class="table table-sm table-bordered analise-colunas-tabela mb-0" id="colunasTabelaPrincipal">
                        <thead class="table-light">
                            <tr>
                                ${this._thSort('Vol.', 'rank')}
                                ${this._thSort('Coluna / Dezenas', 'id')}
                                ${this._thSort('Total', 'total')}
                                ${this._thSort('Presença', 'presenca', `<select class="col-th-filter" data-filter="presencaMin" title="Presença mínima %"><option value="">%</option><option value="50">≥50%</option><option value="60">≥60%</option><option value="70">≥70%</option></select>`)}
                                ${this._thSort('Zerada', 'zerada', `<select class="col-th-filter" data-filter="zeradaMin" title="Zerada mín."><option value="">Zer.</option><option value="300">≥300</option><option value="400">≥400</option><option value="500">≥500</option></select>`)}
                                ${this._thSort('1×', 'vezes1')}
                                ${this._thSort('Dupla', 'dupla', `<select class="col-th-filter" data-filter="dupla" title="Dupla"><option value="">2×</option><option value="com">Com</option><option value="sem">Sem</option></select>`)}
                                ${this._thSort('Trinca', 'trinca', `<select class="col-th-filter" data-filter="trinca" title="Trinca"><option value="">3×</option><option value="com">Com</option><option value="sem">Sem</option></select>`)}
                                ${this._thSort('Quadra', 'quadra', `<select class="col-th-filter" data-filter="quadra" title="Quadra"><option value="">4×</option><option value="com">Com</option></select>`)}
                                <th class="col-th-interactive">
                                    <div class="col-th-wrap">
                                        <span class="col-th-label">Status</span>
                                        <select class="col-th-filter" data-filter="status" title="Status">
                                            <option value="">Todos</option>
                                            <option value="QUENTE">Quente</option>
                                            <option value="NORMAL">Normal</option>
                                            <option value="FRIA">Fria</option>
                                        </select>
                                    </div>
                                </th>
                            </tr>
                        </thead>
                        <tbody id="colunasTabelaBody">${linhasTabela}</tbody>
                    </table>
                </div>

                <div class="insights-grid insights-grid-colunas-centered">
                    <div class="insight-item">
                        <i class="fas fa-fire insight-icon"></i>
                        <div class="insight-content">
                            <span class="insight-label">Coluna com mais dezenas</span>
                            <span class="insight-value-text">${analise.colMaisBolas.nomeCompleto}</span>
                        </div>
                    </div>
                    <div class="insight-item">
                        <i class="fas fa-snowflake insight-icon"></i>
                        <div class="insight-content">
                            <span class="insight-label">Coluna com menos dezenas</span>
                            <span class="insight-value-text">${analise.colMenosBolas.nomeCompleto}</span>
                        </div>
                    </div>
                    <div class="insight-item">
                        <i class="fas fa-link insight-icon"></i>
                        <div class="insight-content">
                            <span class="insight-label">Mais duplas na mesma coluna</span>
                            <span class="insight-value-text">${analise.colMaisDupla.nomeCompleto} (${analise.colMaisDupla.concursosComDupla}x)</span>
                        </div>
                    </div>
                    <div class="insight-item">
                        <i class="fas fa-th insight-icon"></i>
                        <div class="insight-content">
                            <span class="insight-label">Mais trincas na mesma coluna</span>
                            <span class="insight-value-text">${analise.colMaisTrinca.nomeCompleto} (${analise.colMaisTrinca.concursosComTrinca}x)</span>
                        </div>
                    </div>
                    <div class="insight-item">
                        <i class="fas fa-chart-line insight-icon"></i>
                        <div class="insight-content">
                            <span class="insight-label">Maior tendência recente</span>
                            <span class="insight-value-text">${colMaiorCrescimento.nomeCompleto}</span>
                        </div>
                    </div>
                    <div class="insight-item">
                        <i class="fas fa-hourglass-half insight-icon"></i>
                        <div class="insight-content">
                            <span class="insight-label">Coluna mais atrasada</span>
                            <span class="insight-value-text">${colMaisAtrasada.nomeCompleto} <small class="text-muted">(${colMaisAtrasada.atrasoAtual} conc.)</small></span>
                        </div>
                    </div>
                    <div class="insight-item sugestao-aposta">
                        <i class="fas fa-lightbulb insight-icon"></i>
                        <div class="insight-content">
                            <span class="insight-label">Resumo do histórico</span>
                            <span class="insight-value-text">
                                Em <strong>${analise.pctDuplaGlobal}%</strong> dos concursos houve <strong>dupla</strong> em alguma coluna;
                                em <strong>${analise.pctTrincaGlobal}%</strong> houve <strong>trinca</strong> em alguma coluna.
                                Coluna mais quente vs esperado: <strong>${colMaisQuente.nome}</strong>.
                            </span>
                        </div>
                    </div>
                </div>
            </div>`;

            this._bindTabelaInterativa(container);

            setTimeout(() => {
                container.querySelectorAll('.linha-progress').forEach((bar) => {
                    const width = bar.style.width;
                    bar.style.width = '0%';
                    setTimeout(() => {
                        bar.style.width = width;
                    }, 100);
                });
            }, 50);
        }
    }

    const analiseColunasEngine = new AnaliseColunasAnalyzer();
    window.analiseColunasEngine = analiseColunasEngine;
})();
