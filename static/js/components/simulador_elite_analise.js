/**
 * simulador_elite_analise.js
 * Componente responsável pelo "Preview do Último Concurso" e a "Análise do Super Bilhete"
 * Funciona de forma não invasiva ao lado do SimuladorEliteManager
 */

const SimuladorEliteAnalise = {
    // Referência aos concursos globais (deve existir na janela pai)
    getConcursos() {
        return window.concursosCarregados || [];
    },

    async carregarDados() {
        if (window.concursosCarregados && window.concursosCarregados.length > 0) {
            return; // Já carregado
        }
        
        try {
            const response = await fetch('/api/sorteios/todos');
            const data = await response.json();
            
            if (data && data.sorteios) {
                // Formatar para o padrão esperado pelo componente
                window.concursosCarregados = data.sorteios.map(s => {
                    const numeros = [
                        s.posicoes.posicao_1,
                        s.posicoes.posicao_2,
                        s.posicoes.posicao_3,
                        s.posicoes.posicao_4,
                        s.posicoes.posicao_5,
                        s.posicoes.posicao_6,
                        s.posicoes.posicao_7
                    ].map(Number).sort((a, b) => a - b);
                    
                    return {
                        ...s,
                        numeros_ordenados: numeros,
                        data: s.data_sorteio
                    };
                }).sort((a, b) => b.concurso - a.concurso); // Mais recente primeiro
            }
        } catch (e) {
            console.error("Erro ao carregar concursos históricos no SimuladorEliteAnalise:", e);
        }
    },

    // ==========================================
    // MÓDULO 1: PREVIEW DO ÚLTIMO CONCURSO
    // ==========================================
    async atualizarPreviewUltimoConcurso(jogosAtuais) {
        await this.carregarDados();
        
        const container = document.getElementById('ultimo-concurso-preview-elite');
        if (!container) return;

        const concursos = this.getConcursos();
        if (!concursos || concursos.length === 0) {
            container.style.display = 'none';
            return;
        }

        const ultimo = concursos[0]; // O mais recente (índice 0)
        
        // Quantos números repetidos existem entre o ultimo concurso e TODAS as apostas da tela?
        // Vamos achar a "maior similaridade" (a aposta que mais copia o concurso passado)
        let maxRepetidos = 0;
        let numRepetidosMax = [];

        jogosAtuais.forEach(jogo => {
            if (!jogo || jogo.length === 0) return;
            const repetidos = jogo.filter(n => ultimo.numeros_ordenados.includes(n));
            if (repetidos.length > maxRepetidos) {
                maxRepetidos = repetidos.length;
                numRepetidosMax = repetidos;
            }
        });

        let nivelRisco = 'Baixo';
        let corRisco = 'success';
        let iconeRisco = 'check-circle';

        if (maxRepetidos >= 5) {
            nivelRisco = 'Alto';
            corRisco = 'danger';
            iconeRisco = 'exclamation-triangle';
        } else if (maxRepetidos === 4) {
            nivelRisco = 'Médio';
            corRisco = 'warning';
            iconeRisco = 'exclamation-circle';
        }

        // Dezenas formatadas
        const dezenasHtml = ultimo.numeros_ordenados.map(n => {
            const isRepetidaNaPior = numRepetidosMax.includes(n);
            return `<span class="badge ${isRepetidaNaPior ? 'bg-danger text-white' : 'bg-light text-dark border'}" style="font-size: 13px; margin-right: 3px;">${String(n).padStart(2, '0')}</span>`;
        }).join('');

        const html = `
            <div class="d-flex align-items-center justify-content-between flex-wrap gap-2">
                <div class="d-flex align-items-center gap-3">
                    <span class="badge bg-secondary" style="font-size: 12px;"><i class="fas fa-history"></i> Último Concurso #${ultimo.concurso}</span>
                    <span class="text-muted" style="font-size: 12px;"><i class="far fa-calendar-alt"></i> ${ultimo.data || ''}</span>
                    <div class="d-flex align-items-center ms-2">
                        ${dezenasHtml}
                    </div>
                </div>
                <div class="d-flex align-items-center">
                    <div class="text-end" style="font-size: 11px; line-height: 1.2;">
                        <span class="text-muted">Risco de Repetição:</span><br>
                        <span class="text-${corRisco} fw-bold"><i class="fas fa-${iconeRisco}"></i> ${nivelRisco} (${maxRepetidos} repetidas)</span>
                    </div>
                </div>
            </div>
        `;

        container.innerHTML = html;
        container.style.display = 'block';
    },

    // ==========================================
    // MÓDULO 2: ANÁLISE DO SUPER BILHETE
    // ==========================================
    async initSuperBilheteAnalise() {
        await this.carregarDados();
        
        const container = document.getElementById('super-bilhete-analise-container');
        if (!container) return;

        // Limita a 100 concursos no select para performance e clareza
        const concursos = this.getConcursos().slice(0, 100); 
        
        if (!concursos || concursos.length === 0) {
            container.innerHTML = '<div class="alert alert-warning">Carregando base histórica de concursos...</div>';
            return;
        }
        
        let selectOptions = concursos.map((c, i) => {
            let label = `Concurso #${c.concurso} (${c.data || 'Data N/A'})`;
            if (i === 0) label += " - Atual";
            return `<option value="${c.concurso}">${label}</option>`;
        }).join('');

        const html = `
            <div class="card shadow-sm border-0 mt-3" id="painel-analise-super-bilhete">
                <div class="card-header text-white px-3 py-2 d-flex justify-content-between align-items-center" style="background: linear-gradient(135deg, #1f2937 0%, #111827 100%);">
                    <span class="fw-bold"><i class="fas fa-chart-pie text-warning"></i> Desempenho Histórico do Super Bilhete</span>
                    <select id="select-concurso-super-bilhete" class="form-select form-select-sm w-auto bg-dark text-white border-secondary" onchange="SimuladorEliteAnalise.analisarSuperBilhete()">
                        ${selectOptions}
                    </select>
                </div>
                <div class="card-body bg-light p-3" id="resultado-analise-super-bilhete">
                    <!-- Preenchido via JS -->
                </div>
            </div>
            
            <!-- NOVO: Histórico Completo do Super Bilhete -->
            <div id="historico-completo-super-bilhete" class="mt-4" style="display: none;"></div>
        `;

        container.innerHTML = html;
        container.style.display = 'block';
        
        // Executa a primeira análise logo na inicialização
        this.analisarSuperBilhete();
    },

    analisarSuperBilhete() {
        // Encontrar o super bilhete na variável do SimuladorEliteManager
        if (!window.SimuladorEliteManager || !window.SimuladorEliteManager.jogos || window.SimuladorEliteManager.jogos.length < 11) {
            document.getElementById('resultado-analise-super-bilhete').innerHTML = '<div class="alert alert-warning py-2 mb-0">Super Bilhete ainda não gerado. Clique em "Super Bilhete" primeiro.</div>';
            return;
        }

        const superBilhete = window.SimuladorEliteManager.jogos[10]; // A 11ª aposta
        if (!superBilhete || superBilhete.length === 0) {
            document.getElementById('resultado-analise-super-bilhete').innerHTML = '<div class="alert alert-warning py-2 mb-0">Super Bilhete vazio.</div>';
            return;
        }

        const select = document.getElementById('select-concurso-super-bilhete');
        if (!select) return;

        const concursoId = parseInt(select.value, 10);
        
        const concursos = this.getConcursos();
        const concursoSelecionado = concursos.find(c => c.concurso === concursoId);

        if (!concursoSelecionado) {
            document.getElementById('resultado-analise-super-bilhete').innerHTML = '<div class="alert alert-warning py-2 mb-0">Concurso selecionado não encontrado.</div>';
            return;
        }

        const resultado = concursoSelecionado.numeros_ordenados;

        // Lógica de Comparação
        const acertos = superBilhete.filter(n => resultado.includes(n));
        const ausentes = superBilhete.filter(n => !resultado.includes(n));
        const percentual = ((acertos.length / resultado.length) * 100).toFixed(0);

        // Indicadores e Insights
        let statusHtml = '';
        if (acertos.length >= 6) {
            statusHtml = `<span class="badge bg-success" style="font-size: 14px; padding: 8px 12px;"><i class="fas fa-fire"></i> Excelente Compatibilidade</span>`;
        } else if (acertos.length >= 4) {
            statusHtml = `<span class="badge bg-warning text-dark" style="font-size: 14px; padding: 8px 12px;"><i class="fas fa-exclamation-triangle"></i> Compatibilidade Média</span>`;
        } else {
            statusHtml = `<span class="badge bg-danger" style="font-size: 14px; padding: 8px 12px;"><i class="fas fa-snowflake"></i> Baixa Compatibilidade</span>`;
        }

        // Formatação HTML das Dezenas
        const dezenasSuperBilheteHtml = superBilhete.map(n => {
            const hit = acertos.includes(n);
            return `<span class="badge ${hit ? 'bg-success' : 'bg-secondary'} me-1 mb-1" style="font-size: 14px; width: 30px; display: inline-block; text-align: center;">${String(n).padStart(2, '0')}</span>`;
        }).join('');

        const resultadoHtml = resultado.map(n => `<span class="badge bg-dark me-1" style="font-size: 13px;">${String(n).padStart(2, '0')}</span>`).join('');

        // Insigths extras: Pares/Impares
        const pares = superBilhete.filter(n => n % 2 === 0).length;
        const impares = superBilhete.length - pares;
        const perfilAgressividade = superBilhete.length > 10 ? 'Agressivo (Múltiplos Acertos)' : 'Conservador';

        const resultHtml = `
            <div class="row g-3">
                <div class="col-md-6 border-end">
                    <div class="mb-2">
                        <small class="text-muted text-uppercase fw-bold">Super Bilhete (${superBilhete.length} dezenas)</small><br>
                        <div class="mt-1">${dezenasSuperBilheteHtml}</div>
                    </div>
                    <div class="mt-3">
                        <small class="text-muted text-uppercase fw-bold">Resultado #${concursoSelecionado.concurso}</small><br>
                        <div class="mt-1">${resultadoHtml}</div>
                    </div>
                </div>
                
                <div class="col-md-6 ps-md-3">
                    <div class="d-flex justify-content-between align-items-start mb-3">
                        <div>
                            <h4 class="mb-0 text-dark fw-bold">${acertos.length} <small class="text-muted fs-6 fw-normal">Acertos</small></h4>
                            <div class="text-secondary" style="font-size: 13px;">Aproveitamento: ${percentual}% das sorteadas</div>
                        </div>
                        <div>
                            ${statusHtml}
                        </div>
                    </div>

                    <div class="row text-center mt-3 g-2">
                        <div class="col-6">
                            <div class="p-2 border rounded bg-white shadow-sm">
                                <div class="text-muted mb-1" style="font-size: 11px; text-transform: uppercase;">Padrão Par/Ímpar</div>
                                <div class="fw-bold text-dark" style="font-size: 13px;">${pares} Pares / ${impares} Ímpares</div>
                            </div>
                        </div>
                        <div class="col-6">
                            <div class="p-2 border rounded bg-white shadow-sm">
                                <div class="text-muted mb-1" style="font-size: 11px; text-transform: uppercase;">Perfil do Bilhete</div>
                                <div class="fw-bold text-primary" style="font-size: 13px;">${perfilAgressividade}</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <hr class="my-3 text-secondary">
            
            <div class="row g-2" style="font-size: 12px;">
                <div class="col-md-6">
                    <strong class="text-success"><i class="fas fa-check-circle"></i> Dezenas Coincidentes:</strong> 
                    <span class="text-dark">${acertos.length > 0 ? acertos.map(n => String(n).padStart(2, '0')).join(' • ') : 'Nenhuma'}</span>
                </div>
                <div class="col-md-6">
                    <strong class="text-danger"><i class="fas fa-times-circle"></i> Dezenas Ausentes:</strong> 
                    <span class="text-dark">${ausentes.length > 0 ? ausentes.map(n => String(n).padStart(2, '0')).join(' • ') : 'Nenhuma'}</span>
                </div>
            </div>
        `;

        document.getElementById('resultado-analise-super-bilhete').innerHTML = resultHtml;
        
        // Chamada para renderizar a tabela com o histórico de todos os concursos
        this.renderizarHistoricoCompleto(superBilhete);
    },

    mostrarModalConcursos(qtdAcertos, concursosStr) {
        let existing = document.getElementById('modal-concursos-resumo');
        if (existing) existing.remove();

        let badgesHtml = concursosStr.split(',').filter(x => x.trim() !== '').map(c => `<span class="badge bg-secondary border border-dark mb-1 me-1" style="font-size:14px;">#${c.trim()}</span>`).join('');
        if (badgesHtml === '') badgesHtml = '<span class="text-muted">Nenhum concurso encontrado.</span>';

        const modalHtml = `
            <div class="modal fade" id="modal-concursos-resumo" tabindex="-1" aria-hidden="true">
                <div class="modal-dialog modal-dialog-centered modal-dialog-scrollable">
                    <div class="modal-content border-0 shadow">
                        <div class="modal-header bg-dark text-white py-2">
                            <h6 class="modal-title mb-0"><i class="fas fa-trophy text-warning"></i> Concursos com ${qtdAcertos} Acertos</h6>
                            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body bg-light">
                            <p class="text-muted small mb-3">Lista de concursos onde este Super Bilhete atingiu exatos ${qtdAcertos} acertos:</p>
                            <div class="d-flex flex-wrap">
                                ${badgesHtml}
                            </div>
                        </div>
                        <div class="modal-footer py-1 bg-light border-top-0">
                            <button type="button" class="btn btn-secondary btn-sm" data-bs-dismiss="modal">Fechar</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        const modalElement = document.getElementById('modal-concursos-resumo');
        const modal = new bootstrap.Modal(modalElement);
        modal.show();
    },

    // ==========================================
    // MÓDULO 3: HISTÓRICO GERAL (SUPER BILHETE VS TODOS)
    // ==========================================
    renderizarHistoricoCompleto(superBilhete, filtroAcertos = null, sortBy = 'concurso', sortAsc = false) {
        const container = document.getElementById('historico-completo-super-bilhete');
        if (!container) return;

        const concursos = this.getConcursos();
        if (!concursos || concursos.length === 0) return;

        // Processar os dados de cada concurso contra o Super Bilhete
        let historicoData = concursos.map(c => {
            const resultado = c.numeros_ordenados;
            const acertosLista = superBilhete.filter(n => resultado.includes(n));
            const ausentesLista = superBilhete.filter(n => !resultado.includes(n));
            
            return {
                concurso: c.concurso,
                data: c.data || 'N/A',
                resultado: resultado,
                acertos: acertosLista,
                ausentes: ausentesLista,
                totalAcertos: acertosLista.length
            };
        });

        // Contagem Resumo Geral com armazenamento dos concursos
        const resumoAcertos = { 7: [], 6: [], 5: [], 4: [], 3: [], 2: [], 1: [], 0: [] };
        historicoData.forEach(d => {
            if (resumoAcertos[d.totalAcertos] !== undefined) {
                resumoAcertos[d.totalAcertos].push(d.concurso);
            }
        });

        // Aplicar filtro de botões se selecionado
        if (filtroAcertos !== null) {
            historicoData = historicoData.filter(d => d.totalAcertos === filtroAcertos);
        }

        // Ordenação Dinâmica
        historicoData.sort((a, b) => {
            let valA, valB;
            if (sortBy === 'concurso') {
                valA = a.concurso;
                valB = b.concurso;
            } else if (sortBy === 'acertos') {
                valA = a.totalAcertos;
                valB = b.totalAcertos;
            } else if (sortBy === 'ausentes') {
                valA = a.ausentes.length;
                valB = b.ausentes.length;
            } else {
                valA = a.concurso;
                valB = b.concurso;
            }

            if (valA < valB) return sortAsc ? -1 : 1;
            if (valA > valB) return sortAsc ? 1 : -1;
            return 0;
        });

        // Tabela HTML
        let tbodyHtml = '';
        
        if (historicoData.length === 0) {
            tbodyHtml = `<tr><td colspan="5" class="text-center text-muted py-3">Nenhum concurso encontrado com o filtro aplicado.</td></tr>`;
        } else {
            historicoData.forEach(d => {
                // Formatação das Dezenas do Sorteio (Destacando as que acertamos)
                const sorteioHtml = d.resultado.map(n => {
                    const hit = d.acertos.includes(n);
                    return `<span class="badge ${hit ? 'bg-success' : 'bg-dark'} me-1" style="font-size: 11px;">${String(n).padStart(2, '0')}</span>`;
                }).join('');

                // Formatação das Ausentes
                const ausentesHtml = d.ausentes.map(n => {
                    return `<span class="badge border border-danger text-danger me-1" style="font-size: 10px;">${String(n).padStart(2, '0')}</span>`;
                }).join('');

                // Cor do botão de acertos
                let badgeAcertos = 'bg-secondary';
                if (d.totalAcertos >= 6) badgeAcertos = 'bg-success';
                else if (d.totalAcertos >= 4) badgeAcertos = 'bg-warning text-dark';
                else if (d.totalAcertos <= 2) badgeAcertos = 'bg-danger';

                tbodyHtml += `
                    <tr>
                        <td class="text-center fw-bold text-muted align-middle" style="font-size: 12px;">#${d.concurso} <br><small class="fw-normal" style="font-size: 10px;">${d.data}</small></td>
                        <td class="align-middle">${sorteioHtml}</td>
                        <td class="align-middle">
                            ${d.acertos.length > 0 
                                ? d.acertos.map(n => `<span class="badge bg-success me-1" style="font-size: 11px;">${String(n).padStart(2, '0')}</span>`).join('') 
                                : '<span class="text-muted" style="font-size: 11px;">Nenhuma</span>'}
                        </td>
                        <td class="align-middle">${ausentesHtml || '-'}</td>
                        <td class="text-center align-middle">
                            <span class="badge ${badgeAcertos} px-2 py-1" style="font-size: 13px;">${d.totalAcertos}</span>
                        </td>
                    </tr>
                `;
            });
        }

        const btnClass = (val) => filtroAcertos === val ? 'btn-primary text-white fw-bold' : 'btn-outline-primary';

        // Placar Resumo (Scoreboard)
        const getTooltipAttr = (acertos) => {
            if (acertos === 7 && resumoAcertos[7].length > 0) {
                let sorted7 = [...resumoAcertos[7]].sort((a, b) => a - b);
                let detalhes = [];
                for (let i = 0; i < sorted7.length; i++) {
                    if (i === 0) {
                        detalhes.push(sorted7[i]);
                    } else {
                        let gap = sorted7[i] - sorted7[i-1];
                        detalhes.push(`${sorted7[i]} (gap: ${gap})`);
                    }
                }
                
                let mediaStr = '';
                if (sorted7.length > 1) {
                    let media = Math.round((sorted7[sorted7.length-1] - sorted7[0]) / (sorted7.length - 1));
                    mediaStr = ` | Média geral: 1 a cada ${media} concursos`;
                }

                return `title="Concursos: ${detalhes.join(' \u2192 ')}${mediaStr}" style="cursor: help;"`;
            }
            return '';
        };

        const getClickAttr = (acertos) => {
            if ((acertos === 6 || acertos === 5) && resumoAcertos[acertos].length > 0) {
                return `onclick="SimuladorEliteAnalise.mostrarModalConcursos(${acertos}, '${resumoAcertos[acertos].join(',')}')" style="cursor: pointer;" title="Clique para ver os concursos"`;
            }
            return '';
        };

        const scoreboardHtml = `
            <div class="row text-center g-2 p-3 bg-light border-bottom">
                <div class="col">
                    <div class="p-2 border rounded bg-white shadow-sm" style="border-left: 4px solid #198754 !important; transition: transform 0.2s;" onmouseover="this.style.transform='scale(1.02)'" onmouseout="this.style.transform='scale(1)'" ${getTooltipAttr(7)}>
                        <div class="text-muted text-uppercase" style="font-size: 10px;">7 Acertos</div>
                        <div class="fw-bold text-success" style="font-size: 20px;">${resumoAcertos[7].length}<small class="text-muted fw-normal" style="font-size: 11px;">x</small></div>
                        ${resumoAcertos[7].length > 0 ? '<div class="text-secondary" style="font-size: 9px;"><i class="fas fa-info-circle"></i> passe o mouse</div>' : ''}
                    </div>
                </div>
                <div class="col">
                    <div class="p-2 border rounded bg-white shadow-sm" style="border-left: 4px solid #198754 !important; transition: transform 0.2s;" onmouseover="this.style.transform='scale(1.02)'" onmouseout="this.style.transform='scale(1)'" ${getClickAttr(6)}>
                        <div class="text-muted text-uppercase" style="font-size: 10px;">6 Acertos</div>
                        <div class="fw-bold text-success" style="font-size: 20px;">${resumoAcertos[6].length}<small class="text-muted fw-normal" style="font-size: 11px;">x</small></div>
                        ${resumoAcertos[6].length > 0 ? '<div class="text-primary" style="font-size: 9px;"><i class="fas fa-hand-pointer"></i> ver concursos</div>' : ''}
                    </div>
                </div>
                <div class="col">
                    <div class="p-2 border rounded bg-white shadow-sm" style="border-left: 4px solid #ffc107 !important; transition: transform 0.2s;" onmouseover="this.style.transform='scale(1.02)'" onmouseout="this.style.transform='scale(1)'" ${getClickAttr(5)}>
                        <div class="text-muted text-uppercase" style="font-size: 10px;">5 Acertos</div>
                        <div class="fw-bold text-warning text-dark" style="font-size: 20px;">${resumoAcertos[5].length}<small class="text-muted fw-normal" style="font-size: 11px;">x</small></div>
                        ${resumoAcertos[5].length > 0 ? '<div class="text-primary" style="font-size: 9px;"><i class="fas fa-hand-pointer"></i> ver concursos</div>' : ''}
                    </div>
                </div>
                <div class="col">
                    <div class="p-2 border rounded bg-white shadow-sm" style="border-left: 4px solid #ffc107 !important;">
                        <div class="text-muted text-uppercase" style="font-size: 10px;">4 Acertos</div>
                        <div class="fw-bold text-warning text-dark" style="font-size: 20px;">${resumoAcertos[4].length}<small class="text-muted fw-normal" style="font-size: 11px;">x</small></div>
                    </div>
                </div>
                <div class="col">
                    <div class="p-2 border rounded bg-white shadow-sm" style="border-left: 4px solid #dc3545 !important;">
                        <div class="text-muted text-uppercase" style="font-size: 10px;">0 a 3</div>
                        <div class="fw-bold text-danger" style="font-size: 20px;">${resumoAcertos[0].length+resumoAcertos[1].length+resumoAcertos[2].length+resumoAcertos[3].length}<small class="text-muted fw-normal" style="font-size: 11px;">x</small></div>
                    </div>
                </div>
            </div>
        `;

        // Função auxiliar para gerar cabeçalhos ordenáveis
        const thSort = (colKey, label, width) => {
            const isCurrent = sortBy === colKey;
            const icon = isCurrent 
                ? (sortAsc ? '<i class="fas fa-sort-up ms-1 text-primary"></i>' : '<i class="fas fa-sort-down ms-1 text-primary"></i>') 
                : '<i class="fas fa-sort ms-1 text-muted opacity-50"></i>';
            return `<th class="text-center align-middle" width="${width}" style="cursor:pointer; user-select:none;" onclick="SimuladorEliteAnalise.renderizarHistoricoCompleto([${superBilhete.join(',')}], ${filtroAcertos}, '${colKey}', ${isCurrent ? !sortAsc : false})">${label} ${icon}</th>`;
        };

        const html = `
            <div class="card shadow-sm border-0 border-top border-primary border-3">
                <div class="card-header bg-white d-flex justify-content-between align-items-center py-3">
                    <h6 class="mb-0 fw-bold text-primary"><i class="fas fa-list-alt me-1"></i> Histórico Geral de Compatibilidade</h6>
                    <div class="btn-group btn-group-sm" role="group">
                        <button type="button" class="btn ${btnClass(null)}" onclick="SimuladorEliteAnalise.renderizarHistoricoCompleto([${superBilhete.join(',')}], null)">Todos</button>
                        <button type="button" class="btn ${btnClass(7)}" onclick="SimuladorEliteAnalise.renderizarHistoricoCompleto([${superBilhete.join(',')}], 7)">Filtrar 7</button>
                        <button type="button" class="btn ${btnClass(6)}" onclick="SimuladorEliteAnalise.renderizarHistoricoCompleto([${superBilhete.join(',')}], 6)">Filtrar 6</button>
                        <button type="button" class="btn ${btnClass(5)}" onclick="SimuladorEliteAnalise.renderizarHistoricoCompleto([${superBilhete.join(',')}], 5)">Filtrar 5</button>
                        <button type="button" class="btn ${btnClass(4)}" onclick="SimuladorEliteAnalise.renderizarHistoricoCompleto([${superBilhete.join(',')}], 4)">Filtrar 4</button>
                    </div>
                </div>
                ${scoreboardHtml}
                <div class="card-body p-0">
                    <div class="table-responsive" style="max-height: 400px; overflow-y: auto;">
                        <table class="table table-hover table-bordered mb-0" style="font-size: 13px;">
                            <thead class="table-light sticky-top" style="z-index: 1; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                                <tr>
                                    ${thSort('concurso', 'Concurso', '10%')}
                                    <th class="text-center align-middle" width="30%">Dezenas Sorteadas (Real)</th>
                                    ${thSort('acertos', 'Nossas Coincidentes <i class="fas fa-check text-success"></i>', '25%')}
                                    ${thSort('ausentes', 'Nossas Ausentes <i class="fas fa-times text-danger"></i>', '25%')}
                                    ${thSort('acertos', 'Acertos', '10%')}
                                </tr>
                            </thead>
                            <tbody>
                                ${tbodyHtml}
                            </tbody>
                        </table>
                    </div>
                </div>
                <div class="card-footer bg-light text-muted text-center" style="font-size: 11px;">
                    Exibindo ${historicoData.length} concurso(s) ${filtroAcertos !== null ? `com exatos ${filtroAcertos} acertos` : 'no total'}.
                </div>
            </div>
        `;

        container.innerHTML = html;
        container.style.display = 'block';
    }
};

// Globalizar
window.SimuladorEliteAnalise = SimuladorEliteAnalise;
