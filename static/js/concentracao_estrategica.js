/**
 * Concentração Estratégica — geração focada em repetição de dezenas fortes e união histórica.
 * Isolado do modo Cobertura do Simulador Elite; consome insumos do Elite quando disponível.
 */
(function () {
    'use strict';

    const ConcentracaoEstrategicaManager = {
        jogos: [],
        blocos: [],
        nucleoDominante: [],
        premium: [],
        scoreUniaoPares: [],
        uniaoIndex: {},
        metricas: null,
        isReady: false,

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
            const k = this._jogoKey(jogo);
            return lista.some((j) => this._jogoKey(j) === k);
        },

        /** Garante 7 dezenas distintas de qualquer jogo já na lista (evita bilhetes idênticos). */
        _variarJogoUnico(jogoBase, existentes, rotacao, ranking) {
            if (!this._existeJogoIgual(jogoBase, existentes)) return this._uniqSorted(jogoBase).slice(0, 7);
            const base = this._uniqSorted(jogoBase);
            const pool = [...new Set([...rotacao, ...ranking])].filter((n) => n >= 1 && n <= 31);
            for (let s = 0; s < base.length; s++) {
                for (const cand of pool) {
                    if (base.includes(cand)) continue;
                    const alt = this._uniqSorted([...base.slice(0, s), ...base.slice(s + 1), cand]);
                    if (alt.length === 7 && !this._existeJogoIgual(alt, existentes)) return alt;
                }
            }
            for (const cand of pool) {
                const alt = this._uniqSorted([...base.slice(0, 6), cand]);
                if (alt.length === 7 && !this._existeJogoIgual(alt, existentes)) return alt;
            }
            for (let d = 1; d <= 31; d++) {
                const alt = this._uniqSorted([...base.slice(0, 6), d]);
                if (alt.length === 7 && !this._existeJogoIgual(alt, existentes)) return alt;
            }
            return base.slice(0, 7);
        },

        _pushJogoUnico(jogos, blocos, jogo, bloco, rotacao, ranking) {
            const unico = this._variarJogoUnico(jogo, jogos, rotacao, ranking);
            jogos.push(unico);
            blocos.push(bloco);
        },

        _chavePar(a, b) {
            return a < b ? `${a}-${b}` : `${b}-${a}`;
        },

        _scorePar(a, b) {
            return this.uniaoIndex[this._chavePar(a, b)] || 0;
        },

        async carregarScoreUniao() {
            const limite = parseInt(document.getElementById('concLimiteHistorico')?.value, 10) || 250;
            try {
                const r = await fetch(`/api/concentracao/score-uniao?limite=${limite}`);
                const data = await r.json();
                if (!data.sucesso) throw new Error(data.erro || 'Falha ao carregar score de união');
                this.scoreUniaoPares = data.pares || [];
                this.uniaoIndex = {};
                this.scoreUniaoPares.forEach((p) => {
                    this.uniaoIndex[this._chavePar(p.a, p.b)] = p.score;
                });
                return data;
            } catch (e) {
                console.warn('[Concentração]', e);
                this.scoreUniaoPares = [];
                this.uniaoIndex = {};
                return null;
            }
        },

        async ensureElite() {
            const mgr = window.SimuladorEliteManager;
            if (!mgr) return false;
            if (!mgr.isLoaded && typeof mgr.init === 'function') {
                await mgr.init();
            }
            return mgr.isLoaded || (mgr.top10 && mgr.top10.length > 0);
        },

        montarPesosDezenas() {
            const mgr = window.SimuladorEliteManager;
            const pesos = {};
            const add = (n, w) => {
                if (n < 1 || n > 31) return;
                pesos[n] = (pesos[n] || 0) + w;
            };

            if (mgr && typeof mgr.coletarPontuacaoDezenas === 'function') {
                const freq = mgr.coletarPontuacaoDezenas();
                Object.entries(freq).forEach(([n, v]) => add(parseInt(n, 10), v * 2));
            }

            (this.scoreUniaoPares || []).slice(0, 80).forEach((p) => {
                const boost = p.score * 12;
                add(p.a, boost);
                add(p.b, boost);
            });

            for (let d = 1; d <= 31; d++) {
                if (pesos[d] === undefined) pesos[d] = 0;
            }
            return pesos;
        },

        ordenarPorPeso(pesos) {
            return Object.entries(pesos)
                .sort((a, b) => b[1] - a[1] || a[0] - b[0])
                .map(([n]) => parseInt(n, 10));
        },

        gerarJogoAtaque(nucleo6, rotacao, idx) {
            const base = nucleo6.slice(0, 6);
            const extra = rotacao[(idx * 2 + 1) % rotacao.length] || rotacao[idx % rotacao.length];
            return this._uniqSorted([...base, extra]).slice(0, 7);
        },

        gerarJogoSemi(nucleo, rotacao, idx) {
            const n = nucleo.length >= 7 ? nucleo : [...nucleo];
            const extraPool = [...n.slice(5, 9), ...rotacao];
            const coreSize = 4 + (idx % 2);
            const core = n.slice(0, coreSize);
            const pares = [
                [0, 1], [0, 2], [1, 2], [1, 3], [2, 3], [3, 0], [3, 1], [2, 1], [0, 3], [1, 0],
            ];
            const [i, j] = pares[idx % pares.length];
            const jogo = [...core];
            if (extraPool[i] !== undefined) jogo.push(extraPool[i]);
            if (extraPool[j] !== undefined && extraPool[j] !== extraPool[i]) jogo.push(extraPool[j]);
            let ri = idx * 2 + 1;
            while (jogo.length < 7 && ri < extraPool.length + 40) {
                const c = extraPool[ri % extraPool.length];
                if (c !== undefined && !jogo.includes(c)) jogo.push(c);
                ri++;
            }
            if (idx > 0 && core.length > 0) {
                const troca = rotacao[(idx * 3 + 2) % rotacao.length];
                const sai = core[idx % core.length];
                if (troca !== undefined && troca !== sai && !jogo.includes(troca)) {
                    const alt = jogo.filter((d) => d !== sai);
                    alt.push(troca);
                    let r2 = idx;
                    while (alt.length < 7) {
                        const c = rotacao[r2 % rotacao.length];
                        if (!alt.includes(c)) alt.push(c);
                        r2++;
                    }
                    return this._uniqSorted(alt).slice(0, 7);
                }
            }
            return this._uniqSorted(jogo).slice(0, 7);
        },

        gerarJogoDefesa(ranking, idx) {
            const offset = idx * 3 + 1;
            const picked = [];
            for (let k = 0; picked.length < 7 && k < ranking.length + 10; k++) {
                const d = ranking[(offset + k) % ranking.length];
                if (!picked.includes(d)) picked.push(d);
            }
            return this._uniqSorted(picked).slice(0, 7);
        },

        reforcarRepeticaoPremium(jogos, minK, rotacao = [], ranking = []) {
            if (!this.premium.length) return;
            const alvo = this.premium[0];
            let count = jogos.filter((j) => j.includes(alvo)).length;
            let guard = 0;
            while (count < minK && guard < 20) {
                let idx = 0;
                let minOverlap = 99;
                jogos.forEach((j, i) => {
                    if (j.includes(alvo)) return;
                    const ov = j.filter((n) => this.premium.includes(n)).length;
                    if (ov < minOverlap) {
                        minOverlap = ov;
                        idx = i;
                    }
                });
                const outros = jogos.filter((_, i) => i !== idx);
                let j = [...jogos[idx]];
                if (j.length >= 7) j.pop();
                if (!j.includes(alvo)) j.push(alvo);
                j = this._variarJogoUnico(this._uniqSorted(j).slice(0, 7), outros, rotacao, ranking.length ? ranking : this.premium);
                jogos[idx] = j;
                count = jogos.filter((j) => j.includes(alvo)).length;
                guard++;
            }
        },

        calcularMetricas(jogos) {
            if (!jogos.length) return null;
            let somaOverlap = 0;
            let pares = 0;
            for (let i = 0; i < jogos.length; i++) {
                for (let j = i + 1; j < jogos.length; j++) {
                    const inter = jogos[i].filter((n) => jogos[j].includes(n)).length;
                    somaOverlap += inter;
                    pares++;
                }
            }
            const overlapMedio = pares ? (somaOverlap / pares).toFixed(2) : '0';
            const repPremium = {};
            this.premium.forEach((d) => {
                repPremium[d] = jogos.filter((j) => j.includes(d)).length;
            });
            return { overlapMedio, repPremium, totalJogos: jogos.length };
        },

        async gerar() {
            const status = document.getElementById('concStatus');
            if (status) {
                status.className = 'alert alert-info py-2 mb-3';
                status.textContent = 'Gerando apostas com foco em concentração...';
            }

            await this.carregarScoreUniao();
            await this.ensureElite();

            const pesos = this.montarPesosDezenas();
            const ranking = this.ordenarPorPeso(pesos);
            this.nucleoDominante = ranking.slice(0, 9);
            this.premium = ranking.slice(0, 7);

            const qtdAtaque = parseInt(document.getElementById('concQtdAtaque')?.value, 10) || 5;
            const qtdSemi = parseInt(document.getElementById('concQtdSemi')?.value, 10) || 3;
            const qtdDefesa = parseInt(document.getElementById('concQtdDefesa')?.value, 10) || 2;
            const minRep = parseInt(document.getElementById('concMinRepeticao')?.value, 10) || 7;

            const total = qtdAtaque + qtdSemi + qtdDefesa;
            if (total !== 10) {
                if (status) {
                    status.className = 'alert alert-warning py-2 mb-3';
                    status.textContent = 'Ataque + Semi + Defesa deve somar 10 linhas. Ajuste os valores.';
                }
                return;
            }

            const nucleo6 = this.premium.slice(0, 6);
            const rotacao = ranking.filter((d) => !nucleo6.includes(d)).slice(0, 12);
            if (rotacao.length < 4) {
                for (let d = 1; d <= 31 && rotacao.length < 12; d++) {
                    if (!nucleo6.includes(d) && !rotacao.includes(d)) rotacao.push(d);
                }
            }

            const jogos = [];
            const blocos = [];

            for (let i = 0; i < qtdAtaque; i++) {
                let j = this.gerarJogoAtaque(nucleo6, rotacao, i);
                let t = 0;
                while (this._existeJogoIgual(j, jogos) && t < 30) {
                    j = this.gerarJogoAtaque(nucleo6, rotacao, i + t + 1);
                    t++;
                }
                this._pushJogoUnico(jogos, blocos, j, 'ataque', rotacao, ranking);
            }
            for (let i = 0; i < qtdSemi; i++) {
                let j = this.gerarJogoSemi(this.nucleoDominante, rotacao, i);
                let t = 0;
                while (this._existeJogoIgual(j, jogos) && t < 30) {
                    j = this.gerarJogoSemi(this.nucleoDominante, rotacao, i + t + 1);
                    t++;
                }
                this._pushJogoUnico(jogos, blocos, j, 'semi', rotacao, ranking);
            }
            for (let i = 0; i < qtdDefesa; i++) {
                let j = this.gerarJogoDefesa(ranking, i);
                let t = 0;
                while (this._existeJogoIgual(j, jogos) && t < 30) {
                    j = this.gerarJogoDefesa(ranking, i + t + 1);
                    t++;
                }
                this._pushJogoUnico(jogos, blocos, j, 'defesa', rotacao, ranking);
            }

            this.reforcarRepeticaoPremium(jogos, Math.min(minRep, 10), rotacao, ranking);

            this.jogos = jogos;
            this.blocos = blocos;
            this.metricas = this.calcularMetricas(jogos);
            this.render();
            this.isReady = true;

            if (status) {
                status.className = 'alert alert-success py-2 mb-3';
                status.innerHTML =
                    `<strong>Concentração gerada.</strong> Núcleo: ${this.nucleoDominante.slice(0, 7).map((n) => this._pad(n)).join(' ')} ` +
                    `| Overlap médio entre jogos: <strong>${this.metricas.overlapMedio}</strong> dezenas`;
            }
        },

        renderNucleo() {
            const el = document.getElementById('concNucleoDisplay');
            if (!el) return;
            if (!this.nucleoDominante.length) {
                el.innerHTML = '<span class="text-muted small">Gere as apostas para ver o núcleo dominante.</span>';
                return;
            }
            el.innerHTML = this.nucleoDominante
                .map(
                    (n, i) =>
                        `<span class="badge ${i < 7 ? 'bg-dark text-warning' : 'bg-secondary'} me-1 mb-1">${this._pad(n)}</span>`
                )
                .join('');
        },

        renderMetricas() {
            const el = document.getElementById('concMetricas');
            if (!el || !this.metricas) return;
            const reps = Object.entries(this.metricas.repPremium)
                .map(([d, c]) => `${this._pad(d)}→${c} jogos`)
                .join(' · ');
            el.innerHTML = `
                <div class="small">
                    <strong>Overlap médio:</strong> ${this.metricas.overlapMedio} dezenas entre pares de apostas &nbsp;|&nbsp;
                    <strong>Repetição premium:</strong> ${reps || '—'}
                </div>`;
        },

        renderJogos() {
            const container = document.getElementById('concJogosContainer');
            if (!container) return;

            const labels = {
                ataque: { text: 'Ataque pesado', cls: 'bg-danger' },
                semi: { text: 'Semi-convergência', cls: 'bg-warning text-dark' },
                defesa: { text: 'Defesa estatística', cls: 'bg-info text-dark' },
            };

            let html = '';
            this.jogos.forEach((jogo, idx) => {
                const bloco = this.blocos[idx] || 'ataque';
                const meta = labels[bloco] || labels.ataque;
                const dezenasHtml = jogo
                    .map((n) => {
                        const prem = this.premium.includes(n);
                        return `<span class="numero-31 sorteado" style="${prem ? 'box-shadow:0 0 0 2px #dc3545;' : ''}">${this._pad(n)}</span>`;
                    })
                    .join('');
                html += `
                <div class="conc-row d-flex flex-wrap align-items-center gap-2 mb-2 p-2 border rounded bg-white">
                    <span class="badge ${meta.cls}">${meta.text}</span>
                    <span class="text-muted small fw-bold">#${idx + 1}</span>
                    <div class="conc-dezenas d-flex flex-wrap gap-1">${dezenasHtml}</div>
                </div>`;
            });
            container.innerHTML = html || '<p class="text-muted small">Nenhuma aposta gerada.</p>';
        },

        render() {
            this.renderNucleo();
            this.renderMetricas();
            this.renderJogos();
        },

        nomeArquivoDownload() {
            return 'elite_top10_apostas_Concentracao.txt';
        },

        exportar() {
            const prontas = this.jogos.filter((j) => j.length >= 7);
            if (!prontas.length) {
                alert('Gere as apostas antes de exportar.');
                return;
            }
            const conteudo = prontas.map((j) => j.map((n) => this._pad(n)).join(' ')).join('\n');
            const blob = new Blob([conteudo], { type: 'text/plain' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = this.nomeArquivoDownload();
            a.click();
            window.URL.revokeObjectURL(url);
        },

        aplicarNoElite() {
            const mgr = window.SimuladorEliteManager;
            if (!mgr) {
                alert('Simulador Elite não disponível.');
                return;
            }
            if (!this.jogos.length) {
                alert('Gere as apostas na Concentração Estratégica primeiro.');
                return;
            }
            for (let i = 0; i < 10; i++) {
                mgr.jogos[i] = this.jogos[i] ? [...this.jogos[i]] : [];
            }
            if (mgr.nucleoConvergencia.length < 7) {
                mgr.nucleoConvergencia = [...this.nucleoDominante];
            }
            if (typeof mgr.renderizar === 'function') mgr.renderizar();
            const tab = document.getElementById('tab-simulador-elite');
            if (tab) bootstrap.Tab.getOrCreateInstance(tab).show();
            if (typeof mostrarAlerta === 'function') {
                mostrarAlerta('10 linhas aplicadas ao Simulador Elite.', 'success');
            }
        },

        async init() {
            const status = document.getElementById('concStatus');
            if (status) {
                status.className = 'alert alert-secondary py-2 mb-3';
                status.textContent = 'Carregando score de união e insumos do Elite...';
            }
            await this.carregarScoreUniao();
            await this.ensureElite();
            this.renderNucleo();
            if (status) {
                status.className = 'alert alert-info py-2 mb-3';
                status.textContent =
                    'Pronto. Use «Gerar concentração» para montar 10 apostas (Ataque / Semi / Defesa). ' +
                    'Recomendado: preencher o Simulador Elite antes para melhor pontuação.';
            }
        },
    };

    window.ConcentracaoEstrategicaManager = ConcentracaoEstrategicaManager;

    function bindConcentracaoTab() {
        const tab = document.getElementById('tab-concentracao-estrategica');
        if (!tab || tab.dataset.boundConc === '1') return;
        tab.dataset.boundConc = '1';
        tab.addEventListener('shown.bs.tab', () => {
            ConcentracaoEstrategicaManager.init();
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', bindConcentracaoTab);
    } else {
        bindConcentracaoTab();
    }
})();
