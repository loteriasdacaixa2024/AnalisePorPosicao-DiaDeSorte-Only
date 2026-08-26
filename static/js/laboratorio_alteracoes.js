/**
 * Laboratório de Alterações — Análise Visual / Dia de Sorte
 */
(function () {
    'use strict';

    const MAX_PADRAO = 10;
    const MAX_EXPANDIDO = 100;
    const MAX_DEZENAS_CONCURSO = 2;
    const LS_MAIS_APOSTAS = 'laboratorioAlteracoesPermitirMais';
    const MESES = ['', 'Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'];
    const MESES_FULL = ['', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'];

    const MES_TOKEN_MAP = (() => {
        const map = {};
        const norm = (s) => String(s || '').toLowerCase()
            .normalize('NFD').replace(/[\u0300-\u036f]/g, '').trim();
        MESES.forEach((ab, i) => {
            if (!i) return;
            map[norm(ab)] = i;
            map[norm(MESES_FULL[i])] = i;
            map[norm(MESES_FULL[i]).slice(0, 3)] = i;
        });
        map.agosto = 8;
        map.marco = 3;
        map.fevereiro = 2;
        map.setembro = 9;
        map.dezembro = 12;
        return map;
    })();

    const LabAlteracoes = {
        originais: [],
        alteradas: [],
        concurso: null,
        analise: null,
        origem: 'manual',
        modo: 'auto',
        permitirMaisApostas: false,
        coresMeses: {},
        fixasHibrido: [],
        fixarMesHibrido: [],

        getLimiteApostas() {
            return this.permitirMaisApostas ? MAX_EXPANDIDO : MAX_PADRAO;
        },

        ensureHibridoArrays() {
            const lim = this.getLimiteApostas();
            while (this.fixasHibrido.length < lim) {
                this.fixasHibrido.push([]);
                this.fixarMesHibrido.push(false);
            }
        },

        payloadApiBase() {
            return {
                permitir_mais_apostas: this.permitirMaisApostas,
                limite_apostas: this.getLimiteApostas(),
            };
        },

        atualizarUiLimiteApostas() {
            const lim = this.getLimiteApostas();
            const cnt = document.getElementById('labContadorApostas');
            if (cnt) cnt.textContent = `${this.originais.length} / ${lim}`;
            const hint = document.getElementById('labLimiteApostasHint');
            if (hint) {
                hint.textContent = this.permitirMaisApostas
                    ? `Modo expandido: até ${MAX_EXPANDIDO} apostas por lote.`
                    : `Padrão: até ${MAX_PADRAO} apostas. Ative o toggle para importar mais.`;
            }
            const empty = document.getElementById('labEmptyApostasMsg');
            if (empty) {
                empty.textContent = `Nenhuma aposta. Importe até ${lim} linhas${this.permitirMaisApostas ? ' (modo expandido)' : ''}.`;
            }
        },

        carregarPreferenciaMaisApostas() {
            try {
                this.permitirMaisApostas = localStorage.getItem(LS_MAIS_APOSTAS) === '1';
            } catch (e) {
                this.permitirMaisApostas = false;
            }
            const toggle = document.getElementById('labToggleMaisApostas');
            if (toggle) toggle.checked = this.permitirMaisApostas;
            this.ensureHibridoArrays();
            this.atualizarUiLimiteApostas();
        },

        salvarPreferenciaMaisApostas() {
            try {
                localStorage.setItem(LS_MAIS_APOSTAS, this.permitirMaisApostas ? '1' : '0');
            } catch (e) { /* ignore */ }
        },

        init() {
            this.carregarPreferenciaMaisApostas();
            this.bindUi();
            this.carregarConcursosSelect();
            this.carregarCoresMeses();
            this.carregarConcurso();
            this.processarTransferencia();
            this.carregarHistorico();
            const tab = document.getElementById('tab-laboratorio-alteracoes');
            if (tab) {
                tab.addEventListener('shown.bs.tab', () => {
                    this.processarTransferencia();
                    this.render();
                    this.initTooltips(document.getElementById('pane-laboratorio-alteracoes'));
                });
            }
            this.initTooltips(document.getElementById('pane-laboratorio-alteracoes'));
        },

        bindUi() {
            document.getElementById('labBtnImportar')?.addEventListener('click', () => this.importarTexto());
            document.getElementById('labBtnAuto')?.addEventListener('click', () => this.gerarAlteradas('auto'));
            document.getElementById('labBtnHibrido')?.addEventListener('click', () => this.gerarAlteradas('hibrido'));
            document.getElementById('labBtnAnalisar')?.addEventListener('click', () => this.analisar());
            document.getElementById('labBtnSalvar')?.addEventListener('click', () => this.salvar());
            document.getElementById('labBtnExportarTxt')?.addEventListener('click', () => this.exportarAlteradasTxt());
            document.getElementById('labBtnExportarTxtRodape')?.addEventListener('click', () => this.exportarAlteradasTxt());
            document.getElementById('labToggleMaisApostas')?.addEventListener('change', (e) => {
                this.permitirMaisApostas = !!e.target.checked;
                this.salvarPreferenciaMaisApostas();
                this.ensureHibridoArrays();
                const lim = this.getLimiteApostas();
                if (!this.permitirMaisApostas && this.originais.length > MAX_PADRAO) {
                    this.originais = this.originais.slice(0, MAX_PADRAO);
                    this.alteradas = this.alteradas.slice(0, MAX_PADRAO);
                    this.analise = null;
                    alert(`Toggle desligado: mantidas apenas as ${MAX_PADRAO} primeiras apostas.`);
                }
                this.atualizarUiLimiteApostas();
                this.render();
            });
            document.getElementById('labSelectConcurso')?.addEventListener('change', async (e) => {
                const v = parseInt(e.target.value, 10);
                if (!isNaN(v)) await this.carregarConcurso(v, true);
            });
            document.querySelectorAll('input[name="labModo"]').forEach((r) => {
                r.addEventListener('change', () => {
                    this.modo = r.value;
                    document.getElementById('labHibridoPainel').style.display =
                        this.modo === 'hibrido' ? 'block' : 'none';
                    this.render();
                });
            });
            const drop = document.getElementById('labDropZone');
            if (drop) {
                drop.addEventListener('dragover', (e) => { e.preventDefault(); drop.classList.add('border-warning'); });
                drop.addEventListener('dragleave', () => drop.classList.remove('border-warning'));
                drop.addEventListener('drop', (e) => {
                    e.preventDefault();
                    drop.classList.remove('border-warning');
                    const f = e.dataTransfer?.files?.[0];
                    if (f) this.lerArquivo(f);
                });
            }
        },

        async carregarCoresMeses() {
            try {
                const r = await fetch('/api/cores-meses/listar');
                const j = await r.json();
                if (j.sucesso && j.cores) {
                    j.cores.forEach((c) => {
                        const m = parseInt(c.mes, 10);
                        if (m >= 1 && m <= 12) this.coresMeses[m] = c.cor_hex;
                    });
                }
            } catch (e) { /* ignore */ }
        },

        parseMesToken(token) {
            if (token == null || token === '') return null;
            const n = parseInt(token, 10);
            if (!isNaN(n) && n >= 1 && n <= 12) return n;
            const key = String(token).toLowerCase()
                .normalize('NFD').replace(/[\u0300-\u036f]/g, '').trim();
            return MES_TOKEN_MAP[key] || null;
        },

        resolverMes(item) {
            if (!item || typeof item !== 'object') return null;
            if (item.mes != null && item.mes !== '') {
                const m = this.parseMesToken(item.mes);
                if (m) return m;
            }
            if (item.mes_sorte != null) {
                const m = this.parseMesToken(item.mes_sorte);
                if (m) return m;
            }
            const nome = item.mes_nome || item.mesNome || item.mes_sorte_nome;
            if (nome) return this.parseMesToken(nome);
            return null;
        },

        mesStyle(m) {
            if (!m) return 'background:#f8f9fa;color:#6c757d;border:1px solid #dee2e6';
            const hex = this.coresMeses[m];
            if (!hex) return 'background:#e9ecef;color:#212529;border:1px solid #adb5bd';
            return `background:${hex};color:#fff;border-color:${hex}`;
        },

        mesLabel(m) {
            return m ? MESES_FULL[m] : 'Mês não informado';
        },

        async carregarConcursosSelect() {
            const sel = document.getElementById('labSelectConcurso');
            if (!sel) return;
            try {
                const r = await fetch('/api/laboratorio-alteracoes/concursos');
                const j = await r.json();
                if (!j.sucesso) return;
                sel.innerHTML = j.concursos.map((c) =>
                    `<option value="${c.concurso}">${c.label}</option>`
                ).join('');
                if (this.concurso?.concurso) {
                    sel.value = String(this.concurso.concurso);
                }
            } catch (e) {
                console.warn(e);
            }
        },

        async carregarConcurso(num, recalcularAutomatico = false) {
            const sel = document.getElementById('labSelectConcurso');
            if (sel && recalcularAutomatico) {
                sel.disabled = true;
            }
            try {
                const url = num
                    ? `/api/laboratorio-alteracoes/concurso?concurso=${num}`
                    : '/api/laboratorio-alteracoes/concurso';
                const r = await fetch(url);
                const j = await r.json();
                if (j.sucesso) {
                    this.concurso = j.concurso;
                    this.renderConcursoBanner();
                    if (sel && this.concurso) sel.value = String(this.concurso.concurso);
                    if (recalcularAutomatico && this.originais.length && this.alteradas.length) {
                        await this.analisar({ silencioso: true });
                    } else {
                        this.render();
                    }
                }
            } catch (e) {
                console.warn(e);
            } finally {
                if (sel) sel.disabled = false;
            }
        },

        renderConcursoBanner() {
            const el = document.getElementById('labConcursoBanner');
            if (!el || !this.concurso) return;
            const c = this.concurso;
            const nums = (c.numeros || []).map((n) => String(n).padStart(2, '0')).join(' ');
            const mesStyle = this.mesStyle(c.mes_sorte);
            el.innerHTML = `
                <div class="d-flex flex-wrap align-items-center justify-content-center gap-2 text-center lab-concurso-banner-inner w-100">
                    <span class="badge bg-dark">#${c.concurso}</span>
                    <span class="text-muted">${c.data_sorteio || ''}</span>
                    <span class="lab-mes-pill" style="${mesStyle}">${c.mes_nome || ''}</span>
                    <span class="fw-bold lab-concurso-nums">${nums}</span>
                </div>`;
        },

        initTooltips(root) {
            if (typeof bootstrap === 'undefined') return;
            const scope = root || document.getElementById('pane-laboratorio-alteracoes');
            if (!scope) return;
            scope.querySelectorAll('[data-bs-toggle="tooltip"]').forEach((el) => {
                const inst = bootstrap.Tooltip.getInstance(el);
                if (inst) inst.dispose();
                new bootstrap.Tooltip(el, { container: 'body', trigger: 'hover focus' });
            });
        },

        processarTransferencia() {
            const raw = localStorage.getItem('laboratorioAlteracoesTransfer');
            if (!raw) return;
            try {
                const data = JSON.parse(raw);
                localStorage.removeItem('laboratorioAlteracoesTransfer');
                const lista = data.apostas || data.jogos || [];
                this.origem = data.origem || 'gerador';
                this.setOriginais(lista);
                if (data.abrirAba !== false) {
                    const tab = document.getElementById('tab-laboratorio-alteracoes');
                    if (tab && typeof bootstrap !== 'undefined') {
                        bootstrap.Tab.getOrCreateInstance(tab).show();
                    }
                }
            } catch (e) {
                console.warn(e);
            }
        },

        setOriginais(lista) {
            this.ensureHibridoArrays();
            const lim = this.getLimiteApostas();
            this.originais = [];
            for (let i = 0; i < lista.length && this.originais.length < lim; i++) {
                const item = lista[i];
                let nums = item.numeros || item.dezenas || item;
                if (typeof nums === 'string') {
                    nums = nums.split(/[\s,;]+/).map(Number).filter((n) => !isNaN(n) && n >= 1 && n <= 31);
                }
                nums = [...new Set(nums)].sort((a, b) => a - b);
                if (nums.length >= 7) {
                    this.originais.push({
                        numeros: nums.slice(0, 15),
                        mes: this.resolverMes(item),
                    });
                }
            }
            this.alteradas = [];
            this.analise = null;
            this.render();
            if (this.originais.length) {
                this.gerarAlteradas(this.modo || 'auto');
            }
        },

        parseLinhasTexto(txt) {
            const lim = this.getLimiteApostas();
            const linhas = txt.split(/\r?\n/).map((l) => l.trim()).filter(Boolean);
            const apostas = [];
            for (const linha of linhas) {
                if (apostas.length >= lim) break;
                const parts = linha.split(/[\s,;]+/).filter(Boolean);
                const nums = [];
                let mes = null;
                parts.forEach((p) => {
                    const n = parseInt(p, 10);
                    if (!isNaN(n) && n >= 1 && n <= 31) {
                        nums.push(n);
                        return;
                    }
                    if (mes == null) {
                        const m = this.parseMesToken(p);
                        if (m) mes = m;
                    }
                });
                const uniq = [...new Set(nums)].sort((a, b) => a - b);
                if (uniq.length >= 7) {
                    apostas.push({ numeros: uniq.slice(0, 15), mes });
                }
            }
            return apostas;
        },

        importarTexto() {
            const ta = document.getElementById('labTextoImport');
            const txt = ta ? ta.value.trim() : '';
            if (!txt) return;
            const lim = this.getLimiteApostas();
            const linhasValidas = txt.split(/\r?\n/).map((l) => l.trim()).filter(Boolean);
            if (linhasValidas.length > lim) {
                alert(`Máximo de ${lim} apostas${this.permitirMaisApostas ? '' : '. Ative "Mais de 10 apostas" para importar até ' + MAX_EXPANDIDO}.`);
                return;
            }
            const apostas = this.parseLinhasTexto(txt);
            if (!apostas.length) {
                alert(`Nenhuma aposta válida (mín. 7 dezenas, máx. ${lim} linhas).`);
                return;
            }
            this.origem = 'importacao';
            this.setOriginais(apostas);
        },

        lerArquivo(file) {
            const reader = new FileReader();
            reader.onload = () => {
                const texto = String(reader.result || '');
                const lim = this.getLimiteApostas();
                const linhasValidas = texto.split(/\r?\n/).map((l) => l.trim()).filter(Boolean);
                if (linhasValidas.length > lim) {
                    alert(`Máximo de ${lim} apostas no arquivo${this.permitirMaisApostas ? '' : '. Ative o toggle para mais de 10.'}.`);
                    return;
                }
                const apostas = this.parseLinhasTexto(texto);
                if (!apostas.length) {
                    alert('Arquivo sem apostas válidas.');
                    return;
                }
                this.origem = 'arquivo:' + file.name;
                this.setOriginais(apostas);
            };
            reader.readAsText(file);
        },

        async gerarAlteradas(modo) {
            this.modo = modo || 'auto';
            if (!this.originais.length) {
                alert('Importe ou receba apostas originais primeiro.');
                return;
            }
            const body = {
                ...this.payloadApiBase(),
                originais: this.originais,
                modo: this.modo,
                concurso_ref: this.concurso?.concurso,
                fixas_por_linha: this.modo === 'hibrido' ? this.fixasHibrido : undefined,
                fixar_mes_por_linha: this.modo === 'hibrido' ? this.fixarMesHibrido : undefined,
            };
            try {
                const r = await fetch('/api/laboratorio-alteracoes/gerar-alteradas', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(body),
                });
                const j = await r.json();
                if (!j.sucesso) {
                    alert(j.erro || 'Erro ao gerar alteradas.');
                    return;
                }
                this.alteradas = j.alteradas || [];
                this.analise = j.analise;
                if (j.concurso) {
                    this.concurso = j.concurso;
                    this.renderConcursoBanner();
                }
                this.render();
            } catch (e) {
                alert('Falha de rede: ' + e.message);
            }
        },

        async analisar(opcoes) {
            const silencioso = opcoes && opcoes.silencioso;
            if (!this.originais.length || !this.alteradas.length) {
                if (!silencioso) alert('Originais e alteradas necessárias.');
                return false;
            }
            if (!this.concurso?.concurso) {
                if (!silencioso) alert('Selecione um concurso de referência.');
                return false;
            }
            const lim = this.getLimiteApostas();
            const body = {
                ...this.payloadApiBase(),
                originais: this.originais.slice(0, lim),
                alteradas: this.alteradas.slice(0, lim),
                concurso_ref: this.concurso.concurso,
            };
            try {
                const r = await fetch('/api/laboratorio-alteracoes/analisar', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(body),
                });
                const j = await r.json();
                if (!j.sucesso) {
                    if (!silencioso) alert(j.erro || 'Erro na análise.');
                    return false;
                }
                this.analise = j.analise;
                if (j.concurso) this.concurso = j.concurso;
                this.render();
                return true;
            } catch (e) {
                if (!silencioso) alert('Falha: ' + e.message);
                return false;
            }
        },

        async salvar() {
            if (!this.analise || !this.concurso) {
                alert('Execute a análise antes de salvar.');
                return;
            }
            try {
                const r = await fetch('/api/laboratorio-alteracoes/salvar', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        concurso_ref: this.concurso.concurso,
                        origem: this.origem,
                        analise: this.analise,
                    }),
                });
                const j = await r.json();
                if (j.sucesso) {
                    alert('Registro salvo (acertos 4–7 em JSON). ID: ' + j.id);
                    this.carregarHistorico();
                } else {
                    alert(j.erro || 'Erro ao salvar.');
                }
            } catch (e) {
                alert('Falha: ' + e.message);
            }
        },

        async carregarHistorico() {
            const el = document.getElementById('labHistoricoLista');
            if (!el) return;
            try {
                const r = await fetch('/api/laboratorio-alteracoes/historico?limite=15');
                const j = await r.json();
                if (!j.sucesso) return;
                el.innerHTML = (j.historico || []).map((h) => {
                    const r = h.resumo || {};
                    return `<div class="small border-bottom py-1">
                        #${h.id} · ${h.criado_em} · Concurso ${h.concurso_ref} · ${h.origem}<br>
                        Orig ${r.media_originais} → Alt ${r.media_alteradas} (${r.evolucao || ''})
                    </div>`;
                }).join('') || '<span class="text-muted">Nenhum registro.</span>';
            } catch (e) { /* ignore */ }
        },

        hitsSet() {
            return new Set(this.concurso?.numeros || []);
        },

        contarDezenasConcurso(nums) {
            const conc = this.hitsSet();
            return (nums || []).filter((n) => conc.has(n)).length;
        },

        atualizarBotaoExportar() {
            const ok = this.alteradas.length > 0;
            ['labBtnExportarTxt', 'labBtnExportarTxtRodape'].forEach((id) => {
                const btn = document.getElementById(id);
                if (!btn) return;
                btn.disabled = !ok;
                btn.classList.toggle('opacity-50', !ok);
            });
            const bar = document.querySelector('#pane-laboratorio-alteracoes .lab-export-bar');
            if (bar) bar.style.display = ok ? '' : 'none';
        },

        exportarAlteradasTxt() {
            if (!this.alteradas.length) {
                alert('Gere ou edite as apostas alteradas antes de exportar.');
                return;
            }
            const linhas = this.alteradas.map((a, i) => {
                const nums = (a.numeros || []).map((n) => String(n).padStart(2, '0')).join(' ');
                const mes = a.mes;
                const token = mes && mes >= 1 && mes <= 12 ? MESES[mes] : '';
                if (!token) {
                    alert(`Aposta alterada #${i + 1} sem mês — clique no mês para definir.`);
                    return null;
                }
                return `${nums} ${token}`;
            });
            if (linhas.some((l) => l == null)) return;
            const texto = linhas.join('\n') + '\n';
            const blob = new Blob([texto], { type: 'text/plain;charset=utf-8' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            const ref = this.concurso?.concurso ? `_c${this.concurso.concurso}` : '';
            a.href = url;
            a.download = `apostas_alteradas${ref}_${new Date().toISOString().slice(0, 10)}.txt`;
            document.body.appendChild(a);
            a.click();
            a.remove();
            URL.revokeObjectURL(url);
        },

        ciclarMesAlterada(idx) {
            const alt = this.alteradas[idx];
            const orig = this.originais[idx];
            if (!alt) return;
            if (this.modo === 'hibrido' && this.fixarMesHibrido[idx]) return;
            let m = alt.mes || 1;
            for (let t = 0; t < 12; t++) {
                m = m >= 12 ? 1 : m + 1;
                if (!orig?.mes || m !== orig.mes) break;
            }
            alt.mes = m;
            this.analise = null;
            this.render();
        },

        renderDezenas(nums, hits, maxDestaque, tipoGrid, linhaIdx) {
            const hitSet = this.hitsSet();
            const extraCls = tipoGrid === 'orig' ? ' lab-dezena-orig' : (tipoGrid === 'alt' ? ' lab-dezena-alt' : '');
            let html = '';
            for (let n = 1; n <= 31; n++) {
                const sel = nums.includes(n);
                let cls = 'lab-dezena' + extraCls;
                if (sel) cls += ' sel';
                if (sel && tipoGrid === 'alt' && hitSet.has(n)) cls += ' conc';
                if (sel && hitSet.has(n)) {
                    cls += maxDestaque ? ' hit-max' : ' hit';
                }
                const data = tipoGrid ? ` data-n="${n}" data-linha="${linhaIdx}"` : '';
                html += `<span class="${cls}"${data}>${String(n).padStart(2, '0')}</span>`;
            }
            return html;
        },

        renderLinhas() {
            const wrap = document.getElementById('labLinhasContainer');
            if (!wrap) return;
            const n = Math.max(this.originais.length, this.alteradas.length);
            const lim = this.getLimiteApostas();
            if (!n) {
                wrap.innerHTML = `<p class="text-muted text-center lab-empty-msg" id="labEmptyApostasMsg">Nenhuma aposta. Importe até ${lim} linhas.</p>`;
                return;
            }
            let html = '';
            for (let i = 0; i < n && i < lim; i++) {
                const o = this.originais[i] || { numeros: [], mes: null };
                const a = this.alteradas[i];
                const altVazia = !a || !(a.numeros || []).length;
                const linhaAnalise = this.analise?.linhas?.find((l) => l.indice === i + 1);
                const co = linhaAnalise?.conf_orig;
                const ca = linhaAnalise?.conf_alt;
                html += `
                <div class="lab-linha-card">
                    <div class="row g-2">
                        <div class="col-md-6">
                            <div class="small fw-bold text-secondary">Original #${i + 1}
                                ${co ? `<span class="badge bg-secondary ms-1">${co.acertos_dezenas} ac.</span>` : ''}
                                ${co?.mes_acertou ? '<span class="badge bg-warning text-dark ms-1">Mês ✓</span>' : ''}
                            </div>
                            <div class="my-1 lab-grid-orig" data-linha="${i}">${this.renderDezenas(o.numeros, co, co?.acertos_dezenas >= 6, 'orig', i)}</div>
                            <span class="lab-mes-pill lab-mes-orig" data-linha="${i}" style="${this.mesStyle(o.mes)}" title="Mês da Sorte na aposta">${this.mesLabel(o.mes)}</span>
                        </div>
                        <div class="col-md-6">
                            <div class="small fw-bold text-primary">Alterada #${i + 1}
                                ${ca ? `<span class="badge ${ca.acertos_dezenas >= 6 ? 'bg-warning text-dark' : 'bg-primary'} ms-1">${ca.acertos_dezenas} ac.</span>` : ''}
                                ${ca?.mes_acertou ? '<span class="badge bg-warning text-dark ms-1">Mês ✓</span>' : ''}
                            </div>
                            ${altVazia
                                ? '<p class="small text-muted my-2">Clique em <strong>Gerar alteradas</strong> para diversificar (+/− dezenas e mês).</p>'
                                : `<div class="my-1 lab-grid-alt" data-linha="${i}">${this.renderDezenas(a.numeros, ca, ca?.acertos_dezenas >= 6, 'alt', i)}</div>
                            <span class="lab-mes-pill lab-mes-alt ${ca?.mes_acertou ? 'hit-mes' : ''}" data-linha="${i}" style="${this.mesStyle(a.mes)}" title="Clique para trocar o mês da aposta alterada">${this.mesLabel(a.mes)}</span>`}
                        </div>
                    </div>
                </div>`;
            }
            wrap.innerHTML = html;
            this.bindLinhasInteracao(wrap);
        },

        bindLinhasInteracao(wrap) {
            if (!wrap) return;
            wrap.querySelectorAll('.lab-mes-alt').forEach((mesEl) => {
                const idx = parseInt(mesEl.dataset.linha, 10);
                if (this.modo === 'hibrido' && this.fixarMesHibrido[idx]) return;
                mesEl.addEventListener('click', () => this.ciclarMesAlterada(idx));
            });
            if (this.modo === 'manual') {
                wrap.querySelectorAll('.lab-linha-card').forEach((card, idx) => {
                    const alt = this.alteradas[idx];
                    if (!alt) return;
                    card.querySelectorAll('.lab-dezena-alt').forEach((el) => {
                        el.addEventListener('click', () => {
                            const n = parseInt(el.dataset.n, 10);
                            const conc = this.hitsSet();
                            const qtdAlvo = (this.originais[idx]?.numeros || []).length;
                            const pos = alt.numeros.indexOf(n);
                            if (pos >= 0) {
                                if (alt.numeros.length <= qtdAlvo) return;
                                alt.numeros.splice(pos, 1);
                            } else {
                                if (alt.numeros.length >= qtdAlvo) return;
                                if (conc.has(n) && this.contarDezenasConcurso(alt.numeros) >= MAX_DEZENAS_CONCURSO) {
                                    alert(`Máximo ${MAX_DEZENAS_CONCURSO} dezenas do concurso de referência por aposta alterada.`);
                                    return;
                                }
                                alt.numeros.push(n);
                                alt.numeros.sort((a, b) => a - b);
                            }
                            this.analise = null;
                            this.render();
                        });
                    });
                });
                return;
            }
            if (this.modo !== 'hibrido') return;
            wrap.querySelectorAll('.lab-linha-card').forEach((card, idx) => {
                const fixas = this.fixasHibrido[idx] || [];
                card.querySelectorAll('.lab-dezena-orig').forEach((el) => {
                    const n = parseInt(el.dataset.n, 10);
                    if (fixas.includes(n)) el.classList.add('fixa');
                    el.addEventListener('click', () => {
                        if (this.modo !== 'hibrido') return;
                        const arr = this.fixasHibrido[idx] || [];
                        const pos = arr.indexOf(n);
                        if (pos >= 0) {
                            arr.splice(pos, 1);
                            el.classList.remove('fixa');
                        } else {
                            arr.push(n);
                            el.classList.add('fixa');
                        }
                        this.fixasHibrido[idx] = arr.sort((a, b) => a - b);
                    });
                });
                const mesEl = card.querySelector('.lab-mes-orig');
                if (mesEl) {
                    if (this.fixarMesHibrido[idx]) mesEl.classList.add('fixa-mes');
                    mesEl.addEventListener('click', () => {
                        if (this.modo !== 'hibrido') return;
                        this.fixarMesHibrido[idx] = !this.fixarMesHibrido[idx];
                        mesEl.classList.toggle('fixa-mes', this.fixarMesHibrido[idx]);
                    });
                }
            });
        },

        renderResumo() {
            const el = document.getElementById('labResumoPainel');
            if (!el || !this.analise?.resumo) {
                if (el) el.innerHTML = '';
                return;
            }
            const r = this.analise.resumo;
            const tip = (txt) => ` data-bs-toggle="tooltip" data-bs-placement="top" title="${txt.replace(/"/g, '&quot;')}"`;
            el.innerHTML = `
                <div class="lab-resumo-grid small">
                    <div class="lab-metric-box border rounded p-2 text-center"${tip('Média de acertos de dezenas nas apostas originais, comparadas ao resultado do concurso selecionado.')}>
                        <div class="text-muted lab-metric-label">Média Orig. <i class="fas fa-info-circle lab-metric-hint"></i></div>
                        <strong>${r.media_originais}</strong>
                    </div>
                    <div class="lab-metric-box border rounded p-2 text-center"${tip('Média de acertos de dezenas nas apostas alteradas (diversificadas) vs o mesmo concurso.')}>
                        <div class="text-muted lab-metric-label">Média Alt. <i class="fas fa-info-circle lab-metric-hint"></i></div>
                        <strong>${r.media_alteradas}</strong>
                    </div>
                    <div class="lab-metric-box border rounded p-2 text-center"${tip('Variação percentual: ((média alterada − média original) ÷ média original) × 100. Positivo = alteradas melhoraram.')}>
                        <div class="text-muted lab-metric-label">Δ % <i class="fas fa-info-circle lab-metric-hint"></i></div>
                        <strong class="${r.evolucao === 'positiva' ? 'text-success' : (r.evolucao === 'negativa' ? 'text-danger' : '')}">${r.diferenca_percentual > 0 ? '+' : ''}${r.diferenca_percentual}%</strong>
                    </div>
                    <div class="lab-metric-box border rounded p-2 text-center"${tip('Linhas em que a alterada superou / empatou / ficou abaixo da original (por quantidade de acertos de dezenas).')}>
                        <div class="text-muted lab-metric-label">Superaram <i class="fas fa-info-circle lab-metric-hint"></i></div>
                        <strong>${r.superaram}</strong> / ${r.empataram} / ${r.inferiores}
                    </div>
                </div>
                <p class="small text-muted mt-2 mb-0"${tip('Apostas com 4 ou mais acertos de dezenas. Melhor linha = maior número de acertos na coluna.')}>
                    Premiadas (4+): Orig ${r.premiadas_originais} · Alt ${r.premiadas_alteradas}.
                    Melhor: Orig #${r.melhor_original || '—'} · Alt #${r.melhor_alterada || '—'}
                    <i class="fas fa-info-circle lab-metric-hint"></i>
                </p>`;
            this.initTooltips(el);
        },

        renderRanking() {
            const el = document.getElementById('labRankingLista');
            if (!el || !this.analise?.ranking) {
                if (el) el.innerHTML = '';
                return;
            }
            el.innerHTML = `<table class="table table-sm table-striped mb-0"><thead><tr>
                <th>#</th><th>Tipo</th><th>Aposta</th><th>Acertos</th><th>Mês ✓</th>
            </tr></thead><tbody>` +
                this.analise.ranking.map((row) => {
                    const cls = row.acertos >= 7 ? 'lab-rank-7' : (row.acertos >= 6 ? 'lab-rank-6' : '');
                    return `<tr class="${cls}">
                        <td>${row.posicao}º</td>
                        <td>${row.tipo === 'alterada' ? 'Alterada' : 'Original'}</td>
                        <td>${row.tipo === 'alterada' ? 'A' : 'O'}${row.indice}</td>
                        <td><strong>${row.acertos}</strong></td>
                        <td>${row.mes_ok ? '✓' : '—'}</td>
                    </tr>`;
                }).join('') + '</tbody></table>';
        },

        render() {
            this.atualizarUiLimiteApostas();
            this.atualizarBotaoExportar();
            this.renderConcursoBanner();
            this.renderLinhas();
            this.renderResumo();
            this.renderRanking();
            this.initTooltips(document.getElementById('pane-laboratorio-alteracoes'));
        },
    };

    window.LaboratorioAlteracoes = LabAlteracoes;
    LabAlteracoes.init();
})();
