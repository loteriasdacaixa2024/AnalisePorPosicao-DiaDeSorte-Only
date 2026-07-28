
    // ============================================
    // LÓGICA DO DASHBOARD ESTRATÉGICO
    // ============================================

    let chartEficiencia = null;
    let chartRedundancia = null;

    // Carregar dados ao abrir a aba
    document.getElementById('tab-dashboard-estrategico').addEventListener('shown.bs.tab', function () {
        carregarDadosDashboard();
    });

    async function carregarDadosDashboard() {
        try {
            const response = await fetch('/central-conferencias/api/metricas-estrategicas');
            const resultado = await response.json();

            if (resultado.sucesso) {
                atualizarKPIs(resultado.dados);
                renderizarGraficoEficiencia(resultado.dados);
                renderizarGraficoRedundancia(resultado.dados);
                renderizarMapaCalorPontosCegos(resultado.dados);
            } else {
                console.error('Erro ao carregar dados:', resultado.mensagem);
                alert('Não foi possível carregar os dados do dashboard.');
            }
        } catch (error) {
            console.error('Erro na requisição:', error);
        }
    }

    function atualizarKPIs(dados) {
        if (!dados || dados.length === 0) return;

        // Total Conferências
        document.getElementById('kpi-total-conferencias').textContent = dados.length;

        // Eficiência Média (Cobertura %)
        const mediaEficiencia = dados.reduce((acc, curr) => acc + (curr.cobertura ? curr.cobertura.percentual : 0), 0) / dados.length;
        document.getElementById('kpi-eficiencia-media').textContent = mediaEficiencia.toFixed(1) + '%';

        // Totais Financeiros
        const totalInvestido = dados.reduce((acc, curr) => acc + (curr.financeiro ? curr.financeiro.investido : 0), 0);
        const totalLucro = dados.reduce((acc, curr) => acc + (curr.financeiro ? curr.financeiro.lucro : 0), 0);
        const roi = totalInvestido > 0 ? (totalLucro / totalInvestido) * 100 : 0;

        const elRoi = document.getElementById('kpi-roi-global');
        elRoi.textContent = roi.toFixed(1) + '%';
        elRoi.className = `display-6 fw-bold ${roi >= 0 ? 'text-success' : 'text-danger'}`;

        document.getElementById('kpi-lucro-total').textContent =
            totalLucro.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });

        // Custo Médio por Dezena Única
        const mediaCusto = dados.reduce((acc, curr) => acc + (curr.estrategia ? curr.estrategia.custo_dezena_unica : 0), 0) / dados.length;
        document.getElementById('kpi-custo-dezena').textContent =
            mediaCusto.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
    }

    function renderizarGraficoEficiencia(dados) {
        const ctx = document.getElementById('chartEvolucaoEficiencia').getContext('2d');

        if (chartEficiencia) chartEficiencia.destroy();

        const labels = dados.map(d => `Conc. ${d.concurso}`);
        const valores = dados.map(d => d.cobertura ? d.cobertura.percentual : 0);

        chartEficiencia = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Eficiência de Cobertura (%)',
                    data: valores,
                    borderColor: '#2ecc71', // Verde
                    backgroundColor: 'rgba(46, 204, 113, 0.2)',
                    borderWidth: 2,
                    tension: 0.3,
                    fill: true,
                    pointBackgroundColor: '#27ae60'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        title: { display: true, text: '% Números Sorteados Cobertos' }
                    }
                },
                plugins: {
                    legend: { display: false }
                }
            }
        });
    }

    function renderizarGraficoRedundancia(dados) {
        // Pegar o último dado para mostrar o status ATUAL
        if (!dados || dados.length === 0) return;
        const ultimo = dados[dados.length - 1];
        const valorRedundancia = ultimo.estrategia ? ultimo.estrategia.redundancia : 0;

        const elValor = document.getElementById('valor-redundancia');
        if (elValor) elValor.textContent = valorRedundancia.toFixed(2);

        const ctx = document.getElementById('chartRedundancia').getContext('2d');
        if (chartRedundancia) chartRedundancia.destroy();

        // Gráfico Doughnut tipo "Gauge"
        let cor = '#2ecc71'; // Verde (Bom)
        if (valorRedundancia > 1.5) cor = '#f1c40f'; // Amarelo
        if (valorRedundancia > 2.0) cor = '#e74c3c'; // Vermelho

        chartRedundancia = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Redundância', 'Ideal'],
                datasets: [{
                    data: [valorRedundancia, Math.max(0, 3.0 - valorRedundancia)],
                    backgroundColor: [cor, '#ecf0f1'],
                    borderWidth: 0,
                    circumference: 180,
                    rotation: 270
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '75%',
                plugins: {
                    tooltip: { enabled: false },
                    legend: { display: false }
                }
            }
        });
    }

    function renderizarMapaCalorPontosCegos(dados) {
        const container = document.getElementById('heatmap-blindspots');
        container.innerHTML = '';

        // Estilo de Grid para alinhar perfeitamente
        container.className = 'd-grid gap-2 p-3 justify-content-center';
        container.style.gridTemplateColumns = 'repeat(auto-fit, minmax(45px, 1fr))';
        container.style.maxWidth = '100%';

        const frequencia = Array(32).fill(0);
        dados.forEach(d => {
            try {
                const jogados = d.cobertura ? d.cobertura.dezenas_jogadas : [];
                jogados.forEach(num => {
                    if (num >= 1 && num <= 31) frequencia[num]++;
                });
            } catch (e) { console.error(e); }
        });

        // Calcular estatísticas e insights APÓS processar frequências
        setTimeout(() => gerarEstatisticasEInsights(dados, frequencia), 100);

        const maxFreq = Math.max(...frequencia.slice(1)) || 1;

        for (let i = 1; i <= 31; i++) {
            const freq = frequencia[i];
            let bgStyle = '';
            let textStyle = '';
            let borderStyle = '';
            let shadowStyle = 'box-shadow: 0 4px 6px rgba(0,0,0,0.1);';

            if (freq === 0) {
                // Ponto Cego: Gradiente Vermelho Suave
                bgStyle = 'background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);';
                textStyle = 'color: #c0392b; font-weight: 800;';
                borderStyle = 'border: 2px solid #e74c3c;';
            } else {
                // Jogado: Gradiente Verde
                const intensity = Math.max(0.3, freq / maxFreq);
                if (intensity < 0.5) {
                    bgStyle = 'background: linear-gradient(135deg, #d4fc79 0%, #96e6a1 100%);';
                    textStyle = 'color: #2d3436; font-weight: 700;';
                } else {
                    bgStyle = 'background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);';
                    textStyle = 'color: white; font-weight: 700; text-shadow: 0 1px 2px rgba(0,0,0,0.3);';
                }
                borderStyle = 'border: 1px solid rgba(0,0,0,0.05);';
            }

            const div = document.createElement('div');
            div.className = 'd-flex flex-column align-items-center justify-content-center user-select-none';
            div.style.cssText = `
                width: 45px; 
                height: 45px; 
                border-radius: 50%; 
                ${bgStyle} 
                ${textStyle} 
                ${borderStyle}
                ${shadowStyle}
                transition: transform 0.2s;
                cursor: default;
            `;

            div.onmouseover = function () { this.style.transform = 'scale(1.15)'; this.style.zIndex = '10'; };
            div.onmouseout = function () { this.style.transform = 'scale(1)'; this.style.zIndex = '1'; };

            div.title = `Dezena ${i}: Jogada ${freq} vezes`;
            div.innerHTML = `
                <span class="lh-1" style="font-size: 16px;">${i}</span>
                <span style="font-size: 8px; opacity: 0.9; margin-top: -2px;">${freq}x</span>
            `;
            container.appendChild(div);
        }
    }

    function gerarEstatisticasEInsights(dados, frequencia) {
        if (!dados || dados.length === 0) return;

        let listaFreq = [];
        for (let i = 1; i <= 31; i++) {
            listaFreq.push({ num: i, freq: frequencia[i] });
        }
        listaFreq.sort((a, b) => b.freq - a.freq);

        const maisJogadas = listaFreq.slice(0, 5).filter(x => x.freq > 0);
        const pontosCegos = listaFreq.filter(x => x.freq === 0).map(x => x.num).sort((a, b) => a - b);

        // Renderizar Mais Jogadas (Pills Modernos)
        const divMais = document.getElementById('stats-mais-jogadas');
        if (divMais) {
            divMais.innerHTML = '';
            if (maisJogadas.length > 0) {
                maisJogadas.forEach(item => {
                    divMais.innerHTML += `
                        <div class="px-3 py-1 rounded-pill bg-primary bg-gradient text-white shadow-sm d-flex align-items-center gap-2">
                            <span class="fw-bold fs-6">${item.num}</span>
                            <span class="border-start border-white ps-2" style="font-size: 0.8em; opacity: 0.9;">${item.freq}x</span>
                        </div>
                    `;
                });
            } else { divMais.innerHTML = '<span class="text-muted fst-italic">Sem dados suficientes.</span>'; }
        }

        // Renderizar Pontos Cegos (Clean)
        const divCegos = document.getElementById('stats-pontos-cegos');
        if (divCegos) {
            divCegos.innerHTML = '';
            if (pontosCegos.length > 0) {
                pontosCegos.forEach(num => {
                    divCegos.innerHTML += `
                        <div class="px-3 py-1 rounded-pill bg-danger bg-opacity-10 text-danger border border-danger border-opacity-25 shadow-sm fw-bold">
                            ${num}
                        </div>
                    `;
                });
            } else { divCegos.innerHTML = '<span class="text-success fw-bold"><i class="fas fa-check-circle"></i> Cobertura 100%! Sem pontos cegos.</span>'; }
        }

        // Renderizar Insights (Cards)
        const listaDicas = document.getElementById('lista-insights-estrategicos');
        if (!listaDicas) return;
        listaDicas.innerHTML = '';
        const dicas = [];

        // Dica 1: Vizinhos
        dicas.push({
            icon: 'fas fa-bullseye', color: 'text-primary',
            html: `<strong>Técnica do Vizinho:</strong> Jogue vizinhos (+1/-1) das suas favoritas: <b>${maisJogadas.slice(0, 3).map(x => x.num).join(', ')}</b>. O sorteio quase sempre "raspa" nelas.`
        });

        const ultimo = dados[dados.length - 1];
        const redun = ultimo.estrategia ? ultimo.estrategia.redundancia : 0;
        if (redun > 2.0) {
            dicas.push({
                icon: 'fas fa-sync-alt', color: 'text-warning',
                html: `<strong>Alerta de Repetição (${redun.toFixed(2)}):</strong> Você está muito repetitivo ("teimoso"). Troque pelo menos 5 dezenas no próximo jogo para destravar os acertos.`
            });
        }

        if (pontosCegos.length > 0) {
            const sugeridos = pontosCegos.slice(0, 3).join(', ');
            dicas.push({
                icon: 'far fa-snowflake', color: 'text-info',
                html: `<strong>Quebre o Gelo:</strong> Inclua as dezenas <b>${sugeridos}</b>. Elas nunca entraram no seu jogo e estatisticamente devem sair em breve.`
            });
        }

        const cob = ultimo.cobertura ? ultimo.cobertura.percentual : 0;
        if (cob < 50) {
            dicas.push({
                icon: 'fas fa-chart-pie', color: 'text-danger',
                html: `<strong>Baixa Cobertura (${cob}%):</strong> Voce joga em menos da metade do volante. Tente cobrir mais áreas para aumentar a chance matématica.`
            });
        }

        dicas.forEach(dica => {
            listaDicas.innerHTML += `
                <li class="d-flex gap-3 mb-2 p-2 rounded bg-white shadow-sm border-start border-4 ${dica.color === 'text-primary' ? 'border-primary' : dica.color === 'text-danger' ? 'border-danger' : dica.color === 'text-warning' ? 'border-warning' : 'border-info'}">
                    <div class="pt-1"><i class="${dica.icon} ${dica.color} fa-lg"></i></div>
                    <div class="small text-dark lh-sm">${dica.html}</div>
                </li>
            `;
        });

        listaDicas.style.listStyle = 'none';
        listaDicas.style.paddingLeft = '0';
    }

    // ============================================
    // LÓGICA DE ANÁLISE DE VARIÂNCIA NOMINAL
    // ============================================

    window.alternarVisao = function(concurso, visao) {
        const btnCards = document.getElementById(`btn-visao-cards-${concurso}`);
        const btnVariancia = document.getElementById(`btn-visao-variancia-${concurso}`);
        const containerCards = document.getElementById(`container-cards-${concurso}`);
        const containerVariancia = document.getElementById(`container-variancia-${concurso}`);

        if (!btnCards || !btnVariancia || !containerCards || !containerVariancia) return;

        if (visao === 'cards') {
            btnCards.classList.add('active');
            btnVariancia.classList.remove('active');
            containerCards.style.display = 'block';
            containerVariancia.style.display = 'none';
        } else {
            btnCards.classList.remove('active');
            btnVariancia.classList.add('active');
            containerCards.style.display = 'none';
            containerVariancia.style.display = 'block';
        }
    };

    window.renderizarTabelaDesvio = function(concurso, resultado) {
        if (!resultado || !resultado.resultado_sorteio || !resultado.resultado_sorteio.numeros) {
            return '<div class="alert alert-warning">Resultado oficial não disponível para este concurso.</div>';
        }

        const sorteados = [...resultado.resultado_sorteio.numeros].sort((a, b) => a - b);
        let totalDeltasGlobal = 0;
        let totalDeltasAbsGlobal = 0;
        let countDeltas = 0;

        let tableRows = '';
        resultado.apostas.forEach((aposta) => {
            if (aposta.erro_ocr || aposta.dados_incompletos) return;

            const numeros = aposta.fonte === 'JSON' 
                ? (aposta.numeros_apostados || []) 
                : (aposta.dados_extraidos?.numeros_apostados || []);
            
            if (numeros.length < 7) return;

            const numerosOrdenados = [...numeros].sort((a, b) => a - b).slice(0, 7);
            let rowHtml = `<tr><td class="num-aposta-col">${aposta.numero_aposta}</td>`;
            let somaDeltaAbs = 0;

            numerosOrdenados.forEach((num, i) => {
                const delta = num - sorteados[i];
                somaDeltaAbs += Math.abs(delta);
                totalDeltasGlobal += delta;
                totalDeltasAbsGlobal += Math.abs(delta);
                countDeltas++;

                let deltaClass = 'delta-neutral';
                if (delta === 0) deltaClass = 'delta-zero';
                else if (Math.abs(delta) === 1) deltaClass = 'delta-prox';

                rowHtml += `<td>
                    <div class="fw-bold mb-1">${String(num).padStart(2, '0')}</div>
                    <div class="delta-badge ${deltaClass}">${delta > 0 ? '+' : ''}${delta}</div>
                </td>`;
            });

            rowHtml += `<td class="total-desvio-col">${somaDeltaAbs}</td></tr>`;
            tableRows += rowHtml;
        });

        const desvioMedio = countDeltas > 0 ? (totalDeltasGlobal / countDeltas).toFixed(2) : '0.00';
        const desvioMedioAbs = countDeltas > 0 ? (totalDeltasAbsGlobal / (resultado.apostas.length * 7)).toFixed(2) : '0.00';
        
        const tendenciaMsg = desvioMedio > 0.5 ? 'TENDÊNCIA ALTA' : (desvioMedio < -0.5 ? 'TENDÊNCIA BAIXA' : 'EQUILIBRADO');
        const tendenciaCor = desvioMedio > 0.5 ? 'text-danger' : (desvioMedio < -0.5 ? 'text-primary' : 'text-success');

        return `
            <div class="row g-3 mb-4">
                <div class="col-md-8">
                    <div class="desvio-medio-container h-100 d-flex justify-content-between align-items-center">
                        <div>
                            <h5 class="mb-1 text-uppercase fw-800" style="letter-spacing: 1.5px;">Desvio Médio Geral</h5>
                            <p class="mb-0 text-white-50 small">Média ponderada de todos os deltas posicionais das apostas processadas.</p>
                        </div>
                        <div class="text-end">
                            <div class="desvio-medio-valor">${desvioMedio}</div>
                            <div class="fw-bold ${tendenciaCor} badge bg-white px-2 py-1" style="font-size: 0.7rem;">${tendenciaMsg}</div>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card border-0 shadow-sm h-100" style="background: linear-gradient(135deg, #f1c40f 0%, #f39c12 100%); color: #000; border-radius: 12px;">
                        <div class="card-body d-flex flex-column justify-content-center align-items-center text-center">
                            <h6 class="fw-bold mb-1">Média de Soma Absoluta</h6>
                            <h2 class="fw-800 mb-0">${desvioMedioAbs}</h2>
                            <small class="opacity-75">Pontos de desvio por aposta</small>
                        </div>
                    </div>
                </div>
            </div>

            <div class="card border-0 shadow-sm" style="border-radius: 12px; overflow: hidden;">
                <div class="table-responsive">
                    <table class="table table-variancia mb-0">
                        <thead>
                            <tr>
                                <th rowspan="2" class="align-middle" style="width: 60px;">#</th>
                                <th colspan="7">Diferença Posicional (Aposta - Resultado)</th>
                                <th rowspan="2" class="align-middle" style="width: 100px;">Soma Abs.</th>
                            </tr>
                            <tr>
                                <th>P1</th><th>P2</th><th>P3</th><th>P4</th><th>P5</th><th>P6</th><th>P7</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${tableRows}
                        </tbody>
                    </table>
                </div>
            </div>
        `;
    };

    window.carregarVarianciaNominal = function() {
        const concurso = document.getElementById('select-concurso-variancia').value;
        if (!concurso) {
            alert('Por favor, selecione um concurso.');
            return;
        }

        const container = document.getElementById('container-resultado-variancia');
        container.innerHTML = `
            <div class="text-center py-5 bg-white rounded shadow-sm">
                <div class="spinner-border text-primary mb-3" style="width: 3rem; height: 3rem;" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <h5 class="text-primary fw-bold">Processando Variância...</h5>
                <p class="text-muted">Calculando deltas posicionais para o Concurso ${concurso}</p>
            </div>
        `;

        fetch(`/api/conferencia-ocr/processar-concurso/${concurso}`, { method: 'POST' })
            .then(r => r.json())
            .then(data => {
                if (data.sucesso && data.task_id) {
                    monitorarVariancia(data.task_id, concurso);
                } else {
                    container.innerHTML = `<div class="alert alert-danger m-4">Erro ao iniciar processamento: ${data.mensagem || 'Erro desconhecido'}</div>`;
                }
            })
            .catch(err => {
                container.innerHTML = `<div class="alert alert-danger m-4">Erro de conexão: ${err.message}</div>`;
            });
    };

    function monitorarVariancia(taskId, concurso) {
        fetch(`/api/conferencia-ocr/status/${taskId}`)
            .then(r => r.json())
            .then(data => {
                if (data.status === 'sucesso') {
                    const html = window.renderizarTabelaDesvio(concurso, data.resultado);
                    document.getElementById('container-resultado-variancia').innerHTML = html;
                } else if (data.status === 'erro') {
                    document.getElementById('container-resultado-variancia').innerHTML = `<div class="alert alert-danger m-4">Erro: ${data.resultado.mensagem}</div>`;
                } else {
                    // Atualiza progresso visual se necessário
                    const pct = data.progresso || 0;
                    document.getElementById('container-resultado-variancia').innerHTML = `
                        <div class="text-center py-5 bg-white rounded shadow-sm">
                            <div class="spinner-border text-primary mb-3" style="width: 3rem; height: 3rem;" role="status"></div>
                            <h5 class="text-primary fw-bold">Analisando... ${pct}%</h5>
                            <div class="progress mx-auto" style="width: 200px; height: 8px;">
                                <div class="progress-bar progress-bar-striped progress-bar-animated" style="width: ${pct}%"></div>
                            </div>
                        </div>
                    `;
                    setTimeout(() => monitorarVariancia(taskId, concurso), 800);
                }
    }

    // LÓGICA DE ABERTURA DIRETA DE ABA POR HASH DA URL
    document.addEventListener("DOMContentLoaded", function () {
        let hash = window.location.hash;
        if (hash) {
            // Se o usuário passar apenas #conferencia-historica, mapeamos para o ID correto #pane-conferencia-historica se necessário
            if (!hash.startsWith("#pane-") && !document.querySelector(`button[data-bs-target="${hash}"]`)) {
                hash = "#pane-" + hash.substring(1);
            }

            const triggerEl = document.querySelector(`button[data-bs-target="${hash}"]`);
            if (triggerEl) {
                const tab = new bootstrap.Tab(triggerEl);
                tab.show();
                // Opcional: Rolagem suave até as tabs se quiser
                triggerEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        }
    });


