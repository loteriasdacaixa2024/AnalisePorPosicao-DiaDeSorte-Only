/**
 * Busca Automática de Presets — Aba 6A (complementar).
 * Não altera o fluxo manual de Carregar/Preencher/Equilibrar.
 */
(function () {
    const API = '/gerador-especial/api/busca_melhores_saltos';
    let jobId = null;
    let pollTimer = null;
    let rankingCompleto = [];
    let rankSelecionado = null;
    let detalheAtual = null;

    function el(id) { return document.getElementById(id); }

    function pad2(n) { return ('0' + n).slice(-2); }

    function lerParams() {
        const selBase = el('atraso6a_concurso_base');
        const selDezenas = el('atraso6a_dezenas');
        const selMes = el('atraso6a_mes');
        return {
            concurso_base_id: selBase ? selBase.value : 'ultimo',
            dezenas_por_jogo: selDezenas ? parseInt(selDezenas.value, 10) : 7,
            mes_tipo: selMes ? selMes.value : 'sequencial',
            limite_salto_max: parseInt(el('busca6a_limite').value, 10) || 6,
            max_testes: parseInt(el('busca6a_max_testes').value, 10) || 1000,
            modo_busca: el('busca6a_modo').value || 'aleatorio',
            janela_concursos: parseInt(el('busca6a_janela').value, 10) || 0,
            usar_ajustada: el('busca6a_tipo_aposta').value === 'ajustada',
            top_n: parseInt(el('busca6a_top_n').value, 10) || 50,
            simetrico: !!(el('busca6a_simetrico') && el('busca6a_simetrico').checked),
            escopo_percurso: el('busca6a_escopo') ? el('busca6a_escopo').value : 'todos'
        };
    }

    function setBusy(busy) {
        const btn = el('btn-busca6a-iniciar');
        const btnC = el('btn-busca6a-cancelar');
        const wrap = el('busca6a-progresso-wrap');
        if (btn) btn.disabled = !!busy;
        if (btnC) btnC.style.display = busy ? 'inline-block' : 'none';
        if (wrap) wrap.style.display = busy ? 'block' : (el('busca6a-progresso-bar') && parseInt(el('busca6a-progresso-bar').style.width, 10) > 0 ? 'block' : wrap.style.display);
        if (busy && wrap) wrap.style.display = 'block';
    }

    function atualizarProgresso(job) {
        const pct = job.progresso || 0;
        const bar = el('busca6a-progresso-bar');
        const msg = el('busca6a-progresso-msg');
        const pctEl = el('busca6a-progresso-pct');
        if (bar) {
            bar.style.width = pct + '%';
            bar.textContent = pct + '%';
            if (job.status === 'concluido') {
                bar.classList.remove('progress-bar-animated');
                bar.classList.add('bg-success');
                bar.classList.remove('bg-warning', 'text-dark');
            } else {
                bar.classList.add('progress-bar-animated', 'bg-warning', 'text-dark');
                bar.classList.remove('bg-success');
            }
        }
        if (msg) msg.textContent = job.mensagem || '';
        if (pctEl) pctEl.textContent = pct + '%';
    }

    function filtrosAtivos() {
        return {
            min7: !!(el('busca6a_filtro_7') && el('busca6a_filtro_7').checked),
            min6: parseInt(el('busca6a_filtro_6') && el('busca6a_filtro_6').value, 10) || 0,
            min5: parseInt(el('busca6a_filtro_5') && el('busca6a_filtro_5').value, 10) || 0
        };
    }

    function filtrarRanking(lista) {
        const f = filtrosAtivos();
        return (lista || []).filter(r => {
            if (f.min7 && !(r.qtd_7 > 0)) return false;
            if (r.qtd_6 < f.min6) return false;
            if (r.qtd_5 < f.min5) return false;
            return true;
        });
    }

    function renderRanking(lista) {
        const body = el('busca6a-ranking-body');
        if (!body) return;
        const rows = filtrarRanking(lista);
        if (!rows.length) {
            body.innerHTML = '<tr><td colspan="10" class="text-muted py-3">Nenhum preset com os filtros atuais.</td></tr>';
            return;
        }
        body.innerHTML = rows.map(r => {
            const ativo = rankSelecionado === r.rank ? 'table-warning' : '';
            return `<tr class="${ativo}" style="cursor:pointer;" onclick="busca6aVerApostas(${r.rank})">
                <td class="fw-bold">TOP ${r.rank}</td>
                <td class="text-start font-monospace" style="font-size:11px;">${r.preset}</td>
                <td class="fw-bold text-danger">${r.score}</td>
                <td><span class="badge bg-danger">${r.qtd_7}</span></td>
                <td><span class="badge bg-primary">${r.qtd_6}</span></td>
                <td><span class="badge bg-success">${r.qtd_5}</span></td>
                <td>${Number(r.media).toFixed(3)}</td>
                <td>${r.total_concursos}</td>
                <td>${Number(r.percentual).toFixed(2)}%</td>
                <td>
                    <button type="button" class="btn btn-sm btn-outline-info py-0 px-1" onclick="event.stopPropagation();busca6aVerApostas(${r.rank})" title="Ver apostas">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button type="button" class="btn btn-sm btn-outline-success py-0 px-1" onclick="event.stopPropagation();busca6aVerApostas(${r.rank}, true)" title="Aplicar">
                        <i class="fas fa-check"></i>
                    </button>
                </td>
            </tr>`;
        }).join('');
    }

    function renderStats(job) {
        const box = el('busca6a-stats');
        if (!box) return;
        const s = job.estatisticas || {};
        if (!s.presets_testados && job.status !== 'concluido') {
            box.textContent = '';
            return;
        }
        box.innerHTML = `Testados: <strong>${s.presets_testados || job.testados || 0}</strong>
            · Pares Base→próximo: <strong>${s.pares_base_proximo || s.concursos_analisados || '—'}</strong>
            · Base (apostas): <strong>${s.concurso_base || '—'}</strong>
            · Percurso: <strong>${s.primeiro_par || '—'}→…→${s.ultimo_par_base || '—'}×${s.ultimo_par_alvo || '—'}</strong>
            · Tempo: <strong>${s.tempo_segundos != null ? s.tempo_segundos + 's' : '—'}</strong>
            · Score = 7×1000 + 6×100 + 5×10 (walk-forward)`;
    }

    function pararPoll() {
        if (pollTimer) {
            clearInterval(pollTimer);
            pollTimer = null;
        }
    }

    function pollStatus() {
        if (!jobId) return;
        fetch(API + '/status/' + jobId)
            .then(r => r.json())
            .then(data => {
                if (!data.sucesso) return;
                atualizarProgresso(data);
                if (data.ranking && data.ranking.length) {
                    if (data.status === 'concluido') {
                        rankingCompleto = data.ranking;
                    } else {
                        rankingCompleto = data.ranking;
                    }
                    renderRanking(rankingCompleto);
                }
                renderStats(data);
                if (data.status === 'concluido' || data.status === 'erro' || data.status === 'cancelado') {
                    pararPoll();
                    setBusy(false);
                    if (data.status === 'concluido') {
                        rankingCompleto = data.ranking || [];
                        renderRanking(rankingCompleto);
                        renderStats(data);
                    }
                    if (data.status === 'erro') {
                        alert('Erro na busca: ' + (data.erro || data.mensagem || ''));
                    }
                }
            })
            .catch(() => {});
    }

    window.busca6aIniciar = function () {
        if (pollTimer) return;
        const params = lerParams();
        if (params.modo_busca === 'exaustivo' && !params.simetrico) {
            alert('O modo Exaustivo exige "Simétrico (+/− iguais)" marcado.');
            return;
        }
        if (params.modo_busca === 'exaustivo' && params.simetrico) {
            const espaco = Math.pow(params.limite_salto_max, 7);
            if (espaco > params.max_testes) {
                const ok = confirm(
                    'Espaço simétrico = ' + espaco.toLocaleString('pt-BR') +
                    ' presets, maior que o limite de ' + params.max_testes.toLocaleString('pt-BR') +
                    '. A busca usará amostragem aleatória até esse limite. Continuar?'
                );
                if (!ok) return;
            } else if (espaco > 5000) {
                const ok = confirm('Exaustivo irá testar ' + espaco.toLocaleString('pt-BR') + ' presets. Pode demorar. Continuar?');
                if (!ok) return;
            }
        }

        setBusy(true);
        rankSelecionado = null;
        detalheAtual = null;
        el('busca6a-detalhe').style.display = 'none';
        rankingCompleto = [];
        renderRanking([]);
        el('busca6a-ranking-body').innerHTML = '<tr><td colspan="10" class="text-muted py-3"><i class="fas fa-spinner fa-spin"></i> Iniciando…</td></tr>';

        fetch(API + '/iniciar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(params)
        })
            .then(r => r.json())
            .then(data => {
                if (!data.sucesso) {
                    setBusy(false);
                    alert(data.mensagem || 'Falha ao iniciar busca');
                    return;
                }
                jobId = data.job_id;
                atualizarProgresso({ progresso: 0, mensagem: 'Busca iniciada…', status: 'processando' });
                pollTimer = setInterval(pollStatus, 800);
                pollStatus();
            })
            .catch(err => {
                setBusy(false);
                alert('Erro de conexão: ' + err);
            });
    };

    window.busca6aCancelar = function () {
        if (!jobId) return;
        fetch(API + '/cancelar/' + jobId, { method: 'POST' })
            .then(() => pollStatus())
            .catch(() => {});
    };

    window.busca6aAplicarFiltros = function () {
        renderRanking(rankingCompleto);
    };

    window.busca6aLimparFiltros = function () {
        if (el('busca6a_filtro_7')) el('busca6a_filtro_7').checked = false;
        if (el('busca6a_filtro_6')) el('busca6a_filtro_6').value = '0';
        if (el('busca6a_filtro_5')) el('busca6a_filtro_5').value = '0';
        renderRanking(rankingCompleto);
    };

    window.busca6aVerApostas = function (rank, aplicarDepois) {
        if (!jobId) return;
        rankSelecionado = rank;
        renderRanking(rankingCompleto);
        fetch(API + '/apostas/' + jobId + '/' + rank)
            .then(r => r.json())
            .then(data => {
                if (!data.sucesso) {
                    alert(data.mensagem || 'Apostas não encontradas');
                    return;
                }
                detalheAtual = data;
                const box = el('busca6a-detalhe');
                box.style.display = 'block';
                el('busca6a-detalhe-titulo').innerHTML =
                    `<i class="fas fa-list-ol"></i> TOP ${rank} — ${data.preset}`;
                const m = data.metricas || {};
                const tbody = el('busca6a-detalhe-apostas');
                const apostas = (data.apostas || []).slice();
                // Ordena por |linha| para não começar em -25 (onde 1–4 dominam visualmente)
                apostas.sort((a, b) => {
                    const aa = Math.abs(a.linha_offset || 0);
                    const bb = Math.abs(b.linha_offset || 0);
                    if (aa !== bb) return aa - bb;
                    return (a.linha_offset || 0) - (b.linha_offset || 0);
                });
                const nLow = apostas.filter(ap => (ap.numeros || [])[0] <= 4).length;
                const nNeg = apostas.filter(ap => (ap.linha_offset || 0) < 0).length;
                const nPos = apostas.filter(ap => (ap.linha_offset || 0) > 0).length;
                el('busca6a-detalhe-meta').innerHTML =
                    `Score <strong>${m.score}</strong> · 7:<strong>${m.qtd_7}</strong> · 6:<strong>${m.qtd_6}</strong> · 5:<strong>${m.qtd_5}</strong>` +
                    ` · Média <strong>${m.media}</strong> · Seq+ <strong>${m.maior_seq_positiva}</strong> · Pior seca <strong>${m.pior_seq}</strong>` +
                    ` · ${data.usar_ajustada ? 'Ajustada' : 'FINAL'} · Base concurso ${data.concurso_base}` +
                    `<div class="text-muted mt-1" style="font-size:11px;">` +
                    `Lista ordenada por proximidade da linha 0 (não por −25→+25). ` +
                    `Linhas −: ${nNeg} · Linhas +: ${nPos} · Apostas cujo menor nº é ≤4: ${nLow}/${apostas.length} ` +
                    `(efeito do ciclo + ordenação crescente — não é critério do ranking).` +
                    `</div>`;

                tbody.innerHTML = apostas.map((ap, i) => {
                    const nums = (ap.numeros || []).map(n => `<span class="badge bg-dark me-1">${pad2(n)}</span>`).join('');
                    const lado = (ap.linha_offset || 0) < 0 ? 'text-danger' : 'text-success';
                    return `<tr>
                        <td>${i + 1}</td>
                        <td class="fw-bold ${lado}">${ap.linha_offset}</td>
                        <td>${nums}</td>
                        <td>${ap.mes_nome || ''}</td>
                    </tr>`;
                }).join('');

                box.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                if (aplicarDepois) busca6aAplicarPreset();
            })
            .catch(err => alert('Erro: ' + err));
    };

    window.busca6aAplicarPreset = function () {
        if (!detalheAtual) {
            alert('Selecione um preset no ranking primeiro.');
            return;
        }
        if (typeof window.atraso6aAplicarSaltosColuna !== 'function') {
            alert('Painel 6A não disponível.');
            return;
        }
        // Alinha limite da UI com o da busca, se necessário
        const limBusca = (detalheAtual.saltos_coluna || []).reduce((m, v) => Math.max(m, v), 1);
        const limMenos = (detalheAtual.saltos_coluna_menos || []).reduce((m, v) => Math.max(m, v), 1);
        const need = Math.max(limBusca, limMenos);
        let radio = null;
        if (need <= 6) radio = el('atraso6a_lim6');
        else if (need <= 15) radio = el('atraso6a_lim15');
        else radio = el('atraso6a_lim30');
        if (radio && !radio.checked) {
            radio.checked = true;
            if (typeof window.atraso6aAtualizarLimiteSalto === 'function') {
                window.atraso6aAtualizarLimiteSalto();
            }
        }
        window.atraso6aAplicarSaltosColuna(
            detalheAtual.saltos_coluna,
            detalheAtual.saltos_coluna_menos,
            { recarregar: true }
        );
        const alvo = el('atraso6a-resumo-saltos');
        if (alvo) alvo.scrollIntoView({ behavior: 'smooth', block: 'center' });
    };

    window.busca6aExportar = function (formato) {
        if (!jobId || !rankSelecionado) {
            alert('Selecione um preset no ranking para exportar as apostas encontradas.');
            return;
        }
        fetch(API + '/exportar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ job_id: jobId, rank: rankSelecionado, formato: formato || 'txt' })
        })
            .then(async r => {
                if (!r.ok) {
                    const j = await r.json().catch(() => ({}));
                    throw new Error(j.mensagem || ('HTTP ' + r.status));
                }
                const disp = r.headers.get('Content-Disposition') || '';
                let nome = 'BuscaSaltos_Rank' + rankSelecionado + '.' + (formato || 'txt');
                const m = /filename="?([^"]+)"?/i.exec(disp);
                if (m) nome = m[1];
                return r.blob().then(blob => ({ blob, nome }));
            })
            .then(({ blob, nome }) => {
                const a = document.createElement('a');
                a.href = URL.createObjectURL(blob);
                a.download = nome;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
            })
            .catch(err => alert('Falha na exportação: ' + err.message));
    };
})();
