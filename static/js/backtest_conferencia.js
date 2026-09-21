(function () {
    'use strict';

    window._backtestState = window._backtestState || {};

    function pad(n) {
        return String(n).padStart(2, '0');
    }

    function fmtDezenasTom(lista, tom) {
        const bg = tom === 'furo' ? '#c0392b' : tom === 'vicio' ? '#1a5276' : '#FFD700';
        const fg = (tom === 'furo' || tom === 'vicio') ? '#fff' : '#111';
        const border = tom === 'furo' ? 'border:2px solid #922b21;' : (tom === 'vicio' ? 'border:2px solid #154360;' : 'border:2px solid #e6a800;');
        return (lista || []).map(function (n) {
            return '<span class="badge me-1 mb-1" style="background:' + bg + ';color:' + fg + ';' + border + 'font-size:12px;min-width:32px;">' + pad(n) + '</span>';
        }).join('');
    }

    function fmtDezenas(lista, acertadas) {
        const hits = new Set(acertadas || []);
        return (lista || []).map(function (n) {
            const ok = hits.has(n);
            const bg = ok ? '#FFD700' : '#6c757d';
            const fg = ok ? '#000' : '#fff';
            const border = ok ? 'border:2px solid #FFA500;' : '';
            return '<span class="badge me-1 mb-1" style="background:' + bg + ';color:' + fg + ';' + border + 'font-size:12px;min-width:32px;">' + pad(n) + '</span>';
        }).join('');
    }

    function medalha(pos) {
        if (pos === 1) return '<span class="badge" style="background:#C9A227;color:#1a1a2e;">1º</span>';
        if (pos === 2) return '<span class="badge" style="background:#8E9AAF;color:#fff;">2º</span>';
        if (pos === 3) return '<span class="badge" style="background:#B87333;color:#fff;">3º</span>';
        return '<span class="text-muted">' + pos + 'º</span>';
    }

    function badgeAcertos(n) {
        let cls = 'bg-secondary';
        if (n >= 7) cls = 'bg-success';
        else if (n === 6) cls = 'bg-primary';
        else if (n === 5) cls = 'bg-info text-dark';
        else if (n === 4) cls = 'bg-warning text-dark';
        return '<span class="badge ' + cls + ' fs-6">' + n + '</span>';
    }

    function tomLinha(acertos, pos) {
        if (pos === 1) return 'table-warning';
        if (acertos >= 7) return 'table-success';
        if (acertos === 6) return 'table-info';
        return '';
    }

    function extrairApostas(resultado) {
        return (resultado.apostas || []).map(function (aposta, idx) {
            const extra = aposta.dados_extraidos || {};
            const numeros = aposta.numeros_apostados || extra.numeros_apostados || aposta.numeros || [];
            return {
                numero_aposta: aposta.numero_aposta || aposta.numero || (idx + 1),
                numeros: numeros,
                mes: aposta.mes_apostado || extra.mes_apostado || aposta.mes || null,
                erro: !!(aposta.erro || aposta.erro_ocr || aposta.dados_incompletos)
            };
        }).filter(function (a) {
            return !a.erro && Array.isArray(a.numeros) && a.numeros.length >= 7;
        });
    }

    function prefixoApi(path) {
        if (typeof window.appUrl === 'function') return window.appUrl(path);
        return path;
    }

    window.montarHtmlPainelBacktest = function (concurso) {
        return [
            '<div class="card border-0 shadow-sm mb-3">',
            '  <div class="card-header text-white" style="background:linear-gradient(135deg,#1a1a2e 0%,#2d2d44 100%);">',
            '    <h6 class="mb-0"><i class="fas fa-search me-2"></i>Backtest das apostas desta conferência</h6>',
            '  </div>',
            '  <div class="card-body">',
            '    <p class="text-muted mb-3">Avalia as <strong>apostas já cadastradas</strong> deste concurso contra o histórico oficial. Não gera apostas novas e não altera o apostas.json. O concurso atual (' + concurso + ') fica de fora.</p>',
            '    <div class="row g-2 align-items-end mb-3">',
            '      <div class="col-md-2 col-6">',
            '        <label class="form-label small fw-bold mb-1">Concursos analisados</label>',
            '        <select class="form-select form-select-sm" id="bt-limite-' + concurso + '">',
            '          <option value="0" selected>Todos os anteriores</option>',
            '          <option value="50">Últimos 50</option>',
            '          <option value="100">Últimos 100</option>',
            '          <option value="200">Últimos 200</option>',
            '          <option value="500">Últimos 500</option>',
            '        </select>',
            '      </div>',
            '      <div class="col-md-2 col-6">',
            '        <label class="form-label small fw-bold mb-1">De (data)</label>',
            '        <input type="date" class="form-control form-control-sm" id="bt-data-ini-' + concurso + '">',
            '      </div>',
            '      <div class="col-md-2 col-6">',
            '        <label class="form-label small fw-bold mb-1">Até (data)</label>',
            '        <input type="date" class="form-control form-control-sm" id="bt-data-fim-' + concurso + '">',
            '      </div>',
            '      <div class="col-md-2 col-6">',
            '        <label class="form-label small fw-bold mb-1">Acertos mínimos</label>',
            '        <select class="form-select form-select-sm" id="bt-min-exec-' + concurso + '">',
            '          <option value="3" selected>3 (quase + prêmio)</option>',
            '          <option value="4">4 (faixa paga)</option>',
            '          <option value="5">5+</option>',
            '          <option value="0">Todos (0+)</option>',
            '        </select>',
            '      </div>',
            '      <div class="col-md-4 col-12">',
            '        <button type="button" class="btn w-100 fw-bold" id="btn-executar-backtest-' + concurso + '" onclick="executarBacktestConferencia(' + concurso + ')" style="background:#D4B31A;color:#1a1a2e;">',
            '          <i class="fas fa-search me-1"></i> EXECUTAR BACKTEST',
            '        </button>',
            '      </div>',
            '    </div>',
            '    <div id="bt-progresso-' + concurso + '" class="mb-2"></div>',
            '    <div id="bt-resultados-' + concurso + '"></div>',
            '  </div>',
            '</div>'
        ].join('\n');
    };

    window.executarBacktestConferencia = async function (concurso) {
        const resultado = (typeof resultadosProcessamento !== 'undefined') ? resultadosProcessamento[concurso] : null;
        const apostas = resultado ? extrairApostas(resultado) : [];
        const btn = document.getElementById('btn-executar-backtest-' + concurso);
        const prog = document.getElementById('bt-progresso-' + concurso);
        const box = document.getElementById('bt-resultados-' + concurso);
        if (!btn || !prog || !box) return;

        const limite = parseInt(document.getElementById('bt-limite-' + concurso).value, 10) || 0;
        const dataIni = document.getElementById('bt-data-ini-' + concurso).value || null;
        const dataFim = document.getElementById('bt-data-fim-' + concurso).value || null;
        const minAcertos = parseInt(document.getElementById('bt-min-exec-' + concurso).value, 10);
        const nApostas = apostas.length || '?';
        const nConc = limite > 0 ? limite : 'todo o histórico';

        btn.disabled = true;
        box.innerHTML = '';
        prog.innerHTML = '<div class="alert alert-info py-2 mb-0"><div class="spinner-border spinner-border-sm me-2" role="status"></div>Analisando ' + nConc + ' concursos × ' + nApostas + ' apostas...</div>';

        try {
            const resp = await fetch(prefixoApi('/api/conferencia-ocr/backtest'), {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    concurso: concurso,
                    apostas: apostas,
                    limite_concursos: limite,
                    data_ini: dataIni,
                    data_fim: dataFim,
                    min_acertos: isNaN(minAcertos) ? 3 : minAcertos
                })
            });
            const bruto = await resp.text();
            let dados;
            try {
                dados = JSON.parse(bruto);
            } catch (parseErr) {
                const rotaAusente = resp.status === 404;
                prog.innerHTML = '<div class="alert alert-danger py-2 mb-0"><i class="fas fa-exclamation-triangle me-1"></i>' +
                    (rotaAusente
                        ? 'A rota de backtest ainda não está no servidor (HTTP 404). Feche o app.py da porta 5151 e abra de novo para carregar o código novo.'
                        : 'O servidor não devolveu JSON (HTTP ' + resp.status + '). Reinicie o app.py e tente outra vez.') +
                    '</div>';
                return;
            }
            if (!dados.sucesso) {
                prog.innerHTML = '<div class="alert alert-warning py-2 mb-0"><i class="fas fa-info-circle me-1"></i>' + (dados.mensagem || dados.erro || 'Não foi possível executar o backtest.') + '</div>';
                return;
            }
            window._backtestState[concurso] = {
                dados: dados,
                topN: 3,
                minAcertos: (dados.meta && dados.meta.min_acertos_tabela) || 3,
                aposta: '',
                concursoFiltro: ''
            };
            const m = dados.meta || {};
            prog.innerHTML = '<div class="alert alert-success py-2 mb-0"><i class="fas fa-check-circle me-1"></i>Backtest concluído — ' + (m.n_comparacoes || 0).toLocaleString('pt-BR') + ' comparações realizadas (' + (m.n_apostas || 0) + ' apostas × ' + (m.n_concursos || 0) + ' concursos).</div>';
            window.renderizarResultadosBacktest(concurso);
        } catch (err) {
            prog.innerHTML = '<div class="alert alert-danger py-2 mb-0"><i class="fas fa-exclamation-triangle me-1"></i>Falha na comunicação: ' + err.message + '</div>';
        } finally {
            btn.disabled = false;
        }
    };

    window.atualizarFiltroBacktest = function (concurso, campo, valor) {
        const st = window._backtestState[concurso];
        if (!st) return;
        st[campo] = valor;
        window.renderizarResultadosBacktest(concurso);
    };

    function filtrarHits(st) {
        const dados = st.dados;
        let hits = (dados.ranking_hits || []).slice();
        const minA = parseInt(st.minAcertos, 10);
        if (!isNaN(minA)) hits = hits.filter(function (h) { return h.acertos >= minA; });
        if (st.aposta) {
            const n = parseInt(st.aposta, 10);
            hits = hits.filter(function (h) { return h.numero_aposta === n; });
        }
        if (st.concursoFiltro) {
            const c = parseInt(st.concursoFiltro, 10);
            hits = hits.filter(function (h) { return h.concurso === c; });
        }
        return hits;
    }

    function recortarTop(lista, topN) {
        if (topN === 'all' || topN === 0) return lista;
        const n = parseInt(topN, 10);
        if (!n) return lista.slice(0, 3);
        return lista.slice(0, n);
    }

    function montarInsightsBacktest(concurso, dados) {
        const resultado = (typeof resultadosProcessamento !== 'undefined') ? resultadosProcessamento[concurso] : null;
        const apostasConf = resultado ? extrairApostas(resultado) : [];
        const nJogos = apostasConf.length || (dados.meta && dados.meta.n_apostas) || 0;
        const sorteados = ((resultado && resultado.resultado_sorteio && resultado.resultado_sorteio.numeros) || [])
            .map(function (x) { return parseInt(x, 10); })
            .filter(function (x) { return x >= 1 && x <= 31; });
        const setSaiu = new Set(sorteados);
        const freq = {};
        const tamanhos = {};
        apostasConf.forEach(function (a) {
            const len = (a.numeros || []).length;
            tamanhos[len] = (tamanhos[len] || 0) + 1;
            (a.numeros || []).forEach(function (num) {
                const d = parseInt(num, 10);
                if (d >= 1 && d <= 31) freq[d] = (freq[d] || 0) + 1;
            });
        });
        const furos = sorteados.filter(function (d) { return !freq[d]; }).sort(function (a, b) { return a - b; });
        const rank = dados.ranking_apostas || [];
        const melhorAbs = rank.reduce(function (m, a) { return Math.max(m, a.melhor || 0); }, 0);
        let bases = rank.filter(function (a) { return (a.melhor || 0) >= 6; });
        if (!bases.length && melhorAbs >= 5) {
            bases = rank.filter(function (a) { return a.melhor === melhorAbs; });
        }
        bases = bases.slice(0, 2);

        const faltouCount = {};
        (dados.ranking_hits || []).filter(function (h) { return (h.acertos || 0) >= 6; }).forEach(function (h) {
            const ap = new Set(h.dezenas_aposta || []);
            (h.dezenas_sorteadas || []).forEach(function (d) {
                if (!ap.has(d)) faltouCount[d] = (faltouCount[d] || 0) + 1;
            });
        });
        const faltouRepetido = Object.keys(faltouCount)
            .map(function (k) { return parseInt(k, 10); })
            .filter(function (d) { return faltouCount[d] >= 2; })
            .sort(function (a, b) { return faltouCount[b] - faltouCount[a] || a - b; });

        const limiarVicio = Math.max(5, Math.ceil(nJogos * 0.5));
        const nucleoVicio = Object.keys(freq).map(Number)
            .filter(function (d) { return freq[d] >= limiarVicio && !setSaiu.has(d); })
            .sort(function (a, b) { return freq[b] - freq[a] || a - b; })
            .slice(0, 4);

        const itens = [];
        const concMelhor = dados.melhor_geral;
        const qtd6 = Number((dados.distribuicao || {})['6'] || 0);
        const qtd5 = Number((dados.distribuicao || {})['5'] || 0);

        if (nJogos >= 2 && melhorAbs >= 5) {
            itens.push({
                tom: 'nao',
                titulo: 'Não reenviar as ' + nJogos + ' iguais',
                html: 'Não recicle o pacote inteiro' +
                    (concMelhor
                        ? ' só porque a Aposta ' + pad(concMelhor.numero_aposta) +
                          ' fez ' + concMelhor.acertos + ' no concurso ' + concMelhor.concurso +
                          (concMelhor.data ? ' (' + concMelhor.data + ')' : '')
                        : '') +
                    '. O backtest descreve o passado; o próximo sorteio é independente.'
            });
        }

        if (bases.length) {
            const nomes = bases.map(function (a) { return 'Aposta ' + pad(a.numero_aposta); }).join(' e ');
            const feito6 = bases.every(function (a) { return a.melhor >= 6; });
            itens.push({
                tom: 'sim',
                titulo: 'Guardar 1 ou 2 cartelas como base e trocar o resto',
                html: nomes + (feito6 ? ' foram as que chegaram em 6 acertos' : ' tiveram o melhor histórico (' + melhorAbs + ' acertos)') +
                    '. Mantenha essas e redesenhe as demais — não o bloco inteiro.'
            });
        }

        if (furos.length) {
            let extra = '';
            if (faltouRepetido.length) {
                extra = ' O ' + faltouRepetido.map(pad).join(', ') +
                    ' também faltou nos melhores retrospectos (6 acertos).';
            }
            itens.push({
                tom: 'sim',
                titulo: 'Colocar os furos em pelo menos metade dos jogos',
                html: furos.map(pad).join(', ') + ' saíram no ' + concurso +
                    ' e não estavam em nenhum jogo.' + extra,
                dezenas: furos,
                tomDezenas: 'furo'
            });
        }

        if (nucleoVicio.length >= 2) {
            const detalhe = nucleoVicio.map(function (d) { return pad(d) + ' (' + freq[d] + '/' + nJogos + ')'; }).join(', ');
            itens.push({
                tom: 'nao',
                titulo: 'Cortar o bloco viciado',
                html: detalhe + ' — muito jogadas neste arquivo e não saíram. Não recicle esse núcleo no próximo concurso.',
                dezenas: nucleoVicio,
                tomDezenas: 'vicio'
            });
        }

        const so7 = Object.keys(tamanhos).length <= 1 && (tamanhos[7] || nJogos === 0);
        itens.push({
            tom: 'sim',
            titulo: 'Continuar em 7 dezenas',
            html: (so7 ? 'Este arquivo já é jogo simples. ' : '') +
                'Subir para 8–9 não transforma os “' + qtd5 + ' cincos e ' + qtd6 + ' seis” do backtest em 7 acertos. O custo sobe; o 7 continua raro. Melhor espalhar 10 cartelas de 7 cobrindo os furos.'
        });

        return itens;
    }

    function htmlInsightsBacktest(concurso, dados) {
        const itens = montarInsightsBacktest(concurso, dados);
        if (!itens.length) return '';
        const cards = itens.map(function (it) {
            const sim = it.tom === 'sim';
            const borda = sim ? '#1e8449' : '#c0392b';
            const selo = sim
                ? '<span class="badge bg-success me-2">Fazer</span>'
                : '<span class="badge bg-danger me-2">Evitar</span>';
            const bolas = it.dezenas && it.dezenas.length
                ? '<div class="mt-2">' + fmtDezenasTom(it.dezenas, it.tomDezenas || 'hit') + '</div>'
                : '';
            return '<div class="col-lg-6">' +
                '<div class="h-100 p-3 rounded bg-white" style="border-left:4px solid ' + borda + ';">' +
                '<div class="d-flex align-items-start mb-1">' + selo +
                '<strong>' + it.titulo + '</strong></div>' +
                '<div class="small">' + it.html + '</div>' + bolas +
                '</div></div>';
        }).join('');
        return [
            '<div class="card border-0 shadow-sm mb-4" style="border-top:4px solid #C9A227 !important;">',
            '  <div class="card-header bg-white">',
            '    <h6 class="mb-0" style="color:#6b5710;"><i class="fas fa-lightbulb me-2 text-warning"></i>Insights inteligentes — o que aproveitar deste backtest</h6>',
            '  </div>',
            '  <div class="card-body py-3" style="background:#fbf8ef;">',
            '    <p class="small text-muted mb-3">Não é palpite do próximo sorteio. É o que o histórico + os furos deste concurso sugerem fazer com <strong>estas</strong> cartelas.</p>',
            '    <div class="row g-3">' + cards + '</div>',
            '  </div>',
            '</div>'
        ].join('\n');
    }

    window.renderizarResultadosBacktest = function (concurso) {
        const st = window._backtestState[concurso];
        const box = document.getElementById('bt-resultados-' + concurso);
        if (!st || !st.dados || !box) return;

        const dados = st.dados;
        const meta = dados.meta || {};
        const dist = dados.distribuicao || {};
        const melhor = dados.melhor_geral;
        const topN = st.topN === 'all' ? 'all' : parseInt(st.topN, 10) || 3;

        let rankingConc = (dados.ranking_concursos || []).slice();
        const minA = parseInt(st.minAcertos, 10);
        if (!isNaN(minA)) rankingConc = rankingConc.filter(function (c) { return c.melhor_pontuacao >= minA; });
        if (st.concursoFiltro) {
            const cf = parseInt(st.concursoFiltro, 10);
            rankingConc = rankingConc.filter(function (c) { return c.concurso === cf; });
        }
        const rankingConcView = recortarTop(rankingConc, topN);
        const hits = recortarTop(filtrarHits(st), topN === 'all' ? 'all' : topN);
        const apostasRank = dados.ranking_apostas || [];

        const opcoesApostas = ['<option value="">Todas</option>'].concat(
            apostasRank.map(function (a) {
                const sel = String(st.aposta) === String(a.numero_aposta) ? ' selected' : '';
                return '<option value="' + a.numero_aposta + '"' + sel + '>Aposta ' + pad(a.numero_aposta) + '</option>';
            })
        ).join('');

        const distHtml = [0, 1, 2, 3, 4, 5, 6, 7].map(function (k) {
            const v = dist[String(k)] || 0;
            const cls = k >= 7 ? 'bg-success' : k === 6 ? 'bg-primary' : k === 5 ? 'bg-info text-dark' : k === 4 ? 'bg-warning text-dark' : 'bg-light text-dark border';
            return '<span class="badge ' + cls + ' me-1 mb-1">' + k + ' acertos: ' + v.toLocaleString('pt-BR') + '</span>';
        }).join('');

        const headline = melhor
            ? ('Melhor desempenho histórico: <strong>Aposta ' + pad(melhor.numero_aposta) + '</strong> faria <strong>' + melhor.acertos + ' acertos</strong> no concurso <strong>' + melhor.concurso + '</strong>' + (melhor.data ? ' (' + melhor.data + ')' : '') + '.')
            : 'Nenhum resultado no recorte atual. Diminua o filtro de acertos mínimos.';

        const linhasConc = rankingConcView.map(function (c, i) {
            const pos = i + 1;
            const apostasTxt = (c.melhores_apostas || [c.melhor_aposta]).filter(Boolean).map(function (n) { return pad(n); }).join(', ');
            return '<tr class="' + tomLinha(c.melhor_pontuacao, pos) + '">' +
                '<td>' + medalha(pos) + '</td>' +
                '<td class="fw-bold">' + c.concurso + '</td>' +
                '<td>' + (c.data || '—') + '</td>' +
                '<td>Aposta ' + apostasTxt + '</td>' +
                '<td class="text-center">' + badgeAcertos(c.melhor_pontuacao) + '</td>' +
                '<td class="text-center">' + c.qtd_com_melhor + '</td>' +
                '<td>' + fmtDezenas(c.dezenas_sorteadas, []) + '</td>' +
                '</tr>';
        }).join('');

        const linhasHits = hits.map(function (h, i) {
            const pos = i + 1;
            return '<tr class="' + tomLinha(h.acertos, pos) + '">' +
                '<td>' + medalha(pos) + '</td>' +
                '<td class="fw-bold">' + h.concurso + '</td>' +
                '<td>' + (h.data || '—') + '</td>' +
                '<td>Aposta ' + pad(h.numero_aposta) + '</td>' +
                '<td class="text-center">' + badgeAcertos(h.acertos) + (h.acertou_mes ? ' <span class="badge bg-info">Mês</span>' : '') + '</td>' +
                '<td>' + fmtDezenas(h.dezenas_aposta, h.dezenas_acertadas) + '</td>' +
                '<td>' + fmtDezenas(h.dezenas_sorteadas, h.dezenas_acertadas) + '</td>' +
                '</tr>';
        }).join('');

        const apostaSel = st.aposta ? apostasRank.find(function (a) { return String(a.numero_aposta) === String(st.aposta); }) : apostasRank[0];
        let blocoAposta = '';
        if (apostaSel) {
            const topAp = (apostaSel.melhores || []).map(function (t) {
                return '<tr><td>' + t.concurso + '</td><td>' + (t.data || '—') + '</td><td class="text-center">' + badgeAcertos(t.acertos) + '</td><td>' + fmtDezenas(t.dezenas_sorteadas, t.dezenas_acertadas) + '</td></tr>';
            }).join('');
            blocoAposta = [
                '<div class="card border-0 bg-light mb-3">',
                '  <div class="card-body">',
                '    <h6 class="fw-bold">Aposta ' + pad(apostaSel.numero_aposta) + ' — desempenho individual</h6>',
                '    <div class="mb-2">' + fmtDezenas(apostaSel.numeros, []) + '</div>',
                '    <div class="row g-2 small">',
                '      <div class="col-md-3 col-6"><div class="p-2 bg-white rounded border">Concursos: <strong>' + apostaSel.concursos_analisados + '</strong></div></div>',
                '      <div class="col-md-3 col-6"><div class="p-2 bg-white rounded border">Melhor: <strong>' + apostaSel.melhor + '</strong> acertos</div></div>',
                '      <div class="col-md-3 col-6"><div class="p-2 bg-white rounded border">2º / 3º: <strong>' + (apostaSel.segundo != null ? apostaSel.segundo : '—') + '</strong> / <strong>' + (apostaSel.terceiro != null ? apostaSel.terceiro : '—') + '</strong></div></div>',
                '      <div class="col-md-3 col-6"><div class="p-2 bg-white rounded border">Média: <strong>' + apostaSel.media + '</strong></div></div>',
                '      <div class="col-md-3 col-6"><div class="p-2 bg-white rounded border">4+ acertos: <strong>' + apostaSel.qtd_4 + '</strong>×</div></div>',
                '      <div class="col-md-3 col-6"><div class="p-2 bg-white rounded border">5+: <strong>' + apostaSel.qtd_5 + '</strong>× · 6+: <strong>' + apostaSel.qtd_6 + '</strong>× · 7: <strong>' + apostaSel.qtd_7 + '</strong>×</div></div>',
                '      <div class="col-md-3 col-6"><div class="p-2 bg-white rounded border">Mês da sorte: <strong>' + apostaSel.qtd_mes + '</strong>×</div></div>',
                '    </div>',
                '    <div class="table-responsive mt-3"><table class="table table-sm mb-0"><thead><tr><th>Concurso</th><th>Data</th><th>Acertos</th><th>Dezenas sorteadas</th></tr></thead><tbody>' + topAp + '</tbody></table></div>',
                '  </div>',
                '</div>'
            ].join('\n');
        }

        const selTop = function (v, label) {
            const cur = st.topN === 'all' ? 'all' : String(st.topN);
            return '<option value="' + v + '"' + (cur === String(v) ? ' selected' : '') + '>' + label + '</option>';
        };

        box.innerHTML = [
            '<div class="alert alert-dark py-2">' + headline + '</div>',
            '<div class="mb-3"><div class="small text-muted mb-1">Quantas vezes o conjunto atingiu cada quantidade de acertos (todas as comparações):</div>' + distHtml + '</div>',
            htmlInsightsBacktest(concurso, dados),
            '<div class="row g-2 align-items-end mb-3 p-2 rounded border bg-white">',
            '  <div class="col-md-2 col-6"><label class="form-label small fw-bold mb-1">Exibir</label>',
            '    <select class="form-select form-select-sm" onchange="atualizarFiltroBacktest(' + concurso + ',\'topN\', this.value===\'all\' ? \'all\' : parseInt(this.value,10))">',
            selTop(3, 'Top 3'), selTop(5, 'Top 5'), selTop(10, 'Top 10'), selTop('all', 'Todos'),
            '    </select></div>',
            '  <div class="col-md-2 col-6"><label class="form-label small fw-bold mb-1">Acertos mín. (visão)</label>',
            '    <select class="form-select form-select-sm" onchange="atualizarFiltroBacktest(' + concurso + ',\'minAcertos\', parseInt(this.value,10))">',
            [0, 3, 4, 5, 6, 7].filter(function (n) {
                const floor = (dados.meta && dados.meta.min_acertos_tabela) || 0;
                return n >= floor || n === floor;
            }).map(function (n) {
                const label = n === 0 ? '0+' : (n + '+');
                return '<option value="' + n + '"' + (parseInt(st.minAcertos, 10) === n ? ' selected' : '') + '>' + label + '</option>';
            }).join(''),
            '    </select></div>',
            '  <div class="col-md-3 col-6"><label class="form-label small fw-bold mb-1">Aposta</label>',
            '    <select class="form-select form-select-sm" onchange="atualizarFiltroBacktest(' + concurso + ',\'aposta\', this.value)">' + opcoesApostas + '</select></div>',
            '  <div class="col-md-3 col-6"><label class="form-label small fw-bold mb-1">Concurso específico</label>',
            '    <input type="number" class="form-control form-control-sm" placeholder="Ex.: 1227" value="' + (st.concursoFiltro || '') + '" onchange="atualizarFiltroBacktest(' + concurso + ',\'concursoFiltro\', this.value)"></div>',
            '  <div class="col-md-2 col-12 small text-muted">Faixa analisada: ' + (meta.concurso_mais_antigo || '—') + ' → ' + (meta.concurso_mais_recente || '—') + '</div>',
            '</div>',

            '<h6 class="mt-3"><i class="fas fa-trophy me-1 text-warning"></i> Melhores concursos para este conjunto de apostas</h6>',
            '<p class="small text-muted">Resposta direta: em quais concursos passados estas apostas teriam tido o melhor desempenho.</p>',
            '<div class="table-responsive mb-4"><table class="table table-sm table-hover align-middle"><thead class="table-dark"><tr>',
            '<th>Clas.</th><th>Concurso</th><th>Data</th><th>Melhor aposta</th><th class="text-center">Melhor pontuação</th><th class="text-center">Qtd. com essa pontuação</th><th>Dezenas sorteadas</th>',
            '</tr></thead><tbody>',
            linhasConc || '<tr><td colspan="7" class="text-center text-muted">Nenhum concurso no recorte.</td></tr>',
            '</tbody></table></div>',

            '<h6><i class="fas fa-list-ol me-1"></i> Ranking individual (aposta × concurso)</h6>',
            '<div class="table-responsive mb-4"><table class="table table-sm table-hover align-middle"><thead class="table-dark"><tr>',
            '<th>Clas.</th><th>Concurso</th><th>Data</th><th>Aposta</th><th class="text-center">Acertos</th><th>Dezenas da aposta</th><th>Dezenas sorteadas</th>',
            '</tr></thead><tbody>',
            linhasHits || '<tr><td colspan="7" class="text-center text-muted">Nenhuma linha no recorte. Diminua o filtro de acertos.</td></tr>',
            '</tbody></table></div>',
            (meta.total_hits_qualificados > (meta.hits_retornados || 0)
                ? '<p class="small text-muted">Exibindo ' + hits.length + ' de ' + meta.total_hits_qualificados + ' resultados com o recorte atual (teto do servidor: ' + meta.hits_retornados + ').</p>'
                : ''),

            '<h6><i class="fas fa-clone me-1"></i> Análise por aposta</h6>',
            '<p class="small text-muted mb-2">Escolha uma aposta no filtro acima (ou veja a de melhor histórico). Qual teria sido boa no passado?</p>',
            blocoAposta,
            '<p class="small text-muted mb-0">Backtest retrospectivo: frequência passada não prevê o próximo sorteio. Serve para medir cobertura e qualidade das apostas já feitas.</p>'
        ].join('\n');
    };
})();
