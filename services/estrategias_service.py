"""
Service para gerenciamento de estratégias dinâmicas
Trabalha com arquivo JSON editável para configuração de estratégias
"""

import json
import os
from collections import Counter


class EstrategiasService:
    """Service para gerenciar estratégias de análise e geração de apostas"""

    # Caminho do arquivo JSON
    JSON_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'estrategias.json')

    @staticmethod
    def _garantir_arquivo():
        """Garante que o arquivo JSON existe com estratégias padrão"""
        diretorio = os.path.dirname(EstrategiasService.JSON_PATH)
        if not os.path.exists(diretorio):
            os.makedirs(diretorio)

        if not os.path.exists(EstrategiasService.JSON_PATH):
            estrategias_padrao = [
                {
                    "id": "equilibrada",
                    "nome": "Estratégia Equilibrada",
                    "descricao": "Distribui números uniformemente entre grupos baixo, médio e alto",
                    "parametros": {
                        "grupo_baixo": {"min": 1, "max": 10, "quantidade": 2},
                        "grupo_medio": {"min": 11, "max": 20, "quantidade": 3},
                        "grupo_alto": {"min": 21, "max": 31, "quantidade": 2},
                        "pares": {"min": 3, "max": 4},
                        "impares": {"min": 3, "max": 4},
                        "sequencias_max": 2,
                        "finais_iguais_max": 2,
                        "repeticoes_anterior_max": 3,
                        "digitos_unicos": {"permitir": True, "max": 1}
                    }
                },
                {
                    "id": "conservadora",
                    "nome": "Estratégia Conservadora",
                    "descricao": "Evita extremos, foca em números do meio",
                    "parametros": {
                        "grupo_baixo": {"min": 1, "max": 10, "quantidade": 1},
                        "grupo_medio": {"min": 11, "max": 20, "quantidade": 5},
                        "grupo_alto": {"min": 21, "max": 31, "quantidade": 1},
                        "pares": {"min": 3, "max": 4},
                        "impares": {"min": 3, "max": 4},
                        "sequencias_max": 1,
                        "finais_iguais_max": 1,
                        "repeticoes_anterior_max": 2,
                        "digitos_unicos": {"permitir": False, "max": 0}
                    }
                },
                {
                    "id": "agressiva",
                    "nome": "Estratégia Agressiva",
                    "descricao": "Permite mais variações e extremos",
                    "parametros": {
                        "grupo_baixo": {"min": 1, "max": 10, "quantidade": 3},
                        "grupo_medio": {"min": 11, "max": 20, "quantidade": 2},
                        "grupo_alto": {"min": 21, "max": 31, "quantidade": 2},
                        "pares": {"min": 2, "max": 5},
                        "impares": {"min": 2, "max": 5},
                        "sequencias_max": 3,
                        "finais_iguais_max": 3,
                        "repeticoes_anterior_max": 4,
                        "digitos_unicos": {"permitir": True, "max": 2}
                    }
                },
                {
                    "id": "pares_dominantes",
                    "nome": "Estratégia Pares Dominantes",
                    "descricao": "Favorece números pares sobre ímpares",
                    "parametros": {
                        "grupo_baixo": {"min": 1, "max": 10, "quantidade": 2},
                        "grupo_medio": {"min": 11, "max": 20, "quantidade": 2},
                        "grupo_alto": {"min": 21, "max": 31, "quantidade": 3},
                        "pares": {"min": 5, "max": 5},
                        "impares": {"min": 2, "max": 2},
                        "sequencias_max": 2,
                        "finais_iguais_max": 2,
                        "repeticoes_anterior_max": 3,
                        "digitos_unicos": {"permitir": True, "max": 1}
                    }
                },
                {
                    "id": "impares_dominantes",
                    "nome": "Estratégia Ímpares Dominantes",
                    "descricao": "Favorece números ímpares sobre pares",
                    "parametros": {
                        "grupo_baixo": {"min": 1, "max": 10, "quantidade": 3},
                        "grupo_medio": {"min": 11, "max": 20, "quantidade": 2},
                        "grupo_alto": {"min": 21, "max": 31, "quantidade": 2},
                        "pares": {"min": 2, "max": 2},
                        "impares": {"min": 5, "max": 5},
                        "sequencias_max": 2,
                        "finais_iguais_max": 2,
                        "repeticoes_anterior_max": 3,
                        "digitos_unicos": {"permitir": True, "max": 1}
                    }
                },
                {
                    "id": "minimalista",
                    "nome": "Estratégia Minimalista",
                    "descricao": "Restrições mínimas, máxima liberdade",
                    "parametros": {
                        "grupo_baixo": {"min": 1, "max": 10, "quantidade": {"min": 1, "max": 5}},
                        "grupo_medio": {"min": 11, "max": 20, "quantidade": {"min": 1, "max": 5}},
                        "grupo_alto": {"min": 21, "max": 31, "quantidade": {"min": 1, "max": 5}},
                        "pares": {"min": 1, "max": 6},
                        "impares": {"min": 1, "max": 6},
                        "sequencias_max": 5,
                        "finais_iguais_max": 5,
                        "repeticoes_anterior_max": 7,
                        "digitos_unicos": {"permitir": True, "max": 3}
                    }
                }
            ]

            with open(EstrategiasService.JSON_PATH, 'w', encoding='utf-8') as f:
                json.dump(estrategias_padrao, f, ensure_ascii=False, indent=2)

    @staticmethod
    def listar_todas():
        """Lista todas as estratégias"""
        EstrategiasService._garantir_arquivo()

        try:
            with open(EstrategiasService.JSON_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            return {'erro': str(e)}

    @staticmethod
    def buscar_por_id(estrategia_id):
        """Busca estratégia por ID"""
        estrategias = EstrategiasService.listar_todas()

        if isinstance(estrategias, dict) and 'erro' in estrategias:
            return None

        for estrategia in estrategias:
            if estrategia.get('id') == estrategia_id:
                return estrategia

        return None

    @staticmethod
    def adicionar(dados):
        """Adiciona nova estratégia"""
        estrategias = EstrategiasService.listar_todas()

        if isinstance(estrategias, dict) and 'erro' in estrategias:
            estrategias = []

        # Valida ID único
        estrategia_id = dados.get('id')
        if any(e.get('id') == estrategia_id for e in estrategias):
            return {'erro': 'ID já existe'}

        nova_estrategia = {
            'id': estrategia_id,
            'nome': dados.get('nome'),
            'descricao': dados.get('descricao'),
            'parametros': dados.get('parametros', {})
        }

        estrategias.append(nova_estrategia)

        with open(EstrategiasService.JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(estrategias, f, ensure_ascii=False, indent=2)

        return {'sucesso': True, 'estrategia': nova_estrategia}

    @staticmethod
    def atualizar(estrategia_id, dados):
        """Atualiza estratégia existente"""
        estrategias = EstrategiasService.listar_todas()

        if isinstance(estrategias, dict) and 'erro' in estrategias:
            return {'erro': 'Erro ao ler estratégias'}

        encontrado = False
        for estrategia in estrategias:
            if estrategia.get('id') == estrategia_id:
                estrategia['nome'] = dados.get('nome', estrategia['nome'])
                estrategia['descricao'] = dados.get('descricao', estrategia['descricao'])
                estrategia['parametros'] = dados.get('parametros', estrategia['parametros'])
                encontrado = True
                break

        if not encontrado:
            return {'erro': 'Estratégia não encontrada'}

        with open(EstrategiasService.JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(estrategias, f, ensure_ascii=False, indent=2)

        return {'sucesso': True, 'estrategia': estrategia}

    @staticmethod
    def excluir(estrategia_id):
        """Exclui estratégia"""
        estrategias = EstrategiasService.listar_todas()

        if isinstance(estrategias, dict) and 'erro' in estrategias:
            return {'erro': 'Erro ao ler estratégias'}

        estrategias_filtradas = [e for e in estrategias if e.get('id') != estrategia_id]

        if len(estrategias_filtradas) == len(estrategias):
            return {'erro': 'Estratégia não encontrada'}

        with open(EstrategiasService.JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(estrategias_filtradas, f, ensure_ascii=False, indent=2)

        return {'sucesso': True}

    @staticmethod
    def validar_jogo_com_estrategia(numeros, estrategia_id):
        """
        Valida se um jogo atende aos critérios de uma estratégia

        Args:
            numeros: Lista de 7 números
            estrategia_id: ID da estratégia

        Returns:
            dict: {valido: bool, erros: list, detalhes: dict}
        """
        estrategia = EstrategiasService.buscar_por_id(estrategia_id)

        if not estrategia:
            return {'valido': False, 'erros': ['Estratégia não encontrada']}

        parametros = estrategia.get('parametros', {})
        erros = []
        detalhes = {}

        # Valida grupos
        grupo_baixo = parametros.get('grupo_baixo', {})
        grupo_medio = parametros.get('grupo_medio', {})
        grupo_alto = parametros.get('grupo_alto', {})

        nums_baixo = [n for n in numeros if grupo_baixo['min'] <= n <= grupo_baixo['max']]
        nums_medio = [n for n in numeros if grupo_medio['min'] <= n <= grupo_medio['max']]
        nums_alto = [n for n in numeros if grupo_alto['min'] <= n <= grupo_alto['max']]

        detalhes['grupo_baixo'] = len(nums_baixo)
        detalhes['grupo_medio'] = len(nums_medio)
        detalhes['grupo_alto'] = len(nums_alto)

        # Valida quantidade por grupo
        qtd_baixo = grupo_baixo.get('quantidade')
        if isinstance(qtd_baixo, int):
            if len(nums_baixo) != qtd_baixo:
                erros.append(f"Grupo baixo: esperado {qtd_baixo}, obtido {len(nums_baixo)}")
        elif isinstance(qtd_baixo, dict):
            if not (qtd_baixo['min'] <= len(nums_baixo) <= qtd_baixo['max']):
                erros.append(f"Grupo baixo fora do range {qtd_baixo['min']}-{qtd_baixo['max']}")

        # Valida pares/ímpares
        pares = sum(1 for n in numeros if n % 2 == 0)
        impares = 7 - pares

        detalhes['pares'] = pares
        detalhes['impares'] = impares

        config_pares = parametros.get('pares', {})
        if not (config_pares.get('min', 0) <= pares <= config_pares.get('max', 7)):
            erros.append(f"Pares fora do range {config_pares.get('min')}-{config_pares.get('max')}")

        # Valida sequências
        numeros_sorted = sorted(numeros)
        sequencias = 0
        for i in range(len(numeros_sorted) - 1):
            if numeros_sorted[i+1] - numeros_sorted[i] == 1:
                sequencias += 1

        detalhes['sequencias'] = sequencias

        max_seq = parametros.get('sequencias_max', 7)
        if sequencias > max_seq:
            erros.append(f"Muitas sequências: {sequencias} (máx: {max_seq})")

        # Valida finais iguais
        finais = Counter([n % 10 for n in numeros])
        finais_iguais = sum(1 for count in finais.values() if count > 1)

        detalhes['finais_iguais'] = finais_iguais

        max_finais = parametros.get('finais_iguais_max', 7)
        if finais_iguais > max_finais:
            erros.append(f"Muitos finais iguais: {finais_iguais} (máx: {max_finais})")

        # Valida dígitos únicos
        digitos_unicos = sum(1 for n in numeros if n % 11 == 0)
        detalhes['digitos_unicos'] = digitos_unicos

        config_dig = parametros.get('digitos_unicos', {})
        if not config_dig.get('permitir', True) and digitos_unicos > 0:
            erros.append("Dígitos únicos não permitidos")
        elif digitos_unicos > config_dig.get('max', 7):
            erros.append(f"Muitos dígitos únicos: {digitos_unicos} (máx: {config_dig.get('max')})")

        return {
            'valido': len(erros) == 0,
            'erros': erros,
            'detalhes': detalhes
        }
