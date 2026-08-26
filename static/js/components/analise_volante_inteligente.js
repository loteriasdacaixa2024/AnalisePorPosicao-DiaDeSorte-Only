/**
 * Análise do volante (colunas, diagonais, agrupamentos) + gerador estratégico — Dia de Sorte
 * Layout: grade 10 colunas × 4 linhas (31 na posição final).
 */
(function () {
    'use strict';

    const CORES = {
        principal: '#d4b31a',
        claro: '#fcf9e8',
        medio: '#eed877',
        escuro: '#5b4c0b',
        sorteado: '#ffd700',
        borda: '#ffa500',
    };

    const MESES_ABREV = ['JAN', 'FEV', 'MAR', 'ABR', 'MAI', 'JUN', 'JUL', 'AGO', 'SET', 'OUT', 'NOV', 'DEZ'];

    const VolanteGeo = {
        pos: {},
        colunas: {},
        celulas: [],

        init() {
            this.pos = {};
            this.colunas = {};
            for (let c = 0; c < 10; c++) this.colunas[c] = [];
            this.celulas = [];
            for (let n = 1; n <= 31; n++) {
                let row, col;
                if (n === 31) {
                    row = 3;
                    col = 0;
                } else {
                    row = Math.floor((n - 1) / 10);
                    col = (n - 1) % 10;
                }
                this.pos[n] = { row, col };
                this.colunas[col].push(n);
                this.celulas.push({ n, row, col });
            }
        },

        vizinhos(n) {
            const p = this.pos[n];
            if (!p) return [];
            const dirs = [
                [-1, -1], [-1, 0], [-1, 1],
                [0, -1], [0, 1],
                [1, -1], [1, 0], [1, 1],
            ];
            const out = [];
            const map = {};
            this.celulas.forEach((c) => {
                map[`${c.row},${c.col}`] = c.n;
            });
            dirs.forEach(([dr, dc]) => {
                const key = `${p.row + dr},${p.col + dc}`;
                if (map[key]) out.push(map[key]);
            });
            return out;
        },

        diagonaisDefinidas() {
            const map = {};
            this.celulas.forEach((c) => {
                map[`${c.row},${c.col}`] = c.n;
            });
            const diags = [];
            const addDiag = (nums, tipo) => {
                if (nums.length >= 3) diags.push({ id: diags.length, tipo, numeros: nums });
            };
            for (let sr = 0; sr < 4; sr++) {
                for (let sc = 0; sc < 10; sc++) {
                    const asc = [];
                    let r = sr;
                    let c = sc;
                    while (map[`${r},${c}`]) {
                        asc.push(map[`${r},${c}`]);
                        r++;
                        c++;
                    }
                    addDiag(asc, 'ascendente');
                    const desc = [];
                    r = sr;
                    c = sc;
                    while (map[`${r},${c}`]) {
                        desc.push(map[`${r},${c}`]);
                        r++;
                        c--;
                    }
                    addDiag(desc, 'descendente');
                }
            }
            const uniq = [];
            const keys = new Set();
            diags.forEach((d) => {
                const k = d.numeros.join('-');
                if (!keys.has(k)) {
                    keys.add(k);
                    uniq.push(d);
                }
            });
            return uniq;
        },
    };

    VolanteGeo.init();

    class AnaliseVolanteInteligente {
        constructor() {
            this.analise = null;
            this.ultimasApostas = [];
            this.mesExport = 1;
            this.modoExibicaoApostas = 'volante';
            this._metricasDiversidade = null;
            this.LIMITE_AVISO = 500;
            this.LIMITE_CONFIRMA = 2000;
            this.LIMITE_CRITICO = 5000;
            this.LIMITE_MAX = 15000;
            this.DEZ_MIN = 7;
            this.DEZ_MAX = 15;
        }

        setModoExibicao(modo) {
            if (modo === 'volante' || modo === 'normal') {
                this.modoExibicaoApostas = modo;
                this._renderApostas();
            }
        }

        _limitesDezenas() {
            return { min: this.DEZ_MIN, max: this.DEZ_MAX };
        }

        _contadorClasse(qtd) {
            const { min, max } = this._limitesDezenas();
            if (qtd < min || qtd > max) return 'text-danger fw-bold';
            return 'text-success';
        }

        _toggleDezenaAposta(idxAposta, num) {
            if (!this.ultimasApostas[idxAposta]) return;
            const { min, max } = this._limitesDezenas();
            let jogo = [...this.ultimasApostas[idxAposta]];
            const pos = jogo.indexOf(num);

            if (pos >= 0) {
                if (jogo.length <= min) {
                    this._avisarAposta(idxAposta, `Mínimo ${min} dezenas por aposta.`);
                    return;
                }
                jogo.splice(pos, 1);
            } else {
                if (jogo.length >= max) {
                    this._avisarAposta(idxAposta, `Máximo ${max} dezenas por aposta.`);
                    return;
                }
                jogo.push(num);
            }

            this.ultimasApostas[idxAposta] = jogo.sort((a, b) => a - b);
            this._renderApostas();
        }

        _avisarAposta(idx, msg) {
            const el = document.querySelector(`[data-aposta-card="${idx}"] .volante-aposta-aviso`);
            if (el) {
                el.textContent = msg;
                el.classList.add('show');
                setTimeout(() => el.classList.remove('show'), 2200);
            }
        }

        _bindApostasClick() {
            const body = document.getElementById('volanteGeradorResultadosBody');
            if (!body) return;
            body.onclick = (e) => {
                const btn = e.target.closest('[data-volante-num]');
                if (!btn) return;
                e.preventDefault();
                const idx = parseInt(btn.getAttribute('data-aposta-idx'), 10);
                const num = parseInt(btn.getAttribute('data-volante-num'), 10);
                if (!isNaN(idx) && !isNaN(num)) this._toggleDezenaAposta(idx, num);
            };
        }

        _numsConcurso(c) {
            const raw = c.numeros_ordenados || c.numeros || c.dezenas || [];
            return [...raw].map(Number).filter((n) => n >= 1 && n <= 31);
        }

        analisar(concursos) {
            if (!concursos || !concursos.length) return null;
            const lista = concursos.slice();
            const total = lista.length;

            const freqDezena = {};
            const atraso = {};
            for (let n = 1; n <= 31; n++) atraso[n] = total;

            const freqCol = Array(10).fill(0);
            const freqColConc = Array(10).fill(0);
            const diagHits = {};
            VolanteGeo.diagonaisDefinidas().forEach((d) => {
                diagHits[d.id] = 0;
            });

            const paresAdj = {};
            const trincasAdj = {};

            const addPair = (a, b) => {
                const k = a < b ? `${a}-${b}` : `${b}-${a}`;
                paresAdj[k] = (paresAdj[k] || 0) + 1;
            };

            lista.forEach((conc, index) => {
                const nums = this._numsConcurso(conc);
                const colsNoConc = new Set();

                nums.forEach((n) => {
                    freqDezena[n] = (freqDezena[n] || 0) + 1;
                    if (atraso[n] === total) atraso[n] = index;
                    const col = VolanteGeo.pos[n].col;
                    freqCol[col]++;
                    colsNoConc.add(col);
                });
                colsNoConc.forEach((col) => {
                    freqColConc[col]++;
                });

                for (let i = 0; i < nums.length; i++) {
                    for (let j = i + 1; j < nums.length; j++) {
                        if (VolanteGeo.vizinhos(nums[i]).includes(nums[j])) addPair(nums[i], nums[j]);
                    }
                }
                for (let i = 0; i < nums.length; i++) {
                    for (let j = i + 1; j < nums.length; j++) {
                        for (let k = j + 1; k < nums.length; k++) {
                            const set = new Set([nums[i], nums[j], nums[k]]);
                            const v = VolanteGeo.vizinhos(nums[i]);
                            if (v.includes(nums[j]) && v.includes(nums[k])) {
                                const key = [...set].sort((a, b) => a - b).join('-');
                                trincasAdj[key] = (trincasAdj[key] || 0) + 1;
                            }
                        }
                    }
                }

                VolanteGeo.diagonaisDefinidas().forEach((d) => {
                    const inter = d.numeros.filter((n) => nums.includes(n)).length;
                    if (inter >= 3) diagHits[d.id] = (diagHits[d.id] || 0) + 1;
                });
            });

            const colunas = [];
            for (let c = 0; c < 10; c++) {
                const pct = total ? ((freqColConc[c] / total) * 100).toFixed(1) : 0;
                colunas.push({
                    col: c,
                    dezenas: VolanteGeo.colunas[c],
                    hits: freqCol[c],
                    concursosComColuna: freqColConc[c],
                    pct,
                });
            }
            colunas.sort((a, b) => b.hits - a.hits);

            const diagonais = VolanteGeo.diagonaisDefinidas()
                .map((d) => ({
                    ...d,
                    hits: diagHits[d.id] || 0,
                    pct: total ? (((diagHits[d.id] || 0) / total) * 100).toFixed(1) : 0,
                }))
                .sort((a, b) => b.hits - a.hits)
                .slice(0, 12);

            const topPares = Object.entries(paresAdj)
                .map(([k, v]) => {
                    const [a, b] = k.split('-').map(Number);
                    return { a, b, freq: v };
                })
                .sort((a, b) => b.freq - a.freq)
                .slice(0, 15);

            const topTrincas = Object.entries(trincasAdj)
                .map(([k, v]) => ({ nums: k.split('-').map(Number), freq: v }))
                .sort((a, b) => b.freq - a.freq)
                .slice(0, 8);

            const score = {};
            const diagLista = VolanteGeo.diagonaisDefinidas();
            for (let n = 1; n <= 31; n++) {
                const f = (freqDezena[n] || 0) / total;
                const col = VolanteGeo.pos[n].col;
                const colRank = colunas.findIndex((x) => x.col === col);
                const colBoost = colRank >= 0 ? (10 - colRank) * 0.06 : 0;
                let parBoost = 0;
                topPares.slice(0, 12).forEach((p) => {
                    if (p.a === n || p.b === n) parBoost += (p.freq / total) * 0.4;
                });
                let diagBoost = 0;
                diagonais.slice(0, 8).forEach((d) => {
                    if (d.numeros.includes(n)) diagBoost += (d.hits / total) * 0.25;
                });
                const atrasoNorm = Math.min((atraso[n] || 0) / Math.max(1, total * 0.15), 1);
                score[n] = f * 3.8 + colBoost + parBoost + diagBoost + atrasoNorm * 0.35;
            }

            const faixas = [
                { id: 1, nome: 'Linha 1 (01-10)', min: 1, max: 10 },
                { id: 2, nome: 'Linha 2 (11-20)', min: 11, max: 20 },
                { id: 3, nome: 'Linha 3 (21-30)', min: 21, max: 30 },
                { id: 4, nome: 'Linha 4 (31)', min: 31, max: 31 },
            ];
            const linhas = faixas.map((fx) => {
                let hits = 0;
                lista.forEach((c) => {
                    if (this._numsConcurso(c).some((n) => n >= fx.min && n <= fx.max)) hits++;
                });
                return { ...fx, pct: total ? ((hits / total) * 100).toFixed(1) : 0, hits };
            });

            return {
                total,
                colunas,
                diagonais,
                topPares,
                topTrincas,
                linhas,
                score,
                freqDezena,
                atraso,
                colQuente: colunas[0],
                colFria: colunas[colunas.length - 1],
                colMornas: colunas.slice(3, 7),
            };
        }

        _overlap(a, b) {
            const sa = new Set(a);
            return b.filter((n) => sa.has(n)).length;
        }

        _usoGlobalDezenas(anteriores) {
            const uso = {};
            anteriores.forEach((j) => j.forEach((n) => {
                uso[n] = (uso[n] || 0) + 1;
            }));
            return uso;
        }

        /** Pesos por aposta: rotaciona padrão (coluna/diag/par/linha) e penaliza dezenas já usadas. */
        _pesosParaAposta(analise, idx, usoGlobal, salt = 0) {
            const pesos = {};
            const i = idx + salt;
            const colAlvo = analise.colunas[(i * 2 + 1) % analise.colunas.length];
            const colSec = analise.colunas[(i * 3 + 5) % analise.colunas.length];
            const diag = analise.diagonais[(i + 2) % Math.max(1, analise.diagonais.length)];
            const par = analise.topPares[(i + Math.floor(i / 2)) % Math.max(1, analise.topPares.length)];
            const linha = analise.linhas[i % analise.linhas.length];
            const modo = i % 6;

            for (let n = 1; n <= 31; n++) {
                let w = (analise.score[n] || 0) * 0.35;
                w -= (usoGlobal[n] || 0) * 1.15;
                w += ((analise.freqDezena[n] || 0) / analise.total) * (modo === 1 ? 0.9 : 0.35);
                if (modo === 2 && (analise.atraso[n] || 0) > 4) w += 0.5 + Math.min(analise.atraso[n] / 30, 1) * 0.4;
                if (colAlvo.dezenas.includes(n)) w += 0.55;
                if (colSec.dezenas.includes(n) && modo !== 0) w += 0.25;
                if (diag && diag.numeros.includes(n)) w += 0.45;
                if (par && (par.a === n || par.b === n)) w += 0.5;
                if (n >= linha.min && n <= linha.max) w += 0.3;
                const jitter = ((n * 7 + i * 13) % 17) / 100;
                pesos[n] = Math.max(0.02, w + jitter);
            }
            return pesos;
        }

        _sorteioPonderado(pesos, K, analise, idx, salt) {
            const pick = [];
            const i = idx + salt;

            const pushUnique = (n) => {
                if (n >= 1 && n <= 31 && !pick.includes(n) && pick.length < K) pick.push(n);
            };

            const col = analise.colunas[(i * 2 + 1) % analise.colunas.length];
            const dezenasCol = [...col.dezenas].sort(
                (a, b) => (analise.score[b] || 0) - (analise.score[a] || 0) || a - b
            );
            pushUnique(dezenasCol[(i + salt) % dezenasCol.length]);
            pushUnique(dezenasCol[(i + salt + 2) % dezenasCol.length]);

            const diag = analise.diagonais[(i + 1) % Math.max(1, analise.diagonais.length)];
            if (diag) {
                diag.numeros.forEach((n, di) => {
                    if (di < 2) pushUnique(n);
                });
            }

            const par = analise.topPares[(i + 3) % Math.max(1, analise.topPares.length)];
            if (par && pick.length < K - 1) {
                pushUnique(par.a);
                pushUnique(par.b);
            }

            if (i % 3 === 0) {
                const atrasados = Object.entries(analise.atraso)
                    .map(([n, a]) => ({ n: parseInt(n, 10), a }))
                    .sort((a, b) => b.a - a.a)
                    .slice(0, 8);
                pushUnique(atrasados[(i + salt) % atrasados.length]?.n);
            }

            const pool = Object.entries(pesos)
                .map(([n, w]) => ({ n: parseInt(n, 10), w }))
                .filter((x) => !pick.includes(x.n))
                .sort((a, b) => b.w - a.w);

            let pi = (i + salt) % Math.max(1, pool.length);
            while (pick.length < K && pool.length) {
                const slice = pool.slice(pi, pi + 12);
                const totalW = slice.reduce((s, x) => s + x.w, 0);
                let r = Math.random() * totalW;
                for (const x of slice) {
                    r -= x.w;
                    if (r <= 0) {
                        pushUnique(x.n);
                        break;
                    }
                }
                pi = (pi + 7) % pool.length;
            }

            let guard = 0;
            while (pick.length < K && guard < 31) {
                pushUnique((guard % 31) + 1);
                guard++;
            }
            return pick.sort((a, b) => a - b).slice(0, K);
        }

        _montarAposta(K, idx, anteriores, analise) {
            const uso = this._usoGlobalDezenas(anteriores);
            const maxOverlap = Math.max(2, Math.floor(K * 0.42));

            for (let t = 0; t < 100; t++) {
                const pesos = this._pesosParaAposta(analise, idx, uso, t);
                const jogo = this._sorteioPonderado(pesos, K, analise, idx, t);
                const dup = anteriores.some((a) => this._jogoKey(a) === this._jogoKey(jogo));
                const muitoParecido = anteriores.some((a) => this._overlap(a, jogo) > maxOverlap);
                if (!dup && !muitoParecido) return jogo;
            }

            const pesos = this._pesosParaAposta(analise, idx, uso, idx * 17);
            return this._sorteioPonderado(pesos, K, analise, idx, idx * 17);
        }

        async resolverMesAtrasado() {
            try {
                const r = await fetch('/api/estatisticas/mes-sorte');
                const j = await r.json();
                if (j.menos_sorteado && j.menos_sorteado.mes) {
                    this.mesExport = parseInt(j.menos_sorteado.mes, 10);
                    return j.menos_sorteado;
                }
            } catch (e) {
                console.warn('[Volante]', e);
            }
            this.mesExport = new Date().getMonth() + 1;
            return { mes: this.mesExport, nome: 'Automático' };
        }

        _pad(n) {
            return String(n).padStart(2, '0');
        }

        _jogoKey(j) {
            return [...j].sort((a, b) => a - b).join(',');
        }

        async gerar() {
            const qtd = parseInt(document.getElementById('volanteQtdApostas')?.value, 10) || 10;
            const K = parseInt(document.getElementById('volanteQtdDezenas')?.value, 10) || 7;
            const status = document.getElementById('volanteGeradorStatus');

            if (qtd > this.LIMITE_MAX) {
                alert(`Limite máximo: ${this.LIMITE_MAX} apostas por geração.`);
                return;
            }
            if (qtd >= this.LIMITE_CRITICO) {
                const ok = confirm(
                    `Você solicitou ${qtd} apostas. Isso pode demorar e consumir muita memória.\n\n` +
                        'Recomendado: use exportação TXT após gerar. Deseja continuar?'
                );
                if (!ok) return;
            } else if (qtd >= this.LIMITE_CONFIRMA) {
                const ok = confirm(`Gerar ${qtd} apostas? O processamento pode levar alguns segundos.`);
                if (!ok) return;
            } else if (qtd >= this.LIMITE_AVISO && status) {
                status.className = 'alert alert-warning py-2 small';
                status.textContent = `Gerando ${qtd} apostas — aguarde...`;
            }

            if (!this.analise) {
                alert('Carregue os concursos na análise visual primeiro.');
                return;
            }

            await this.resolverMesAtrasado();
            const apostas = [];
            for (let i = 0; i < qtd; i++) {
                apostas.push(this._montarAposta(K, i, apostas, this.analise));
            }
            this.ultimasApostas = apostas;
            this._metricasDiversidade = this._calcularMetricasDiversidade(apostas);
            this._renderApostas();
            if (status) {
                const mesTxt = MESES_ABREV[this.mesExport - 1] || '???';
                const div = this._metricasDiversidade;
                status.className = 'alert alert-success py-2 small';
                status.innerHTML =
                    `<strong>${qtd} apostas</strong> (${K} dez.) · Mês: <strong>${mesTxt}</strong> · ` +
                    `Base: <strong>histórico completo</strong> com ${this.analise.total} concursos carregados. ` +
                    `Overlap médio: <strong>${div.overlapMedio}</strong> dezenas em comum entre cada par de apostas ` +
                    `(quanto <strong>menor</strong>, mais diversificado; padrões rotativos: coluna/diagonal/par).`;
            }
        }

        _calcularMetricasDiversidade(apostas) {
            let soma = 0;
            let pares = 0;
            for (let i = 0; i < apostas.length; i++) {
                for (let j = i + 1; j < apostas.length; j++) {
                    soma += this._overlap(apostas[i], apostas[j]);
                    pares++;
                }
            }
            return { overlapMedio: pares ? (soma / pares).toFixed(2) : '0' };
        }

        exportarTxt() {
            if (!this.ultimasApostas.length) {
                alert('Gere as apostas antes de exportar.');
                return;
            }
            const { min, max } = this._limitesDezenas();
            const invalidas = this.ultimasApostas.filter((j) => j.length < min || j.length > max);
            if (invalidas.length) {
                alert(
                    `${invalidas.length} aposta(s) com quantidade inválida (use entre ${min} e ${max} dezenas). Ajuste clicando nos números.`
                );
                return;
            }
            const mesTxt = MESES_ABREV[this.mesExport - 1] || 'JAN';
            const lines = this.ultimasApostas.map((j) =>
                j.map((n) => this._pad(n)).join(' ') + ' ' + mesTxt
            );
            const blob = new Blob([lines.join('\n')], { type: 'text/plain;charset=utf-8' });
            const a = document.createElement('a');
            a.href = URL.createObjectURL(blob);
            a.download = 'gerador_volante_circulos.txt';
            a.click();
            URL.revokeObjectURL(a.href);
        }

        _htmlCelulaVolante(n, selecionado, idxAposta) {
            const cls = selecionado ? 'sorteado' : 'nao-sorteado';
            return `<button type="button" class="numero-circulo volante-num-btn ${cls}"
                data-aposta-idx="${idxAposta}" data-volante-num="${n}"
                title="Clique para ${selecionado ? 'remover' : 'incluir'} ${this._pad(n)}">${this._pad(n)}</button>`;
        }

        _htmlGradeVolanteInterativo(jogo, idxAposta) {
            const set = new Set(jogo);
            let html = '';
            for (let n = 1; n <= 31; n++) {
                html += this._htmlCelulaVolante(n, set.has(n), idxAposta);
            }
            return html;
        }

        _htmlApostaNormal(jogo, idxAposta, mesTxt) {
            const set = new Set(jogo);
            const chips = [];
            for (let n = 1; n <= 31; n++) {
                const sel = set.has(n);
                chips.push(
                    `<button type="button" class="volante-pill ${sel ? 'volante-pill-on' : ''}"
                        data-aposta-idx="${idxAposta}" data-volante-num="${n}">${this._pad(n)}</button>`
                );
            }
            return `
            <div class="volante-normal-card" data-aposta-card="${idxAposta}">
                <div class="volante-normal-head">
                    <span><strong>#${idxAposta + 1}</strong> <span class="${this._contadorClasse(jogo.length)}">${jogo.length} dez.</span></span>
                    <span class="badge-volante-mes">${mesTxt}</span>
                </div>
                <div class="volante-normal-chips">${chips.join('')}</div>
                <div class="volante-normal-resumo">${jogo.map((n) => this._pad(n)).join(' ') || '—'}</div>
                <div class="volante-aposta-aviso"></div>
            </div>`;
        }

        _htmlApostaVolante(jogo, idxAposta, mesTxt) {
            return `
            <div class="volante-aposta-card-editable" data-aposta-card="${idxAposta}">
                <div class="volante-aposta-head">
                    <div>
                        <strong>Aposta #${idxAposta + 1}</strong>
                        <span class="ms-1 ${this._contadorClasse(jogo.length)}">${jogo.length} dez.</span>
                    </div>
                    <span class="badge-volante-mes">${mesTxt}</span>
                </div>
                <p class="volante-aposta-dica"><i class="fas fa-hand-pointer"></i> Clique nos números para ajustar</p>
                <div class="grade-circulos grade-circulos-editavel">
                    ${this._htmlGradeVolanteInterativo(jogo, idxAposta)}
                </div>
                <div class="volante-aposta-resumo">${jogo.map((n) => this._pad(n)).join(' ')}</div>
                <div class="volante-aposta-aviso"></div>
            </div>`;
        }

        _renderApostas() {
            const root = document.getElementById('volanteGeradorResultados');
            if (!root) return;

            if (!this.ultimasApostas.length) {
                root.innerHTML = '';
                return;
            }

            const mesTxt = MESES_ABREV[this.mesExport - 1] || '—';
            const maxPreview = 50;
            const show = this.ultimasApostas.slice(0, maxPreview);
            const modo = this.modoExibicaoApostas;
            const volanteAtivo = modo === 'volante';

            let corpo = '';
            if (volanteAtivo) {
                corpo = `<div class="volante-gerador-grid">${show
                    .map((jogo, i) => this._htmlApostaVolante(jogo, i, mesTxt))
                    .join('')}</div>`;
            } else {
                corpo = `<div class="volante-lista-normal">${show
                    .map((jogo, i) => this._htmlApostaNormal(jogo, i, mesTxt))
                    .join('')}</div>`;
            }

            root.innerHTML = `
                <div class="volante-resultados-toolbar">
                    <h6 class="volante-resultados-titulo mb-0">
                        <i class="fas fa-ticket-alt"></i> Apostas geradas
                        <span class="text-muted fw-normal">(${show.length}${this.ultimasApostas.length > maxPreview ? ` / ${this.ultimasApostas.length}` : ''})</span>
                    </h6>
                    <div class="btn-group btn-group-sm volante-modo-toggle" role="group">
                        <button type="button" class="btn ${volanteAtivo ? 'btn-volante-active' : 'btn-outline-volante'}"
                            onclick="analiseVolanteInteligente.setModoExibicao('volante')">
                            <i class="fas fa-th"></i> Ver no volante
                        </button>
                        <button type="button" class="btn ${!volanteAtivo ? 'btn-volante-active' : 'btn-outline-volante'}"
                            onclick="analiseVolanteInteligente.setModoExibicao('normal')">
                            <i class="fas fa-list"></i> Ver normal
                        </button>
                    </div>
                </div>
                <p class="volante-edit-hint small text-muted mb-2">
                    <i class="fas fa-edit"></i> Cada aposta explora um recorte do histórico (coluna/diagonal/par diferente). Clique para ajustar (${this.DEZ_MIN}–${this.DEZ_MAX} dezenas).
                    ${this._metricasDiversidade ? ` Overlap médio: <strong>${this._metricasDiversidade.overlapMedio}</strong>.` : ''}
                </p>
                <div id="volanteGeradorResultadosBody">${corpo}</div>
                ${
                    this.ultimasApostas.length > maxPreview
                        ? `<p class="small text-muted mt-2 mb-0">
                            <i class="fas fa-info-circle"></i> Exibindo ${maxPreview} na tela · demais no <strong>Exportar TXT</strong>.
                           </p>`
                        : ''
                }`;

            this._bindApostasClick();
        }

        render(containerId, concursos) {
            const container = document.getElementById(containerId);
            if (!container) return;

            this.analise = this.analisar(concursos);
            if (!this.analise) {
                container.innerHTML =
                    '<div class="alert alert-warning">Sem concursos para análise do volante.</div>';
                return;
            }

            const a = this.analise;
            const colTop = a.colunas
                .slice(0, 5)
                .map(
                    (c) =>
                        `<span class="badge me-1 mb-1" style="background:${CORES.escuro};color:#fff">Col ${c.col + 1}: ${c.dezenas.map((n) => this._pad(n)).join(' ')} (${c.pct}%)</span>`
                )
                .join('');

            const diagHtml = a.diagonais
                .slice(0, 6)
                .map(
                    (d) =>
                        `<li class="small"><span class="badge bg-secondary">${d.tipo}</span> ${d.numeros.map((n) => this._pad(n)).join(' → ')} <strong>${d.hits}</strong>x</li>`
                )
                .join('');

            const paresHtml = a.topPares
                .slice(0, 6)
                .map((p) => `<span class="badge bg-light text-dark border me-1">${this._pad(p.a)}-${this._pad(p.b)} (${p.freq})</span>`)
                .join('');

            const avisoHistorico =
                a.total < 400
                    ? `<div class="alert alert-warning py-2 small mb-3">
                        <i class="fas fa-exclamation-triangle"></i> Apenas <strong>${a.total}</strong> concursos carregados.
                        No topo da Análise Visual, escolha limite <strong>Todos</strong> e clique em <strong>Carregar</strong> para usar todo o histórico da Dia de Sorte.
                       </div>`
                    : `<div class="alert alert-success py-2 small mb-3">
                        <i class="fas fa-database"></i> Histórico completo: <strong>${a.total}</strong> concursos entram na análise (colunas, diagonais, pares, frequência e atraso).
                       </div>`;

            container.innerHTML = `
            <div class="volante-inteligente-container" id="volanteGeradorSection">
                <div class="volante-inteligente-header">
                    <h3 class="volante-inteligente-title"><i class="fas fa-brain"></i> Análise do volante + Gerador inteligente</h3>
                    <span class="badge" style="background:${CORES.principal};color:${CORES.escuro}">${a.total} concursos</span>
                </div>

                ${avisoHistorico}

                <div class="alert alert-light border mb-3 py-2 px-3" style="font-size:12px;border-left:4px solid ${CORES.principal}!important;">
                    <div class="fw-bold text-dark mb-1"><i class="fas fa-info-circle" style="color:${CORES.principal}"></i> O que esta análise faz</div>
                    <ul class="mb-0 ps-3 small text-muted">
                        <li>Lê o volante em <strong>10 colunas × 4 linhas</strong> e analisa <strong>todo o histórico carregado</strong> na Análise Visual: colunas, diagonais, duplas, linhas, frequência e atraso.</li>
                        <li><strong>Dica:</strong> no topo da página, use limite <strong>Todos</strong> e clique em Carregar para incluir todos os concursos do banco.</li>
                        <li>O <strong>gerador</strong> monta cada aposta com <strong>padrão diferente</strong> (coluna/diagonal/par/linha rotativos) e <strong>diversifica</strong> entre jogos — não é igual à Concentração (que repete dezenas de propósito).</li>
                        <li><strong>Edição:</strong> após gerar, clique nos números para ajustar cada aposta (volante ou lista).</li>
                        <li><strong>Exportação TXT:</strong> uma aposta por linha + mês abreviado <strong>automático</strong> (mês mais atrasado no histórico).</li>
                        <li>Também disponível via link na aba <strong>Quadrantes</strong>.</li>
                    </ul>
                </div>

                <div class="row g-3 mb-3">
                    <div class="col-md-6">
                        <h6 class="small fw-bold" style="color:${CORES.escuro}"><i class="fas fa-columns"></i> Colunas (verticais)</h6>
                        <p class="small text-muted mb-1">Quente: col ${a.colQuente.col + 1} · Fria: col ${a.colFria.col + 1}</p>
                        <div>${colTop}</div>
                    </div>
                    <div class="col-md-6">
                        <h6 class="small fw-bold" style="color:${CORES.escuro}"><i class="fas fa-slash"></i> Diagonais recorrentes</h6>
                        <ul class="mb-0 ps-3">${diagHtml || '<li class="small text-muted">—</li>'}</ul>
                    </div>
                    <div class="col-12">
                        <h6 class="small fw-bold" style="color:${CORES.escuro}"><i class="fas fa-link"></i> Duplas adjacentes no volante</h6>
                        <div>${paresHtml || '<span class="small text-muted">—</span>'}</div>
                    </div>
                </div>

                <div class="card border-0 shadow-sm mb-3" style="background:${CORES.claro};border:1px solid ${CORES.principal}!important;">
                    <div class="card-body py-3">
                        <h6 class="fw-bold mb-2" style="color:${CORES.escuro}"><i class="fas fa-magic"></i> Gerador estratégico</h6>
                        <div class="row g-2 align-items-end mb-2">
                            <div class="col-6 col-md-3">
                                <label class="form-label small mb-0">Dezenas por aposta</label>
                                <select id="volanteQtdDezenas" class="form-select form-select-sm">
                                    ${[7, 8, 9, 10, 11, 12, 13, 14, 15]
                                        .map((n) => `<option value="${n}"${n === 7 ? ' selected' : ''}>${n}</option>`)
                                        .join('')}
                                </select>
                            </div>
                            <div class="col-6 col-md-3">
                                <label class="form-label small mb-0">Quantidade de apostas</label>
                                <input type="number" id="volanteQtdApostas" class="form-control form-control-sm" min="1" max="15000" value="10">
                            </div>
                            <div class="col-12 col-md-6">
                                <p class="small text-muted mb-0">Alerta a partir de ${this.LIMITE_AVISO} · confirmação ≥ ${this.LIMITE_CONFIRMA} · crítico ≥ ${this.LIMITE_CRITICO}</p>
                            </div>
                        </div>
                        <div class="d-flex flex-wrap gap-2">
                            <button type="button" class="btn btn-sm fw-bold text-dark" style="background:${CORES.principal}"
                                onclick="analiseVolanteInteligente.gerar()">
                                <i class="fas fa-cogs"></i> Gerar apostas
                            </button>
                            <button type="button" class="btn btn-outline-dark btn-sm" onclick="analiseVolanteInteligente.exportarTxt()">
                                <i class="fas fa-download"></i> Exportar TXT
                            </button>
                        </div>
                        <div id="volanteGeradorStatus" class="alert alert-secondary py-2 mt-2 mb-0 small">Pronto para gerar.</div>
                        <div id="volanteGeradorResultados" class="mt-3"></div>
                    </div>
                </div>
            </div>`;
        }
    }

    const analiseVolanteInteligente = new AnaliseVolanteInteligente();
    window.analiseVolanteInteligente = analiseVolanteInteligente;

    window.abrirGeradorVolanteCirculos = function () {
        const tab = document.getElementById('tab-circulos');
        if (tab) bootstrap.Tab.getOrCreateInstance(tab).show();
        setTimeout(() => {
            const conc = typeof concursosCarregados !== 'undefined' ? concursosCarregados : [];
            if (conc.length) analiseVolanteInteligente.render('analiseVolanteInteligenteContainer', conc);
            document.getElementById('volanteGeradorSection')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 350);
    };
})();
