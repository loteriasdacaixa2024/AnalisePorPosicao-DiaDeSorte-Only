"""
Servidor Flask + Extrator de Bolões da Caixa
Versão WEB - Comunica com a interface HTML (central_conferencias.html)

Instalação:
    pip install flask flask-cors selenium

Uso:
    python servidor_boloes.py

Requisitos:
    - Microsoft Edge instalado
    - Edge WebDriver (msedgedriver.exe) no PATH ou na mesma pasta
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import json
import os
import sys
import time
import threading
from datetime import datetime

SCRIPT_BOLOES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'conferencias-boloes', 'script')
if SCRIPT_BOLOES_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_BOLOES_DIR)

from boloes_filtro_loterica import (
    CATALOGO_MODALIDADES,
    FiltroLotericaConfig,
    aplicar_filtro_loterica,
    avancar_para_pagina_filtrada,
    bolao_atende_filtro,
    bolao_corresponde_loterica,
    cfg_com_qtd,
    config_from_api,
    fila_qtd_dezenas,
    gerar_arquivo_base,
    garantir_sessao_caixa,
    manter_sessao_ativa,
    modalidade_por_slug,
    preparar_extracao_pagina,
    preparar_pagina_filtrada,
    tem_proxima_pagina,
)
from boloes_modalidades import MODALIDADES, TODAS_MODALIDADES

app = Flask(__name__)
CORS(app)

# ============================================
# CONFIGURAÇÕES PADRÃO
# ============================================
DEST_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'conferencias-boloes')  # Pasta padrão para salvar os arquivos JSON
MODALIDADE_PADRAO = 'dia-de-sorte'

URL_BOLOES = "https://www.loteriasonline.caixa.gov.br/silce-web/#/bolao-caixa"

NOMES_MODALIDADES = {mod.slug: mod.label for mod in CATALOGO_MODALIDADES}

# ============================================
# ESTADO GLOBAL (compartilhado com interface)
# ============================================
estado = {
    'status': 'parado',      # parado, rodando, concluido, erro
    'pagina': 0,
    'boloes': 0,
    'percentual': 0,
    'log': [],
    'arquivo': '',
    'mensagem': '',
    'filtro_loterica': None,
    'modalidade_rotulo': '',
}

driver = None
extracao_thread = None

# ============================================
# MECANISMO DE PAUSAR / CONTINUAR (TERMINAL)
# ============================================
pausa_event = threading.Event()
termino_event = threading.Event()


def verificar_pausa() -> bool:
    """Chamado dentro do loop. Se pausado, bloqueia ate continuar ou terminar.
    Retorna True se deve continuar, False se foi parado."""
    if pausa_event.is_set():
        adicionar_log('�️  EXTRAÇÃO PAUSADA — pressione [c] para continuar ou [s] para parar.', 'warning')
        while pausa_event.is_set():
            if termino_event.is_set():
                estado['status'] = 'parado'
                adicionar_log('🛑 Extração encerrada durante pausa.', 'warning')
                return False
            time.sleep(0.5)
        adicionar_log('▶️  Extração retomada!', 'success')
    return True


def terminal_input_listener():
    """Thread que lera comandos do terminal para pausar/continuar/parar."""
    print("\n" + "=" * 60)
    print("  CONTROLES NO TERMINAL:")
    print("    [p] Pausar extração")
    print("    [c] Continuar extração")
    print("    [s] Parar extração")
    print("=" * 60 + "\n")

    try:
        import msvcrt
        use_msvcrt = True
    except ImportError:
        use_msvcrt = False

    while not termino_event.is_set():
        try:
            if use_msvcrt:
                if msvcrt.kbhit():
                    ch = msvcrt.getch().decode('utf-8', errors='ignore').strip().lower()
                else:
                    time.sleep(0.2)
                    continue
            else:
                ch = input().strip().lower()

            if not ch:
                continue
            cmd = ch[0]

            if cmd == 'p':
                if estado['status'] == 'rodando':
                    pausa_event.set()
                    print("⏸️  Comando PAUSAR recebido.")
                else:
                    print("ℹ️  Não há extração em andamento.")
            elif cmd == 'c':
                if pausa_event.is_set():
                    pausa_event.clear()
                    print("▶️  Comando CONTINUAR recebido.")
                else:
                    print("ℹ️  Extração não está pausada.")
            elif cmd == 's':
                termino_event.set()
                pausa_event.clear()
                print("🛑 Comando PARAR recebido.")
        except (EOFError, KeyboardInterrupt):
            termino_event.set()
            pausa_event.clear()
            break
        except Exception:
            time.sleep(0.5)


# ============================================
# FUNÇÕES AUXILIARES
# ============================================
def adicionar_log(texto, tipo='info'):
    """Adiciona mensagem ao log (será enviada para a interface)"""
    estado['log'].append({'texto': texto, 'tipo': tipo})
    # Limitar tamanho do log
    if len(estado['log']) > 100:
        estado['log'] = estado['log'][-50:]
    print(f"[{tipo.upper()}] {texto}")


def extrair_dados_popup():
    """Extrai os dados do popup do bolão"""
    global driver
    try:
        time.sleep(1.5)
        popup = WebDriverWait(driver, 8).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".modal-content, .modal, [class*='modal'], [role='dialog']"))
        )
        from boloes_extrair_popup import parse_campos_popup
        return parse_campos_popup(popup.text)
    except Exception:
        return None


def fechar_popup():
    """Fecha o popup atual"""
    global driver
    try:
        close_btns = driver.find_elements(By.CSS_SELECTOR,
            "button.close, .btn-close, [class*='close'], button[aria-label='Close'], "
            ".modal-header button, [class*='modal'] .close")
        for btn in close_btns:
            try:
                if btn.is_displayed():
                    btn.click()
                    time.sleep(0.5)
                    return True
            except:
                pass
    except:
        pass

    try:
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
        time.sleep(0.5)
        return True
    except:
        pass

    return False


def encontrar_botoes_boloes():
    """Encontra todos os botões de bolões na página"""
    global driver
    seletores = [
        "button.btn-primary",
        "button.btn-success",
        "button[class*='btn'][class*='primary']",
        "button[class*='btn'][class*='success']",
        ".card button",
        "[class*='bolao'] button",
        "button[class*='apostar']",
        "button[class*='comprar']",
        "button[class*='ver']",
    ]

    todos_botoes = []
    for seletor in seletores:
        try:
            botoes = driver.find_elements(By.CSS_SELECTOR, seletor)
            for btn in botoes:
                if btn not in todos_botoes and btn.is_displayed():
                    texto = btn.text.lower()
                    if any(palavra in texto for palavra in ['ver', 'detalh', 'comprar', 'apostar', 'cotas', 'jogo']):
                        todos_botoes.append(btn)
        except:
            pass

    return todos_botoes


def ir_proxima_pagina():
    """Tenta ir para a próxima página"""
    global driver
    try:
        seletores_prox = [
            "button[aria-label*='proxim']",
            "button[aria-label*='next']",
            "a[aria-label*='proxim']",
            "a[aria-label*='next']",
            ".pagination .next",
            ".pagination li:last-child a",
            "button[class*='next']",
            "[class*='pagination'] button:last-child",
            "button[class*='arrow-right']",
            "button[class*='chevron-right']",
            ".page-item:last-child .page-link",
        ]

        for seletor in seletores_prox:
            try:
                botoes = driver.find_elements(By.CSS_SELECTOR, seletor)
                for btn in botoes:
                    if btn.is_displayed() and btn.is_enabled():
                        classes = btn.get_attribute('class') or ''
                        if 'disabled' not in classes:
                            btn.click()
                            time.sleep(2)
                            return True
            except:
                pass

        return False
    except:
        return False


def _normalizar_txt(txt: str) -> str:
    """Normaliza texto para comparação (lowercase, sem acentos, sem espaços extras)."""
    import unicodedata
    txt = (txt or '').lower().strip()
    # Remove acentos
    txt = ''.join(
        c for c in unicodedata.normalize('NFD', txt)
        if unicodedata.category(c) != 'Mn'
    )
    txt = txt.replace('-', ' ').replace('  ', ' ').strip()
    return txt


def detectar_modalidade_site(driver) -> str:
    """Detecta qual modalidade está selecionada no site da Caixa.
    Busca por elementos cards/tabs com texto correspondente a uma modalidade known.
    Retorna o label da modalidade detectada ou string vazia se não conseguiu."""
    seletores_cards = [
        "[class*='card']",
        "[class*='modalidade']",
        "[role='tab']",
        "[role='option']",
        ".nav-item",
        "button",
        "a",
    ]
    for seletor in seletores_cards:
        try:
            elementos = driver.find_elements(By.CSS_SELECTOR, seletor)
            for el in elementos:
                txt = el.text.strip()
                if not txt or len(txt) > 80:
                    continue
                txt_norm = _normalizar_txt(txt)
                # Ignora genéricos / vazios / ícones
                if txt_norm in ('', ' ', 'loterica', 'lotéricas', 'caixa', 'loterias',
                                'jogos', 'bolão', 'bolões', 'aposta', 'apostas'):
                    continue
                for mod in TODAS_MODALIDADES:
                    for frag in [mod.label, mod.tecla, mod.epoca or '', *mod.keywords]:
                        frag_norm = _normalizar_txt(frag)
                        if frag_norm and frag_norm in txt_norm:
                            return mod.label
        except Exception:
            continue
    return ''


def validar_modalidade_site(driver, modalidade_slug: str) -> bool:
    """Verifica se a modalidade selecionada no site bate com a solicitada.
    Loga alerta se divergir e retorna True (ok) ou False (divergente)."""
    mod = modalidade_por_slug(modalidade_slug)
    if not mod:
        return True  # sem catálogo, não valida

    detectada = detectar_modalidade_site(driver)
    if not detectada:
        # Não detectou nada; confia no usuário
        adicionar_log(
            '⚠️  Não foi possível detectar a modalidade automaticamente no site '
            '(confira se a correta está selecionada).',
            'warning',
        )
        return True

    alvo_norm = _normalizar_txt(mod.label)
    detect_norm = _normalizar_txt(detectada)

    # Compara: o label detectado deve conter o slug parser ou vice-versa
    if (alvo_norm in detect_norm) or (detect_norm in alvo_norm):
        adicionar_log(f'✅ Modalidade selecionada no site: {detectada} (OK)', 'success')
        return True
    # Também compara via keywords
    for kw in mod.keywords:
        kw_norm = _normalizar_txt(kw)
        if kw_norm and kw_norm in detect_norm:
            adicionar_log(f'✅ Modalidade selecionada no site: {detectada} (OK)', 'success')
            return True

    adicionar_log(
        f'� DIVERGÊNCIA DE MODALIDADE! Solicitado: "{mod.label}" '
        f'| Selecionado no site: "{detectada}". '
        f'Altere no site para "{mod.label}" ou corrija o filtro.',
        'error',
    )
    return False


def salvar_json(boloes, pasta, arquivo_base=None):
    """Salva os bolões em arquivo JSON (não grava lista vazia)."""
    if not boloes:
        nome = f"{arquivo_base}.json" if arquivo_base else f"boloes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        arquivo = os.path.join(pasta, nome)
        if os.path.isfile(arquivo):
            adicionar_log(f'Mantendo arquivo anterior — 0 bolões nesta rodada ({nome})', 'warning')
            return arquivo
        adicionar_log('Nenhum bolão extraído — JSON vazio não foi gravado.', 'warning')
        return ''
    nome = f"{arquivo_base}.json" if arquivo_base else f"boloes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    arquivo = os.path.join(pasta, nome)
    with open(arquivo, 'w', encoding='utf-8') as f:
        json.dump(boloes, f, ensure_ascii=False, indent=2)
    return arquivo


def executar_extracao(modalidade_slug, pasta, filtro_cfg: FiltroLotericaConfig = None):
    """Função principal de extração (roda em thread separada)"""
    global driver, estado

    mod_rotulo = modalidade_por_slug(modalidade_slug) if modalidade_slug else None
    rotulo_nome = mod_rotulo.label if mod_rotulo else 'modalidade selecionada no site'

    try:
        if not os.path.exists(pasta):
            os.makedirs(pasta, exist_ok=True)

        adicionar_log('Iniciando navegador Edge...', 'info')
        driver = webdriver.Edge()
        driver.maximize_window()
        driver.get(URL_BOLOES)

        adicionar_log('Navegador aberto!', 'success')
        adicionar_log('=' * 50, 'info')
        adicionar_log('AGUARDANDO LOGIN E MODALIDADE', 'warning')
        adicionar_log('=' * 50, 'info')
        adicionar_log('1. Faça login no site da Caixa', 'warning')
        adicionar_log('2. Selecione a MODALIDADE desejada no site', 'warning')
        if filtro_cfg:
            dez = filtro_cfg.qtd_dezenas or 'qualquer'
            adicionar_log(f'3. Lotérica alvo (script aplica): {filtro_cfg.termo} | dezenas: {dez}', 'warning')
        adicionar_log('4. Aguarde 30 segundos na lista de bolões filtrada', 'warning')

        for i in range(30, 0, -5):
            if estado['status'] != 'rodando':
                return
            adicionar_log(f'Aguardando... {i} segundos', 'info')
            time.sleep(5)

        arquivo_base = gerar_arquivo_base(filtro_cfg, mod_rotulo) if filtro_cfg else None
        estado['modalidade_rotulo'] = rotulo_nome

        adicionar_log('=' * 40, 'info')
        adicionar_log('VALIDANDO MODALIDADE NO SITE...', 'warning')
        if not validar_modalidade_site(driver, modalidade_slug):
            adicionar_log('� EXTRAÇÃO ABORTalidade não confere.', 'error')
            estado['status'] = 'erro'
            estado['mensagem'] = (
                f'Modalidade "{rotulo_nome}" não está selecionada no site. '
                f'Selecione a modalidade correte e tente novamente.'
            )
            return
        adicionar_log('Iniciando extração automática...', 'success')

        boloes = []
        textos_ja_extraidos = set()
        max_paginas = 50
        filas_dez = fila_qtd_dezenas(filtro_cfg, modalidade_slug)

        if filtro_cfg.varrer_dezenas:
            adicionar_log(
                f'Varredura de dezenas: {" → ".join(str(q) for q in filas_dez)}',
                'info',
            )

        for idx_dez, qtd in enumerate(filas_dez, 1):
            if estado['status'] != 'rodando':
                break

            # Verificar se foi pausado ou terminado antes de cada filtro
            if not verificar_pausa():
                break

            cfg = cfg_com_qtd(filtro_cfg, qtd)
            pagina = 1
            paginas_sem_novos = 0

            adicionar_log('=' * 40, 'info')
            adicionar_log(f'Filtro dezenas: {qtd} ({idx_dez}/{len(filas_dez)})', 'warning')
            adicionar_log('=' * 40, 'info')

            while estado['status'] == 'rodando' and pagina <= max_paginas:
                # Verificar se foi pausado ou terminado
                if not verificar_pausa():
                    break

                estado['pagina'] = pagina
                adicionar_log(f'Filtro + página {pagina} (dezenas={qtd})...', 'info')

                if not garantir_sessao_caixa(
                    driver, pagina,
                    log_fn=lambda m: adicionar_log(m, 'info'),
                    modo_web=True,
                    estado_check=estado,
                ):
                    adicionar_log('Sessão perdida — extração interrompida.', 'error')
                    break

                if not preparar_extracao_pagina(
                    driver, cfg, pagina,
                    log_fn=lambda m: adicionar_log(m, 'info'),
                    modo_web=True,
                    estado_check=estado,
                ):
                    adicionar_log(f'Falha ao preparar página {pagina} com filtro.', 'error')
                    break

                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)
                driver.execute_script("window.scrollTo(0, 0);")
                time.sleep(1)

                botoes = encontrar_botoes_boloes()
                adicionar_log(f'Encontrados {len(botoes)} bolões na página', 'info')

                if len(botoes) == 0:
                    paginas_sem_novos += 1
                    if paginas_sem_novos >= 2:
                        adicionar_log('Nenhum bolão em páginas consecutivas.', 'warning')
                        break
                else:
                    paginas_sem_novos = 0

                novos_pagina = 0
                duplicados_pagina = 0
                rejeitados = 0

                for i, botao in enumerate(botoes):
                    if estado['status'] != 'rodando':
                        break

                    try:
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", botao)
                        time.sleep(0.3)
                        botao.click()
                        time.sleep(1.5)

                        dados = extrair_dados_popup()

                        if dados and dados.get('hash_bolao'):
                            if cfg and not bolao_corresponde_loterica(dados, cfg):
                                rejeitados += 1
                                lot_out = (dados.get('nome_loterica') or 'N/A')[:35]
                                adicionar_log(f'Ignorado (outra lotérica): {lot_out}', 'warning')
                                fechar_popup()
                                time.sleep(0.3)
                                continue

                            if cfg and not bolao_atende_filtro(dados, cfg):
                                rejeitados += 1
                                q1 = dados.get('qtd_dezenas_aposta_1') or len(dados.get('dezenas_aposta') or [])
                                adicionar_log(
                                    f'Ignorado ({q1} dez., filtro={cfg.qtd_dezenas}): '
                                    f'{(dados.get("nome_loterica") or "N/A")[:30]}',
                                    'warning',
                                )
                                fechar_popup()
                                time.sleep(0.3)
                                continue

                            assinatura = dados.get('hash_bolao')
                            if assinatura in textos_ja_extraidos:
                                duplicados_pagina += 1
                            else:
                                textos_ja_extraidos.add(assinatura)
                                dados['pagina'] = pagina
                                dados['indice'] = len(boloes) + 1
                                if qtd is not None:
                                    dados['filtro_qtd_dezenas'] = qtd
                                boloes.append(dados)
                                novos_pagina += 1
                                estado['boloes'] = len(boloes)

                                loterica = dados.get('nome_loterica', 'N/A')[:35]
                                adicionar_log(f"#{len(boloes)}: {loterica}", 'success')

                        fechar_popup()
                        time.sleep(0.3)
                        if (i + 1) % 5 == 0:
                            manter_sessao_ativa(driver)
                    except Exception:
                        fechar_popup()
                        continue

                adicionar_log(
                    f'Página {pagina} concluída: {novos_pagina} novos | total {len(boloes)}',
                    'info',
                )

                if boloes:
                    arquivo = salvar_json(boloes, pasta, arquivo_base)
                    estado['arquivo'] = arquivo

                if not tem_proxima_pagina(driver):
                    adicionar_log(f'Fim filtro {qtd} dezenas — última página: {pagina}', 'info')
                    break

                pagina += 1
                estado['percentual'] = min(95, (idx_dez - 1) * 30 + pagina * 3)
                manter_sessao_ativa(driver)

            adicionar_log(f'Filtro {qtd} dezenas concluído | total: {len(boloes)}', 'success')

        estado['status'] = 'concluido'
        estado['percentual'] = 100
        adicionar_log('=' * 50, 'success')
        adicionar_log('EXTRAÇÃO CONCLUÍDA!', 'success')
        adicionar_log(f'Total: {len(boloes)} bolões extraídos', 'success')
        adicionar_log(f'Arquivo: {estado["arquivo"]}', 'success')
        adicionar_log('=' * 50, 'success')

    except Exception as e:
        estado['status'] = 'erro'
        estado['mensagem'] = str(e)
        adicionar_log(f'ERRO: {str(e)}', 'error')
    finally:
        if driver:
            try:
                adicionar_log('Fechando navegador...', 'info')
                driver.quit()
            except:
                pass


# ============================================
# ROTAS DA API (Flask)
# ============================================

@app.route('/status', methods=['GET'])
def api_status():
    """Retorna status do servidor"""
    return jsonify({
        'status': 'online',
        'versao': 'v1.1',
        'modalidade_padrao': MODALIDADE_PADRAO,
        'pasta_padrao': DEST_DIR,
        'modalidades': [
            {'slug': m.slug, 'label': m.label, 'numero': m.numero, 'especial': m.especial}
            for m in CATALOGO_MODALIDADES
        ],
    })


@app.route('/progresso', methods=['GET'])
def api_progresso():
    """Retorna progresso da extração atual (inclui tamanho do arquivo em tempo real)"""
    logs_para_enviar = estado['log'].copy()
    estado['log'] = []  # Limpar logs já enviados

    arquivo_path = estado['arquivo']
    tamanho_bytes = 0
    if arquivo_path and os.path.isfile(arquivo_path):
        try:
            tamanho_bytes = os.path.getsize(arquivo_path)
        except OSError:
            tamanho_bytes = 0

    tamanho_kb = round(tamanho_bytes / 1024, 1)

    return jsonify({
        'status': estado['status'],
        'pagina': estado['pagina'],
        'boloes': estado['boloes'],
        'percentual': estado['percentual'],
        'log': logs_para_enviar,
        'arquivo': arquivo_path,
        'tamanho_bytes': tamanho_bytes,
        'tamanho_kb': tamanho_kb,
        'pausado': pausa_event.is_set(),
        'terminado': termino_event.is_set(),
        'mensagem': estado['mensagem'],
        'modalidade_rotulo': estado.get('modalidade_rotulo', ''),
    })


@app.route('/iniciar', methods=['POST'])
def api_iniciar():
    """Inicia a extração de bolões"""
    global extracao_thread

    dados = request.json or {}
    modalidade = dados.get('modalidade', MODALIDADE_PADRAO)
    pasta = dados.get('pasta', '') or DEST_DIR
    filtro_cfg = config_from_api(
        dados.get('loterica', ''),
        dados.get('qtd_dezenas'),
        varrer_dezenas=bool(dados.get('varrer_dezenas')),
    )

    if estado['status'] == 'rodando':
        return jsonify({'erro': 'Extração já em andamento'}), 400

    if not filtro_cfg:
        return jsonify({'erro': 'Informe a lotérica (código ou nome) para filtrar os bolões.'}), 400

    mod = modalidade_por_slug(modalidade)
    rotulo = mod.label if mod else modalidade

    estado['status'] = 'rodando'
    estado['pagina'] = 0
    estado['boloes'] = 0
    estado['percentual'] = 0
    estado['log'] = []
    estado['arquivo'] = ''
    estado['mensagem'] = ''
    estado['filtro_loterica'] = filtro_cfg.termo
    estado['modalidade_rotulo'] = rotulo

    # Resetar flags de pausa/termino para nova extracao
    pausa_event.clear()
    termino_event.clear()

    adicionar_log(f'Rótulo arquivo: {rotulo} (modalidade você seleciona no site)', 'info')
    adicionar_log(f'Pasta: {pasta}', 'info')
    adicionar_log(f'Lotérica: {filtro_cfg.termo}', 'info')
    if filtro_cfg.qtd_dezenas:
        adicionar_log(f'Dezenas: {filtro_cfg.qtd_dezenas}', 'info')
    if filtro_cfg.varrer_dezenas:
        adicionar_log('Varredura: todas qtd. de dezenas da modalidade', 'info')

    extracao_thread = threading.Thread(
        target=executar_extracao,
        args=(modalidade, pasta, filtro_cfg),
    )
    extracao_thread.daemon = True
    extracao_thread.start()

    return jsonify({'status': 'iniciado', 'modalidade': modalidade, 'pasta': pasta})


@app.route('/pausar', methods=['POST'])
def api_pausar():
    """Pausa a extração atual (pode ser retomada com /continuar)"""
    if estado['status'] != 'rodando':
        return jsonify({'erro': 'Não há extração em andamento para pausar.'}), 400
    pausa_event.set()
    return jsonify({'status': 'pausado'})


@app.route('/continuar', methods=['POST'])
def api_continuar():
    """Retoma a extração pausada"""
    if not pausa_event.is_set():
        return jsonify({'erro': 'Extração não está pausada.'}), 400
    pausa_event.clear()
    return jsonify({'status': 'rodando'})


@app.route('/parar', methods=['POST'])
def api_parar():
    """Para definitivamente a extração atual"""
    termino_event.set()
    estado['status'] = 'parado'
    pausa_event.clear()  # desbloqueia se estiver pausado
    adicionar_log('Extração interrompida pelo usuário', 'warning')
    return jsonify({'status': 'parado'})


# ============================================
# MAIN
# ============================================
if __name__ == '__main__':
    print("=" * 60)
    print("  SERVIDOR DE EXTRAÇÃO DE BOLÕES DA CAIXA")
    print("  Versão WEB - Interface HTML")
    print("=" * 60)
    print(f"\n  Pasta padrão: {DEST_DIR}")
    print(f"  Modalidade padrão: {NOMES_MODALIDADES.get(MODALIDADE_PADRAO, MODALIDADE_PADRAO)}")
    print(f"\n  Servidor rodando em: http://localhost:5001")
    print("\n  Abra o arquivo central_conferencias.html")
    print("  e acesse a aba 'Download Bolões'")
    print("\n" + "=" * 60)
    print("  Aguardando comandos da interface web e terminal...")
    print("=" * 60 + "\n")

    # Iniciar thread que lê comandos do terminal (pausar/continuar/parar)
    terminal_thread = threading.Thread(target=terminal_input_listener, daemon=True)
    terminal_thread.start()

    app.run(host='0.0.0.0', port=5001, debug=False, threaded=True)
