/**

 * Botão discreto "→ Laboratório" nos geradores do sistema.

 */

(function () {

    'use strict';



    const MAX_PADRAO = 10;

    const MAX_EXPANDIDO = 100;

    const LS_MAIS_APOSTAS = 'laboratorioAlteracoesPermitirMais';



    const ROTAS_LAB = [

        '/gerador-especial',

        '/gerador-inteligente',

        '/gerador-padroes',

        '/desdobramentos',

        '/ferramentas/fechamentos',

        '/analise-ciclos-dezenas',

        '/palpites',

        '/estatisticas',

        '/visualizacao-tubular',

        '/analise/estrutura-apostas',

        '/analise-visual',

    ];



    function getLimiteApostas() {

        try {

            return localStorage.getItem(LS_MAIS_APOSTAS) === '1' ? MAX_EXPANDIDO : MAX_PADRAO;

        } catch (e) {

            return MAX_PADRAO;

        }

    }



    function coletarApostasGenerico() {

        const lim = getLimiteApostas();

        const apostas = [];



        if (window.SimuladorEliteManager && window.SimuladorEliteManager.jogos) {

            window.SimuladorEliteManager.jogos.slice(0, lim).forEach((j) => {

                if (j && j.length >= 7) apostas.push({ numeros: [...j] });

            });

            if (apostas.length) return { apostas, origem: 'simulador-elite' };

        }



        if (window.simulacoesFiltros && Array.isArray(window.simulacoesFiltros)) {

            window.simulacoesFiltros.slice(0, lim).forEach((s) => {

                if (s && s.numeros && s.numeros.length >= 7) {

                    apostas.push({ numeros: s.numeros, mes: s.mes });

                }

            });

            if (apostas.length) return { apostas, origem: 'simulador-filtros' };

        }



        if (window.EngineFinalEliteDiaSorte && window.EngineFinalEliteDiaSorte.ultimasApostas) {

            window.EngineFinalEliteDiaSorte.ultimasApostas.slice(0, lim).forEach((a) => {

                apostas.push({

                    numeros: a.numeros || a,

                    mes: a.mes != null ? a.mes : window.EngineFinalEliteDiaSorte.ultimoMesSorteNum,

                });

            });

            if (apostas.length) return { apostas, origem: 'engine-final' };

        }



        const textareas = document.querySelectorAll('textarea');

        for (const ta of textareas) {

            const val = (ta.value || '').trim();

            if (val.length < 10) continue;

            const linhas = val.split(/\r?\n/).filter((l) => l.trim());

            const tmp = [];

            linhas.forEach((linha) => {

                const nums = linha.split(/[\s,;]+/).map((x) => parseInt(x, 10)).filter((n) => n >= 1 && n <= 31);

                const uniq = [...new Set(nums)].sort((a, b) => a - b);

                if (uniq.length >= 7) tmp.push({ numeros: uniq });

            });

            if (tmp.length) return { apostas: tmp.slice(0, lim), origem: location.pathname };

        }



        return { apostas: [], origem: location.pathname };

    }



    function enviarParaLaboratorio(apostas, origem) {

        const lim = getLimiteApostas();

        if (!apostas || !apostas.length) {

            alert(`Nenhuma aposta válida na tela (mín. 7 dezenas, máx. ${lim}).`);

            return;

        }

        if (apostas.length > lim) {

            alert(`Máximo de ${lim} apostas. ${lim === MAX_PADRAO ? 'Ative "Mais de 10 apostas" no Laboratório.' : 'Reduza o lote.'}`);

            return;

        }

        localStorage.setItem('laboratorioAlteracoesTransfer', JSON.stringify({

            apostas,

            origem: origem || location.pathname,

            ts: Date.now(),

        }));

        const url = '/analise-visual#pane-laboratorio-alteracoes';

        if (location.pathname.includes('/analise-visual')) {

            window.location.hash = 'pane-laboratorio-alteracoes';

            if (window.LaboratorioAlteracoes) {

                window.LaboratorioAlteracoes.processarTransferencia();

            } else {

                location.reload();

            }

        } else {

            window.open(url, '_blank');

        }

    }



    function estaNoPaneLaboratorio() {

        const hash = (location.hash || '').replace('#', '');

        if (hash === 'pane-laboratorio-alteracoes') return true;

        const pane = document.getElementById('pane-laboratorio-alteracoes');

        return !!(pane && pane.classList.contains('active'));

    }



    function deveMostrarBotaoLab() {

        const path = location.pathname;

        if (!ROTAS_LAB.some((r) => path.includes(r.replace(/\/$/, '')))) return false;

        if (path.includes('/analise-visual') && estaNoPaneLaboratorio()) return false;

        return true;

    }



    function removerBotaoLab() {

        document.getElementById('btnLabAlteracoesGlobal')?.remove();

    }



    function injetarBotao() {

        if (!deveMostrarBotaoLab()) {

            removerBotaoLab();

            return;

        }

        if (document.getElementById('btnLabAlteracoesGlobal')) return;



        const lim = getLimiteApostas();

        const btn = document.createElement('button');

        btn.type = 'button';

        btn.id = 'btnLabAlteracoesGlobal';

        btn.className = 'btn btn-sm btn-outline-secondary';

        btn.title = `Enviar para Laboratório de Alterações (máx. ${lim})`;

        btn.innerHTML = '<i class="fas fa-flask"></i> Lab';

        btn.style.cssText = 'position:fixed;bottom:12px;right:12px;z-index:1050;opacity:0.92;font-size:12px;';

        btn.addEventListener('click', () => {

            const { apostas, origem } = coletarApostasGenerico();

            enviarParaLaboratorio(apostas, origem);

        });

        document.body.appendChild(btn);

    }



    function atualizarBotaoLab() {

        removerBotaoLab();

        injetarBotao();

    }



    window.LaboratorioAlteracoesEnviar = {

        coletar: coletarApostasGenerico,

        enviar: enviarParaLaboratorio,

        getLimiteApostas,

    };



    if (document.readyState === 'loading') {

        document.addEventListener('DOMContentLoaded', atualizarBotaoLab);

    } else {

        atualizarBotaoLab();

    }



    window.addEventListener('hashchange', atualizarBotaoLab);



    document.addEventListener('shown.bs.tab', (e) => {

        const target = e.target.getAttribute('data-bs-target') || e.target.getAttribute('href') || '';

        if (target === '#pane-laboratorio-alteracoes' || target.includes('laboratorio-alteracoes')) {

            atualizarBotaoLab();

        } else if (location.pathname.includes('/analise-visual')) {

            atualizarBotaoLab();

        }

    });

})();


