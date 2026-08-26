content = open('templates/gerador_especial.html', 'r', encoding='utf-8').read()

# The insertion anchor - right before the closing of the Tabs content div
ANCHOR = '\n</div> <!-- Fim Conte\u00fado Tabs -->\n</div> <!-- Fim Container Geral -->'

ANALISADOR_PANE = """
        <!-- ========================================== -->
        <!-- ABA 10: ANALISADOR DE APOSTAS EM MASSA     -->
        <!-- ========================================== -->
        <div id="analisador" class="aba-pane" style="display:none;">
            <div class="card shadow-sm border-0 mb-4" style="border-top: 4px solid #6f42c1 !important;">
                <div class="card-header d-flex align-items-center justify-content-between py-3" style="background: linear-gradient(135deg,#6f42c1,#8a63d2); color:#fff;">
                    <div>
                        <h5 class="mb-0 fw-bold"><i class="fas fa-microscope me-2"></i> Analisador de Apostas em Massa</h5>
                        <small class="opacity-75">Importe centenas ou milhares de apostas e analise automaticamente por grupo associativo</small>
                    </div>
                    <span id="analis_counter_badge" class="badge bg-white text-dark" style="font-size:14px; display:none;">
                        <i class="fas fa-ticket-alt" style="color:#6f42c1;"></i> <span id="analis_total_loaded">0</span> apostas
                    </span>
                </div>

                <div class="card-body p-4">
                    <!-- DROP ZONE -->
                    <div id="analis_dropzone"
                         class="rounded-3 text-center py-5 mb-4"
                         style="border: 3px dashed #6f42c1; background: linear-gradient(135deg,#f8f5ff,#fff); cursor:pointer; transition: all .3s;"
                         ondragover="analisDropOver(event)" ondragleave="analisDropLeave(event)" ondrop="analisDropFile(event)"
                         onclick="document.getElementById('analis_file_input').click()">
                        <i class="fas fa-cloud-upload-alt mb-3" style="font-size:3rem; color:#6f42c1; opacity:.7;"></i>
                        <h5 class="fw-bold mb-1" style="color:#6f42c1;">Arraste um arquivo .txt aqui</h5>
                        <p class="text-muted mb-3" style="font-size:13px;">ou clique para selecionar &bull; ou cole diretamente abaixo</p>
                        <span class="badge" style="background:#6f42c1; font-size:12px; padding:6px 16px;">Sem limite de apostas</span>
                        <input type="file" id="analis_file_input" accept=".txt" style="display:none;" onchange="analisLoadFile(event)">
                    </div>

                    <!-- TEXTAREA -->
                    <div class="mb-3">
                        <label class="form-label fw-bold" style="color:#6f42c1;"><i class="fas fa-paste me-1"></i> Cole ou edite as apostas aqui:</label>
                        <textarea id="analis_textarea" class="form-control font-monospace" rows="8"
                                  placeholder="01 02 03 04 05 06 07 Jan&#10;08 09 10 11 12 13 14 Mar&#10;..."
                                  oninput="analisContarLinhas()"
                                  style="font-size:13px; border-color:#6f42c1; resize:vertical;"></textarea>
                        <div class="d-flex justify-content-between mt-1">
                            <small class="text-muted"><i class="fas fa-info-circle me-1"></i>Formato: <code>D1 D2 D3 D4 D5 D6 D7 Mes</code> &mdash; uma aposta por linha</small>
                            <small id="analis_line_count" class="text-muted fw-bold">0 linhas</small>
                        </div>
                    </div>

                    <!-- BUTTONS -->
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

                    <!-- RESULTADO -->
                    <div id="analis_resultado" style="display:none;">

                        <!-- STAT CARDS -->
                        <div class="row g-3 mb-4">
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
                                        <div class="text-muted" style="font-size:12px;">&#10003; V\u00e1lidas</div>
                                    </div>
                                </div>
                            </div>
                            <div class="col-6 col-md-3">
                                <div class="card text-center border-0 shadow-sm h-100" style="border-top:3px solid #dc3545!important;">
                                    <div class="card-body py-3">
                                        <div class="fw-bold text-danger" style="font-size:2rem;" id="stat_err">0</div>
                                        <div class="text-muted" style="font-size:12px;">Com Erros</div>
                                    </div>
                                </div>
                            </div>
                            <div class="col-6 col-md-3">
                                <div class="card text-center border-0 shadow-sm h-100" style="border-top:3px solid #fd7e14!important;">
                                    <div class="card-body py-3">
                                        <div class="fw-bold text-warning" style="font-size:2rem;" id="stat_espalhamento">0</div>
                                        <div class="text-muted" style="font-size:12px;">M\u00e9dia de Grupos Ativos</div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- MES STATS -->
                        <div class="card border-0 shadow-sm mb-4">
                            <div class="card-header fw-bold py-2" style="background:#6f42c1; color:#fff; font-size:13px;">
                                <i class="fas fa-calendar-alt me-2"></i> Distribui\u00e7\u00e3o por M\u00eas da Sorte
                            </div>
                            <div class="card-body py-3">
                                <div id="analis_mes_stats" class="d-flex flex-wrap gap-2 justify-content-center"></div>
                            </div>
                        </div>

                        <!-- GRUPO STATS -->
                        <div class="card border-0 shadow-sm mb-4">
                            <div class="card-header fw-bold py-2" style="background:#6f42c1; color:#fff; font-size:13px;">
                                <i class="fas fa-layer-group me-2"></i> Presen\u00e7a por Grupo (total de apari\u00e7\u00f5es nas apostas)
                            </div>
                            <div class="card-body py-3">
                                <div id="analis_grupo_stats" class="d-flex flex-wrap gap-2 justify-content-center"></div>
                            </div>
                        </div>

                        <!-- PAGINATION CONTROLS -->
                        <div class="d-flex justify-content-between align-items-center mb-2">
                            <div class="fw-bold" style="color:#6f42c1; font-size:14px;">
                                <i class="fas fa-table me-1"></i> Tabela de Apostas
                                <span class="badge bg-secondary ms-2" id="analis_paginfo"></span>
                            </div>
                            <div class="d-flex gap-2 align-items-center">
                                <label class="text-muted" style="font-size:12px;">Por p\u00e1g.:</label>
                                <select id="analis_perpage" class="form-select form-select-sm" style="width:75px;" onchange="analisRenderPage(1)">
                                    <option value="50">50</option>
                                    <option value="100" selected>100</option>
                                    <option value="250">250</option>
                                    <option value="500">500</option>
                                </select>
                                <button class="btn btn-sm btn-outline-secondary" id="btn_prev_pag" onclick="analisRenderPage(analisCurrentPage-1)">&lsaquo; Ant</button>
                                <button class="btn btn-sm btn-outline-secondary" id="btn_next_pag" onclick="analisRenderPage(analisCurrentPage+1)">Pr&oacute;x &rsaquo;</button>
                            </div>
                        </div>

                        <!-- TABLE -->
                        <div class="table-responsive rounded-3 shadow-sm" style="max-height:600px; overflow-y:auto;">
                            <table class="table table-sm table-bordered mb-0 text-center align-middle" id="analis_tabela" style="font-size:12px;">
                                <thead style="position:sticky; top:0; z-index:5; background:#6f42c1; color:#fff;">
                                    <tr>
                                        <th class="text-center py-2" style="min-width:40px;">#</th>
                                        <th class="text-center" style="min-width:200px;">DEZENAS</th>
                                        <th class="text-center" style="min-width:80px;">M\u00caS</th>
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
                                        <th class="text-center" style="min-width:100px;">GRUPOS ATIVOS</th>
                                        <th class="text-center" style="min-width:80px;">STATUS</th>
                                    </tr>
                                </thead>
                                <tbody id="analis_tbody"></tbody>
                            </table>
                        </div>
                        <div class="d-flex justify-content-center gap-1 mt-3 flex-wrap" id="analis_pagination_bottom"></div>
                    </div><!-- /analis_resultado -->
                </div>
            </div>
        </div><!-- /aba analisador -->"""

if ANCHOR in content:
    content = content.replace(ANCHOR, ANALISADOR_PANE + ANCHOR, 1)
    open('templates/gerador_especial.html', 'w', encoding='utf-8').write(content)
    print("OK - aba HTML inserted")
else:
    # Try to find the anchor with different encoding
    idx = content.find('Fim Conte')
    print("Fim Conte at:", idx)
    print(repr(content[idx-5:idx+60]))
