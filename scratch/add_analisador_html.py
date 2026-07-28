content = open('templates/gerador_especial.html', 'r', encoding='utf-8').read()

# ─────────────────────────────────────────────────────────────────────────────
# 1. Add Tab Button (after fatiamento button, before </div> of nav)
# ─────────────────────────────────────────────────────────────────────────────
NAV_OLD = """        <button id="btn-aba-fatiamento" class="btn btn-outline-info px-4 py-2"
            style="font-weight: bold; font-size: 16px;" onclick="mostrarAba('fatiamento')">
            <i class="fas fa-cubes"></i> 9. Matriz de D\u00edgitos (Fatiamento)
        </button>

    </div>"""

NAV_NEW = """        <button id="btn-aba-fatiamento" class="btn btn-outline-info px-4 py-2"
            style="font-weight: bold; font-size: 16px;" onclick="mostrarAba('fatiamento')">
            <i class="fas fa-cubes"></i> 9. Matriz de D\u00edgitos (Fatiamento)
        </button>
        <button id="btn-aba-analisador" class="btn btn-outline-purple px-4 py-2"
            style="font-weight: bold; font-size: 16px; border-color: #6f42c1; color: #6f42c1;" onclick="mostrarAba('analisador')">
            <i class="fas fa-microscope"></i> 10. Analisador em Massa
        </button>

    </div>"""

if NAV_OLD in content:
    content = content.replace(NAV_OLD, NAV_NEW, 1)
    print("NAV button added OK")
else:
    print("NAV OLD NOT FOUND")

# ─────────────────────────────────────────────────────────────────────────────
# 2. Add Tab Pane (before closing of geradoresTabsContent)
#    Insert just before the last </div> + {% endblock %}
# ─────────────────────────────────────────────────────────────────────────────
PANE_ANCHOR = "    </div>\n\n</div>\n{% endblock %}"

ANALISADOR_PANE = """
        <!-- ========================================== -->
        <!-- ABA 10: ANALISADOR DE APOSTAS EM MASSA     -->
        <!-- ========================================== -->
        <div id="analisador" class="aba-pane" style="display:none;">
            <div class="card shadow-sm border-0 mb-4" style="border-top: 4px solid #6f42c1 !important;">
                <!-- HEADER -->
                <div class="card-header d-flex align-items-center justify-content-between py-3" style="background: linear-gradient(135deg,#6f42c1,#8a63d2); color:#fff;">
                    <div>
                        <h5 class="mb-0 fw-bold"><i class="fas fa-microscope me-2"></i> Analisador de Apostas em Massa</h5>
                        <small class="opacity-75">Importe centenas ou milhares de apostas e analise automaticamente por grupo associativo</small>
                    </div>
                    <span id="analis_counter_badge" class="badge bg-white text-dark" style="font-size:14px; display:none;">
                        <i class="fas fa-ticket-alt text-purple"></i> <span id="analis_total_loaded">0</span> apostas
                    </span>
                </div>

                <div class="card-body p-4">
                    <!-- DROP ZONE + TEXTAREA -->
                    <div id="analis_dropzone"
                         class="rounded-3 border-3 border-dashed text-center py-5 mb-4 position-relative"
                         style="border: 3px dashed #6f42c1; background: linear-gradient(135deg,#f8f5ff,#fff); cursor:pointer; transition: all .3s;"
                         ondragover="analisDropOver(event)" ondragleave="analisDropLeave(event)" ondrop="analisDropFile(event)"
                         onclick="document.getElementById('analis_file_input').click()">
                        <i class="fas fa-cloud-upload-alt mb-3" style="font-size:3rem; color:#6f42c1; opacity:.7;"></i>
                        <h5 class="fw-bold text-purple mb-1" style="color:#6f42c1;">Arraste um arquivo .txt aqui</h5>
                        <p class="text-muted mb-3" style="font-size:13px;">ou clique para selecionar · ou cole diretamente abaixo</p>
                        <span class="badge" style="background:#6f42c1; font-size:12px; padding:6px 16px;">Sem limite de apostas</span>
                        <input type="file" id="analis_file_input" accept=".txt" style="display:none;" onchange="analisLoadFile(event)">
                    </div>

                    <div class="mb-3">
                        <label class="form-label fw-bold text-purple" style="color:#6f42c1;"><i class="fas fa-paste me-1"></i> Cole ou edite as apostas aqui:</label>
                        <textarea id="analis_textarea" class="form-control font-monospace"
                                  rows="8"
                                  placeholder="01 02 03 04 05 06 07 Jan&#10;08 09 10 11 12 13 14 Mar&#10;..."
                                  style="font-size:13px; border-color:#6f42c1; resize:vertical;"></textarea>
                        <div class="d-flex justify-content-between mt-2">
                            <small class="text-muted"><i class="fas fa-info-circle me-1"></i>Formato: <code>D1 D2 D3 D4 D5 D6 D7 Mes</code> &mdash; uma aposta por linha</small>
                            <small id="analis_line_count" class="text-muted">0 linhas</small>
                        </div>
                    </div>

                    <!-- ACTION BUTTONS -->
                    <div class="d-flex gap-2 flex-wrap mb-4">
                        <button class="btn btn-lg fw-bold px-5" style="background:#6f42c1; color:#fff;" onclick="analisProcessar()">
                            <i class="fas fa-play-circle me-2"></i> ANALISAR APOSTAS
                        </button>
                        <button class="btn btn-outline-secondary" onclick="analisLimpar()">
                            <i class="fas fa-trash-alt me-1"></i> Limpar
                        </button>
                        <button class="btn btn-outline-secondary" onclick="analisProcessar()">
                            <i class="fas fa-sync-alt me-1"></i> Re-analisar
                        </button>
                    </div>

                    <!-- LOADING -->
                    <div id="analis_loading" style="display:none;" class="text-center py-4">
                        <div class="spinner-border" style="color:#6f42c1; width:3rem; height:3rem;"></div>
                        <p class="mt-3 fw-bold" style="color:#6f42c1;">Analisando apostas...</p>
                    </div>

                    <!-- RESULTADO SECTION -->
                    <div id="analis_resultado" style="display:none;">

                        <!-- STATS CARDS -->
                        <div class="row g-3 mb-4" id="analis_stats_row">
                            <div class="col-6 col-md-3">
                                <div class="card text-center border-0 shadow-sm h-100" style="border-top:3px solid #6f42c1!important;">
                                    <div class="card-body py-3">
                                        <div class="fw-bold" style="font-size:2rem; color:#6f42c1;" id="stat_total">0</div>
                                        <div class="text-muted" style="font-size:12px;">Total de Apostas</div>
                                    </div>
                                </div>
                            </div>
                            <div class="col-6 col-md-3">
                                <div class="card text-center border-0 shadow-sm h-100" style="border-top:3px solid #198754!important;">
                                    <div class="card-body py-3">
                                        <div class="fw-bold text-success" style="font-size:2rem;" id="stat_ok">0</div>
                                        <div class="text-muted" style="font-size:12px;">\u2705 Apostas V\u00e1lidas</div>
                                    </div>
                                </div>
                            </div>
                            <div class="col-6 col-md-3">
                                <div class="card text-center border-0 shadow-sm h-100" style="border-top:3px solid #dc3545!important;">
                                    <div class="card-body py-3">
                                        <div class="fw-bold text-danger" style="font-size:2rem;" id="stat_err">0</div>
                                        <div class="text-muted" style="font-size:12px;">\u274c Com Erros</div>
                                    </div>
                                </div>
                            </div>
                            <div class="col-6 col-md-3">
                                <div class="card text-center border-0 shadow-sm h-100" style="border-top:3px solid #fd7e14!important;">
                                    <div class="card-body py-3">
                                        <div class="fw-bold text-warning" style="font-size:2rem;" id="stat_espalhamento">0</div>
                                        <div class="text-muted" style="font-size:12px;">\ud83c\udf10 M\u00e9dia de Grupos</div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- MES STATS -->
                        <div class="card border-0 shadow-sm mb-4">
                            <div class="card-header fw-bold" style="background:#6f42c1; color:#fff; font-size:13px;">
                                <i class="fas fa-calendar-alt me-2"></i> Distribui\u00e7\u00e3o por M\u00eas da Sorte
                            </div>
                            <div class="card-body py-3">
                                <div id="analis_mes_stats" class="d-flex flex-wrap gap-2 justify-content-center"></div>
                            </div>
                        </div>

                        <!-- GRUPOS STATS -->
                        <div class="card border-0 shadow-sm mb-4">
                            <div class="card-header fw-bold" style="background:#6f42c1; color:#fff; font-size:13px;">
                                <i class="fas fa-layer-group me-2"></i> Presen\u00e7a por Grupo (total de apari\u00e7\u00f5es)
                            </div>
                            <div class="card-body py-3">
                                <div id="analis_grupo_stats" class="d-flex flex-wrap gap-2 justify-content-center"></div>
                            </div>
                        </div>

                        <!-- PAGINATION CONTROLS -->
                        <div class="d-flex justify-content-between align-items-center mb-2">
                            <div class="fw-bold" style="color:#6f42c1; font-size:14px;">
                                <i class="fas fa-table me-1"></i> Tabela de Apostas
                                <span class="badge bg-secondary ms-2" id="analis_paginfo">p\u00e1g. 1</span>
                            </div>
                            <div class="d-flex gap-2 align-items-center">
                                <label class="text-muted" style="font-size:12px;">Apostas por p\u00e1g:</label>
                                <select id="analis_perpage" class="form-select form-select-sm" style="width:80px;" onchange="analisRenderPage(1)">
                                    <option value="50">50</option>
                                    <option value="100" selected>100</option>
                                    <option value="250">250</option>
                                    <option value="500">500</option>
                                </select>
                                <button class="btn btn-sm btn-outline-secondary" onclick="analisRenderPage(analisCurrentPage-1)" id="btn_prev_pag">\u2039 Ant</button>
                                <button class="btn btn-sm btn-outline-secondary" onclick="analisRenderPage(analisCurrentPage+1)" id="btn_next_pag">Pr\u00f3x \u203a</button>
                            </div>
                        </div>

                        <!-- RESULTS TABLE -->
                        <div class="table-responsive rounded-3 shadow-sm" style="max-height:600px; overflow-y:auto;">
                            <table class="table table-sm table-bordered mb-0 text-center" id="analis_tabela"
                                   style="font-size:12px; border-collapse:separate; border-spacing:0;">
                                <thead style="position:sticky; top:0; z-index:5; background:#6f42c1; color:#fff;">
                                    <tr>
                                        <th class="text-center py-2">#</th>
                                        <th class="text-center">DEZENAS</th>
                                        <th class="text-center">M\u00caS</th>
                                        <th class="text-center">G0</th>
                                        <th class="text-center">G1</th>
                                        <th class="text-center">G2</th>
                                        <th class="text-center">G3</th>
                                        <th class="text-center">G4</th>
                                        <th class="text-center">G5</th>
                                        <th class="text-center">G6</th>
                                        <th class="text-center">G7</th>
                                        <th class="text-center">G8</th>
                                        <th class="text-center">G9</th>
                                        <th class="text-center">G\u00caM</th>
                                        <th class="text-center">GRUPOS ATIVOS</th>
                                        <th class="text-center">STATUS</th>
                                    </tr>
                                </thead>
                                <tbody id="analis_tbody">
                                </tbody>
                            </table>
                        </div>

                        <!-- BOTTOM PAGINATION -->
                        <div class="d-flex justify-content-center gap-2 mt-3" id="analis_pagination_bottom"></div>

                    </div><!-- /analis_resultado -->
                </div><!-- /card-body -->
            </div><!-- /card -->
        </div><!-- /aba analisador -->
"""

if PANE_ANCHOR in content:
    content = content.replace(PANE_ANCHOR, ANALISADOR_PANE + "\n    </div>\n\n</div>\n{% endblock %}", 1)
    print("PANE added OK")
else:
    print("PANE ANCHOR NOT FOUND")
    idx = content.rfind('</div>')
    print("Last </div> at:", idx)

open('templates/gerador_especial.html', 'w', encoding='utf-8').write(content)
print("Done - HTML saved")
