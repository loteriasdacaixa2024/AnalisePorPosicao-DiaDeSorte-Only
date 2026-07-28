# -*- coding: utf-8 -*-
"""
Serviço de Filtragem de Combinações do Dia de Sorte
Lê arquivo .txt com 2.629.575 combinações e aplica filtros dinâmicos
"""

import os
import time
from datetime import datetime
from typing import List, Dict, Set, Tuple, Optional
import json

# Cache global em memória
_cache_combinacoes = None
_cache_timestamp = None
_cache_ttl = 3600  # 1 hora

# Cache para números quentes e frios
_cache_quentes_frios = None
_cache_quentes_frios_timestamp = None
_cache_quentes_frios_ttl = 7200  # 2 horas

# Cache para análise de pares/ímpares
_cache_pares_impares = None
_cache_pares_impares_timestamp = None
_cache_pares_impares_ttl = 7200  # 2 horas

# Cache para análise de soma
_cache_soma = None
_cache_soma_timestamp = None
_cache_soma_ttl = 7200  # 2 horas

# Cache para análise de faixas
_cache_faixas = None
_cache_faixas_timestamp = None
_cache_faixas_ttl = 7200  # 2 horas

# Cache para análise de primos
_cache_primos = None
_cache_primos_timestamp = None
_cache_primos_ttl = 7200  # 2 horas

# Cache para análise de dígitos iniciais
_cache_digitos_iniciais = None
_cache_digitos_iniciais_timestamp = None
_cache_digitos_iniciais_ttl = 7200  # 2 horas


class FiltradorCombinacoesService:
    """Serviço para filtrar combinações do Dia de Sorte"""

    # Caminho do arquivo com todas as combinações
    ARQUIVO_COMBINACOES = os.path.join('geradores', 'txt', 'combinacoes_dia_sorte_completas.txt')

    # Números quentes e frios - serão carregados do banco via API
    NUMEROS_QUENTES = []
    NUMEROS_FRIOS = []

    # Análise de pares/ímpares - dados reais do banco
    PADRAO_PARES_MAIS_COMUM = {'min': 3, 'max': 4}  # Será atualizado
    MEDIA_PARES = 3.5  # Será atualizado

    # Análise de soma - dados reais do banco
    SOMA_MINIMA_IDEAL = 100  # Será atualizado
    SOMA_MAXIMA_IDEAL = 150  # Será atualizado
    SOMA_MEDIA = 125  # Será atualizado

    # Análise de faixas (Baixa/Média/Alta) - dados reais do banco
    PADRAO_FAIXAS_MAIS_COMUM = None  # Será atualizado com padrão tipo "2B+3M+2A"

    # Análise de primos - dados reais do banco (top 3 padrões)
    TOP_3_PADROES_PRIMOS = []  # Será atualizado com top 3

    # Análise de dígitos iniciais - dados reais do banco (top 3 padrões)
    TOP_3_PADROES_DIGITOS_INICIAIS = []  # Será atualizado com top 3

    def __init__(self):
        self.todas_combinacoes = []
        self.total_original = 0
        self.estatisticas = {}
        # Carrega análises do banco na inicialização
        self._carregar_numeros_quentes_frios()
        self._carregar_analise_pares_impares()
        self._carregar_analise_soma()
        self._carregar_analise_faixas()
        self._carregar_analise_primos()
        self._carregar_analise_digitos_iniciais()

    def _carregar_numeros_quentes_frios(self):
        """Carrega números quentes e frios do banco de dados com cache"""
        global _cache_quentes_frios, _cache_quentes_frios_timestamp

        # Verifica se o cache ainda é válido
        if _cache_quentes_frios is not None and _cache_quentes_frios_timestamp is not None:
            if time.time() - _cache_quentes_frios_timestamp < _cache_quentes_frios_ttl:
                print(f"[OK] Usando cache de números quentes/frios")
                FiltradorCombinacoesService.NUMEROS_QUENTES = _cache_quentes_frios['quentes']
                FiltradorCombinacoesService.NUMEROS_FRIOS = _cache_quentes_frios['frios']
                return

        # Busca do banco de dados
        try:
            from services.analise_quentes_frios_service import AnaliseQuentesFriosService

            print(f"[INFO] Carregando números quentes e frios do banco de dados...")

            # Busca os 10 mais quentes e 10 mais frios
            resultado = AnaliseQuentesFriosService.obter_numeros_quentes_frios(top=10)

            # Extrai apenas os números
            quentes = [item['numero'] for item in resultado['quentes']]
            frios = [item['numero'] for item in resultado['frios']]

            print(f"[OK] Números quentes (reais do banco): {quentes}")
            print(f"[OK] Números frios (reais do banco): {frios}")

            # Atualiza classe e cache
            FiltradorCombinacoesService.NUMEROS_QUENTES = quentes
            FiltradorCombinacoesService.NUMEROS_FRIOS = frios

            _cache_quentes_frios = {
                'quentes': quentes,
                'frios': frios
            }
            _cache_quentes_frios_timestamp = time.time()

        except Exception as e:
            # Se falhar ao buscar do banco, usa valores padrão e loga o erro
            print(f"[AVISO] Erro ao carregar números do banco: {e}")
            print(f"[AVISO] Usando valores padrão de exemplo")

            FiltradorCombinacoesService.NUMEROS_QUENTES = [5, 10, 12, 15, 18, 20, 23, 25, 28, 30]
            FiltradorCombinacoesService.NUMEROS_FRIOS = [1, 2, 3, 7, 9, 14, 17, 21, 26, 31]

    def _carregar_analise_pares_impares(self):
        """Carrega análise de pares/ímpares do banco de dados com cache"""
        global _cache_pares_impares, _cache_pares_impares_timestamp

        # Verifica cache
        if _cache_pares_impares is not None and _cache_pares_impares_timestamp is not None:
            if time.time() - _cache_pares_impares_timestamp < _cache_pares_impares_ttl:
                print(f"[OK] Usando cache de análise pares/ímpares")
                FiltradorCombinacoesService.PADRAO_PARES_MAIS_COMUM = _cache_pares_impares['padrao']
                FiltradorCombinacoesService.MEDIA_PARES = _cache_pares_impares['media']
                return

        # Busca do banco
        try:
            from services.analise_pares_impares_service import AnaliseParesImparesService

            print(f"[INFO] Carregando análise de pares/ímpares do banco...")
            resultado = AnaliseParesImparesService.obter_distribuicao_pares_impares()

            # Pega o padrão mais comum (primeiro da lista ordenada por frequência)
            padrao_mais_comum = resultado['padroes'][0] if resultado['padroes'] else {'pares': 3, 'impares': 4}

            # Define range baseado no padrão mais comum (±1)
            pares_comum = padrao_mais_comum['pares']
            padrao = {
                'min': max(0, pares_comum - 1),
                'max': min(7, pares_comum + 1)
            }

            media_pares = resultado.get('media_pares_por_sorteio', 3.5)

            print(f"[OK] Padrão de pares mais comum (reais): {pares_comum}P ({padrao['min']} a {padrao['max']})")
            print(f"[OK] Média de pares por sorteio: {media_pares}")

            # Atualiza classe e cache
            FiltradorCombinacoesService.PADRAO_PARES_MAIS_COMUM = padrao
            FiltradorCombinacoesService.MEDIA_PARES = media_pares

            _cache_pares_impares = {'padrao': padrao, 'media': media_pares}
            _cache_pares_impares_timestamp = time.time()

        except Exception as e:
            print(f"[AVISO] Erro ao carregar análise pares/ímpares: {e}")
            print(f"[AVISO] Usando valores padrão")

    def _carregar_analise_soma(self):
        """Carrega análise de soma do banco de dados com cache"""
        global _cache_soma, _cache_soma_timestamp

        # Verifica cache
        if _cache_soma is not None and _cache_soma_timestamp is not None:
            if time.time() - _cache_soma_timestamp < _cache_soma_ttl:
                print(f"[OK] Usando cache de análise de soma")
                FiltradorCombinacoesService.SOMA_MINIMA_IDEAL = _cache_soma['min']
                FiltradorCombinacoesService.SOMA_MAXIMA_IDEAL = _cache_soma['max']
                FiltradorCombinacoesService.SOMA_MEDIA = _cache_soma['media']
                return

        # Busca do banco
        try:
            from services.analise_soma_dezenas_service import AnaliseSomaDezenasService

            print(f"[INFO] Carregando análise de soma do banco...")
            resultado = AnaliseSomaDezenasService.analisar_somas()

            # Pega faixa mais comum das análises
            soma_media = resultado.get('soma_media', 125)
            desvio_padrao = resultado.get('desvio_padrao', 20)

            # Define faixa ideal como média ± 1 desvio padrão
            soma_min = int(soma_media - desvio_padrao)
            soma_max = int(soma_media + desvio_padrao)

            print(f"[OK] Faixa de soma ideal (reais): {soma_min} a {soma_max}")
            print(f"[OK] Soma média: {soma_media}, Desvio: {desvio_padrao}")

            # Atualiza classe e cache
            FiltradorCombinacoesService.SOMA_MINIMA_IDEAL = soma_min
            FiltradorCombinacoesService.SOMA_MAXIMA_IDEAL = soma_max
            FiltradorCombinacoesService.SOMA_MEDIA = soma_media

            _cache_soma = {'min': soma_min, 'max': soma_max, 'media': soma_media}
            _cache_soma_timestamp = time.time()

        except Exception as e:
            print(f"[AVISO] Erro ao carregar análise de soma: {e}")
            print(f"[AVISO] Usando valores padrão")

    def _carregar_analise_faixas(self):
        """Carrega análise de faixas (Baixa/Média/Alta) do banco de dados com cache"""
        global _cache_faixas, _cache_faixas_timestamp

        # Verifica cache
        if _cache_faixas is not None and _cache_faixas_timestamp is not None:
            if time.time() - _cache_faixas_timestamp < _cache_faixas_ttl:
                print(f"[OK] Usando cache de análise de faixas")
                FiltradorCombinacoesService.PADRAO_FAIXAS_MAIS_COMUM = _cache_faixas['padrao']
                return

        # Busca do banco
        try:
            from services.analise_dezenas_service import AnaliseDezenasFaixasService

            print(f"[INFO] Carregando análise de faixas do banco...")
            resultado = AnaliseDezenasFaixasService.obter_distribuicao_faixas()

            # Pega o padrão mais comum (primeiro da lista ordenada por frequência)
            padroes = resultado.get('padroes', [])
            if padroes:
                padrao_mais_comum = padroes[0]
                padrao_info = {
                    'descricao': padrao_mais_comum['descricao'],
                    'baixa': padrao_mais_comum['baixa'],
                    'media': padrao_mais_comum['media'],
                    'alta': padrao_mais_comum['alta'],
                    'frequencia': padrao_mais_comum['frequencia'],
                    'percentual': padrao_mais_comum['percentual']
                }

                print(f"[OK] Padrão de faixas mais comum (reais): {padrao_info['descricao']} - {padrao_info['percentual']}%")

                # Atualiza classe e cache
                FiltradorCombinacoesService.PADRAO_FAIXAS_MAIS_COMUM = padrao_info
                _cache_faixas = {'padrao': padrao_info}
                _cache_faixas_timestamp = time.time()

        except Exception as e:
            print(f"[AVISO] Erro ao carregar análise de faixas: {e}")
            print(f"[AVISO] Usando valores padrão")

    def _carregar_analise_primos(self):
        """Carrega análise de primos/compostos do banco de dados com cache"""
        global _cache_primos, _cache_primos_timestamp

        # Verifica cache
        if _cache_primos is not None and _cache_primos_timestamp is not None:
            if time.time() - _cache_primos_timestamp < _cache_primos_ttl:
                print(f"[OK] Usando cache de análise de primos")
                FiltradorCombinacoesService.TOP_3_PADROES_PRIMOS = _cache_primos['top3']
                return

        # Busca do banco
        try:
            from services.analise_primos_compostos_service import AnalisePrimosCompostosService

            print(f"[INFO] Carregando análise de primos do banco...")
            resultado = AnalisePrimosCompostosService.analisar_primos_compostos()

            # Pega os top 3 padrões mais comuns
            padroes = resultado.get('padroes', [])
            top_3 = []
            for i, padrao in enumerate(padroes[:3]):
                top_3.append({
                    'posicao': i + 1,
                    'padrao': padrao['padrao'],
                    'descricao': padrao['descricao'],
                    'primos': padrao['primos'],
                    'compostos': padrao['compostos'],
                    'frequencia': padrao['frequencia'],
                    'percentual': padrao['percentual']
                })

            if top_3:
                print(f"[OK] Top 3 padrões de primos (reais):")
                for p in top_3:
                    emoji = '🥇' if p['posicao'] == 1 else ('🥈' if p['posicao'] == 2 else '🥉')
                    print(f"   {emoji} {p['padrao']}: {p['frequencia']}x ({p['percentual']}%)")

            # Atualiza classe e cache
            FiltradorCombinacoesService.TOP_3_PADROES_PRIMOS = top_3
            _cache_primos = {'top3': top_3}
            _cache_primos_timestamp = time.time()

        except Exception as e:
            print(f"[AVISO] Erro ao carregar análise de primos: {e}")
            print(f"[AVISO] Usando valores padrão")

    def _carregar_analise_digitos_iniciais(self):
        """Carrega análise de dígitos iniciais do banco de dados com cache"""
        global _cache_digitos_iniciais, _cache_digitos_iniciais_timestamp

        # Verifica cache
        if _cache_digitos_iniciais is not None and _cache_digitos_iniciais_timestamp is not None:
            if time.time() - _cache_digitos_iniciais_timestamp < _cache_digitos_iniciais_ttl:
                print(f"[OK] Usando cache de análise de dígitos iniciais")
                FiltradorCombinacoesService.TOP_3_PADROES_DIGITOS_INICIAIS = _cache_digitos_iniciais['top3']
                return

        # Busca do banco
        try:
            from services.analise_digito_padrao_inicial_final_service import AnaliseDigitoPadraoInicialFinalService

            print(f"[INFO] Carregando análise de dígitos iniciais do banco...")
            resultado = AnaliseDigitoPadraoInicialFinalService.analisar_padroes()

            # Pega os top 3 padrões de dígitos iniciais
            padroes = resultado.get('top_padroes_iniciais', [])
            top_3 = []
            for i, padrao_info in enumerate(padroes[:3]):
                # Formato do padrão: "0:X | 1:Y | 2:Z | 3:W"
                # Vamos converter para formato simples: "X Y Z W"
                padrao_original = padrao_info['padrao']
                # Extrai os valores
                partes = [p.split(':')[1].strip() for p in padrao_original.split('|')]
                padrao_simples = ' '.join(partes)

                top_3.append({
                    'posicao': i + 1,
                    'padrao': padrao_simples,
                    'descricao': padrao_original,
                    'frequencia': padrao_info['frequencia'],
                    'percentual': padrao_info['porcentagem']
                })

            if top_3:
                print(f"[OK] Top 3 padrões de dígitos iniciais (reais):")
                for p in top_3:
                    emoji = '🥇' if p['posicao'] == 1 else ('🥈' if p['posicao'] == 2 else '🥉')
                    print(f"   {emoji} {p['padrao']}: {p['frequencia']}x ({p['percentual']}%)")

            # Atualiza classe e cache
            FiltradorCombinacoesService.TOP_3_PADROES_DIGITOS_INICIAIS = top_3
            _cache_digitos_iniciais = {'top3': top_3}
            _cache_digitos_iniciais_timestamp = time.time()

        except Exception as e:
            print(f"[AVISO] Erro ao carregar análise de dígitos iniciais: {e}")
            print(f"[AVISO] Usando valores padrão")

    @staticmethod
    def carregar_combinacoes_cache() -> List[List[int]]:
        """Carrega combinações do arquivo com cache em memória"""
        global _cache_combinacoes, _cache_timestamp

        # Verifica se o cache ainda é válido
        if _cache_combinacoes is not None and _cache_timestamp is not None:
            if time.time() - _cache_timestamp < _cache_ttl:
                print(f"[OK] Usando cache em memória ({len(_cache_combinacoes)} combinações)")
                return _cache_combinacoes

        # Cache expirado ou inexistente - recarrega do arquivo
        print(f"[INFO] Carregando combinações de {FiltradorCombinacoesService.ARQUIVO_COMBINACOES}...")
        inicio = time.time()

        if not os.path.exists(FiltradorCombinacoesService.ARQUIVO_COMBINACOES):
            raise FileNotFoundError(
                f"Arquivo de combinações não encontrado: {FiltradorCombinacoesService.ARQUIVO_COMBINACOES}\n"
                f"Execute o gerador de combinações primeiro!"
            )

        combinacoes = []
        with open(FiltradorCombinacoesService.ARQUIVO_COMBINACOES, 'r', encoding='utf-8') as f:
            for linha in f:
                linha = linha.strip()
                if linha and not linha.startswith('#'):  # Ignora linhas vazias e comentários
                    # Formato esperado: "01,05,12,15,23,28,31" ou "1,5,12,15,23,28,31"
                    numeros = [int(n) for n in linha.split(',')]
                    if len(numeros) == 7:  # Valida que são 7 números
                        combinacoes.append(sorted(numeros))

        tempo_decorrido = time.time() - inicio
        print(f"[OK] {len(combinacoes)} combinações carregadas em {tempo_decorrido:.2f}s")

        # Atualiza o cache
        _cache_combinacoes = combinacoes
        _cache_timestamp = time.time()

        return combinacoes

    def aplicar_filtros(self, filtros: Dict) -> Dict:
        """
        Aplica filtros às combinações e retorna resultado

        Args:
            filtros: Dicionário com os filtros a aplicar

        Returns:
            Dicionário com combinações filtradas e estatísticas
        """
        inicio_total = time.time()

        # Carrega todas as combinações (com cache)
        self.todas_combinacoes = self.carregar_combinacoes_cache()
        self.total_original = len(self.todas_combinacoes)

        combinacoes_filtradas = self.todas_combinacoes.copy()
        estatisticas_filtros = []

        # Aplica cada filtro sequencialmente
        if filtros.get('pares_impares'):
            combinacoes_filtradas, stats = self._filtrar_pares_impares(
                combinacoes_filtradas, filtros['pares_impares']
            )
            estatisticas_filtros.append(stats)

        if filtros.get('faixas_numeros'):
            combinacoes_filtradas, stats = self._filtrar_faixas_numeros(
                combinacoes_filtradas, filtros['faixas_numeros']
            )
            estatisticas_filtros.append(stats)

        if filtros.get('numeros_quentes'):
            combinacoes_filtradas, stats = self._filtrar_numeros_quentes(
                combinacoes_filtradas, filtros['numeros_quentes']
            )
            estatisticas_filtros.append(stats)

        if filtros.get('numeros_frios'):
            combinacoes_filtradas, stats = self._filtrar_numeros_frios(
                combinacoes_filtradas, filtros['numeros_frios']
            )
            estatisticas_filtros.append(stats)

        if filtros.get('soma'):
            combinacoes_filtradas, stats = self._filtrar_soma(
                combinacoes_filtradas, filtros['soma']
            )
            estatisticas_filtros.append(stats)

        if filtros.get('sequencias'):
            combinacoes_filtradas, stats = self._filtrar_sequencias(
                combinacoes_filtradas, filtros['sequencias']
            )
            estatisticas_filtros.append(stats)

        if filtros.get('primos'):
            combinacoes_filtradas, stats = self._filtrar_primos(
                combinacoes_filtradas, filtros['primos']
            )
            estatisticas_filtros.append(stats)

        if filtros.get('digitos_iniciais'):
            combinacoes_filtradas, stats = self._filtrar_digitos_iniciais(
                combinacoes_filtradas, filtros['digitos_iniciais']
            )
            estatisticas_filtros.append(stats)

        if filtros.get('numeros_especificos'):
            combinacoes_filtradas, stats = self._filtrar_numeros_especificos(
                combinacoes_filtradas, filtros['numeros_especificos']
            )
            estatisticas_filtros.append(stats)
            
        if filtros.get('muralha_bordas'):
            combinacoes_filtradas, stats = self._filtrar_muralha_bordas(
                combinacoes_filtradas, filtros['muralha_bordas']
            )
            estatisticas_filtros.append(stats)
            
        if filtros.get('espelhos'):
            combinacoes_filtradas, stats = self._filtrar_espelhos(
                combinacoes_filtradas, filtros['espelhos']
            )
            estatisticas_filtros.append(stats)

        tempo_total = time.time() - inicio_total

        # Retorna TODAS as combinações filtradas (sem limite)
        return {
            'sucesso': True,
            'total_original': self.total_original,
            'total_filtrado': len(combinacoes_filtradas),
            'percentual_reducao': round((1 - len(combinacoes_filtradas) / self.total_original) * 100, 2),
            'combinacoes': combinacoes_filtradas,  # TODAS as combinações
            'estatisticas_filtros': estatisticas_filtros,
            'tempo_processamento': round(tempo_total, 3),
            'filtros_aplicados': list(filtros.keys())
        }

    def _filtrar_pares_impares(self, combinacoes: List[List[int]], regras: Dict) -> Tuple[List[List[int]], Dict]:
        """Filtra por quantidade de pares/ímpares"""
        inicio = time.time()
        
        # Nova regra OBRIGATÓRIA: 3P4I é diferente de 4P3I. Tratamento exato de quantidades de pares aceitas.
        exatos = regras.get('exatos')
        
        # Retrocompatibilidade caso venha range do front-end por cache antigo
        if not exatos and 'min_pares' in regras:
            exatos = list(range(regras.get('min_pares', 0), regras.get('max_pares', 7) + 1))
            
        if not exatos:
            exatos = [0, 1, 2, 3, 4, 5, 6, 7]

        resultado = []
        for comb in combinacoes:
            qtd_pares = sum(1 for n in comb if n % 2 == 0)
            if qtd_pares in exatos:
                resultado.append(comb)

        regra_log = " ou ".join([f"{p}P/{7-p}I" for p in exatos]) if exatos else "Livre"

        stats = {
            'filtro': 'Pares/Ímpares',
            'antes': len(combinacoes),
            'depois': len(resultado),
            'eliminadas': len(combinacoes) - len(resultado),
            'percentual': round((len(resultado) / len(combinacoes)) * 100, 2) if combinacoes else 0,
            'tempo': round(time.time() - inicio, 3),
            'regra': regra_log
        }

        return resultado, stats

    def _filtrar_faixas_numeros(self, combinacoes: List[List[int]], regras: Dict) -> Tuple[List[List[int]], Dict]:
        """Filtra por faixas de números (Baixos 01-09, Médios 10-19, Altos 20-29, Muito Altos 30-31)"""
        inicio = time.time()

        # Extrai regras com min e max
        min_baixos = regras.get('baixos', {}).get('min', 0)
        max_baixos = regras.get('baixos', {}).get('max', 7)

        min_medios = regras.get('medios', {}).get('min', 0)
        max_medios = regras.get('medios', {}).get('max', 7)

        min_altos = regras.get('altos', {}).get('min', 0)
        max_altos = regras.get('altos', {}).get('max', 7)

        min_muito_altos = regras.get('muito_altos', {}).get('min', 0)
        max_muito_altos = regras.get('muito_altos', {}).get('max', 2)

        resultado = []
        for comb in combinacoes:
            faixas = {
                'baixos': 0,       # 01-09
                'medios': 0,       # 10-19
                'altos': 0,        # 20-29
                'muito_altos': 0   # 30-31
            }

            for num in comb:
                if 1 <= num <= 9:
                    faixas['baixos'] += 1
                elif 10 <= num <= 19:
                    faixas['medios'] += 1
                elif 20 <= num <= 29:
                    faixas['altos'] += 1
                elif 30 <= num <= 31:
                    faixas['muito_altos'] += 1

            # Verifica se atende todas as regras (min E max)
            if (min_baixos <= faixas['baixos'] <= max_baixos and
                min_medios <= faixas['medios'] <= max_medios and
                min_altos <= faixas['altos'] <= max_altos and
                min_muito_altos <= faixas['muito_altos'] <= max_muito_altos):
                resultado.append(comb)

        regra_texto = f"Baixos:{min_baixos}-{max_baixos}, Médios:{min_medios}-{max_medios}, Altos:{min_altos}-{max_altos}, Muito Altos:{min_muito_altos}-{max_muito_altos}"

        stats = {
            'filtro': 'Faixas de Números',
            'antes': len(combinacoes),
            'depois': len(resultado),
            'eliminadas': len(combinacoes) - len(resultado),
            'percentual': round((len(resultado) / len(combinacoes)) * 100, 2) if combinacoes else 0,
            'tempo': round(time.time() - inicio, 3),
            'regra': regra_texto
        }

        return resultado, stats

    def _filtrar_digitos_iniciais(self, combinacoes: List[List[int]], regras: Dict) -> Tuple[List[List[int]], Dict]:
        """Filtra por dígitos iniciais (linha 0, linha 10, linha 20, linha 30)"""
        inicio = time.time()

        resultado = []
        for comb in combinacoes:
            # Mapeamento do frontend
            contagem = {'digito_0': 0, 'digito_1': 0, 'digito_2': 0, 'digito_3': 0}

            for num in comb:
                # Transforma 5 em '05', pega o '0' como dígito inicial. 
                primeiro_digito = str(num).zfill(2)[0]
                chave = f"digito_{primeiro_digito}"
                if chave in contagem:
                    contagem[chave] += 1

            # Verifica se atende todas as regras enviadas
            atende = True
            for chave_regras, restricao in regras.items():
                if chave_regras not in contagem:
                    continue

                if 'min' in restricao and contagem[chave_regras] < restricao['min']:
                    atende = False
                    break
                if 'max' in restricao and contagem[chave_regras] > restricao['max']:
                    atende = False
                    break

            if atende:
                resultado.append(comb)

        # Monta texto final limpo
        partes = []
        for ch, rest in regras.items():
            nome = ch.replace('digito_', 'Díg. ')
            partes.append(f"{nome}: {rest.get('min', 0)} a {rest.get('max', 7)}")
        texto_regra = " | ".join(partes)

        stats = {
            'filtro': 'Dígitos Iniciais',
            'antes': len(combinacoes),
            'depois': len(resultado),
            'eliminadas': len(combinacoes) - len(resultado),
            'percentual': round((len(resultado) / len(combinacoes)) * 100, 2) if combinacoes else 0,
            'tempo': round(time.time() - inicio, 3),
            'regra': texto_regra
        }

        return resultado, stats

    def _filtrar_numeros_quentes(self, combinacoes: List[List[int]], regras: Dict) -> Tuple[List[List[int]], Dict]:
        """Filtra por números mais sorteados"""
        inicio = time.time()
        numeros_quentes = set(regras.get('numeros', self.NUMEROS_QUENTES))
        min_presentes = regras.get('min_presentes', 2)
        max_presentes = regras.get('max_presentes', 7)

        resultado = []
        for comb in combinacoes:
            qtd_quentes = sum(1 for n in comb if n in numeros_quentes)
            if min_presentes <= qtd_quentes <= max_presentes:
                resultado.append(comb)

        stats = {
            'filtro': 'Números Quentes',
            'antes': len(combinacoes),
            'depois': len(resultado),
            'eliminadas': len(combinacoes) - len(resultado),
            'percentual': round((len(resultado) / len(combinacoes)) * 100, 2) if combinacoes else 0,
            'tempo': round(time.time() - inicio, 3),
            'regra': f'{min_presentes} a {max_presentes} números quentes'
        }

        return resultado, stats

    def _filtrar_numeros_frios(self, combinacoes: List[List[int]], regras: Dict) -> Tuple[List[List[int]], Dict]:
        """Filtra por números menos sorteados"""
        inicio = time.time()
        numeros_frios = set(regras.get('numeros', self.NUMEROS_FRIOS))
        min_presentes = regras.get('min_presentes', 0)
        max_presentes = regras.get('max_presentes', 3)

        resultado = []
        for comb in combinacoes:
            qtd_frios = sum(1 for n in comb if n in numeros_frios)
            if min_presentes <= qtd_frios <= max_presentes:
                resultado.append(comb)

        stats = {
            'filtro': 'Números Frios',
            'antes': len(combinacoes),
            'depois': len(resultado),
            'eliminadas': len(combinacoes) - len(resultado),
            'percentual': round((len(resultado) / len(combinacoes)) * 100, 2) if combinacoes else 0,
            'tempo': round(time.time() - inicio, 3),
            'regra': f'{min_presentes} a {max_presentes} números frios'
        }

        return resultado, stats

    def _filtrar_soma(self, combinacoes: List[List[int]], regras: Dict) -> Tuple[List[List[int]], Dict]:
        """Filtra pela soma dos números"""
        inicio = time.time()
        min_soma = regras.get('min', 70)
        max_soma = regras.get('max', 180)

        resultado = []
        for comb in combinacoes:
            soma = sum(comb)
            if min_soma <= soma <= max_soma:
                resultado.append(comb)

        stats = {
            'filtro': 'Soma dos Números',
            'antes': len(combinacoes),
            'depois': len(resultado),
            'eliminadas': len(combinacoes) - len(resultado),
            'percentual': round((len(resultado) / len(combinacoes)) * 100, 2) if combinacoes else 0,
            'tempo': round(time.time() - inicio, 3),
            'regra': f'Soma entre {min_soma} e {max_soma}'
        }

        return resultado, stats

    def _filtrar_sequencias(self, combinacoes: List[List[int]], regras: Dict) -> Tuple[List[List[int]], Dict]:
        """Filtra por sequências consecutivas"""
        inicio = time.time()
        max_consecutivos = regras.get('max_consecutivos', 3)

        resultado = []
        for comb in combinacoes:
            numeros_sorted = sorted(comb)
            consecutivos = 1
            max_encontrado = 1

            for i in range(1, len(numeros_sorted)):
                if numeros_sorted[i] == numeros_sorted[i-1] + 1:
                    consecutivos += 1
                    max_encontrado = max(max_encontrado, consecutivos)
                else:
                    consecutivos = 1

            if max_encontrado <= max_consecutivos:
                resultado.append(comb)

        stats = {
            'filtro': 'Sequências Consecutivas',
            'antes': len(combinacoes),
            'depois': len(resultado),
            'eliminadas': len(combinacoes) - len(resultado),
            'percentual': round((len(resultado) / len(combinacoes)) * 100, 2) if combinacoes else 0,
            'tempo': round(time.time() - inicio, 3),
            'regra': f'Máximo {max_consecutivos} consecutivos'
        }

        return resultado, stats

    def _filtrar_primos(self, combinacoes: List[List[int]], regras: Dict) -> Tuple[List[List[int]], Dict]:
        """Filtra por números primos"""
        inicio = time.time()

        primos = {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31}
        min_primos = regras.get('min', 0)
        max_primos = regras.get('max', 7)

        resultado = []
        for comb in combinacoes:
            qtd_primos = sum(1 for n in comb if n in primos)
            if min_primos <= qtd_primos <= max_primos:
                resultado.append(comb)

        stats = {
            'filtro': 'Números Primos',
            'antes': len(combinacoes),
            'depois': len(resultado),
            'eliminadas': len(combinacoes) - len(resultado),
            'percentual': round((len(resultado) / len(combinacoes)) * 100, 2) if combinacoes else 0,
            'tempo': round(time.time() - inicio, 3),
            'regra': f'{min_primos} a {max_primos} primos'
        }

        return resultado, stats

    def _filtrar_numeros_especificos(self, combinacoes: List[List[int]], regras: Dict) -> Tuple[List[List[int]], Dict]:
        """Filtra por números específicos (fixos obrigatórios ou excluídos)"""
        inicio = time.time()

        obrigatorios = set(regras.get('obrigatorios', []))
        excluidos = set(regras.get('excluidos', []))

        resultado = []
        for comb in combinacoes:
            comb_set = set(comb)

            # Deve conter todos os obrigatórios
            if obrigatorios and not obrigatorios.issubset(comb_set):
                continue

            # Não deve conter nenhum dos excluídos
            if excluidos and comb_set.intersection(excluidos):
                continue

            resultado.append(comb)

        stats = {
            'filtro': 'Números Específicos',
            'antes': len(combinacoes),
            'depois': len(resultado),
            'eliminadas': len(combinacoes) - len(resultado),
            'percentual': round((len(resultado) / len(combinacoes)) * 100, 2) if combinacoes else 0,
            'tempo': round(time.time() - inicio, 3),
            'regra': f'Obrigatórios: {list(obrigatorios)}, Excluídos: {list(excluidos)}'
        }

        return resultado, stats

    def _filtrar_muralha_bordas(self, combinacoes: List[List[int]], regras: Dict) -> Tuple[List[List[int]], Dict]:
        """Filtra pela Muralha das Bordas (posições extremas)"""
        inicio = time.time()
        
        inicio_max = regras.get('inicio_max', 5)
        final_min = regras.get('final_min', 26)

        resultado = []
        for comb in combinacoes:
            if comb[0] <= inicio_max and comb[-1] >= final_min:
                resultado.append(comb)

        stats = {
            'filtro': 'Muralha de Bordas',
            'antes': len(combinacoes),
            'depois': len(resultado),
            'eliminadas': len(combinacoes) - len(resultado),
            'percentual': round((len(resultado) / len(combinacoes)) * 100, 2) if combinacoes else 0,
            'tempo': round(time.time() - inicio, 3),
            'regra': f'Borda Ini <= {inicio_max} | Borda Fim >= {final_min}'
        }

        return resultado, stats

    def _filtrar_espelhos(self, combinacoes: List[List[int]], regras: Dict) -> Tuple[List[List[int]], Dict]:
        """Filtra por Espelhos Máximos (ex: 13 e 31)"""
        inicio = time.time()
        
        max_espelhos = regras.get('max_espelhos', 1)
        
        PARES_ESPELHOS = [
            (1, 10), (2, 20), (3, 30), 
            (12, 21), (13, 31)
        ]

        resultado = []
        for comb in combinacoes:
            comb_set = set(comb)
            qtd_espelhos = 0
            for a, b in PARES_ESPELHOS:
                if a in comb_set and b in comb_set:
                    qtd_espelhos += 1
                    
            if qtd_espelhos <= max_espelhos:
                resultado.append(comb)

        stats = {
            'filtro': 'Trava de Espelhos',
            'antes': len(combinacoes),
            'depois': len(resultado),
            'eliminadas': len(combinacoes) - len(resultado),
            'percentual': round((len(resultado) / len(combinacoes)) * 100, 2) if combinacoes else 0,
            'tempo': round(time.time() - inicio, 3),
            'regra': f'Max Espelhos = {max_espelhos}'
        }

        return resultado, stats


def gerar_arquivo_combinacoes_txt(caminho_saida: str = None) -> Dict:
    """
    Gera arquivo .txt com todas as 2.629.575 combinações possíveis
    Usa o gerador dia_sorte_generator para criar as combinações
    """
    import os
    if caminho_saida is None:
        caminho_saida = FiltradorCombinacoesService.ARQUIVO_COMBINACOES

    # Garantir que as pastas existem antes de criar o arquivo
    os.makedirs(os.path.dirname(caminho_saida), exist_ok=True)

    print(f"📝 Gerando arquivo de combinações em {caminho_saida}...")
    inicio = time.time()

    from itertools import combinations

    total_combinacoes = 0

    with open(caminho_saida, 'w', encoding='utf-8') as f:
        # Cabeçalho
        f.write(f"# Todas as combinações do Dia de Sorte (C(31,7) = 2.629.575)\n")
        f.write(f"# Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"# Formato: num1,num2,num3,num4,num5,num6,num7\n\n")

        # Gera todas as combinações de 7 números entre 1 e 31
        for comb in combinations(range(1, 32), 7):
            # Formata como "01,05,12,15,23,28,31"
            linha = ','.join(f'{n:02d}' for n in comb)
            f.write(linha + '\n')
            total_combinacoes += 1

    tempo_decorrido = time.time() - inicio
    tamanho_mb = os.path.getsize(caminho_saida) / (1024 * 1024)

    print(f"✅ {total_combinacoes} combinações geradas em {tempo_decorrido:.2f}s")
    print(f"📦 Tamanho do arquivo: {tamanho_mb:.2f} MB")

    return {
        'sucesso': True,
        'caminho': caminho_saida,
        'total_combinacoes': total_combinacoes,
        'tempo_geracao': round(tempo_decorrido, 2),
        'tamanho_mb': round(tamanho_mb, 2)
    }
