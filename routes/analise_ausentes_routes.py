import os
import glob
import json
from flask import Blueprint, render_template, request, jsonify
from models.sorteio import Sorteio
from config import Config

analise_ausentes_bp = Blueprint('analise_ausentes', __name__)

@analise_ausentes_bp.route('/analise-ausentes')
def index():
    return render_template('analise_ausentes.html')

@analise_ausentes_bp.route('/api/analise-ausentes/concursos-disponiveis')
def get_concursos_disponiveis():
    base_dir = os.path.join(Config.BASE_DIR, 'conferencia_apostas')
    pattern = os.path.join(base_dir, '*', 'apostas.json')
    arquivos = glob.glob(pattern)
    
    concursos = []
    for arquivo in arquivos:
        nome_pasta = os.path.basename(os.path.dirname(arquivo))
        if nome_pasta.isdigit():
            concursos.append(int(nome_pasta))
    
    concursos.sort(reverse=True)
    return jsonify({'concursos': concursos})

@analise_ausentes_bp.route('/api/analise-ausentes/<int:concurso>')
def analisar_ausentes(concurso):
    arquivo_apostas = os.path.join(Config.BASE_DIR, 'conferencia_apostas', str(concurso), 'apostas.json')
    
    if not os.path.exists(arquivo_apostas):
        return jsonify({'erro': f'Arquivo apostas.json não encontrado para o concurso {concurso}.'}), 404
        
    try:
        with open(arquivo_apostas, 'r', encoding='utf-8') as f:
            dados = json.load(f)
            
        universo_apostado = set()
        apostas_list = dados.get('apostas', [])
        for aposta in apostas_list:
            numeros = aposta.get('numeros', [])
            for n in numeros:
                # Tratar para ser sempre inteiro válido
                if str(n).isdigit():
                    universo_apostado.add(int(n))
                
        ausentes = set(range(1, 32)) - universo_apostado
        
        # Buscar sorteio correspondente no banco
        sorteio = Sorteio.query.filter_by(concurso=concurso).first()
        sorteio_real = []
        if sorteio:
            dezenas_raw = [
                sorteio.sorteio_1 or sorteio.posicao_1,
                sorteio.sorteio_2 or sorteio.posicao_2,
                sorteio.sorteio_3 or sorteio.posicao_3,
                sorteio.sorteio_4 or sorteio.posicao_4,
                sorteio.sorteio_5 or sorteio.posicao_5,
                sorteio.sorteio_6 or sorteio.posicao_6,
                sorteio.sorteio_7 or sorteio.posicao_7
            ]
            # Filtrar por garantia de números válidos
            sorteio_real = sorted([int(n) for n in dezenas_raw if n and str(n).isdigit()])
            
        ausentes_sorteados = ausentes.intersection(set(sorteio_real))
        acertos_da_aposta = universo_apostado.intersection(set(sorteio_real))
        
        return jsonify({
            'concurso': concurso,
            'universo_apostado': sorted(list(universo_apostado)),
            'ausentes': sorted(list(ausentes)),
            'sorteio_real': sorteio_real,
            'ausentes_sorteados': sorted(list(ausentes_sorteados)),
            'acertos_da_aposta': sorted(list(acertos_da_aposta)),
            'stats': {
                'total_apostado': len(universo_apostado),
                'total_ausentes': len(ausentes),
                'tamanho_sorteio': len(sorteio_real),
                'total_ausentes_sorteados': len(ausentes_sorteados),
                'teto_maximo_acertos': len(sorteio_real) - len(ausentes_sorteados) if len(sorteio_real) > 0 else 0
            }
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'erro': str(e)}), 500

@analise_ausentes_bp.route('/api/analise-ausentes/historico')
def analise_historico():
    base_dir = os.path.join(Config.BASE_DIR, 'conferencia_apostas')
    pattern = os.path.join(base_dir, '*', 'apostas.json')
    arquivos = glob.glob(pattern)
    
    resultados = []
    frequencia_escapes = {}
    
    # Pré-carregar os sorteios para os concursos encontrados
    concursos_ids = []
    for arquivo in arquivos:
        nome_pasta = os.path.basename(os.path.dirname(arquivo))
        if nome_pasta.isdigit():
            concursos_ids.append(int(nome_pasta))
            
    sorteios = Sorteio.query.filter(Sorteio.concurso.in_(concursos_ids)).all()
    sorteios_map = {s.concurso: s for s in sorteios}
    
    for arquivo in arquivos:
        nome_pasta = os.path.basename(os.path.dirname(arquivo))
        if not nome_pasta.isdigit():
            continue
            
        concurso = int(nome_pasta)
        sorteio = sorteios_map.get(concurso)
        
        # Só analisa se tiver sorteio válido
        if not sorteio or (not sorteio.sorteio_1 and not sorteio.posicao_1):
            continue
            
        try:
            with open(arquivo, 'r', encoding='utf-8') as f:
                dados = json.load(f)
                
            universo_apostado = set()
            for aposta in dados.get('apostas', []):
                for n in aposta.get('numeros', []):
                    if str(n).isdigit():
                        universo_apostado.add(int(n))
                        
            ausentes = set(range(1, 32)) - universo_apostado
            
            dezenas_raw = [
                sorteio.sorteio_1 or sorteio.posicao_1,
                sorteio.sorteio_2 or sorteio.posicao_2,
                sorteio.sorteio_3 or sorteio.posicao_3,
                sorteio.sorteio_4 or sorteio.posicao_4,
                sorteio.sorteio_5 or sorteio.posicao_5,
                sorteio.sorteio_6 or sorteio.posicao_6,
                sorteio.sorteio_7 or sorteio.posicao_7
            ]
            sorteio_real = sorted([int(n) for n in dezenas_raw if n and str(n).isdigit()])
            
            ausentes_sorteados = ausentes.intersection(set(sorteio_real))
            
            for dezena in ausentes_sorteados:
                frequencia_escapes[dezena] = frequencia_escapes.get(dezena, 0) + 1
                
            resultados.append({
                'concurso': concurso,
                'total_apostado': len(universo_apostado),
                'escapes_qtd': len(ausentes_sorteados),
                'escapes_dezenas': sorted(list(ausentes_sorteados)),
                'teto_acertos': len(sorteio_real) - len(ausentes_sorteados) if len(sorteio_real) > 0 else 0
            })
            
        except Exception:
            pass # Ignora arquivos corrompidos silenciosamente no histórico
            
    # Ordenar resultados do mais recente para o mais antigo
    resultados.sort(key=lambda x: x['concurso'], reverse=True)
    
    # Preparar array de frequências ordenado por mais frequentes primeiro
    frequencia_array = [{'dezena': k, 'qtd': v} for k, v in frequencia_escapes.items()]
    frequencia_array.sort(key=lambda x: x['qtd'], reverse=True)
    
    # Gerar Histograma de Escapes (Volume de Escapes X Frequência e Concursos)
    histograma = {}
    for r in resultados:
        qtd = r['escapes_qtd']
        if qtd not in histograma:
            histograma[qtd] = {'vezes': 0, 'concursos': []}
        histograma[qtd]['vezes'] += 1
        histograma[qtd]['concursos'].append(r['concurso'])
        
    histograma_array = [
        {'qtd_escapes': k, 'vezes': v['vezes'], 'concursos': sorted(v['concursos'], reverse=True)} 
        for k, v in histograma.items()
    ]
    histograma_array.sort(key=lambda x: x['qtd_escapes'])
    
    return jsonify({
        'total_concursos_analisados': len(resultados),
        'historico': resultados,
        'frequencia_escapes': frequencia_array,
        'histograma_escapes': histograma_array
    })
