/**
 * Impressão: 30 listas por posição + 30 apostas — aba Ciclo por Posição
 */
(function () {
    'use strict';

    const API_RESUMO = '/api/estatisticas/ciclo-por-posicao/resumo';
    let pacoteCache = null;
    let selecao = { tipo: null, pos: null, linha: null, dezena: null };

    function pad(n) {
        return String(n).padStart(2, '0');
    }

    function el(id) {
        return document.getElementById(id);
    }

    function atualizarPainelSelecao(msg) {
        const box = el('cicloImpSelecao');
        if (box) box.innerHTML = msg;
    }

    function limparSelecaoVisual() {
        document.querySelectorAll('.ciclo-imp-row-sel, .ciclo-imp-cell-sel, .ciclo-imp-regra-sel').forEach((n) => {
            n.classList.remove('ciclo-imp-row-sel', 'ciclo-imp-cell-sel', 'ciclo-imp-regra-sel');
        });
    }

    function aplicarPacote(j) {
        if (!j || !j.sucesso) return;
        pacoteCache = j;
        selecao = { tipo: null, pos: null, linha: null, dezena: null };
        atualizarPainelSelecao(
            'Dados do <strong>último concurso do banco</strong> carregados. Clique em uma linha da tabela ou em uma célula da matriz.'
        );
        renderUltimo(j.ultimo_sorteio);
        renderTabelaRegra(j.tabela_regra);
        renderConferenciaDup(j.matriz_30);
        renderMatriz(j.matriz_30);
        renderValidacao(j.validacoes_colunas);
        renderApostas(j.apostas);
    }

    async function parseJsonResponse(r) {
        const text = await r.text();
        const ct = (r.headers.get('content-type') || '').toLowerCase();
        if (!ct.includes('application/json')) {
            if (text.trim().startsWith('<')) {
                throw new Error(
                    'Servidor retornou página HTML em vez de JSON. Reinicie o Python (feche a janela do servidor e abra de novo o DiaDeSorte_POSICAO.bat).'
                );
            }
            throw new Error(`Resposta inválida (HTTP ${r.status}).`);
        }
        return JSON.parse(text);
    }

    async function carregarImpressao30() {
        const qtd = parseInt(el('cicloImpQtdApostas')?.value, 10) || 30;
        const dez = parseInt(el('cicloImpDezenas')?.value, 10) || 7;
        const ult = el('cicloImpUltimo');
        const mat = el('cicloImpMatriz');

        if (ult) ult.textContent = 'Consultando último concurso no banco…';
        if (mat) mat.innerHTML = '<div class="p-3 text-center"><div class="spinner-border spinner-border-sm"></div></div>';

        try {
            const r = await fetch(`${API_RESUMO}?impressao=1&apostas=${qtd}&dezenas=${dez}`);
            const j = await parseJsonResponse(r);
            if (!r.ok) throw new Error(j.erro || `Erro HTTP ${r.status}`);
            const pacote = j.impressao || j;
            if (!pacote.sucesso) throw new Error(pacote.erro || 'Falha ao montar impressão');
            aplicarPacote(pacote);
        } catch (e) {
            if (ult) ult.innerHTML = `<span class="text-danger"><strong>Erro:</strong> ${e.message}</span>`;
            if (mat) mat.innerHTML = '';
        }
    }

    function renderUltimo(u) {
        const box = el('cicloImpUltimo');
        if (!box || !u) return;
        const cols = u.posicoes.map((p) => `<strong>${p.posicao}º</strong> ${pad(p.dezena)}`).join(' · ');
        box.innerHTML = `
            <strong>Último concurso no banco: nº ${u.concurso}</strong>${u.data ? ` · ${u.data}` : ''}<br>
            ${cols}<br>
            <span class="text-muted">Estas 7 dezenas não entram nos jogos gerados abaixo.</span>`;
    }

    function renderTabelaRegra(tab) {
        const box = el('cicloImpTabelaRegra');
        if (!box) return;
        if (!tab) {
            box.innerHTML = '<p class="small text-muted p-2 mb-0">Sem dados no banco.</p>';
            return;
        }
        let body = '';
        tab.linhas.forEach((r) => {
            const saiu = r.saiu_ultimo_concurso != null ? pad(r.saiu_ultimo_concurso) : '—';
            const nao = r.nao_apostar != null ? pad(r.nao_apostar) : '—';
            body += `<tr class="ciclo-imp-regra-row" data-pos="${r.posicao}" role="button" tabindex="0">
                <td class="fw-bold">${r.rotulo}</td>
                <td class="text-center">${saiu}</td>
                <td class="text-center text-danger fw-bold">${nao}</td>
                <td class="text-center">${r.quantidade_jogaveis}</td>
                <td class="ciclo-imp-lista-jogaveis small">${r.dezenas_texto || '—'}</td>
            </tr>`;
        });
        box.innerHTML = `
            <table class="table table-sm table-bordered table-hover mb-0 ciclo-imp-table-regra">
                <caption class="caption-top small text-muted px-2 pt-2">
                    Último no banco: <strong>nº ${tab.concurso_base}</strong>
                    ${tab.data_ultimo ? ` (${tab.data_ultimo})` : ''}
                    · Próximo: <strong>nº ${tab.proximo_concurso}</strong>
                </caption>
                <thead class="table-warning">
                    <tr>
                        <th>Posição</th>
                        <th class="text-center">Saiu (último)</th>
                        <th class="text-center">Não apostar</th>
                        <th class="text-center">Qtd.</th>
                        <th>Dezenas jogáveis</th>
                    </tr>
                </thead>
                <tbody>${body}</tbody>
            </table>`;

        box.querySelectorAll('.ciclo-imp-regra-row').forEach((row) => {
            const ativar = () => {
                limparSelecaoVisual();
                row.classList.add('ciclo-imp-regra-sel');
                const pos = parseInt(row.getAttribute('data-pos'), 10);
                const linha = tab.linhas.find((x) => x.posicao === pos);
                selecao = { tipo: 'regra', pos, linha: null, dezena: null };
                atualizarPainelSelecao(
                    `<strong>Posição ${pos}</strong> · não apostar <strong>${pad(linha.nao_apostar)}</strong> · ` +
                        `<strong>${linha.quantidade_jogaveis}</strong> jogáveis: ${linha.dezenas_texto}`
                );
            };
            row.addEventListener('click', ativar);
            row.addEventListener('keydown', (ev) => {
                if (ev.key === 'Enter' || ev.key === ' ') {
                    ev.preventDefault();
                    ativar();
                }
            });
        });
    }

    function classeTipoCelula(tipo) {
        if (tipo === 'jogavel') return 'ciclo-imp-cel-jogavel';
        if (tipo === 'complemento' || tipo === 'saida') return 'ciclo-imp-cel-complemento';
        if (tipo === 'nao_apostar') return 'ciclo-imp-cel-nao-apostar';
        return 'ciclo-imp-cel-complemento';
    }

    /** Cores fixas na célula (falta vs completou) — não depende só de negrito/CSS em cache */
    function estiloInlineCelula(tipo) {
        if (tipo === 'jogavel') {
            return 'background-color:#fff176!important;color:#3e2723!important;font-weight:600;';
        }
        if (tipo === 'nao_apostar') {
            return 'background-color:#ffcdd2!important;color:#b71c1c!important;font-weight:600;';
        }
        return 'background-color:#90caf9!important;color:#0d47a1!important;font-weight:600;';
    }

    function tituloTipoCelula(tipo) {
        const leg = {
            jogavel: 'Jogável — pendente do ciclo (pode apostar)',
            complemento: 'Complemento — completa 01–31 (já saiu no ciclo ou fora da lista jogável)',
            nao_apostar: 'Não apostar — saiu no último concurso nesta posição',
            saida: 'Já saiu no ciclo atual',
        };
        return leg[tipo] || '';
    }

    function renderConferenciaDup(matriz) {
        const box = el('cicloImpConferenciaDup');
        if (!box || !matriz) return;
        const okCol = matriz.colunas_sem_duplicata !== false;
        const okLin = matriz.linhas_sem_duplicata !== false;
        const partes = [];
        if (okCol && okLin) {
            partes.push(
                '<span class="badge bg-success me-1">OK colunas</span> Cada posição lista 01–31 uma vez.'
            );
            partes.push(
                '<span class="badge bg-success me-1">OK linhas</span> Nenhuma dezena repetida na mesma linha.'
            );
        } else {
            if (!okCol) {
                let det = '';
                for (let p = 1; p <= 7; p++) {
                    const c = matriz.colunas[p];
                    if (c?.duplicatas?.length) {
                        det += ` P${p}: ${c.duplicatas.map(pad).join(', ')};`;
                    }
                }
                partes.push(
                    `<span class="badge bg-danger me-1">Coluna</span> Duplicata na lista jogável:${det || ' verifique.'}`
                );
            }
            if (!okLin) {
                const dups = matriz.duplicatas_entre_colunas || [];
                const det = dups
                    .map((d) => `linha ${d.linha}: ${pad(d.dezena)} em P${d.posicoes.join('/')}`)
                    .join('; ');
                partes.push(
                    `<span class="badge bg-danger me-1">Linha</span> Repetição na mesma linha: ${det || ' verifique.'}`
                );
            }
        }
        partes.push(
            '<span class="ms-1 small text-muted">Veja a legenda de cores abaixo da matriz.</span>'
        );
        box.innerHTML = partes.join(' ');
    }

    function htmlLegendaMatriz() {
        return `<div class="ciclo-imp-legenda-matriz" role="list">
            <span><span class="ciclo-imp-legenda-amostra ciclo-imp-cel-jogavel" style="${estiloInlineCelula('jogavel')}">07</span> <strong>Amarelo</strong> — ainda falta no ciclo (jogável)</span>
            <span><span class="ciclo-imp-legenda-amostra ciclo-imp-cel-complemento" style="${estiloInlineCelula('complemento')}">12</span> <strong>Azul</strong> — completou a coluna 01–31 (já saiu / fora da lista)</span>
            <span><span class="ciclo-imp-legenda-amostra ciclo-imp-cel-nao-apostar" style="${estiloInlineCelula('nao_apostar')}">05</span> Vermelho — não apostar (último sorteio na posição)</span>
        </div>`;
    }

    function textoReferenciaPadrao(matriz) {
        const ref =
            matriz?.referencia_padrao ||
            pacoteCache?.referencia_padrao ||
            pacoteCache?.matriz_30?.referencia_padrao;
        if (!ref?.texto) return '';
        return `<p class="small text-muted mb-2 ciclo-imp-ref-padrao">
            Média histórica (soma-dezenas + dígitos-únicos): <strong>${ref.texto}</strong> —
            apostas priorizam volantes próximos a esse padrão.
            <a href="/analise/soma-dezenas" target="_blank" class="ms-1">Soma</a> ·
            <a href="/analise/digitos-unicos" target="_blank">Dígitos</a>
        </p>`;
    }

    /** Uma aposta por linha da matriz (P1…P7), igual ao que aparece na grade colorida. */
    function extrairApostasDaMatriz(matriz, limite) {
        const grid = matriz?.grid;
        if (!grid?.length) return [];
        const max = limite || 30;
        const out = [];
        const ordenado = [...grid].sort((a, b) => (a.linha || 0) - (b.linha || 0));
        for (const row of ordenado) {
            if (out.length >= max) break;
            const porPos = [];
            for (let p = 1; p <= 7; p++) {
                const cel = row.celulas?.[p];
                if (cel?.dezena == null) {
                    porPos.length = 0;
                    break;
                }
                porPos.push(Number(cel.dezena));
            }
            if (porPos.length !== 7) continue;
            if (new Set(porPos).size !== 7) continue;
            const numeros = [...porPos].sort((a, b) => a - b);
            out.push({
                numero: out.length + 1,
                linha_matriz: row.linha,
                numeros,
                texto: numeros.map((n) => pad(n)).join(' '),
                padrao_digitos_soma: row.padrao?.padrao_digitos_soma || '',
            });
        }
        return out;
    }

    function limiteApostasConfigurado() {
        return parseInt(el('cicloImpQtdApostas')?.value, 10) || 30;
    }

    function listaApostasExibicao() {
        const matriz = pacoteCache?.matriz_30;
        const daMatriz = extrairApostasDaMatriz(matriz, limiteApostasConfigurado());
        if (daMatriz.length) {
            return { lista: daMatriz, origem: 'matriz' };
        }
        const geradas = pacoteCache?.apostas?.apostas;
        if (geradas?.length) {
            return { lista: geradas, origem: 'geradas' };
        }
        return { lista: [], origem: null };
    }

    function montarApostasParaIntegracao() {
        const { lista } = listaApostasExibicao();
        if (lista.length) {
            return lista.map((a) => ({
                numeros: [...a.numeros].sort((x, y) => x - y),
                mes: 1,
            }));
        }
        const nums = [];
        const cols = pacoteCache?.matriz_30?.colunas || {};
        for (let p = 1; p <= 7; p++) {
            const jog = cols[p]?.dezenas_jogaveis;
            if (jog?.length) nums.push(jog[0]);
        }
        if (nums.length < 7) return [];
        return [{ numeros: nums.slice(0, 7).sort((a, b) => a - b), mes: 1 }];
    }

    function enviarMatrizParaVisualizador() {
        const apostas = montarApostasParaIntegracao();
        if (!apostas.length) {
            alert('Aguarde o carregamento da matriz e das apostas, ou clique em Atualizar impressão.');
            return;
        }
        localStorage.setItem('simuladorJogosTransfer', JSON.stringify(apostas));
        localStorage.setItem('simuladorJogosTransferOrigem', 'ciclo-matriz-linhas');
        window.open('/analise-visual/#pane-simulador-filtros', '_blank');
    }

    function enviarMatrizParaConferencia() {
        const apostas = montarApostasParaIntegracao();
        if (!apostas.length) {
            alert('Nenhuma aposta disponível para enviar.');
            return;
        }
        const btn = el('cicloImpBtnConferencia');
        const original = btn?.innerHTML;
        if (btn) {
            btn.disabled = true;
            btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> ENVIANDO...';
        }
        let matrizTxt = '';
        apostas.forEach((ap) => {
            matrizTxt += ap.numeros.map((d) => pad(d)).join(' ') + '\r\n';
        });
        fetch('/gerador-especial/api/enviar-conferencia', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                concurso_base: 'Estatisticas_Ciclo_Por_Posicao',
                matriz_original: matrizTxt,
                detalhes: 'Matriz Ciclos Faltantes — Estatísticas',
            }),
        })
            .then((r) => r.json())
            .then((data) => {
                if (btn) {
                    btn.disabled = false;
                    btn.innerHTML = original;
                }
                if (data.sucesso) {
                    if (data.sessao_id) {
                        sessionStorage.setItem(
                            'conferenciaHistoricaAbrirSessao',
                            String(data.sessao_id)
                        );
                    }
                    window.location.href = '/central-conferencias#pane-conferencia-historica';
                } else {
                    alert('Erro: ' + (data.erro || 'Falha ao enviar'));
                }
            })
            .catch((err) => {
                if (btn) {
                    btn.disabled = false;
                    btn.innerHTML = original;
                }
                alert('Erro de conexão: ' + err.message);
            });
    }

    function renderMatriz(matriz) {
        const box = el('cicloImpMatriz');
        if (!box || !matriz) return;

        let head = '<tr><th class="text-center ciclo-imp-idx-col">Índice</th>';
        for (let p = 1; p <= 7; p++) {
            const c = matriz.colunas[p];
            const qj = c?.quantidade_jogaveis ?? c?.quantidade ?? 0;
            const qc = c?.quantidade_complemento ?? 0;
            const ok = c?.sem_duplicata !== false;
            head += `<th class="ciclo-imp-col-head ciclo-imp-col-pos${ok ? '' : ' table-danger'}" data-pos="${p}">
                Pos. ${p}<br><span class="fw-normal small">${qj} jog. + ${qc} compl.</span></th>`;
        }
        head += '<th class="ciclo-imp-padrao-col text-center">Padrão</th></tr>';

        let body = '';
        for (const row of matriz.grid || []) {
            const idx = row.linha;
            body += `<tr class="ciclo-imp-matriz-row" data-linha="${idx}">`;
            body += `<td class="text-center fw-bold ciclo-imp-idx-col ciclo-imp-idx-click">${idx}</td>`;
            for (let p = 1; p <= 7; p++) {
                const cel = row.celulas[p];
                const vazio = cel == null;
                const n = vazio ? null : cel.dezena ?? cel;
                const tipo = vazio ? '' : cel.tipo || 'jogavel';
                const clsTipo = vazio ? '' : ` ${classeTipoCelula(tipo)}`;
                const title = vazio ? '' : tituloTipoCelula(tipo);
                const estilo = vazio ? '' : estiloInlineCelula(tipo);
                body += `<td class="text-center ciclo-imp-cell ciclo-imp-cell-click${vazio ? ' ciclo-imp-vazio' : clsTipo}"
                    style="${estilo}"
                    data-pos="${p}" data-linha="${idx}" data-dezena="${vazio ? '' : n}" data-tipo="${tipo}"
                    title="${title}">${vazio ? '·' : pad(n)}</td>`;
            }
            const pr = row.padrao || {};
            body += `<td class="text-center ciclo-imp-padrao-col"><span class="ciclo-imp-padrao-ds ciclo-imp-cell">${pr.padrao_digitos_soma || '—'}</span></td>`;
            body += '</tr>';
        }

        box.innerHTML = `
            ${textoReferenciaPadrao(matriz)}
            ${htmlLegendaMatriz()}
            <div class="table-responsive ciclo-imp-matriz-wrap">
            <table class="table table-sm table-bordered table-hover mb-0 ciclo-imp-table">
                <thead class="table-warning">${head}</thead>
                <tbody>${body}</tbody>
            </table>
            </div>`;

        box.querySelectorAll('.ciclo-imp-cell-click').forEach((cell) => {
            if (cell.classList.contains('ciclo-imp-vazio')) return;
            cell.addEventListener('click', () => {
                limparSelecaoVisual();
                cell.classList.add('ciclo-imp-cell-sel');
                const pos = parseInt(cell.getAttribute('data-pos'), 10);
                const linha = parseInt(cell.getAttribute('data-linha'), 10);
                const dezena = parseInt(cell.getAttribute('data-dezena'), 10);
                const tipo = cell.getAttribute('data-tipo') || '';
                selecao = { tipo: 'celula', pos, linha, dezena };
                const pr = matriz.grid[linha - 1]?.padrao;
                const extra = pr?.padrao_digitos_soma ? ` · Padrão linha <strong>${pr.padrao_digitos_soma}</strong>` : '';
                atualizarPainelSelecao(
                    `<strong>Matriz</strong> · índice <strong>${linha}</strong> · posição <strong>${pos}</strong> · dezena <strong>${pad(dezena)}</strong>${tipo ? ` · <em>${tituloTipoCelula(tipo)}</em>` : ''}${extra}`
                );
            });
        });

        box.querySelectorAll('.ciclo-imp-idx-click').forEach((cell) => {
            cell.addEventListener('click', () => {
                const linha = parseInt(cell.textContent, 10);
                limparSelecaoVisual();
                cell.closest('tr')?.classList.add('ciclo-imp-row-sel');
                const partes = [];
                for (let p = 1; p <= 7; p++) {
                    const c = matriz.grid[linha - 1]?.celulas[p];
                    if (c != null) {
                        const n = c.dezena ?? c;
                        partes.push(`P${p}=${pad(n)}`);
                    }
                }
                selecao = { tipo: 'indice', pos: null, linha, dezena: null };
                const pr = matriz.grid[linha - 1]?.padrao;
                const padInfo = pr?.padrao_digitos_soma
                    ? `<br>Padrão linha: <strong>${pr.padrao_digitos_soma}</strong>`
                    : '';
                atualizarPainelSelecao(
                    `<strong>Índice ${linha}</strong>${partes.length ? ': ' + partes.join(' · ') : ''}${padInfo}`
                );
            });
        });

        box.querySelectorAll('.ciclo-imp-col-head').forEach((th) => {
            th.addEventListener('click', () => {
                const pos = parseInt(th.getAttribute('data-pos'), 10);
                const c = matriz.colunas[pos];
                limparSelecaoVisual();
                th.classList.add('ciclo-imp-cell-sel');
                selecao = { tipo: 'coluna', pos, linha: null, dezena: null };
                atualizarPainelSelecao(
                    `<strong>Coluna posição ${pos}</strong> · ${c.quantidade_jogaveis ?? c.quantidade} jogáveis + ${c.quantidade_complemento ?? 0} complemento`
                );
            });
        });
    }

    function renderValidacao(validacoes) {
        const box = el('cicloImpValidacao');
        if (!box) return;
        let html = '<table class="table table-sm table-bordered mb-0"><thead><tr><th>Pos.</th><th>Lista única</th><th>Qtd.</th></tr></thead><tbody>';
        (validacoes || []).forEach((v) => {
            const ok = v.lista_jogaveis_sem_duplicata;
            html += `<tr>
                <td>P${v.posicao}</td>
                <td class="text-center">${ok ? '<span class="text-success">✓</span>' : '<span class="text-danger">✗ repetida</span>'}</td>
                <td class="text-center">${v.qtd_jogaveis}</td>
            </tr>`;
        });
        html += '</tbody></table>';
        box.innerHTML = html;
    }

    function renderApostas(ap) {
        const box = el('cicloImpApostas');
        if (!box) return;
        const { lista, origem } = listaApostasExibicao();
        const refTxt =
            pacoteCache?.referencia_padrao?.texto || ap?.referencia_padrao?.texto;
        const origemTxt =
            origem === 'matriz'
                ? 'cada linha = <strong>índice da matriz</strong> (P1…P7, cores amarelo/azul)'
                : 'jogos gerados pelo motor Elite (podem diferir da matriz)';
        let html = `<p class="small mb-2 p-2 border-bottom">
            <strong>${lista.length}</strong> jogos · 7 dezenas · ${origemTxt}
            ${refTxt ? ` · meta <strong>${refTxt}</strong>` : ''}
        </p>`;
        if (!lista.length) {
            box.innerHTML = html + '<p class="small text-muted p-2 mb-0">Nenhuma linha da matriz disponível.</p>';
            return;
        }
        html += '<table class="table table-sm mb-0 table-hover"><tbody>';
        lista.forEach((a) => {
            const padTxt = a.padrao_digitos_soma
                ? `<span class="ciclo-imp-aposta-padrao ms-2">${a.padrao_digitos_soma}</span>`
                : '';
            const idx =
                origem === 'matriz' && a.linha_matriz != null
                    ? `L${a.linha_matriz}`
                    : `${a.numero}.`;
            html += `<tr class="ciclo-imp-aposta-row" role="button" data-nums="${a.texto}">
                <td class="text-end pe-2 fw-bold" style="width:44px">${idx}</td>
                <td class="ciclo-imp-aposta-nums">${a.texto}${padTxt}</td></tr>`;
        });
        html += '</tbody></table>';
        box.innerHTML = html;
        box.querySelectorAll('.ciclo-imp-aposta-row').forEach((row) => {
            row.addEventListener('click', () => {
                copiarTexto(row.getAttribute('data-nums') || '');
            });
        });
    }

    function copiarTexto(texto) {
        if (navigator.clipboard?.writeText) {
            navigator.clipboard.writeText(texto).then(() => atualizarPainelSelecao(`Copiado: <code>${texto}</code>`));
        }
    }

    function exportarTxt() {
        const { lista } = listaApostasExibicao();
        if (!lista.length) {
            alert('Aguarde o carregamento ou clique em Atualizar impressão.');
            return;
        }
        const linhas = lista.map((a) => a.texto);
        const blob = new Blob([linhas.join('\n') + '\n'], { type: 'text/plain;charset=utf-8' });
        const a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = `ciclo_posicao_${new Date().toISOString().slice(0, 10)}.txt`;
        a.click();
        URL.revokeObjectURL(a.href);
    }

    function imprimir() {
        const w = window.open('', '_blank');
        if (!w) {
            alert('Permita pop-ups para imprimir.');
            return;
        }
        w.document.write(`
            <html><head><title>Ciclo por Posição</title>
            <style>body{font:12px Arial} table{border-collapse:collapse;width:100%} th,td{border:1px solid #333;padding:4px}</style>
            </head><body>
            ${el('cicloImpUltimo')?.innerHTML || ''}
            ${el('cicloImpTabelaRegra')?.innerHTML || ''}
            ${el('cicloImpConferenciaDup')?.innerHTML || ''}
            ${el('cicloImpMatriz')?.innerHTML || ''}
            <h4>Apostas</h4>${el('cicloImpApostas')?.innerHTML || ''}
            </body></html>`);
        w.document.close();
        w.print();
    }

    function init() {
        el('cicloImpBtnAtualizar')?.addEventListener('click', carregarImpressao30);
        el('cicloImpBtnExportar')?.addEventListener('click', exportarTxt);
        el('cicloImpBtnPrint')?.addEventListener('click', imprimir);
        el('cicloImpBtnVisual')?.addEventListener('click', enviarMatrizParaVisualizador);
        el('cicloImpBtnConferencia')?.addEventListener('click', enviarMatrizParaConferencia);
        window.cicloImpressao30Carregar = carregarImpressao30;
        window.cicloImpressao30AplicarPacote = aplicarPacote;
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
