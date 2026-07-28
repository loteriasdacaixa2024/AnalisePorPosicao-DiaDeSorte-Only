/**
 * Conferência retroativa de bolões — catálogo das 9 modalidades Caixa.
 * Mesma estrutura para todas; histórico local depende da instância (Dia de Sorte hoje).
 */
(function (global) {
    'use strict';

    const MODALIDADES = [
        {
            slug: 'mega-sena', label: 'Mega-Sena', numero: 1,
            qtdSorteados: 6, faixasPremio: [6, 5, 4], minDezenas: 6, maxDezenas: 20,
            historicoLocal: false, extra: null,
        },
        {
            slug: 'quina', label: 'Quina', numero: 2,
            qtdSorteados: 5, faixasPremio: [5, 4, 3, 2], minDezenas: 5, maxDezenas: 15,
            historicoLocal: false, extra: null,
        },
        {
            slug: 'lotofacil', label: 'Lotofácil', numero: 3,
            qtdSorteados: 15, faixasPremio: [15, 14, 13, 12, 11], minDezenas: 15, maxDezenas: 20,
            historicoLocal: false, extra: null,
        },
        {
            slug: 'lotomania', label: 'Lotomania', numero: 4,
            qtdSorteados: 20, faixasPremio: [20, 19, 18, 17, 16, 15, 0], minDezenas: 50, maxDezenas: 50,
            historicoLocal: false, extra: null,
        },
        {
            slug: 'timemania', label: 'Timemania', numero: 5,
            qtdSorteados: 7, faixasPremio: [7, 6, 5, 4, 3], minDezenas: 10, maxDezenas: 10,
            historicoLocal: false, extra: 'time',
        },
        {
            slug: 'dia-de-sorte', label: 'Dia de Sorte', numero: 6,
            qtdSorteados: 7, faixasPremio: [7, 6, 5, 4], minDezenas: 7, maxDezenas: 15,
            historicoLocal: true, extra: 'mes',
        },
        {
            slug: 'super-sete', label: 'Super Sete', numero: 7,
            qtdSorteados: 7, faixasPremio: [7, 6, 5, 4, 3], minDezenas: 7, maxDezenas: 21,
            historicoLocal: false, extra: 'colunas',
        },
        {
            slug: 'dupla-sena', label: 'Dupla Sena', numero: 8,
            qtdSorteados: 6, faixasPremio: [6, 5, 4, 3], minDezenas: 6, maxDezenas: 15,
            historicoLocal: false, extra: 'dupla',
        },
        {
            slug: 'mais-milionaria', label: '+Milionária', numero: 9,
            qtdSorteados: 6, faixasPremio: [6, 5, 4, 3, 2], minDezenas: 6, maxDezenas: 12,
            historicoLocal: false, extra: 'trevos',
        },
    ];

    const SLUG_ALIASES = {
        'mega-sena': 'mega-sena', 'mega sena': 'mega-sena', 'megasena': 'mega-sena', 'mega_sena': 'mega-sena',
        'quina': 'quina', 'quina-sao-joao': 'quina', 'quina de sao joao': 'quina',
        'lotofacil': 'lotofacil', 'lotofácil': 'lotofacil', 'lotofacil-independencia': 'lotofacil',
        'lotomania': 'lotomania',
        'timemania': 'timemania',
        'dia-de-sorte': 'dia-de-sorte', 'dia de sorte': 'dia-de-sorte', 'dia_de_sorte': 'dia-de-sorte',
        'super-sete': 'super-sete', 'super sete': 'super-sete', 'super_sete': 'super-sete',
        'dupla-sena': 'dupla-sena', 'dupla sena': 'dupla-sena', 'dupla_sena': 'dupla-sena',
        'mais-milionaria': 'mais-milionaria', 'mais milionaria': 'mais-milionaria',
        '+milionaria': 'mais-milionaria', '+milionária': 'mais-milionaria', 'mais_milionaria': 'mais-milionaria',
    };

    const MESES_NUMEROS = {
        'JANEIRO': 1, 'FEVEREIRO': 2, 'MARÇO': 3, 'MARCO': 3, 'ABRIL': 4,
        'MAIO': 5, 'JUNHO': 6, 'JULHO': 7, 'AGOSTO': 8,
        'SETEMBRO': 9, 'OUTUBRO': 10, 'NOVEMBRO': 11, 'DEZEMBRO': 12,
        'JAN': 1, 'FEV': 2, 'MAR': 3, 'ABR': 4, 'MAI': 5, 'JUN': 6,
        'JUL': 7, 'AGO': 8, 'SET': 9, 'OUT': 10, 'NOV': 11, 'DEZ': 12,
    };

    function normTexto(s) {
        return (s || '')
            .normalize('NFD')
            .replace(/[\u0300-\u036f]/g, '')
            .toLowerCase()
            .replace(/_/g, '-')
            .replace(/\s+/g, ' ')
            .trim();
    }

    function getModalidade(slugOuLabel) {
        const raw = normTexto(slugOuLabel);
        const slug = SLUG_ALIASES[raw] || raw;
        return MODALIDADES.find((m) => m.slug === slug) || null;
    }

    function getTodasModalidades() {
        return MODALIDADES.slice();
    }

    function detectarModalidadeBolao(bolao) {
        const candidatos = [
            bolao?.modalidade_slug,
            bolao?.parser_slug,
            bolao?.modalidade,
        ];
        for (const c of candidatos) {
            const mod = getModalidade(c);
            if (mod) return mod;
        }
        const texto = bolao?.texto_completo || '';
        if (/mais.?milion/i.test(texto) || /MAIS_MILIONARIA/i.test(texto)) {
            return getModalidade('mais-milionaria');
        }
        if (/dia de sorte|dia_de_sorte/i.test(texto)) return getModalidade('dia-de-sorte');
        if (/mega.?sena/i.test(texto)) return getModalidade('mega-sena');
        if (/\bquina\b/i.test(texto)) return getModalidade('quina');
        return getModalidade('dia-de-sorte');
    }

    function parseNumero(n) {
        const v = parseInt(String(n).replace(/\D/g, ''), 10);
        return Number.isFinite(v) ? v : null;
    }

    function numerosUnicos(arr) {
        return [...new Set((arr || []).map(parseNumero).filter((n) => n !== null))];
    }

    function extrairMesBolao(bolao, idxAposta) {
        const esp = bolao?.dados_especiais || {};
        if (esp.mes_sorte) {
            const m = String(esp.mes_sorte).trim().toUpperCase();
            if (MESES_NUMEROS[m]) return m;
        }
        const texto = bolao?.texto_completo || '';
        const meses = texto.match(/Mês da Sorte\s*:\s*(\w+)/gi) || [];
        if (meses[idxAposta]) {
            return meses[idxAposta].replace(/Mês da Sorte\s*:\s*/i, '').toUpperCase();
        }
        return null;
    }

    function extrairJogos(bolao, mod) {
        const m = mod || detectarModalidadeBolao(bolao);
        const min = m.minDezenas;
        const max = m.maxDezenas;
        const jogos = [];

        if (Array.isArray(bolao?.apostas) && bolao.apostas.length) {
            bolao.apostas.forEach((ap, idx) => {
                const nums = numerosUnicos(ap.dezenas || ap.numeros);
                if (nums.length < min || nums.length > max) return;
                const jogo = { numeros: nums };
                if (m.extra === 'mes') jogo.mes = extrairMesBolao(bolao, idx);
                if (m.extra === 'trevos' && ap.trevos) {
                    jogo.trevos = ap.trevos.map(parseNumero).filter((n) => n !== null);
                }
                if (m.extra === 'time' && ap.time_coracao) jogo.time = ap.time_coracao;
                if (m.extra === 'colunas' && ap.colunas) jogo.colunas = ap.colunas;
                jogos.push(jogo);
            });
            if (jogos.length) return jogos;
        }

        const mesesTexto = (bolao?.texto_completo || '').match(/Mês da Sorte\s*:\s*(\w+)/gi) || [];
        const mesesLimpos = mesesTexto.map((x) => x.replace(/Mês da Sorte\s*:\s*/i, '').toUpperCase());

        (bolao?.jogos || []).forEach((jogo, idx) => {
            const nums = numerosUnicos(Array.isArray(jogo) ? jogo : (jogo.numeros || jogo.dezenas || []));
            if (nums.length < min || nums.length > max) return;
            jogos.push({
                numeros: nums,
                mes: mesesLimpos[idx] || jogo.mes || null,
            });
        });

        return jogos;
    }

    function novoContadorResultados(mod) {
        const faixas = {};
        mod.faixasPremio.forEach((f) => { faixas[f] = 0; });
        return {
            faixas,
            ac7: 0, ac6: 0, ac5: 0, ac4: 0,
            mesCerto: 0,
            extras: { mes: 0, trevos: 0, time: 0 },
        };
    }

    function criarResumoVazio() {
        const out = {};
        MODALIDADES.forEach((mod) => {
            out[mod.slug] = {
                slug: mod.slug,
                label: mod.label,
                numero: mod.numero,
                boloes: 0,
                jogos: 0,
                lotericas: 0,
                concursos: 0,
                faixas: {},
                extras: { mes: 0 },
                historicoDisponivel: mod.historicoLocal,
                conferido: false,
                aviso: mod.historicoLocal ? '' : 'Histórico não sincronizado nesta instância',
            };
            mod.faixasPremio.forEach((f) => { out[mod.slug].faixas[f] = 0; });
        });
        return out;
    }

    function extrairNumerosSorteados(sorteio, mod) {
        const ordem = sorteio?.ordem_crescente || sorteio?.posicoes || {};
        const keys = ['posicao_1', 'posicao_2', 'posicao_3', 'posicao_4', 'posicao_5', 'posicao_6', 'posicao_7'];
        const nums = keys.map((k) => parseNumero(ordem[k])).filter((n) => n !== null);
        return nums.slice(0, mod.qtdSorteados);
    }

    function minFaixaPremio(mod) {
        const positivas = mod.faixasPremio.filter((f) => f > 0);
        return positivas.length ? Math.min(...positivas) : 0;
    }

    function registrarPremiacao(resultados, acertos, mod, extras) {
        if (!mod.faixasPremio.includes(acertos)) return;
        resultados.faixas[acertos] = (resultados.faixas[acertos] || 0) + 1;
        if (mod.slug === 'dia-de-sorte') {
            if (acertos === 7) resultados.ac7++;
            else if (acertos === 6) resultados.ac6++;
            else if (acertos === 5) resultados.ac5++;
            else if (acertos === 4) resultados.ac4++;
            if (extras?.mesAcertou) {
                resultados.mesCerto++;
                resultados.extras.mes++;
            }
        }
    }

    function conferirLotericasContraSorteios(lotericasMap, sorteios, mod) {
        const minFaixa = minFaixaPremio(mod);
        for (const sorteio of sorteios) {
            const numerosSorteados = extrairNumerosSorteados(sorteio, mod);
            const mesSorteado = sorteio.mes_sorte;

            for (const loterica of lotericasMap.values()) {
                for (const jogo of loterica.jogos) {
                    const nums = numerosUnicos(jogo.numeros);
                    const acertos = nums.filter((n) => numerosSorteados.includes(n)).length;

                    let mesAcertou = false;
                    if (mod.extra === 'mes' && jogo.mes) {
                        mesAcertou = (MESES_NUMEROS[jogo.mes] || 0) === mesSorteado;
                    }

                    if (acertos >= minFaixa || (mod.slug === 'lotomania' && acertos === 0)) {
                        registrarPremiacao(loterica.resultados, acertos, mod, { mesAcertou });

                        if (mod.slug === 'dia-de-sorte' && acertos >= 6) {
                            const existente = loterica.melhoresResultados.find((r) => r.concurso === sorteio.concurso);
                            const payload = {
                                concurso: sorteio.concurso,
                                data: sorteio.data_sorteio,
                                acertos,
                                mesAcertou,
                                numerosAcertados: nums.filter((n) => numerosSorteados.includes(n)),
                                numerosSorteados: numerosSorteados.slice(),
                                mesSorteado,
                            };
                            if (existente) {
                                if (acertos > existente.acertos) Object.assign(existente, payload);
                            } else {
                                loterica.melhoresResultados.push(payload);
                            }
                        }
                    }
                }
            }
        }
    }

    function agregarResumoModalidade(resumo, mod, lotericasMap, totalConcursos) {
        const r = resumo[mod.slug];
        if (!r) return;
        r.lotericas = lotericasMap.size;
        r.concursos = totalConcursos;
        r.conferido = true;
        r.aviso = '';

        lotericasMap.forEach((lot) => {
            mod.faixasPremio.forEach((f) => {
                r.faixas[f] = (r.faixas[f] || 0) + (lot.resultados.faixas[f] || 0);
            });
            if (mod.extra === 'mes') {
                r.extras.mes += lot.resultados.mesCerto || 0;
            }
        });
    }

    function formatarFaixasResumo(mod, faixas) {
        return mod.faixasPremio
            .map((f) => {
                const n = faixas[f] || 0;
                const lbl = f === 0 ? '0 ac.' : `${f} ac.`;
                return `<span class="badge bg-light text-dark border me-1 mb-1">${lbl}: <strong>${n}</strong></span>`;
            })
            .join('');
    }

    function renderHtmlResumoAcertosPorModalidade(resumo, opts) {
        const somenteComBoloes = opts?.somenteComBoloes !== false;
        const linhas = MODALIDADES.filter((mod) => {
            const r = resumo[mod.slug];
            if (!r) return false;
            return somenteComBoloes ? r.boloes > 0 : true;
        });

        if (!linhas.length) {
            return '<p class="text-muted mb-0"><i class="fas fa-info-circle"></i> Nenhum bolão carregado para resumo por modalidade.</p>';
        }

        let html = `
        <div class="table-responsive">
            <table class="table table-sm table-bordered mb-0 align-middle">
                <thead style="background:#443908;color:#fff;">
                    <tr>
                        <th>#</th>
                        <th>Modalidade</th>
                        <th class="text-center">Bolões</th>
                        <th class="text-center">Jogos</th>
                        <th class="text-center">Lotéricas</th>
                        <th class="text-center">Concursos</th>
                        <th>Acertos retroativos (ocorrências c/ prêmio)</th>
                        <th class="text-center">Status</th>
                    </tr>
                </thead>
                <tbody>`;

        linhas.forEach((mod) => {
            const r = resumo[mod.slug];
            const totalPremios = mod.faixasPremio.reduce((acc, f) => acc + (r.faixas[f] || 0), 0);
            const status = r.conferido
                ? (totalPremios > 0 ? '<span class="badge bg-success">Conferido</span>' : '<span class="badge bg-secondary">Sem prêmios</span>')
                : `<span class="badge bg-warning text-dark" title="${r.aviso || ''}">Aguardando histórico</span>`;

            html += `
                <tr>
                    <td class="text-muted">${mod.numero}</td>
                    <td><strong style="color:#715f0e;">${mod.label}</strong></td>
                    <td class="text-center">${r.boloes}</td>
                    <td class="text-center">${r.jogos}</td>
                    <td class="text-center">${r.lotericas || '—'}</td>
                    <td class="text-center">${r.conferido ? r.concursos : '—'}</td>
                    <td>${r.conferido ? formatarFaixasResumo(mod, r.faixas) : `<small class="text-muted">${r.aviso || '—'}</small>`}${mod.extra === 'mes' && r.conferido && r.extras.mes ? `<br><small class="text-success">Mês da Sorte: ${r.extras.mes}</small>` : ''}</td>
                    <td class="text-center">${status}</td>
                </tr>`;
        });

        html += '</tbody></table></div>';
        html += `<p class="small text-muted mt-2 mb-0"><i class="fas fa-history"></i> Contagem = quantas vezes os jogos do bolão teriam sido premiados em concursos passados (não é composição do bolão à venda).</p>`;
        return html;
    }

    function atualizarResumoContagensCarregamento(resumo, boloesProcessados) {
        MODALIDADES.forEach((mod) => {
            resumo[mod.slug].boloes = 0;
            resumo[mod.slug].jogos = 0;
        });
        (boloesProcessados || []).forEach((b) => {
            const slug = b.modalidade_slug || detectarModalidadeBolao(b).slug;
            if (!resumo[slug]) return;
            resumo[slug].boloes += 1;
            resumo[slug].jogos += (b.jogos || []).length;
        });
    }

    global.BoloesConferenciaModalidades = {
        MODALIDADES,
        getModalidade,
        getTodasModalidades,
        detectarModalidadeBolao,
        extrairJogos,
        novoContadorResultados,
        criarResumoVazio,
        extrairNumerosSorteados,
        conferirLotericasContraSorteios,
        agregarResumoModalidade,
        renderHtmlResumoAcertosPorModalidade,
        atualizarResumoContagensCarregamento,
        minFaixaPremio,
    };
}(typeof window !== 'undefined' ? window : globalThis));
