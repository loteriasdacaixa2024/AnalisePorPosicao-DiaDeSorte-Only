/**
 * Componente: Análise Visual de Linhas (Faixas) - Dia de Sorte
 * Linhas: 1 (01-10), 2 (11-20), 3 (21-30), 4 (31)
 */

class AnaliseLinhasAnalyzer {
    constructor() {
        this.linhas = [
            { id: 1, nome: 'Linha 1 (01-10)', min: 1, max: 10, totalNumeros: 10 },
            { id: 2, nome: 'Linha 2 (11-20)', min: 11, max: 20, totalNumeros: 10 },
            { id: 3, nome: 'Linha 3 (21-30)', min: 21, max: 30, totalNumeros: 10 },
            { id: 4, nome: 'Linha 4 (31)', min: 31, max: 31, totalNumeros: 1 }
        ];
    }

    /**
     * Identifica em qual linha o número está
     */
    getLinha(numero) {
        const n = parseInt(numero, 10);
        return this.linhas.find(l => n >= l.min && n <= l.max);
    }

    /**
     * Processa um array de concursos para gerar as estatísticas das linhas
     */
    calcularEstatisticas(concursos) {
        if (!concursos || concursos.length === 0) return null;

        // Estuda do primeiro ao último sorteio sem limites
        const concursosAnalisar = concursos;
        const totalConcursos = concursosAnalisar.length;

        // Inicializar contadores
        const stats = this.linhas.map(l => ({
            ...l,
            frequenciaBolas: 0, // Total de dezenas
            concursosPresente: 0, // Em quantos concursos saiu pelo menos 1 número
            concursosZerada: 0, // Em quantos concursos NÃO saiu a linha
            frequenciaRecente: 0, // Concursos presente nos últimos 10
            atrasoAtual: 0,
            ocorreuNoUltimo: false
        }));

        let totalNumerosSorteados = 0;

        // Iterar sobre os concursos (assumindo que estão do mais recente para o mais antigo)
        concursosAnalisar.forEach((conc, index) => {
            const numeros = conc.numeros || conc.dezenas || [];
            
            const linhasNesteConcurso = new Set();
            
            numeros.forEach(num => {
                const linha = this.getLinha(num);
                if (linha) {
                    linhasNesteConcurso.add(linha.id);
                    const stat = stats.find(s => s.id === linha.id);
                    stat.frequenciaBolas++;
                    totalNumerosSorteados++;
                }
            });

            // Processar presença/falha no concurso para cada linha
            stats.forEach(stat => {
                if (linhasNesteConcurso.has(stat.id)) {
                    stat.concursosPresente++;
                    if (index < 10) {
                        stat.frequenciaRecente++;
                    }
                    if (index === 0) {
                        stat.ocorreuNoUltimo = true;
                    }
                } else {
                    stat.concursosZerada++;
                }
            });
        });

        // Calcular atraso de cada linha (quantos concursos seguidos desde o mais recente a linha não apareceu)
        stats.forEach(stat => {
            let atraso = 0;
            for (let i = 0; i < concursosAnalisar.length; i++) {
                const conc = concursosAnalisar[i];
                const numeros = conc.numeros || conc.dezenas || [];
                const temNaLinha = numeros.some(n => this.getLinha(n)?.id === stat.id);
                if (temNaLinha) {
                    break;
                }
                atraso++;
            }
            stat.atrasoAtual = atraso;
        });

        // Calcular percentuais baseados em concursos
        stats.forEach(stat => {
            stat.percentual = totalConcursos > 0 ? ((stat.concursosPresente / totalConcursos) * 100).toFixed(1) : 0;
            stat.percentualZerada = totalConcursos > 0 ? ((stat.concursosZerada / totalConcursos) * 100).toFixed(1) : 0;
            
            // Expected presence (probabilidade de a linha aparecer em um concurso de 7 dezenas)
            // L1 (10 dezenas) ~95.8% de chance de aparecer em 7 sorteios.
            // L4 (1 dezena) = 7/31 = ~22.5% de chance de aparecer.
            let prob;
            if (stat.totalNumeros === 10) prob = 0.958; // 95.8%
            else prob = 0.225; // 22.5%
            
            stat.esperado = prob * 100;
            stat.diferencaEsperado = parseFloat(stat.percentual) - stat.esperado;
            
            // Avaliar status baseado principalmente no desempenho RECENTE (últimos 10 concursos)
            let esperadoRecente = prob * Math.min(10, totalConcursos);
            
            if (stat.frequenciaRecente > esperadoRecente * 1.15) {
                // Mais de 15% acima do esperado recente
                stat.status = 'QUENTE';
                stat.statusClass = 'status-quente';
            } else if (stat.frequenciaRecente < esperadoRecente * 0.85 || stat.atrasoAtual > 2) {
                // Menos de 85% do esperado recente ou muito atrasada
                stat.status = 'FRIA';
                stat.statusClass = 'status-fria';
            } else {
                stat.status = 'NORMAL';
                stat.statusClass = 'status-normal';
            }
        });

        // Ordenar por presença em concursos (maior para menor) para o Ranking
        const ranking = [...stats].sort((a, b) => b.concursosPresente - a.concursosPresente);

        return {
            totalConcursos,
            totalNumerosSorteados,
            ranking,
            linhas: stats
        };
    }

    /**
     * Renderiza o componente no container especificado
     */
    renderizar(containerId, dadosConcursos) {
        const container = document.getElementById(containerId);
        if (!container) return;

        const analise = this.calcularEstatisticas(dadosConcursos);
        if (!analise || analise.ranking.length === 0) {
            container.innerHTML = `<div class="alert alert-warning">Não foi possível calcular a análise de linhas com os dados fornecidos.</div>`;
            return;
        }

        const top1 = analise.ranking[0];
        const top2 = analise.ranking[1];
        const top3 = analise.ranking[2];
        const linhaMaisAtrasada = [...analise.linhas].sort((a, b) => b.atrasoAtual - a.atrasoAtual)[0];
        const linhaMaisQuente = [...analise.linhas].sort((a, b) => b.diferencaEsperado - a.diferencaEsperado)[0];

        const html = `
            <div class="analise-linhas-container">
                <div class="analise-linhas-header">
                    <h3 class="analise-linhas-title">
                        <i class="fas fa-layer-group"></i> ANÁLISE DE LINHAS
                    </h3>
                    <span class="badge bg-secondary">Últimos ${analise.totalConcursos} concursos</span>
                </div>

                <!-- RANKING DAS LINHAS -->
                <div class="ranking-grid" style="grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));">
                    ${analise.ranking.map((linha, index) => {
                        let badge = '';
                        if (index === 0) badge = '🏆';
                        else if (index === 1) badge = '🥈';
                        else if (index === 2) badge = '🥉';
                        else badge = '📊';

                        return `
                        <div class="ranking-card top-${index + 1}">
                            <div class="ranking-badge">${badge}</div>
                            <div class="ranking-title">${index + 1}º Lugar &rarr; ${linha.nome}</div>
                            <div class="ranking-stats">
                                <div class="stat-item">
                                    <span class="stat-label">Presença</span>
                                    <span class="stat-value">${linha.concursosPresente} concursos</span>
                                </div>
                                <div class="stat-item">
                                    <span class="stat-label">Zerada</span>
                                    <span class="stat-value text-danger">${linha.concursosZerada} vezes</span>
                                </div>
                                <div class="stat-item">
                                    <span class="stat-label">Percentual Total</span>
                                    <span class="stat-value">${linha.percentual}%</span>
                                </div>
                                <div class="stat-item">
                                    <span class="stat-label">Tendência (10 conc.)</span>
                                    <span class="stat-value">${linha.frequenciaRecente} presenças</span>
                                </div>
                                <div class="stat-item">
                                    <span class="stat-label">Status</span>
                                    <span class="status-badge ${linha.statusClass}">${linha.status}</span>
                                </div>
                            </div>
                        </div>
                        `;
                    }).join('')}
                </div>

                <!-- TENDÊNCIA VISUAL -->
                <div class="tendencia-section">
                    <h4 class="section-title"><i class="fas fa-chart-bar"></i> Visão Geral (Concursos com Presença vs Zerada)</h4>
                    ${analise.ranking.map((linha, index) => {
                        let barClass = 'bar-other';
                        if (index === 0) barClass = 'bar-top1';
                        else if (index === 1) barClass = 'bar-top2';
                        else if (index === 2) barClass = 'bar-top3';

                        return `
                        <div class="linha-bar-container">
                            <div class="linha-label">Linha ${linha.id}</div>
                            <div class="linha-progress-wrap">
                                <div class="linha-progress ${barClass}" style="width: ${linha.percentual}%;"></div>
                            </div>
                            <div class="linha-percent">${linha.percentual}%</div>
                        </div>
                        `;
                    }).join('')}
                </div>

                <!-- INSIGHTS ESTRATÉGICOS -->
                <div class="insights-grid">
                    <div class="insight-item">
                        <i class="fas fa-fire insight-icon"></i>
                        <div class="insight-content">
                            <span class="insight-label">Linha Mais Quente</span>
                            <span class="insight-value-text">${linhaMaisQuente.nome}</span>
                        </div>
                    </div>
                    <div class="insight-item">
                        <i class="fas fa-snowflake insight-icon"></i>
                        <div class="insight-content">
                            <span class="insight-label">Linha Mais Atrasada</span>
                            <span class="insight-value-text">${linhaMaisAtrasada.nome} <small class="text-muted">(${linhaMaisAtrasada.atrasoAtual} conc.)</small></span>
                        </div>
                    </div>
                    <div class="insight-item">
                        <i class="fas fa-chart-line insight-icon"></i>
                        <div class="insight-content">
                            <span class="insight-label">Maior Crescimento</span>
                            <span class="insight-value-text">${[...analise.linhas].sort((a,b) => b.frequenciaRecente - a.frequenciaRecente)[0].nome}</span>
                        </div>
                    </div>
                    
                    <div class="insight-item sugestao-aposta">
                        <i class="fas fa-lightbulb insight-icon"></i>
                        <div class="insight-content">
                            <span class="insight-label">Sugestão Inteligente de Aposta</span>
                            <span class="insight-value-text">
                                Concentre seus jogos selecionando 2-3 dezenas da <strong>${top1.nome}</strong> 
                                e inclua ao menos 1 dezena da <strong>${linhaMaisAtrasada.nome}</strong> para equilibrar probabilidade e retorno à média.
                            </span>
                        </div>
                    </div>
                </div>
            </div>
        `;

        container.innerHTML = html;
        
        // Ativar animação das barras após renderizar
        setTimeout(() => {
            const progressBars = container.querySelectorAll('.linha-progress');
            progressBars.forEach(bar => {
                const width = bar.style.width;
                bar.style.width = '0%';
                setTimeout(() => {
                    bar.style.width = width;
                }, 100);
            });
        }, 50);
    }
}

// Instância global para facilitar o uso
const analiseLinhasEngine = new AnaliseLinhasAnalyzer();
