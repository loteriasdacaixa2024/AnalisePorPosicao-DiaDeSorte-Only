"""
Service para gerenciamento de garantias de apostas
Trabalha com arquivo JSON editável manualmente ou via API
"""

import json
import os
from datetime import datetime


class GarantiasService:
    """Service para gerenciar garantias de apostas do Dia de Sorte"""

    # Caminho do arquivo JSON
    JSON_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'garantias.json')

    @staticmethod
    def _garantir_diretorio():
        """Garante que o diretório data/ existe"""
        diretorio = os.path.dirname(GarantiasService.JSON_PATH)
        if not os.path.exists(diretorio):
            os.makedirs(diretorio)

    @staticmethod
    def _garantir_arquivo():
        """Garante que o arquivo JSON existe com dados padrão"""
        GarantiasService._garantir_diretorio()

        if not os.path.exists(GarantiasService.JSON_PATH):
            dados_padrao = [
                {"id": 1, "dezenas": 8, "apostas": 3, "garantia": "5 pontos", "observacao": "Estrutura simples, ideal para iniciantes"},
                {"id": 2, "dezenas": 9, "apostas": 4, "garantia": "6 pontos", "observacao": "Clássico fechamento '9 em 4' (ótimo equilíbrio)"},
                {"id": 3, "dezenas": 10, "apostas": 5, "garantia": "6 pontos", "observacao": "Fechamento '10 em 5', ideal para grids 7x5"},
                {"id": 4, "dezenas": 11, "apostas": 8, "garantia": "6 pontos", "observacao": "Boa cobertura, ainda econômica"},
                {"id": 5, "dezenas": 12, "apostas": 10, "garantia": "6 pontos", "observacao": "Equilíbrio entre custo e garantia"},
                {"id": 6, "dezenas": 13, "apostas": 16, "garantia": "6 pontos", "observacao": "Excelente para uso em grupo pequeno"},
                {"id": 7, "dezenas": 14, "apostas": 20, "garantia": "6 pontos", "observacao": "Padrão profissional de desdobramento"},
                {"id": 8, "dezenas": 15, "apostas": 25, "garantia": "6 pontos", "observacao": "Mesmo formato da Mega-Sena básica"},
                {"id": 9, "dezenas": 16, "apostas": 36, "garantia": "6 pontos", "observacao": "Cobertura ampla, custo moderado"},
                {"id": 10, "dezenas": 17, "apostas": 45, "garantia": "6 pontos", "observacao": "Fechamento intermediário para bolões"},
                {"id": 11, "dezenas": 18, "apostas": 60, "garantia": "6 pontos", "observacao": "Alta cobertura, custo mais elevado"},
                {"id": 12, "dezenas": 19, "apostas": 75, "garantia": "6 pontos", "observacao": "Cobertura de ~90% se 7 entre as 19"},
                {"id": 13, "dezenas": 20, "apostas": 100, "garantia": "6 pontos", "observacao": "Fechamento quase completo (recomendado p/ bolões)"},
                {"id": 14, "dezenas": 21, "apostas": 120, "garantia": "6 pontos", "observacao": "Forte, ideal p/ sistemas automáticos"},
                {"id": 15, "dezenas": 22, "apostas": 150, "garantia": "6 pontos", "observacao": "Cobertura excelente, custo alto"},
                {"id": 16, "dezenas": 23, "apostas": 180, "garantia": "6 pontos", "observacao": "Usado em fechamentos balanceados"},
                {"id": 17, "dezenas": 24, "apostas": 210, "garantia": "6 pontos", "observacao": "Quase total, só perde para fechamento completo"},
                {"id": 18, "dezenas": 25, "apostas": 240, "garantia": "6 pontos", "observacao": "Cobertura de elite"},
                {"id": 19, "dezenas": 26, "apostas": 300, "garantia": "6 pontos", "observacao": "Muito alto custo, uso em grupos grandes"},
                {"id": 20, "dezenas": 27, "apostas": 400, "garantia": "7 pontos possíveis", "observacao": "Cobertura quase total"},
                {"id": 21, "dezenas": 28, "apostas": 500, "garantia": "7 pontos possíveis", "observacao": "Garantia máxima sem redundância total"},
                {"id": 22, "dezenas": 29, "apostas": 650, "garantia": "7 pontos possíveis", "observacao": "Fechamento completo prático"},
                {"id": 23, "dezenas": 30, "apostas": 800, "garantia": "7 pontos possíveis", "observacao": "100% de chance de 7 dentro do grupo"},
                {"id": 24, "dezenas": 31, "apostas": 8893, "garantia": "7 pontos garantidos", "observacao": "Fechamento total (todas as combinações possíveis)"}
            ]
            GarantiasService._salvar_json(dados_padrao)

    @staticmethod
    def _salvar_json(dados):
        """Salva dados no arquivo JSON"""
        with open(GarantiasService.JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)

    @staticmethod
    def listar_todas():
        """
        Lista todas as garantias

        Returns:
            list: Lista de dicionários com garantias
        """
        GarantiasService._garantir_arquivo()

        try:
            with open(GarantiasService.JSON_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            return {'erro': str(e)}

    @staticmethod
    def buscar_por_id(garantia_id):
        """
        Busca garantia por ID

        Args:
            garantia_id: ID da garantia

        Returns:
            dict: Garantia encontrada ou None
        """
        garantias = GarantiasService.listar_todas()

        if isinstance(garantias, dict) and 'erro' in garantias:
            return None

        for garantia in garantias:
            if garantia.get('id') == int(garantia_id):
                return garantia

        return None

    @staticmethod
    def buscar_por_dezenas(num_dezenas):
        """
        Busca garantia pelo número de dezenas

        Args:
            num_dezenas: Número de dezenas

        Returns:
            dict: Garantia encontrada ou None
        """
        garantias = GarantiasService.listar_todas()

        if isinstance(garantias, dict) and 'erro' in garantias:
            return None

        for garantia in garantias:
            if garantia.get('dezenas') == int(num_dezenas):
                return garantia

        return None

    @staticmethod
    def adicionar(dados):
        """
        Adiciona nova garantia

        Args:
            dados: Dicionário com dados da garantia

        Returns:
            dict: Garantia adicionada com sucesso ou erro
        """
        garantias = GarantiasService.listar_todas()

        if isinstance(garantias, dict) and 'erro' in garantias:
            garantias = []

        # Gera novo ID
        novo_id = max([g.get('id', 0) for g in garantias], default=0) + 1

        nova_garantia = {
            'id': novo_id,
            'dezenas': dados.get('dezenas'),
            'apostas': dados.get('apostas'),
            'garantia': dados.get('garantia'),
            'observacao': dados.get('observacao', '')
        }

        garantias.append(nova_garantia)
        GarantiasService._salvar_json(garantias)

        return {'sucesso': True, 'garantia': nova_garantia}

    @staticmethod
    def atualizar(garantia_id, dados):
        """
        Atualiza garantia existente

        Args:
            garantia_id: ID da garantia
            dados: Novos dados

        Returns:
            dict: Resultado da operação
        """
        garantias = GarantiasService.listar_todas()

        if isinstance(garantias, dict) and 'erro' in garantias:
            return {'erro': 'Erro ao ler garantias'}

        encontrado = False
        for garantia in garantias:
            if garantia.get('id') == int(garantia_id):
                garantia['dezenas'] = dados.get('dezenas', garantia['dezenas'])
                garantia['apostas'] = dados.get('apostas', garantia['apostas'])
                garantia['garantia'] = dados.get('garantia', garantia['garantia'])
                garantia['observacao'] = dados.get('observacao', garantia.get('observacao', ''))
                encontrado = True
                break

        if not encontrado:
            return {'erro': 'Garantia não encontrada'}

        GarantiasService._salvar_json(garantias)
        return {'sucesso': True, 'garantia': garantia}

    @staticmethod
    def excluir(garantia_id):
        """
        Exclui garantia

        Args:
            garantia_id: ID da garantia

        Returns:
            dict: Resultado da operação
        """
        garantias = GarantiasService.listar_todas()

        if isinstance(garantias, dict) and 'erro' in garantias:
            return {'erro': 'Erro ao ler garantias'}

        garantias_filtradas = [g for g in garantias if g.get('id') != int(garantia_id)]

        if len(garantias_filtradas) == len(garantias):
            return {'erro': 'Garantia não encontrada'}

        GarantiasService._salvar_json(garantias_filtradas)
        return {'sucesso': True}

    @staticmethod
    def calcular_custo(num_dezenas, valor_aposta=2.50):
        """
        Calcula custo total baseado no número de dezenas

        Args:
            num_dezenas: Número de dezenas escolhidas
            valor_aposta: Valor de cada aposta (padrão R$ 2,50)

        Returns:
            dict: Informações de custo
        """
        garantia = GarantiasService.buscar_por_dezenas(num_dezenas)

        if not garantia:
            return {'erro': 'Garantia não encontrada para este número de dezenas'}

        num_apostas = garantia.get('apostas', 0)
        custo_total = num_apostas * valor_aposta

        return {
            'dezenas': num_dezenas,
            'apostas': num_apostas,
            'valor_aposta': valor_aposta,
            'custo_total': custo_total,
            'garantia': garantia.get('garantia'),
            'observacao': garantia.get('observacao', '')
        }
