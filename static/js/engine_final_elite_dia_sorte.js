/**
 * Engine Final (última etapa) — Análise Visual / Dia de Sorte
 * Mescla o estado do Simulador Elite (Cobertura/Convergência) com correlação Mês → dezenas.
 */
(function () {
    'use strict';

    const EngineFinalEliteDiaSorte = {
        precos: null,
        mesStats: null,
        /** { 1: '#hex', '1': '#hex', ... } — /api/cores-meses/listar */
        coresMeses: null,
        ultimasApostas: [],
        /** Nome do mês usado na última geração (para cópia e UI). */
        ultimoMesSorteNome: '',
        /** 1–12 — usado na cópia TXT (abreviação). */
        ultimoMesSorteNum: null,

        _ready(fn) {
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', fn);
            } else {
                fn();
            }
        },

        async ensureConcursos() {
            if (window.SimuladorEliteAnalise && typeof window.SimuladorEliteAnalise.carregarDados === 'function') {
                await window.SimuladorEliteAnalise.carregarDados();
            }
        },

        async carregarPrecos() {
            if (this.precos) return this.precos;
            try {
                const r = await fetch('/api/configuracoes/precos-dezenas');
                const j = await r.json();
                if (j.sucesso && j.precos) this.precos = j.precos;
                else this.precos = {};
            } catch (e) {
                console.warn('[Engine Final] preços:', e);
                this.precos = {};
            }
            return this.precos;
        },

        async carregarMesStats() {
            try {
                const r = await fetch('/api/estatisticas/mes-sorte');
                this.mesStats = await r.json();
            } catch (e) {
                console.warn('[Engine Final] mes-sorte:', e);
                this.mesStats = null;
            }
            return this.mesStats;
        },

        async carregarCoresMeses() {
            if (this.coresMeses && Object.keys(this.coresMeses).length > 0) return this.coresMeses;
            this.coresMeses = {};
            try {
                const r = await fetch('/api/cores-meses/listar');
                const j = await r.json();
                if (j.sucesso && Array.isArray(j.cores)) {
                    j.cores.forEach((c) => {
                        const m = parseInt(c.mes, 10);
                        if (!isNaN(m) && m >= 1 && m <= 12 && c.cor_hex) {
                            this.coresMeses[m] = c.cor_hex;
                            this.coresMeses[String(m)] = c.cor_hex;
                        }
                    });
                }
            } catch (e) {
                console.warn('[Engine Final] cores-meses:', e);
            }
            return this.coresMeses;
        },

        _hexToRgb(hex) {
            let h = String(hex || '').replace('#', '').trim();
            if (h.length === 3) {
                h = h.split('').map((ch) => ch + ch).join('');
            }
            const num = parseInt(h, 16);
            if (Number.isNaN(num) || h.length !== 6) return { r: 134, g: 142, b: 150 };
            return { r: (num >> 16) & 255, g: (num >> 8) & 255, b: num & 255 };
        },

        /** Luminância relativa ~0–1 (para contraste do texto no pill do mês). */
        _relLum(hex) {
            const { r, g, b } = this._hexToRgb(hex);
            const lin = (c) => {
                const x = c / 255;
                return x <= 0.03928 ? x / 12.92 : Math.pow((x + 0.055) / 1.055, 2.4);
            };
            const R = lin(r);
            const G = lin(g);
            const B = lin(b);
            return 0.2126 * R + 0.7152 * G + 0.0722 * B;
        },

        /** Cor de fundo (config) e cor de texto legível. */
        _estiloMes(mesNum) {
            const map = this.coresMeses || {};
            const raw = map[mesNum] || map[String(mesNum)];
            const bg = (raw && String(raw).trim()) || '#868e96';
            try {
                const L = this._relLum(bg);
                const fg = L > 0.45 ? '#1a1a1a' : '#ffffff';
                return { bg, fg };
            } catch (e) {
                return { bg, fg: '#ffffff' };
            }
        },

        eliteLinhasPreenchidas() {
            let n = 0;
            const mgr = window.SimuladorEliteManager;
            if (!mgr || !mgr.jogos) return 0;
            for (let i = 0; i < 10; i++) {
                const j = mgr.jogos[i];
                if (j && j.length >= 7) n++;
            }
            return n;
        },

        buildPesosElite() {
            const mgr = window.SimuladorEliteManager;
            const w = {};
            if (!mgr || !mgr.jogos) return w;
            for (let i = 0; i < 10; i++) {
                const j = mgr.jogos[i];
                if (!j || j.length < 7) continue;
                const lw = 11 - i;
                j.forEach((num) => {
                    const n = parseInt(num, 10);
                    if (n >= 1 && n <= 31) w[n] = (w[n] || 0) + lw * 3;
                });
            }
            if (typeof mgr.isConvergencia === 'function' && mgr.isConvergencia()) {
                const nuc = typeof mgr.obterNucleoAtual === 'function' ? mgr.obterNucleoAtual() : [];
                nuc.forEach((num, idx) => {
                    const n = parseInt(num, 10);
                    if (n >= 1 && n <= 31) w[n] = (w[n] || 0) + (9 - idx) * 2;
                });
            }
            return w;
        },

        mesNome(num) {
            const names = {
                1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho',
                7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
            };
            return names[num] || String(num);
        },

        /** Abreviação para TXT (ex.: 01 02 … 07 Jan). */
        mesAbrev(num) {
            const abbr = {
                1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr', 5: 'Mai', 6: 'Jun',
                7: 'Jul', 8: 'Ago', 9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'
            };
            const n = parseInt(num, 10);
            return abbr[n] || '';
        },

        resolverMesNumero() {
            const mod = document.querySelector('input[name="engineFinalMesModo"]:checked');
            if (mod && mod.value === 'manual') {
                const sel = document.getElementById('engineFinalMesManual');
                return parseInt(sel && sel.value, 10) || 1;
            }
            const tipo = document.getElementById('engineFinalMesAutoTipo');
            const t = tipo ? tipo.value : 'atrasado';
            if (!this.mesStats) return 1;
            if (t === 'frequente' && this.mesStats.mais_sorteado) return this.mesStats.mais_sorteado.mes;
            if (this.mesStats.menos_sorteado) return this.mesStats.menos_sorteado.mes;
            if (this.mesStats.mais_sorteado) return this.mesStats.mais_sorteado.mes;
            return 1;
        },

        pickTopK(combined, K) {
            const arr = Object.entries(combined)
                .map(([n, v]) => ({ n: parseInt(n, 10), v: Number(v) || 0 }))
                .filter((x) => x.n >= 1 && x.n <= 31);
            arr.sort((a, b) => b.v - a.v || a.n - b.n);
            const seen = new Set();
            const out = [];
            for (const x of arr) {
                if (out.length >= K) break;
                if (!seen.has(x.n)) {
                    seen.add(x.n);
                    out.push(x.n);
                }
            }
            let d = 1;
            while (out.length < K && d <= 31) {
                if (!seen.has(d)) {
                    seen.add(d);
                    out.push(d);
                }
                d++;
            }
            return out.sort((a, b) => a - b);
        },

        _arraysIguais(a, b) {
            if (!a || !b || a.length !== b.length) return false;
            for (let i = 0; i < a.length; i++) if (a[i] !== b[i]) return false;
            return true;
        },

        /** Ordena dezenas 1–31 por score (maior primeiro). */
        _rankingPorScore(scoreMap) {
            return Object.entries(scoreMap)
                .map(([n, v]) => ({ n: parseInt(n, 10), v: Number(v) || 0 }))
                .filter((x) => x.n >= 1 && x.n <= 31)
                .sort((a, b) => b.v - a.v || a.n - b.n)
                .map((x) => x.n);
        },

        /** Escolhe K dezenas sem reposição, pesos proporcionais a pesoFn(n). */
        _amostragemPesadaSemReposicao(pool, pesoFn, K) {
            const poolArr = [...new Set(pool)].filter((n) => n >= 1 && n <= 31);
            const out = [];
            for (let k = 0; k < K && poolArr.length > 0; k++) {
                let sum = 0;
                const wts = poolArr.map((n) => {
                    const w = Math.max(0.05, pesoFn(n));
                    sum += w;
                    return w;
                });
                let r = Math.random() * sum;
                let chosenIdx = 0;
                for (let i = 0; i < wts.length; i++) {
                    r -= wts[i];
                    if (r <= 0) {
                        chosenIdx = i;
                        break;
                    }
                }
                out.push(poolArr[chosenIdx]);
                poolArr.splice(chosenIdx, 1);
            }
            let fill = 1;
            while (out.length < K && fill <= 31) {
                if (!out.includes(fill)) out.push(fill);
                fill++;
            }
            return out.sort((a, b) => a - b);
        },

        /**
         * Aposta 0 = ranking direto (consenso). Demais = amostragem no pool das melhores
         * com jitter forte + rejeição de duplicata.
         */
        _montarDezenasAposta(baseS, K, indiceAposta, anteriores) {
            const ranked = this._rankingPorScore(baseS);
            if (ranked.length === 0) {
                return this.pickTopK(
                    Object.fromEntries(Array.from({ length: 31 }, (_, i) => [i + 1, 1])),
                    K
                );
            }

            if (indiceAposta === 0) {
                return this.pickTopK(baseS, K);
            }

            const poolSize = Math.min(31, Math.max(K + 10, K + 6 + indiceAposta * 5));
            const pool = ranked.slice(0, poolSize);
            const jitterBase = 28 + indiceAposta * 8;

            for (let tentativa = 0; tentativa < 60; tentativa++) {
                const jitter = jitterBase + tentativa * 4;
                const nums = this._amostragemPesadaSemReposicao(
                    pool,
                    (n) => (baseS[n] || 0) + Math.random() * jitter,
                    K
                );
                const dup = anteriores.some((prev) => this._arraysIguais(prev, nums));
                if (!dup) return nums;
            }

            const rankedFull = this._rankingPorScore(baseS);
            const baseLinha = anteriores[0] && anteriores[0].length === K ? [...anteriores[0]] : this.pickTopK(baseS, K);
            for (let s = 0; s < K; s++) {
                for (const inn of rankedFull) {
                    if (baseLinha.includes(inn)) continue;
                    const trial = [...baseLinha];
                    trial[s] = inn;
                    trial.sort((a, b) => a - b);
                    const dup2 = anteriores.some((prev) => this._arraysIguais(prev, trial));
                    if (!dup2) return trial;
                }
            }

            return this._amostragemPesadaSemReposicao(
                rankedFull,
                (n) => (baseS[n] || 0) + (n % 7) * 19 + indiceAposta * 31 + Math.random() * 80,
                K
            );
        },

        _precoUnitario(K) {
            if (!this.precos) return 0;
            let unit = this.precos[K];
            if (unit === undefined) unit = this.precos[String(K)];
            return parseFloat(unit) || 0;
        },

        atualizarPrecoDisplay() {
            const sel = document.getElementById('engineFinalQtdDezenas');
            const qap = document.getElementById('engineFinalQtdApostas');
            if (!sel) return;
            const K = parseInt(sel.value, 10);
            const qa = Math.max(1, Math.min(50, parseInt(qap && qap.value, 10) || 1));
            const unit = this._precoUnitario(K);
            const elU = document.getElementById('engineFinalPrecoUnit');
            const elT = document.getElementById('engineFinalCustoTotal');
            const fmt = (v) => (v ? `R$ ${v.toFixed(2).replace('.', ',')}` : '—');
            if (elU) elU.textContent = fmt(unit);
            if (elT) elT.textContent = unit ? fmt(unit * qa) : '—';
        },

        atualizarRecomendacaoTexto() {
            const el = document.getElementById('engineFinalMesRecomendacao');
            if (!el || !this.mesStats) return;
            const ma = this.mesStats.mais_sorteado;
            const me = this.mesStats.menos_sorteado;
            if (ma && me) {
                el.innerHTML =
                    `<span class="text-muted">Recomendação (histórico):</span> mais sorteado — <strong>${ma.nome}</strong> (${ma.frequencia}x); ` +
                    `mais atrasado — <strong>${me.nome}</strong> (${me.frequencia}x).`;
            } else {
                el.textContent = '';
            }
        },

        refreshStatus() {
            const el = document.getElementById('engineFinalStatusElite');
            if (!el) return;
            const mgr = window.SimuladorEliteManager;
            const filled = this.eliteLinhasPreenchidas();
            const modo = mgr && mgr.getModo ? mgr.getModo() : '?';
            const modoLabel = modo === 'convergencia' ? 'Convergência' : 'Cobertura';
            if (!filled) {
                el.className = 'alert alert-warning py-2 mb-0';
                el.innerHTML =
                    '<i class="fas fa-exclamation-triangle"></i> Nenhuma linha do Elite com 7 dezenas. Abra a aba ' +
                    '<strong>Simulador Elite (Top 10)</strong>, escolha Cobertura ou Convergência e clique em ' +
                    '<strong>Girar Mágica</strong> / <strong>Girar Convergência</strong>.';
                return;
            }
            el.className = 'alert alert-info py-2 mb-0';
            el.innerHTML =
                `<i class="fas fa-link"></i> <strong>${filled}/10</strong> linhas Elite preenchidas · modo ` +
                `<strong>${modoLabel}</strong> · pesos desta engine seguem o quadro atual do Elite.`;
        },

        toggleMesManualUI() {
            const manual = document.querySelector('input[name="engineFinalMesModo"]:checked')?.value === 'manual';
            const box = document.getElementById('engineFinalMesManualWrap');
            const autoBox = document.getElementById('engineFinalMesAutoWrap');
            if (box) box.style.display = manual ? 'block' : 'none';
            if (autoBox) autoBox.style.display = manual ? 'none' : 'block';
        },

        async onTabShown() {
            await this.ensureConcursos();
            await this.carregarPrecos();
            await this.carregarMesStats();
            await this.carregarCoresMeses();
            this.refreshStatus();
            this.atualizarRecomendacaoTexto();
            this.atualizarPrecoDisplay();
            this.toggleMesManualUI();
        },

        async gerar() {
            const filled = this.eliteLinhasPreenchidas();
            if (!filled) {
                window.alert('Preencha o Simulador Elite primeiro (mínimo 1 linha com 7 dezenas).');
                return;
            }
            await this.carregarMesStats();
            const mesNum = this.resolverMesNumero();
            const mesNome = this.mesNome(mesNum);

            let mesBonus = {};
            try {
                const r = await fetch(`/api/ciclos-dezenas/dezenas-por-mes?mes=${mesNum}`);
                const j = await r.json();
                if (j.sucesso && j.dados && Array.isArray(j.dados.numeros)) {
                    j.dados.numeros.forEach((d, idx) => {
                        const n = parseInt(d, 10);
                        if (n >= 1 && n <= 31) mesBonus[n] = (10 - idx) * 1.5;
                    });
                }
            } catch (e) {
                console.warn('[Engine Final] dezenas-por-mes:', e);
            }

            const K = parseInt(document.getElementById('engineFinalQtdDezenas').value, 10) || 7;
            const qtd = Math.min(
                50,
                Math.max(1, parseInt(document.getElementById('engineFinalQtdApostas').value, 10) || 5)
            );

            const outDiv = document.getElementById('engineFinalResultados');
            if (!outDiv) return;
            outDiv.innerHTML =
                '<div class="text-center p-3"><div class="spinner-border spinner-border-sm text-success"></div> Gerando...</div>';

            await this.carregarCoresMeses();
            const { bg: mesBg, fg: mesFg } = this._estiloMes(mesNum);

            const baseW = this.buildPesosElite();
            const baseS = {};
            for (let n = 1; n <= 31; n++) {
                baseS[n] = (baseW[n] || 0) + (mesBonus[n] || 0);
            }

            const apostas = [];
            const anteriores = [];

            for (let q = 0; q < qtd; q++) {
                const nums = this._montarDezenasAposta(baseS, K, q, anteriores);
                anteriores.push(nums);
                apostas.push({ nums });
            }

            this.ultimoMesSorteNome = mesNome;
            this.ultimoMesSorteNum = mesNum;
            this.ultimasApostas = apostas.map((a) => a.nums);

            const numsHtml = (nums) =>
                nums
                    .map((n) => `<span class="numero-31 sorteado">${String(n).padStart(2, '0')}</span>`)
                    .join('');

            outDiv.innerHTML = apostas
                .map(
                    (a) => `
                <div class="engine-final-row">
                    <div class="engine-final-dezenas">${numsHtml(a.nums)}</div>
                    <span class="engine-final-mes-pill" style="background-color:${mesBg};color:${mesFg}">${mesNome}</span>
                </div>`
                )
                .join('');
        },

        exportarTxtDownload() {
            if (!this.ultimasApostas.length) {
                window.alert('Gere apostas antes de exportar.');
                return;
            }
            const mesTxt = this.mesAbrev(this.ultimoMesSorteNum) || '???';
            const lines = this.ultimasApostas.map((nums) => {
                const dez = nums.map((n) => String(n).padStart(2, '0')).join(' ');
                return `${dez} ${mesTxt}`;
            }).join('\n');
            const stamp = new Date();
            const pad = (x) => String(x).padStart(2, '0');
            const fname = `engine-final-dia-sorte-${stamp.getFullYear()}${pad(stamp.getMonth() + 1)}${pad(stamp.getDate())}-${pad(stamp.getHours())}${pad(stamp.getMinutes())}.txt`;
            const blob = new Blob([lines], { type: 'text/plain;charset=utf-8' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = fname;
            a.rel = 'noopener';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        },

        bind() {
            const tab = document.getElementById('tab-engine-final-elite');
            if (tab) {
                tab.addEventListener('shown.bs.tab', () => this.onTabShown());
            }

            ['engineFinalQtdDezenas', 'engineFinalQtdApostas'].forEach((id) => {
                const el = document.getElementById(id);
                if (el) {
                    el.addEventListener('change', () => this.atualizarPrecoDisplay());
                    el.addEventListener('input', () => this.atualizarPrecoDisplay());
                }
            });
            document.querySelectorAll('input[name="engineFinalMesModo"]').forEach((r) => {
                r.addEventListener('change', () => this.toggleMesManualUI());
            });
            const btn = document.getElementById('engineFinalBtnGerar');
            if (btn) btn.addEventListener('click', () => this.gerar());
            const btnExport = document.getElementById('engineFinalBtnExportar');
            if (btnExport) btnExport.addEventListener('click', () => this.exportarTxtDownload());
        }
    };

    EngineFinalEliteDiaSorte._ready(() => EngineFinalEliteDiaSorte.bind());
    window.EngineFinalEliteDiaSorte = EngineFinalEliteDiaSorte;
})();
