content = open('templates/gerador_especial.html', 'r', encoding='utf-8').read()

# Localizar o início e o fim do bloco do painel
start_marker = '<!-- PAINEL DE INTELIGÊNCIA: TOP 3 E LEGENDA -->'
end_marker_after = '<div class="card-body bg-white p-0">'

idx_start = content.find(start_marker)
if idx_start == -1:
    # Tenta variação sem acento
    start_marker = '<!-- PAINEL DE INTELIG'
    idx_start = content.find(start_marker)

# Encontrar o início da linha onde está start_marker (retroceder até \n)
line_start = content.rfind('\n', 0, idx_start) + 1

# Encontrar onde termina o bloco do painel (onde começa o card-body da tabela)
idx_end = content.find(end_marker_after, idx_start)
# Retroceder até o \n antes do card-body
line_end = content.rfind('\n', 0, idx_end) + 1

print(f"Block starts at char {line_start}, ends at char {line_end}")
print("--- Current block ---")
print(repr(content[line_start:line_end][:200]))
print("...")
print(repr(content[line_start:line_end][-200:]))

new_block = '''                    <!-- PAINEL DE INTELIGÊNCIA: 2 COLUNAS LADO A LADO -->
                    <div class="card-body border-bottom bg-light p-3">
                        <div class="row g-3">

                            <!-- COLUNA ESQUERDA: TOP 3 Saídas + TOP 3 Espalhados -->
                            <div class="col-md-6 border-end pe-3">
                                <h6 class="fw-bold text-primary text-center mb-2">
                                    <i class="fas fa-trophy text-warning"></i> TOP 3 (TOTAL DE SAÍDAS)
                                </h6>
                                <div id="placard_top3" class="d-flex justify-content-center gap-2 mb-3">
                                    <span class="text-muted">Carregando análise histórica...</span>
                                </div>
                                <hr class="my-2">
                                <h6 class="fw-bold text-success text-center mb-1">
                                    <i class="fas fa-project-diagram"></i> TOP 3 SORTEIOS MAIS ESPALHADOS
                                </h6>
                                <p class="text-muted text-center mb-2" style="font-size: 11px;">Quais concursos ativaram o maior número de grupos distintos?</p>
                                <div id="placard_espalhados" class="d-flex flex-row flex-wrap justify-content-center gap-2">
                                    <span class="text-muted">Carregando análise...</span>
                                </div>
                            </div>

                            <!-- COLUNA DIREITA: Recorde Máximo + Total ao Longo -->
                            <div class="col-md-6 ps-3">
                                <h6 class="fw-bold text-danger text-center mb-1">
                                    <i class="fas fa-fire"></i> RECORDE MÁXIMO EM 1 ÚNICO SORTEIO
                                </h6>
                                <p class="text-muted text-center mb-2" style="font-size: 11px;">Maior quantidade de dezenas deste grupo que já saíram juntas num mesmo concurso.</p>
                                <div id="placard_recordes" class="d-flex flex-wrap justify-content-center gap-1 mb-3">
                                    <span class="text-muted">Carregando análise...</span>
                                </div>
                                <hr class="my-2">
                                <h6 class="fw-bold text-primary text-center mb-1">
                                    <i class="fas fa-chart-bar"></i> TOTAL AO LONGO DOS SORTEIOS
                                </h6>
                                <p class="text-muted text-center mb-2" style="font-size: 11px;">Soma de todas as aparições de cada grupo em todos os concursos analisados.</p>
                                <div id="placard_totais" class="d-flex flex-wrap justify-content-center gap-1">
                                    <span class="text-muted">Carregando análise...</span>
                                </div>
                            </div>

                        </div>
                    </div>
'''

result = content[:line_start] + new_block + content[line_end:]
open('templates/gerador_especial.html', 'w', encoding='utf-8').write(result)
print("Done! File written.")
