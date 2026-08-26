/**
 * Mutação Controlada — derivações dos 10 jogos Elite (originais + mutados).
 * Preserva 60–80% do núcleo; altera apenas dezenas secundárias com score/ união.
 */
(function () {
    'use strict';

    const MutacaoControladaManager = {
        originais: [],
        mutados: [],
        metricas: null,
        scoreUniaoPares: [],
        uniaoIndex: {},

        _pad(n) {
            return String(n).padStart(2, '0');
        },

        _uniqSorted(arr) {
            return [...new Set(arr)].filter((n) => n >= 1 && n <= 31).sort((a, b) => a - b);
        },

        _jogoKey(jogo) {
            return this._uniqSorted(jogo).join(',');
        },

        _existeJogoIgual(jogo, lista) {
            return lista.some((j) => this._jogoKey(j) === this._jogoKey(jogo));
        },

        _overlap(a, b) {
            const sa = new Set(this._uniqSorted(a));
            return this._uniqSorted(b).filter((n) => sa.has(n)).length;
        },

        _variarJogoUnico(jogoBase, existentes, pool) {
            if (!this._existeJogoIgual(jogoBase, existentes)) return this._uniqSorted(jogoBase).slice(0, 7);
            const base = this._uniqSorted(jogoBase);
            for (let s = 0; s < base.length; s++) {
                for (const cand of pool) {
                    if (base.includes(cand)) continue;
                    const alt = this._uniqSorted([...base.slice(0, s), ...base.slice(s + 1), cand]);
                    if (alt.length === 7 && !this._existeJogoIgual(alt, existentes)) return alt;
                }
            }
            for (let d = 1; d <= 31; d++) {
                const alt = this._uniqSorted([...base.slice(0, 6), d]);
                if (alt.length === 7 && !this._existeJogoIgual(alt, existentes)) return alt;
            }
            return base.slice(0, 7);
        },

        async carregarScoreUniao() {
            try {
                const r = await fetch('/api/concentracao/score-uniao?limite=250');
                const data = await r.json();
                if (data.sucesso) {
                    this.scoreUniaoPares = data.pares || [];
                    this.uniaoIndex = {};
                    this.scoreUniaoPares.forEach((p) => {
                        const k = p.a < p.b ? `${p.a}-${p.b}` : `${p.b}-${p.a}`;
                        this.uniaoIndex[k] = p.score;
                    });
                }
            } catch (e) {
                console.warn('[Mutação]', e);
            }
        },

        montarPesos() {
            const mgr = window.SimuladorEliteManager;
            const pesos = {};
            const add = (n, w) => {
                if (n >= 1 && n <= 31) pesos[n] = (pesos[n] || 0) + w;
            };
            if (mgr && typeof mgr.coletarPontuacaoDezenas === 'function') {
                Object.entries(mgr.coletarPontuacaoDezenas()).forEach(([n, v]) => add(parseInt(n, 10), v * 2));
            }
            (this.scoreUniaoPares || []).slice(0, 60).forEach((p) => {
                add(p.a, p.score * 10);
                add(p.b, p.score * 10);
            });
            for (let d = 1; d <= 31; d++) {
                if (pesos[d] === undefined) pesos[d] = 0;
            }
            return pesos;
        },

        rankingPesos(pesos) {
            return Object.entries(pesos)
                .sort((a, b) => b[1] - a[1] || a[0] - b[0])
                .map(([n]) => parseInt(n, 10));
        },

        candidatosUniao(nucleo, excluir) {
            const set = new Set(nucleo);
            const out = [];
            for (const p of this.scoreUniaoPares) {
                const inA = set.has(p.a);
                const inB = set.has(p.b);
                if (!inA && !inB) continue;
                const cand = inA ? p.b : p.a;
                if (!excluir.has(cand) && cand >= 1 && cand <= 31) {
                    out.push({ d: cand, s: p.score });
                }
            }
            out.sort((a, b) => b.s - a.s);
            return out.map((x) => x.d);
        },

        obterJogosElite() {
            const mgr = window.SimuladorEliteManager;
            if (!mgr || !mgr.jogos) return [];
            return mgr.jogos.map((j) => this._uniqSorted(j)).filter((j) => j.length >= 7);
        },

        getPctPreservar() {
            const v = parseInt(document.getElementById('mutPctPreservar')?.value, 10);
            return Number.isNaN(v) ? 70 : v;
        },

        /** Núcleo preservado: 5 ou 6 dezenas (≈71–86% de 7). */
        nucleoPreservadoCount(pct) {
            if (pct >= 75) return 6;
            if (pct >= 65) return 5;
            return 5;
        },

        mutarJogo(original, pesos, ranking, idx, existentes) {
            const orig = this._uniqSorted(original);
            const pct = this.getPctPreservar();
            const preserveN = this.nucleoPreservadoCount(pct);
            const minOverlap = preserveN >= 6 ? 6 : 5;

            const peso = (d) => pesos[d] || 0;
            const ranked = [...orig].sort((a, b) => peso(b) - peso(a) || a - b);
            const nucleo = ranked.slice(0, preserveN);
            const secundarias = ranked.slice(preserveN);
            const excluir = new Set(orig);
            const poolUniao = this.candidatosUniao(nucleo, excluir);
            const poolGeral = ranking.filter((d) => !nucleo.includes(d));
            const pool = [...new Set([...poolUniao, ...poolGeral])];

            let mutado = [...nucleo];
            const trocas = Math.min(7 - preserveN, secundarias.length + 1);
            for (let t = 0; t < trocas && mutado.length < 7; t++) {
                const cand = pool[(idx * 2 + t + 1) % pool.length];
                if (cand !== undefined && !mutado.includes(cand)) mutado.push(cand);
            }
            let ri = idx;
            while (mutado.length < 7) {
                const c = pool[ri % pool.length];
                if (c !== undefined && !mutado.includes(c)) mutado.push(c);
                ri++;
            }
            mutado = this._uniqSorted(mutado).slice(0, 7);

            if (this._overlap(mutado, orig) < minOverlap) {
                mutado = this._uniqSorted([...ranked.slice(0, preserveN + 1), pool[idx % pool.length]]).slice(0, 7);
                while (mutado.length < 7) {
                    const c = pool[(ri++) % pool.length];
                    if (!mutado.includes(c)) mutado.push(c);
                }
                mutado = this._uniqSorted(mutado).slice(0, 7);
            }

            if (this._jogoKey(mutado) === this._jogoKey(orig)) {
                for (const cand of pool) {
                    const alt = this._uniqSorted([...ranked.slice(0, preserveN), cand]);
                    while (alt.length < 7) {
                        const c = pool[(ri++) % pool.length];
                        if (!alt.includes(c)) alt.push(c);
                    }
                    const u = this._uniqSorted(alt).slice(0, 7);
                    if (this._overlap(u, orig) >= minOverlap && this._jogoKey(u) !== this._jogoKey(orig)) {
                        mutado = u;
                        break;
                    }
                }
            }

            return this._variarJogoUnico(mutado, existentes, pool);
        },

        calcularMetricas() {
            const overlaps = this.mutados.map((m, i) => this._overlap(m, this.originais[i] || []));
            const media =
                overlaps.length > 0 ? (overlaps.reduce((a, b) => a + b, 0) / overlaps.length).toFixed(2) : '0';
            const todos = [...this.originais, ...this.mutados];
            let dup = 0;
            for (let i = 0; i < todos.length; i++) {
                for (let j = i + 1; j < todos.length; j++) {
                    if (this._jogoKey(todos[i]) === this._jogoKey(todos[j])) dup++;
                }
            }
            return { mediaPreservacao: media, duplicatas: dup };
        },

        async gerar() {
            const status = document.getElementById('mutStatus');
            await this.carregarScoreUniao();

            const mgr = window.SimuladorEliteManager;
            if (!mgr) {
                if (status) {
                    status.className = 'alert alert-danger py-2';
                    status.textContent = 'Simulador Elite não encontrado.';
                }
                return;
            }
            if (!mgr.isLoaded && typeof mgr.init === 'function') await mgr.init();

            const brutos = this.obterJogosElite();
            if (brutos.length < 10) {
                if (status) {
                    status.className = 'alert alert-warning py-2';
                    status.innerHTML =
                        '<strong>Antes da mutação:</strong> vá em <b>Simulador Elite (Top 10)</b>, configure Cobertura ou Convergência e clique em <b>Girar Sorte Mágica</b> até as 10 linhas estarem preenchidas (7 dezenas).';
                }
                this.originais = brutos;
                this.mutados = [];
                this.render();
                return;
            }

            this.originais = brutos.slice(0, 10);
            const pesos = this.montarPesos();
            const ranking = this.rankingPesos(pesos);
            const existentes = [...this.originais];
            this.mutados = [];

            for (let i = 0; i < 10; i++) {
                let m = this.mutarJogo(this.originais[i], pesos, ranking, i, existentes);
                let t = 0;
                while (this._existeJogoIgual(m, existentes) && t < 40) {
                    m = this.mutarJogo(this.originais[i], pesos, ranking, i + t + 1, existentes);
                    t++;
                }
                this.mutados.push(m);
                existentes.push(m);
            }

            this.metricas = this.calcularMetricas();
            this.render();

            if (status) {
                status.className = 'alert alert-success py-2';
                status.innerHTML =
                    `<strong>20 apostas prontas</strong> (10 originais Elite + 10 mutadas). ` +
                    `Preservação média do núcleo: <strong>${this.metricas.mediaPreservacao}</strong>/7 dezenas por linha` +
                    (this.metricas.duplicatas > 0 ? ` · <span class="text-warning">Revise: ${this.metricas.duplicatas} par(es) duplicado(s)</span>` : '.');
            }
        },

        _renderLista(containerId, jogos, badgeCls, badgeText) {
            const el = document.getElementById(containerId);
            if (!el) return;
            if (!jogos.length) {
                el.innerHTML = '<p class="text-muted small mb-0">—</p>';
                return;
            }
            el.innerHTML = jogos
                .map((jogo, idx) => {
                    const dezenas = jogo
                        .map((n) => `<span class="numero-31 sorteado">${this._pad(n)}</span>`)
                        .join('');
                    return `
                    <div class="mut-row d-flex flex-wrap align-items-center gap-2 mb-2 p-2 border rounded bg-white">
                        <span class="badge ${badgeCls}">${badgeText}</span>
                        <span class="text-muted small fw-bold">#${idx + 1}</span>
                        <div class="mut-dezenas d-flex flex-wrap gap-1">${dezenas}</div>
                    </div>`;
                })
                .join('');
        },

        render() {
            this._renderLista('mutOriginaisContainer', this.originais, 'bg-primary', 'Original Elite');
            this._renderLista('mutMutadosContainer', this.mutados, 'bg-secondary', 'Mutação');
            const met = document.getElementById('mutMetricas');
            if (met && this.metricas) {
                met.innerHTML = `<span class="small">Preservação média: <strong>${this.metricas.mediaPreservacao}</strong>/7 · Total: <strong>${this.originais.length + this.mutados.length}</strong> apostas</span>`;
            }
        },

        _baixarTxt(linhas, nome) {
            const conteudo = linhas.map((j) => j.map((n) => this._pad(n)).join(' ')).join('\n');
            const blob = new Blob([conteudo], { type: 'text/plain' });
            const a = document.createElement('a');
            a.href = URL.createObjectURL(blob);
            a.download = nome;
            a.click();
            URL.revokeObjectURL(a.href);
        },

        exportarOriginais() {
            if (this.originais.length < 1) {
                alert('Gere as mutações antes (ou preencha o Elite).');
                return;
            }
            this._baixarTxt(this.originais, 'elite_top10_apostas_Mutacao_Originais.txt');
        },

        exportarMutados() {
            if (this.mutados.length < 1) {
                alert('Clique em Gerar mutações primeiro.');
                return;
            }
            this._baixarTxt(this.mutados, 'elite_top10_apostas_Mutacao_Mutados.txt');
        },

        exportarAmbos() {
            if (this.mutados.length < 1) {
                alert('Clique em Gerar mutações primeiro.');
                return;
            }
            const bloco = (titulo, jogos) => {
                const h = `# ${titulo}\n`;
                const body = jogos.map((j) => j.map((n) => this._pad(n)).join(' ')).join('\n');
                return h + body;
            };
            const conteudo = `${bloco('ORIGINAIS ELITE', this.originais)}\n\n${bloco('MUTADOS', this.mutados)}`;
            const blob = new Blob([conteudo], { type: 'text/plain' });
            const a = document.createElement('a');
            a.href = URL.createObjectURL(blob);
            a.download = 'elite_top10_apostas_Mutacao_Completo.txt';
            a.click();
            URL.revokeObjectURL(a.href);
        },

        irParaElite() {
            const tab = document.getElementById('tab-simulador-elite');
            if (tab) bootstrap.Tab.getOrCreateInstance(tab).show();
        },

        async init() {
            const status = document.getElementById('mutStatus');
            await this.carregarScoreUniao();
            const brutos = this.obterJogosElite();
            this.originais = brutos.slice(0, 10);
            this.mutados = [];
            this.render();
            if (status) {
                if (brutos.length >= 10) {
                    status.className = 'alert alert-info py-2';
                    status.textContent =
                        'Elite com 10 linhas detectado. Clique em «Gerar mutações» para criar as 10 variantes.';
                } else {
                    status.className = 'alert alert-warning py-2';
                    status.innerHTML =
                        'Passo 1: <a href="#" onclick="MutacaoControladaManager.irParaElite(); return false;">Simulador Elite</a> → Girar Sorte Mágica. Passo 2: volte aqui e gere as mutações.';
                }
            }
        },
    };

    window.MutacaoControladaManager = MutacaoControladaManager;

    function bindMutacaoTab() {
        const tab = document.getElementById('tab-mutacao-controlada');
        if (!tab || tab.dataset.boundMut === '1') return;
        tab.dataset.boundMut = '1';
        tab.addEventListener('shown.bs.tab', () => MutacaoControladaManager.init());
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', bindMutacaoTab);
    } else {
        bindMutacaoTab();
    }
})();
