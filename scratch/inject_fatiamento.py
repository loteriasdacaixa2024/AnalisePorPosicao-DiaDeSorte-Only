import os

file_path = r"D:\Loterias\AnalisePorPosicao-DiaDeSorte-Only\templates\gerador_especial.html"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Nav Button
nav_target = """        <button id="btn-aba-ciclo_posicional" class="btn btn-outline-dark px-4 py-2"
            style="font-weight: bold; font-size: 16px;" onclick="mostrarAba('ciclo_posicional')">
            <i class="fas fa-bullseye"></i> 8. Ciclo Posicional
        </button>"""
nav_replacement = nav_target + """
        <button id="btn-aba-fatiamento" class="btn btn-outline-info px-4 py-2"
            style="font-weight: bold; font-size: 16px;" onclick="mostrarAba('fatiamento')">
            <i class="fas fa-cubes"></i> 9. Matriz de Dígitos (Fatiamento)
        </button>"""
content = content.replace(nav_target, nav_replacement)

# 2. Tab HTML
tab_target = """        <!-- ========================================== -->
        <!-- ABA 9: BATALHA DE GERADORES                -->"""
tab_html = """
        <!-- ========================================== -->
        <!-- ABA 9: MATRIZ DE DÍGITOS (FATIAMENTO)      -->
        <!-- ========================================== -->
        <div id="fatiamento" style="display: none;">
            <div class="gerador-especial-container" style="max-width: 1200px; margin: 0 auto; padding: 20px;">
                <h2 class="mt-2" style="color: #0dcaf0;"><i class="fas fa-cubes"></i> Gerador Fatiamento Numérico</h2>
                <p class="text-muted mb-4">Geração de apostas baseadas no limite de aparições matemáticas de cada dígito por concurso (O Raio-X).</p>

                <div class="row">
                    <div class="col-md-3">
                        <div class="card shadow-sm border-0 mb-4" style="border-top: 5px solid #0dcaf0 !important;">
                            <div class="card-header bg-info text-white fw-bold">
                                <i class="fas fa-filter"></i> Limites de Dígitos
                            </div>
                            <div class="card-body bg-light p-2" style="font-size: 13px;">
                                <p class="text-muted mb-2"><small>Defina o teto (máx.) que cada dígito pode aparecer na mesma aposta.</small></p>
                                <div class="row g-1">
                                    <div class="col-6"><label>Díg 0:</label><input type="number" id="fat_dig_0" class="form-control form-control-sm" value="2" min="0" max="7"></div>
                                    <div class="col-6"><label>Díg 1:</label><input type="number" id="fat_dig_1" class="form-control form-control-sm border-primary fw-bold" value="4" min="0" max="7"></div>
                                    <div class="col-6"><label>Díg 2:</label><input type="number" id="fat_dig_2" class="form-control form-control-sm border-primary fw-bold" value="3" min="0" max="7"></div>
                                    <div class="col-6"><label>Díg 3:</label><input type="number" id="fat_dig_3" class="form-control form-control-sm" value="2" min="0" max="7"></div>
                                    <div class="col-6"><label>Díg 4:</label><input type="number" id="fat_dig_4" class="form-control form-control-sm border-warning" value="1" min="0" max="7"></div>
                                    <div class="col-6"><label>Díg 5:</label><input type="number" id="fat_dig_5" class="form-control form-control-sm border-warning" value="1" min="0" max="7"></div>
                                    <div class="col-6"><label>Díg 6:</label><input type="number" id="fat_dig_6" class="form-control form-control-sm" value="2" min="0" max="7"></div>
                                    <div class="col-6"><label>Díg 7:</label><input type="number" id="fat_dig_7" class="form-control form-control-sm border-warning" value="1" min="0" max="7"></div>
                                    <div class="col-6"><label>Díg 8:</label><input type="number" id="fat_dig_8" class="form-control form-control-sm border-warning" value="1" min="0" max="7"></div>
                                    <div class="col-6"><label>Díg 9:</label><input type="number" id="fat_dig_9" class="form-control form-control-sm" value="2" min="0" max="7"></div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="col-md-9">
                        <div class="card shadow-sm border-0 mb-4" style="border-top: 5px solid #198754 !important;">
                            <div class="card-header bg-success text-white fw-bold">
                                <i class="fas fa-cogs"></i> Configurações Base
                            </div>
                            <div class="card-body bg-light">
                                <div class="row g-3">
                                    <div class="col-md-4">
                                        <label class="form-label fw-bold">Paridade (P/I):</label>
                                        <select id="fat_paridade" class="form-select">
                                            <option value="livre">Livre (Qualquer)</option>
                                            <option value="equilibrado" selected>Equilibrado (3/4 ou 4/3 se 7 dez)</option>
                                            <option value="mais_pares">Mais Pares</option>
                                            <option value="mais_impares">Mais Ímpares</option>
                                        </select>
                                    </div>
                                    <div class="col-md-4">
                                        <label class="form-label fw-bold">Dezenas / Aposta:</label>
                                        <input type="number" id="fat_dezenas" class="form-control" value="7" min="7" max="15">
                                    </div>
                                    <div class="col-md-4">
                                        <label class="form-label fw-bold">Qtd Apostas:</label>
                                        <input type="number" id="fat_qtd_apostas" class="form-control" value="10" min="1" max="1000">
                                    </div>
                                    <div class="col-md-12">
                                        <label class="form-label fw-bold">Mês da Sorte:</label>
                                        <select id="fat_mes" class="form-select">
                                            <option value="aleatorio" selected>Aleatório</option>
                                            <option value="1">Janeiro</option>
                                            <option value="2">Fevereiro</option>
                                            <option value="3">Março</option>
                                            <option value="4">Abril</option>
                                            <option value="5">Maio</option>
                                            <option value="6">Junho</option>
                                            <option value="7">Julho</option>
                                            <option value="8">Agosto</option>
                                            <option value="9">Setembro</option>
                                            <option value="10">Outubro</option>
                                            <option value="11">Novembro</option>
                                            <option value="12">Dezembro</option>
                                        </select>
                                    </div>
                                </div>

                                <div class="mt-4 text-center">
                                    <button class="btn btn-info btn-lg px-5 shadow fw-bold text-white" onclick="gerarFatiamento()">
                                        <i class="fas fa-play"></i> GERAR APOSTAS FATIADAS
                                    </button>
                                </div>
                            </div>
                        </div>

                        <!-- RESULTADOS -->
                        <div class="card shadow-sm border-0" id="res_fat_card" style="display:none;">
                            <div class="card-header bg-dark text-white fw-bold d-flex justify-content-between align-items-center">
                                <span><i class="fas fa-list-ol"></i> Apostas Geradas</span>
                                <div>
                                    <button class="btn btn-sm btn-light fw-bold" onclick="exportarFatiamentoTXT()"><i class="fas fa-download"></i> TXT</button>
                                </div>
                            </div>
                            <div class="card-body bg-light">
                                <p class="mb-2 p-2 bg-white border rounded">
                                    <strong>Resumo:</strong> Foram geradas <span id="res_fat_qtd" class="text-success fw-bold"></span> apostas após <span id="res_fat_tentativas" class="text-danger fw-bold"></span> tentativas internas do motor.
                                </p>
                                <div class="table-responsive" style="max-height: 400px; overflow-y: auto;">
                                    <table class="table table-bordered table-sm text-center bg-white mb-0" id="tabela_fat">
                                        <thead class="table-info sticky-top">
                                            <tr>
                                                <th style="width: 50px;">#</th>
                                                <th>Dezenas da Aposta</th>
                                                <th style="width: 120px;">Mês</th>
                                            </tr>
                                        </thead>
                                        <tbody id="tbody_fat"></tbody>
                                    </table>
                                </div>

                                <div class="text-center mt-4 d-flex justify-content-center gap-2">
                                    <button class="btn btn-lg btn-success fw-bold px-4 shadow" onclick="enviarFatParaConferencia()">
                                        <i class="fas fa-check-double"></i> ENVIAR PARA CONFERÊNCIA AGORA
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
""" + tab_target
content = content.replace(tab_target, tab_html)

# 3. JS display logic
js1_target = "        let cicloPosicionalEl = document.getElementById('ciclo_posicional');\n        if (cicloPosicionalEl) cicloPosicionalEl.style.display = (aba === 'ciclo_posicional') ? 'block' : 'none';"
js1_repl = js1_target + "\n\n        let fatiamentoEl = document.getElementById('fatiamento');\n        if (fatiamentoEl) fatiamentoEl.style.display = (aba === 'fatiamento') ? 'block' : 'none';"
content = content.replace(js1_target, js1_repl)

# 4. JS declaration
js2_target = "        let btn_ciclo = document.getElementById('btn-aba-ciclo_posicional');\n        let btn_batalha = document.getElementById('btn-aba-batalha');"
js2_repl = "        let btn_ciclo = document.getElementById('btn-aba-ciclo_posicional');\n        let btn_fatiamento = document.getElementById('btn-aba-fatiamento');\n        let btn_batalha = document.getElementById('btn-aba-batalha');"
content = content.replace(js2_target, js2_repl)

# 5. JS Outline reset
js3_target = "        if (btn_ciclo) { btn_ciclo.className = 'btn btn-outline-dark px-4 py-2'; btn_ciclo.style.color = '#000'; }\n        if (btn_batalha) { btn_batalha.className = 'btn btn-outline-danger px-4 py-2'; btn_batalha.style.color = '#000'; }"
js3_repl = "        if (btn_ciclo) { btn_ciclo.className = 'btn btn-outline-dark px-4 py-2'; btn_ciclo.style.color = '#000'; }\n        if (btn_fatiamento) { btn_fatiamento.className = 'btn btn-outline-info px-4 py-2'; btn_fatiamento.style.color = '#000'; }\n        if (btn_batalha) { btn_batalha.className = 'btn btn-outline-danger px-4 py-2'; btn_batalha.style.color = '#000'; }"
content = content.replace(js3_target, js3_repl)

# 6. JS Active State
js4_target = "        } else if (aba === 'ciclo_posicional') {\n            if (btn_ciclo) { btn_ciclo.className = 'btn btn-dark px-4 py-2'; btn_ciclo.style.color = '#fff'; }\n        } else if (aba === 'batalha') {"
js4_repl = "        } else if (aba === 'ciclo_posicional') {\n            if (btn_ciclo) { btn_ciclo.className = 'btn btn-dark px-4 py-2'; btn_ciclo.style.color = '#fff'; }\n        } else if (aba === 'fatiamento') {\n            if (btn_fatiamento) { btn_fatiamento.className = 'btn btn-info px-4 py-2'; btn_fatiamento.style.color = '#fff'; }\n        } else if (aba === 'batalha') {"
content = content.replace(js4_target, js4_repl)

# 7. Add Functions for Fatiamento globally in JS
js_functions = """
    // --- Lógica Fatiamento ---
    let globalFatApostas = [];
    
    function gerarFatiamento() {
        const btn = document.querySelector('#fatiamento button.btn-info');
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Gerando...';
        btn.disabled = true;

        const payload = {
            qtd_apostas: document.getElementById('fat_qtd_apostas').value,
            dezenas_por_jogo: document.getElementById('fat_dezenas').value,
            filtros: {
                paridade: document.getElementById('fat_paridade').value
            },
            limites: {
                '0': document.getElementById('fat_dig_0').value,
                '1': document.getElementById('fat_dig_1').value,
                '2': document.getElementById('fat_dig_2').value,
                '3': document.getElementById('fat_dig_3').value,
                '4': document.getElementById('fat_dig_4').value,
                '5': document.getElementById('fat_dig_5').value,
                '6': document.getElementById('fat_dig_6').value,
                '7': document.getElementById('fat_dig_7').value,
                '8': document.getElementById('fat_dig_8').value,
                '9': document.getElementById('fat_dig_9').value
            }
        };

        fetch('/api/gerador-especial/gerar-fatiamento', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
        })
        .then(r => r.json())
        .then(data => {
            btn.innerHTML = '<i class="fas fa-play"></i> GERAR APOSTAS FATIADAS';
            btn.disabled = false;
            
            if (data.error || data.sucesso === false) {
                alert("Erro: " + (data.mensagem || data.error));
                return;
            }
            
            globalFatApostas = data.apostas;
            
            // Format array with months
            const selMes = document.getElementById('fat_mes').value;
            const nomesMes = ['', 'Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'];
            
            globalFatApostas = globalFatApostas.map(ap => {
                let mNum = selMes === 'aleatorio' ? Math.floor(Math.random() * 12) + 1 : parseInt(selMes);
                return {
                    dezenas: ap,
                    mes_num: mNum,
                    mes_nome: nomesMes[mNum]
                };
            });

            document.getElementById('res_fat_qtd').innerText = data.qtd_gerada;
            document.getElementById('res_fat_tentativas').innerText = data.tentativas;
            document.getElementById('res_fat_card').style.display = 'block';

            let tbody = document.getElementById('tbody_fat');
            tbody.innerHTML = '';
            globalFatApostas.forEach((ap, idx) => {
                let d = ap.dezenas.map(x => x.toString().padStart(2, '0')).join(' - ');
                tbody.innerHTML += `<tr><td>${idx+1}</td><td class="fw-bold">${d}</td><td><span class="badge bg-secondary">${ap.mes_nome}</span></td></tr>`;
            });
            
            // Re-renderizar Batalha se ela estiver rodando
            atualizarStatusGeradores('Fatiamento Num.', data.qtd_gerada + " apostas");
        })
        .catch(e => {
            btn.innerHTML = '<i class="fas fa-play"></i> GERAR APOSTAS FATIADAS';
            btn.disabled = false;
            alert("Erro de conexão.");
        });
    }

    function exportarFatiamentoTXT() {
        if (!globalFatApostas || globalFatApostas.length === 0) return;
        let conteudo = "";
        globalFatApostas.forEach(ap => {
            let nums = ap.dezenas.map(x => x.toString().padStart(2, '0')).join(' ');
            conteudo += `${nums} ${ap.mes_nome}\\n`;
        });
        baixarArquivo(conteudo, 'Gerador_Fatiamento_Numerico.txt', 'text/plain');
    }

    function enviarFatParaConferencia() {
        if (!globalFatApostas || globalFatApostas.length === 0) return;
        let btn = document.querySelector('#res_fat_card button.btn-success');
        let oldHTML = btn.innerHTML;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Enviando...';
        btn.disabled = true;

        fetch('/api/batalha/salvar-sessao', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                gerador_nome: 'Fatiamento Numérico',
                apostas: globalFatApostas
            })
        })
        .then(response => response.json())
        .then(data => {
            btn.innerHTML = '<i class="fas fa-check"></i> ENVIADO COM SUCESSO!';
            btn.classList.replace('btn-success', 'btn-dark');
            setTimeout(() => {
                btn.innerHTML = oldHTML;
                btn.classList.replace('btn-dark', 'btn-success');
                btn.disabled = false;
                window.open('/central-conferencias#pane-conferencia-historica', '_blank');
            }, 1500);
        });
    }
"""

js_inject_target = "    // ==========================================\n    // FUNÇÕES COMPARTILHADAS / UTILITÁRIOS\n    // =========================================="
content = content.replace(js_inject_target, js_functions + "\n\n" + js_inject_target)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("INJECTION COMPLETE.")
