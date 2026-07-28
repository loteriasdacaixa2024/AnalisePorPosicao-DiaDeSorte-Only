// Configuração DEFINITIVA de TODAS as Análises do Sistema
// Dashboard de Análises - Dia de Sorte
// Baseado no arquivo api.txt fornecido pelo usuário

const ANALISES_CONFIG = {
    // ========================================================================
    // ANÁLISES ESTATÍSTICAS BÁSICAS (7)
    // ========================================================================

    'atrasados': {
        titulo: 'Números Atrasados',
        icone: 'fa-clock',
        descricao: 'Números que estão há mais tempo sem aparecer',
        rota: '/api/analise/atrasados',
        processar: (data) => {
            const dezenas = data.dezenas_atrasadas || data.atrasados || [];
            const top3 = dezenas.slice(0, 3).map(d => ({
                descricao: `Dezena ${d.numero || d.dezena} (${d.atraso} sorteios)`,
                percentual: d.atraso
            }));
            const insight = dezenas[0]
                ? `A dezena ${dezenas[0].numero || dezenas[0].dezena} está há ${dezenas[0].atraso} sorteios sem aparecer. Considere incluir números atrasados em suas apostas estratégicas.`
                : 'Sem dados disponíveis.';
            return { top3, insight };
        }
    },

    'meses': {
        titulo: 'Meses da Sorte',
        icone: 'fa-calendar-alt',
        descricao: 'Frequência e padrões dos meses da sorte',
        rota: '/api/analise/meses',
        processar: (data) => {
            const meses = data.meses || [];
            const ordenados = [...meses].sort((a, b) => b.frequencia - a.frequencia);
            const top3 = ordenados.slice(0, 3).map(m => ({
                descricao: `${m.nome} (${m.frequencia}x)`,
                percentual: m.percentual
            }));
            const atrasado = [...meses].sort((a, b) => b.atraso - a.atraso)[0];
            const maisFreq = ordenados[0];
            const insight = maisFreq && atrasado
                ? `${maisFreq.nome} é o mês mais frequente (${maisFreq.percentual}%). ${atrasado.nome} está há ${atrasado.atraso} sorteios sem aparecer.`
                : 'Sem dados disponíveis.';
            return { top3, insight };
        }
    },

    'combinacoes': {
        titulo: 'Combinações',
        icone: 'fa-link',
        descricao: 'Combinações de números frequentes',
        rota: '/api/analise/combinacoes',
        processar: (data) => {
            const combinacoes = data.combinacoes || data.pares || [];
            const top3 = combinacoes.slice(0, 3).map(c => ({
                descricao: c.descricao || `${c.numeros?.join(', ') || ''}`,
                percentual: c.percentual || c.frequencia
            }));
            const insight = combinacoes[0]
                ? `Combinações frequentes identificadas. Use para criar apostas estratégicas.`
                : 'Sem dados disponíveis.';
            return { top3, insight };
        }
    },

    'numeros-juntos': {
        titulo: 'Números Juntos',
        icone: 'fa-users',
        descricao: 'Números que aparecem juntos frequentemente',
        rota: '/api/analise/numeros-juntos',
        processar: (data) => {
            const juntos = data.pares || data.numeros_juntos || [];
            const top3 = juntos.slice(0, 3).map(j => ({
                descricao: j.descricao || `${j.numero1}-${j.numero2}`,
                percentual: j.percentual || j.frequencia
            }));
            const insight = juntos[0]
                ? `Par ${juntos[0].numero1 || ''}-${juntos[0].numero2 || ''} aparece frequentemente. Considere duplas históricas.`
                : 'Sem dados disponíveis.';
            return { top3, insight };
        }
    },

    'quentes-frios': {
        titulo: 'Quentes e Frios',
        icone: 'fa-thermometer-half',
        descricao: 'Números mais e menos frequentes recentemente',
        rota: '/api/analise/quentes-frios',
        processar: (data) => {
            const quentes = data.quentes || [];
            const top3 = quentes.slice(0, 3).map(q => ({
                descricao: `Dezena ${q.numero} (${q.frequencia}x)`,
                percentual: q.percentual || ((q.frequencia / (data.janela || 1)) * 100).toFixed(2)
            }));
            const insight = quentes[0]
                ? `Dezena ${quentes[0].numero} está "quente" com ${quentes[0].frequencia} aparições nos últimos ${data.janela || 'X'} sorteios.`
                : 'Sem dados disponíveis.';
            return { top3, insight };
        }
    },

    'defasagem': {
        titulo: 'Defasagem',
        icone: 'fa-chart-line',
        descricao: 'Análise de defasagem e tendências',
        rota: '/api/analise/defasagem',
        processar: (data) => {
            const padroes = data.padroes || data.defasagens || [];
            const top3 = padroes.slice(0, 3).map(p => ({
                descricao: p.descricao || `Dezena ${p.numero || p.dezena}`,
                percentual: p.percentual || p.defasagem
            }));
            const insight = padroes[0]
                ? `Análise de defasagem mostra tendências importantes. Use para identificar números com maior probabilidade de sair em breve.`
                : 'Sem dados disponíveis.';
            return { top3, insight };
        }
    },

    'numeros-devidos': {
        titulo: 'Números Devidos',
        icone: 'fa-bell',
        descricao: 'Números com alta probabilidade de sair',
        rota: '/api/analise/numeros-devidos',
        processar: (data) => {
            const devidos = data.numeros_devidos || data.devidos || [];
            const top3 = devidos.slice(0, 3).map(d => ({
                descricao: `Dezena ${d.numero || d.dezena}`,
                percentual: d.probabilidade || d.percentual || d.score
            }));
            const insight = devidos[0]
                ? `Dezena ${devidos[0].numero || devidos[0].dezena} tem alta probabilidade de sair. Números "devidos" são candidatos estratégicos.`
                : 'Sem dados disponíveis.';
            return { top3, insight };
        }
    },

    // ========================================================================
    // ANÁLISES DE PADRÕES NUMÉRICOS (8)
    // ========================================================================

    'pares-impares': {
        titulo: 'Pares e Ímpares',
        icone: 'fa-balance-scale',
        descricao: 'Distribuição entre números pares e ímpares',
        rota: '/api/analise/pares-impares',
        processar: (data) => {
            const padroes = data.padroes || [];
            const top3 = padroes.slice(0, 3).map(p => ({
                descricao: p.descricao,
                percentual: p.percentual
            }));
            const insight = padroes[0]
                ? `${padroes[0].descricao} é o padrão mais frequente (${padroes[0].percentual}%). Média: ${data.media_pares_por_sorteio || '?'} pares por jogo.`
                : 'Sem dados disponíveis.';
            return { top3, insight };
        }
    },

    'primos-compostos': {
        titulo: 'Primos e Compostos',
        icone: 'fa-divide',
        descricao: 'Números primos vs números compostos',
        rota: '/api/analise/primos-compostos',
        processar: (data) => {
            const padroes = data.padroes || [];
            const top3 = padroes.slice(0, 3).map(p => ({
                descricao: p.descricao,
                percentual: p.percentual
            }));
            const insight = padroes[0]
                ? `Padrão ${padroes[0].descricao} domina com ${padroes[0].percentual}%. Equilibre primos e compostos.`
                : 'Sem dados disponíveis.';
            return { top3, insight };
        }
    },

    'multiplos': {
        titulo: 'Múltiplos',
        icone: 'fa-times',
        descricao: 'Múltiplos de 3, 5, 7 e outros padrões',
        rota: '/api/analise/multiplos',
        processar: (data) => {
            const padroes = data.padroes || [];
            const top3 = padroes.slice(0, 3).map(p => ({
                descricao: p.descricao,
                percentual: p.percentual
            }));
            const insight = padroes[0]
                ? `${padroes[0].descricao} aparece em ${padroes[0].percentual}% dos sorteios.`
                : 'Sem dados disponíveis.';
            return { top3, insight };
        }
    },

    'fibonacci': {
        titulo: 'Fibonacci',
        icone: 'fa-wave-square',
        descricao: 'Números da sequência Fibonacci',
        rota: '/api/analise/fibonacci',
        processar: (data) => {
            const padroes = data.padroes || [];
            const top3 = padroes.slice(0, 3).map(p => ({
                descricao: p.descricao || p.padrao,
                percentual: p.percentual
            }));
            const insight = padroes[0]
                ? `Fibonacci: ${padroes[0].descricao || padroes[0].padrao}. Números da sequência: 1, 2, 3, 5, 8, 13, 21.`
                : 'Sem dados disponíveis.';
            return { top3, insight };
        }
    },

    'capicua': {
        titulo: 'Números Capicua',
        icone: 'fa-sync-alt',
        descricao: 'Números capicuas (11, 22, etc)',
        rota: '/api/analise/capicua',
        processar: (data) => {
            const padroes = data.padroes || [];
            const top3 = padroes.slice(0, 3).map(p => ({
                descricao: p.descricao || p.padrao,
                percentual: p.percentual
            }));
            const insight = padroes[0]
                ? `${padroes[0].descricao || padroes[0].padrao} (${padroes[0].percentual}%). Capicuas: 11, 22.`
                : 'Sem dados disponíveis.';
            return { top3, insight };
        }
    },

    'raiz-digital': {
        titulo: 'Raiz Digital',
        icone: 'fa-square-root-alt',
        descricao: 'Soma reduzida dos números (numerologia)',
        rota: '/api/analise/raiz-digital',
        processar: (data) => {
            const padroes = data.padroes || [];
            const top3 = padroes.slice(0, 3).map(p => ({
                descricao: p.descricao || `Raiz ${p.raiz}`,
                percentual: p.percentual
            }));
            const insight = padroes[0]
                ? `Raiz digital mais comum: ${padroes[0].descricao || padroes[0].raiz} (${padroes[0].percentual}%).`
                : 'Sem dados disponíveis.';
            return { top3, insight };
        }
    },

    'digitos-unicos': {
        titulo: 'Dígitos Únicos',
        icone: 'fa-fingerprint',
        descricao: 'Quantidade de dígitos únicos por jogo',
        rota: '/api/analise/digitos-unicos',
        processar: (data) => {
            const padroes = data.padroes || [];
            const top3 = padroes.slice(0, 3).map(p => ({
                descricao: p.descricao || `${p.digitos_unicos} dígitos`,
                percentual: p.percentual
            }));
            const insight = padroes[0]
                ? `${padroes[0].descricao} é o mais comum (${padroes[0].percentual}%).`
                : 'Sem dados disponíveis.';
            return { top3, insight };
        }
    },

    'digito-inicial-final': {
        titulo: 'Dígito Inicial e Final',
        icone: 'fa-indent',
        descricao: 'Padrões de dígitos iniciais e finais',
        rota: '/api/analise/digito-inicial-final',
        processar: (data) => {
            const padroes = data.padroes || data.top_padroes_digitos_iniciais || [];
            const top3 = padroes.slice(0, 3).map(p => ({
                descricao: p.descricao || p.padrao,
                percentual: p.percentual
            }));
            const insight = padroes[0]
                ? `Padrão dominante: ${padroes[0].descricao || padroes[0].padrao} (${padroes[0].percentual}%).`
                : 'Sem dados disponíveis.';
            return { top3, insight };
        }
    },

    // ========================================================================
    // ANÁLISES DE DISTRIBUIÇÃO (7)
    // ========================================================================

    'dezenas': {
        titulo: 'Distribuição de Dezenas',
        icone: 'fa-hashtag',
        descricao: 'Análise de distribuição por faixas',
        rota: '/api/analise/dezenas',
        processar: (data) => {
            const padroes = data.padroes || [];
            const top3 = padroes.slice(0, 3).map(p => ({
                descricao: p.descricao,
                percentual: p.percentual
            }));
            const insight = padroes[0]
                ? `Padrão ${padroes[0].descricao} aparece em ${padroes[0].percentual}% dos sorteios.`
                : 'Sem dados disponíveis.';
            return { top3, insight };
        }
    },

    'quadrantes': {
        titulo: 'Quadrantes do Volante',
        icone: 'fa-th',
        descricao: 'Distribuição por quadrantes (1-7, 8-15, 16-23, 24-31)',
        rota: '/api/analise/quadrantes',
        processar: (data) => {
            const padroes = data.padroes || [];
            const top3 = padroes.slice(0, 3).map(p => ({
                descricao: p.descricao,
                percentual: p.percentual
            }));
            const insight = padroes[0]
                ? `${padroes[0].descricao} (${padroes[0].percentual}%). Distribua números entre os 4 quadrantes.`
                : 'Sem dados disponíveis.';
            return { top3, insight };
        }
    },

    'gaps': {
        titulo: 'Distância/Gap entre Números',
        icone: 'fa-ruler-horizontal',
        descricao: 'Distâncias entre números sorteados',
        rota: '/api/analise/gaps',
        processar: (data) => {
            const padroes = data.padroes || data.top_gaps || [];
            const top3 = padroes.slice(0, 3).map(p => ({
                descricao: p.descricao || p.padrao,
                percentual: p.percentual
            }));
            const insight = padroes[0]
                ? `Gap mais comum: ${padroes[0].descricao || padroes[0].padrao} (${padroes[0].percentual}%). Use para espaçar números.`
                : 'Sem dados disponíveis.';
            return { top3, insight };
        }
    },

    'consecutivos': {
        titulo: 'Vizinhos / Consecutivos',
        icone: 'fa-sort-numeric-up',
        descricao: 'Quantidade de números consecutivos',
        rota: '/api/analise/consecutivos',
        processar: (data) => {
            const padroes = data.padroes || [];
            const top3 = padroes.slice(0, 3).map(p => ({
                descricao: p.descricao || p.padrao,
                percentual: p.percentual
            }));
            const insight = padroes[0]
                ? `${padroes[0].descricao || padroes[0].padrao} (${padroes[0].percentual}%). Inclua ou evite consecutivos conforme padrão.`
                : 'Sem dados disponíveis.';
            return { top3, insight };
        }
    },

    'espelhados': {
        titulo: 'Números Espelhados',
        icone: 'fa-mirror',
        descricao: 'Números espelhados (01-31, 02-30, etc)',
        rota: '/api/analise/espelhados',
        processar: (data) => {
            const padroes = data.padroes || [];
            const top3 = padroes.slice(0, 3).map(p => ({
                descricao: p.descricao || p.padrao,
                percentual: p.percentual
            }));
            const insight = padroes[0]
                ? `${padroes[0].descricao || padroes[0].padrao} (${padroes[0].percentual}%). Espelhados: 01-31, 02-30, etc.`
                : 'Sem dados disponíveis.';
            return { top3, insight };
        }
    },

    'soma-dezenas': {
        titulo: 'Soma das Dezenas',
        icone: 'fa-calculator',
        descricao: 'Análise da soma das dezenas sorteadas',
        rota: '/api/analise/soma-dezenas',
        processar: (data) => {
            const padroes = data.padroes || data.faixas_soma || [];
            const top3 = padroes.slice(0, 3).map(p => ({
                descricao: p.descricao || `Soma: ${p.faixa}`,
                percentual: p.percentual
            }));
            const insight = data.soma_media
                ? `Soma média: ${data.soma_media}. Faixa mais comum: ${padroes[0]?.descricao} (${padroes[0]?.percentual}%).`
                : 'Sem dados disponíveis.';
            return { top3, insight };
        }
    },

    'repeticoes': {
        titulo: 'Repetições',
        icone: 'fa-redo',
        descricao: 'Números repetidos entre sorteios consecutivos',
        rota: '/api/analise/repeticoes',
        processar: (data) => {
            const padroes = data.padroes || [];
            const top3 = padroes.slice(0, 3).map(p => ({
                descricao: p.descricao || p.padrao,
                percentual: p.percentual
            }));
            const insight = padroes[0]
                ? `${padroes[0].descricao || padroes[0].padrao} (${padroes[0].percentual}%). Repetições são comuns!`
                : 'Sem dados disponíveis.';
            return { top3, insight };
        }
    },

    // ========================================================================
    // ANÁLISES DE SEQUÊNCIAS (2)
    // ========================================================================

    'sequencias': {
        titulo: 'Sequências',
        icone: 'fa-stream',
        descricao: 'Sequências de números consecutivos',
        rota: '/api/analise/sequencias',
        processar: (data) => {
            const padroes = data.padroes || [];
            const top3 = padroes.slice(0, 3).map(p => ({
                descricao: p.descricao || p.padrao,
                percentual: p.percentual
            }));
            const insight = padroes[0]
                ? `Mais comum: ${padroes[0].descricao || padroes[0].padrao} (${padroes[0].percentual}%).`
                : 'Sem dados disponíveis.';
            return { top3, insight };
        }
    },

    'padroes-sequencias': {
        titulo: 'Padrões de Sequências',
        icone: 'fa-code-branch',
        descricao: 'Padrões avançados de sequências',
        rota: '/api/analise/padroes-sequencias',
        processar: (data) => {
            const padroes = data.padroes || [];
            const top3 = padroes.slice(0, 3).map(p => ({
                descricao: p.descricao || p.padrao,
                percentual: p.percentual
            }));
            const insight = padroes[0]
                ? `Padrão avançado: ${padroes[0].descricao} (${padroes[0].percentual}%).`
                : 'Sem dados disponíveis.';
            return { top3, insight };
        }
    },

    // ========================================================================
    // ANÁLISES TEMPORAIS - MESES (7)
    // ========================================================================

    'evolucao-meses': {
        titulo: 'Evolução dos Meses',
        icone: 'fa-chart-area',
        descricao: 'Evolução temporal dos meses da sorte',
        rota: '/api/analise/evolucao-meses',
        processar: (data) => {
            const meses = data.meses || [];
            const top3 = meses.slice(0, 3).map(m => ({
                descricao: `${m.nome || m.mes}`,
                percentual: m.percentual || m.frequencia
            }));
            const insight = meses[0]
                ? `Evolução mostra ${meses[0].nome || meses[0].mes} em destaque. Acompanhe tendências temporais.`
                : 'Sem dados disponíveis.';
            return { top3, insight };
        }
    },

    'ciclos-meses': {
        titulo: 'Ciclos de Meses',
        icone: 'fa-sync',
        descricao: 'Ciclos e padrões de repetição dos meses',
        rota: '/api/analise/ciclos-meses',
        processar: (data) => {
            const ciclos = data.ciclos || [];
            const top3 = ciclos.slice(0, 3).map(c => ({
                descricao: c.descricao || `Ciclo ${c.ciclo}`,
                percentual: c.percentual || c.frequencia
            }));
            const insight = ciclos[0]
                ? `Ciclo dominante: ${ciclos[0].descricao} (${ciclos[0].percentual}%). Use ciclos para previsão.`
                : 'Sem dados disponíveis.';
            return { top3, insight };
        }
    },

    'transicao-meses': {
        titulo: 'Transição de Meses',
        icone: 'fa-exchange-alt',
        descricao: 'Padrões de transição entre meses',
        rota: '/api/analise/transicao-meses',
        processar: (data) => {
            const transicoes = data.transicoes || [];
            const top3 = transicoes.slice(0, 3).map(t => ({
                descricao: `${t.de} → ${t.para}`,
                percentual: t.percentual || t.frequencia
            }));
            const insight = transicoes[0]
                ? `Transição mais comum: ${transicoes[0].de} → ${transicoes[0].para} (${transicoes[0].percentual}%).`
                : 'Sem dados disponíveis.';
            return { top3, insight };
        }
    },

    'correlacao-mes-dezenas': {
        titulo: 'Correlação Mês × Dezenas',
        icone: 'fa-project-diagram',
        descricao: 'Relação entre mês da sorte e dezenas',
        rota: '/api/analise/correlacao-mes-dezenas',
        processar: (data) => {
            const correlacoes = data.correlacoes || data.correlacao_mes_dezena || [];
            const top3 = correlacoes.slice(0, 3).map(c => ({
                descricao: `${c.mes_nome}: Dezena ${c.dezena}`,
                percentual: c.frequencia || c.percentual
            }));
            const insight = correlacoes[0]
                ? `${correlacoes[0].mes_nome} tem forte correlação com dezena ${correlacoes[0].dezena}.`
                : 'Sem dados disponíveis.';
            return { top3, insight };
        }
    },

    'acumulos-mes': {
        titulo: 'Acúmulos por Mês',
        icone: 'fa-layer-group',
        descricao: 'Acúmulos e concentrações mensais',
        rota: '/api/analise/acumulos-mes',
        processar: (data) => {
            const acumulos = data.acumulos || [];
            const top3 = acumulos.slice(0, 3).map(a => ({
                descricao: `${a.mes_nome || a.mes}`,
                percentual: a.acumulo || a.percentual
            }));
            const insight = acumulos[0]
                ? `Maior acúmulo: ${acumulos[0].mes_nome || acumulos[0].mes} (${acumulos[0].acumulo || acumulos[0].percentual}%).`
                : 'Sem dados disponíveis.';
            return { top3, insight };
        }
    },

    // ========================================================================
    // ANÁLISES PREDITIVAS (2)
    // ========================================================================

    'previsao-atrasados': {
        titulo: 'Previsão de Atrasados',
        icone: 'fa-crystal-ball',
        descricao: 'Previsão baseada em números atrasados',
        rota: '/api/analise/previsao-atrasados',
        processar: (data) => {
            const previsoes = data.previsoes || data.atrasados || [];
            const top3 = previsoes.slice(0, 3).map(p => ({
                descricao: `Dezena ${p.numero || p.dezena}`,
                percentual: p.probabilidade || p.score || p.atraso
            }));
            const insight = previsoes[0]
                ? `Previsão aponta dezena ${previsoes[0].numero || previsoes[0].dezena} com alta probabilidade.`
                : 'Sem dados disponíveis.';
            return { top3, insight };
        }
    },

    'matriz-probabilidade': {
        titulo: 'Matriz de Probabilidade',
        icone: 'fa-border-all',
        descricao: 'Matriz de probabilidades por posição',
        rota: '/api/analise/matriz-probabilidade',
        processar: (data) => {
            const matriz = data.matriz || [];
            const top3 = matriz.slice(0, 3).map(m => ({
                descricao: m.descricao || `Posição ${m.posicao}`,
                percentual: m.probabilidade || m.percentual
            }));
            const insight = matriz[0]
                ? `Matriz mostra probabilidades por posição. Use para apostas direcionadas.`
                : 'Sem dados disponíveis.';
            return { top3, insight };
        }
    },

    // ========================================================================
    // ANÁLISES AVANÇADAS (8)
    // ========================================================================

    'frequencia-premios': {
        titulo: 'Frequência de Prêmios',
        icone: 'fa-trophy',
        descricao: 'Análise dos jogos com acertadores',
        rota: '/api/analise/frequencia-premios',
        processar: (data) => {
            const dezenas = data.top_dezenas || [];
            const top3 = dezenas.slice(0, 3).map(d => ({
                descricao: `Dezena ${d.dezena} (${d.frequencia}x)`,
                percentual: d.percentual
            }));
            const insight = data.total_premios
                ? `${data.total_premios} prêmios analisados. Total pago: R$ ${(data.valor_total_pago || 0).toLocaleString('pt-BR')}. Foque em padrões vencedores!`
                : 'Sem dados disponíveis.';
            return { top3, insight };
        }
    },

    'ciclos-intervalos': {
        titulo: 'Ciclos e Intervalos',
        icone: 'fa-history',
        descricao: 'Análise de ciclos e intervalos temporais',
        rota: '/api/analise/ciclos-intervalos',
        processar: (data) => {
            const ciclos = data.ciclos || [];
            const top3 = ciclos.slice(0, 3).map(c => ({
                descricao: c.descricao || `Ciclo ${c.duracao} sorteios`,
                percentual: c.percentual || c.frequencia
            }));
            const insight = ciclos[0]
                ? `Ciclo dominante: ${ciclos[0].descricao} (${ciclos[0].percentual}%).`
                : 'Sem dados disponíveis.';
            return { top3, insight };
        }
    },

    'repeticao-persistencia': {
        titulo: 'Repetição e Persistência',
        icone: 'fa-recycle',
        descricao: 'Padrões de repetição e persistência',
        rota: '/api/analise/repeticao-persistencia',
        processar: (data) => {
            const padroes = data.padroes || [];
            const top3 = padroes.slice(0, 3).map(p => ({
                descricao: p.descricao || p.padrao,
                percentual: p.percentual
            }));
            const insight = padroes[0]
                ? `${padroes[0].descricao} (${padroes[0].percentual}%). Repetição é padrão!`
                : 'Sem dados disponíveis.';
            return { top3, insight };
        }
    },

    'distribuicao-numerica': {
        titulo: 'Distribuição Numérica',
        icone: 'fa-chart-bar',
        descricao: 'Distribuição dos números ao longo do intervalo',
        rota: '/api/analise/distribuicao-numerica',
        processar: (data) => {
            const distribuicao = data.distribuicao || [];
            const top3 = distribuicao.slice(0, 3).map(d => ({
                descricao: d.descricao || `Faixa ${d.faixa}`,
                percentual: d.percentual
            }));
            const insight = distribuicao[0]
                ? `Distribuição mostra ${distribuicao[0].descricao} em destaque (${distribuicao[0].percentual}%).`
                : 'Sem dados disponíveis.';
            return { top3, insight };
        }
    },

    'sazonal': {
        titulo: 'Análise Sazonal',
        icone: 'fa-leaf',
        descricao: 'Padrões sazonais e tendências temporais',
        rota: '/api/analise/sazonal',
        processar: (data) => {
            const sazonalidade = data.sazonalidade || [];
            const top3 = sazonalidade.slice(0, 3).map(s => ({
                descricao: s.descricao || s.periodo,
                percentual: s.percentual || s.intensidade
            }));
            const insight = sazonalidade[0]
                ? `Sazonalidade: ${sazonalidade[0].descricao} (${sazonalidade[0].percentual}%). Considere época do ano.`
                : 'Sem dados disponíveis.';
            return { top3, insight };
        }
    },

    'probabilidade-condicional': {
        titulo: 'Probabilidade Condicional',
        icone: 'fa-sitemap',
        descricao: 'Probabilidades condicionadas a eventos',
        rota: '/api/analise/probabilidade-condicional',
        processar: (data) => {
            const condicoes = data.condicoes || [];
            const top3 = condicoes.slice(0, 3).map(c => ({
                descricao: c.descricao || c.condicao,
                percentual: c.probabilidade || c.percentual
            }));
            const insight = condicoes[0]
                ? `Maior probabilidade condicional: ${condicoes[0].descricao} (${condicoes[0].probabilidade}%).`
                : 'Sem dados disponíveis.';
            return { top3, insight };
        }
    },

    'tubular': {
        titulo: 'Análise Tubular',
        icone: 'fa-th-large',
        descricao: 'Visualização tubular dos dados',
        rota: '/api/analise/tubular',
        processar: (data) => {
            const padroes = data.padroes || data.tubular || [];
            const top3 = padroes.slice(0, 3).map(p => ({
                descricao: p.descricao || p.padrao,
                percentual: p.percentual || p.frequencia
            }));
            const insight = padroes[0]
                ? `Visualização tubular mostra ${padroes[0].descricao}. Use para análise visual.`
                : 'Ferramenta de visualização disponível.';
            return { top3, insight };
        }
    }
};

// Total: 33 análises com rotas corretas do api.txt
// Removidas: gaps-completo, gaps-expandido, valores-probabilidades (404)
// Removidas: calculadora-probabilidade, simulador-apostas (405 - POST only)
// Removidas: expectativa-meses, gaps-expandido, quadrantes-expandido (não listadas no api.txt)
