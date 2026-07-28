import re
import os

file_path = 'templates/central_conferencias.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Remove the exact modal block
modal_match = re.search(r'<!-- Modal Panorama Histórico \(Top 3 ABS\) -->.*?<div class="modal fade" id="modalPanoramaHistorico".*?</div>\s*</div>\s*</div>\s*</div>', content, re.DOTALL)
if modal_match:
    content = content.replace(modal_match.group(0), '')
    print('Removed modal HTML.')
else:
    print('Failed to find exact modal match. Check the regex or file.')

# 2. Insert the new container
new_container_html = '''
        <!-- CONTAINER PANORAMA HISTÓRICO GLOBAL (FORA DO MODAL) -->
        <div id="container-panorama-global-page" class="card shadow-sm border-0 mt-4" style="display: none;">
            <div class="card-header bg-primary text-white border-0 d-flex justify-content-between align-items-center">
                <h5 class="mb-0 fw-bold"><i class="fas fa-trophy text-warning me-2"></i> Panorama Histórico de ABS</h5>
                <button type="button" class="btn-close btn-close-white" onclick="fecharPanoramaHistorico()"></button>
            </div>
            <div class="card-body p-4 bg-light">
                <!-- Progress Section -->
                <div id="panorama-progress-container">
                    <div class="text-center mb-3">
                        <div class="spinner-border text-primary" role="status" style="width: 3rem; height: 3rem;">
                            <span class="visually-hidden">Loading...</span>
                        </div>
                        <h5 class="mt-3 fw-bold text-primary" id="panorama-status-text">Analisando histórico global...</h5>
                        <p class="text-muted small">Isso pode levar alguns segundos dependendo do volume de dados.</p>
                    </div>
                    <div class="progress" style="height: 15px; border-radius: 10px;">
                        <div id="panorama-progress-bar" class="progress-bar progress-bar-striped progress-bar-animated bg-primary" role="progressbar" style="width: 0%">0%</div>
                    </div>
                </div>

                <!-- Result Section -->
                <div id="panorama-result-container" style="display: none;">
                    
                    <div class="row mb-4">
                        <div class="col-12">
                            <div class="card border-0 shadow-sm bg-white text-center p-3">
                                <h6 class="text-muted fw-bold mb-1">MÉDIA GERAL DO SEU HISTÓRICO ABS</h6>
                                <h2 class="text-primary fw-bold mb-0" id="panorama-media-geral">0.00</h2>
                                <small class="text-muted" id="panorama-total-apostas">Analisando 0 apostas em 0 concursos</small>
                            </div>
                        </div>
                    </div>

                    <h5 class="fw-bold text-center mb-4 text-dark">Top 3 Melhores Performances (Menor ABS)</h5>
                    
                    <div class="row d-flex justify-content-center align-items-end" id="panorama-podium" style="min-height: 200px;">
                        <!-- Injetado via JS -->
                    </div>
                    
                    <!-- Evolução Histórica Completa -->
                    <div class="mt-5 text-start">
                        <div class="d-flex justify-content-between align-items-center mb-3">
                            <h6 class="fw-bold text-muted mb-0"><i class="fas fa-history me-2"></i>Evolução do ABS (Histórico Completo)</h6>
                            <input type="text" id="filtro-evolucao" class="form-control shadow-sm border-0" placeholder="🔍 Filtrar concurso, data ou ABS..." onkeyup="filtrarEvolucao()" style="max-width: 300px; border-radius: 20px;">
                        </div>
                        <div class="table-responsive" style="border-radius: 8px; border: 1px solid #e0e0e0;">
                            <table class="table table-sm table-hover text-center align-middle mb-0" style="font-size: 0.9rem;" id="tabela-evolucao">
                                <thead class="table-light sticky-top" style="z-index: 1;">
                                    <tr>
                                        <th>Concurso</th>
                                        <th>Data</th>
                                        <th>Apostas</th>
                                        <th>ABS Médio</th>
                                    </tr>
                                </thead>
                                <tbody id="panorama-evolucao-tbody">
                                    <!-- Injetado via JS -->
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>
'''

insertion_target = '<!-- ABA NOVA: BACKTEST DE AUSENTES (ESCAPES)     -->'
insertion_idx = content.find(insertion_target)
if insertion_idx != -1:
    insert_pos = content.rfind('</div>', 0, insertion_idx)
    if insert_pos != -1:
        content = content[:insert_pos] + new_container_html + '\n        ' + content[insert_pos:]
        print('Inserted new container HTML.')
else:
    print('Failed to find insertion target.')

# 3. Update JS Functions
content = content.replace('if (!panoramaModalInstance) {', '// if (!panoramaModalInstance) {')
content = content.replace('panoramaModalInstance = new bootstrap.Modal(document.getElementById(\'modalPanoramaHistorico\'));', '//')
content = content.replace('panoramaModalInstance.show();', 'document.getElementById("container-panorama-global-page").scrollIntoView({behavior: "smooth"});')

content = content.replace('function abrirPanoramaHistorico() {', 'function abrirPanoramaHistorico() {\\n    document.getElementById("container-resultado-variancia").style.display = "none";\\n    document.getElementById("container-panorama-global-page").style.display = "block";')

js_funcs = '''
    function fecharPanoramaHistorico() {
        document.getElementById('container-panorama-global-page').style.display = 'none';
        document.getElementById('container-resultado-variancia').style.display = 'block';
    }

    function filtrarEvolucao() {
        const input = document.getElementById('filtro-evolucao');
        const filter = input.value.toUpperCase();
        const tbody = document.getElementById('panorama-evolucao-tbody');
        const trs = tbody.getElementsByTagName('tr');

        for (let i = 0; i < trs.length; i++) {
            const tds = trs[i].getElementsByTagName('td');
            let match = false;
            for (let j = 0; j < tds.length; j++) {
                if (tds[j]) {
                    const txtValue = tds[j].textContent || tds[j].innerText;
                    if (txtValue.toUpperCase().indexOf(filter) > -1) {
                        match = true;
                        break;
                    }
                }
            }
            if (match) {
                trs[i].style.display = '';
            } else {
                trs[i].style.display = 'none';
            }
        }
    }
'''
content = content.replace('function renderizarPodioPanorama(dados) {', js_funcs + '\\n    function renderizarPodioPanorama(dados) {')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print('File updated successfully.')
