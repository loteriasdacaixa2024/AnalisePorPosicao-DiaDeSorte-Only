# Sistema: Análise por Posição - Dia de Sorte
# Padrão dígitos/soma (mesma regra das análises Soma e Dígitos Únicos)

from services.analise_digitos_unicos_service import AnaliseDigitosUnicosService
from services.analise_soma_dezenas_service import AnaliseSomaDezenasService


class MatrizPadraoAderenciaService:
    """Padrão dígitos/soma por linha da matriz + referência histórica (média)."""

    @staticmethod
    def padrao_digitos_soma(numeros):
        """Qtd. dígitos únicos (dezena+unidade) / soma — igual resultados e APIs."""
        nums = [int(n) for n in numeros if n is not None]
        if not nums:
            return {'digitos': 0, 'soma': 0, 'texto': '—'}
        digitos = set()
        soma = 0
        for n in nums:
            soma += n
            digitos.add(n // 10)
            digitos.add(n % 10)
        d = len(digitos)
        return {'digitos': d, 'soma': soma, 'texto': f'{d} / {soma}'}

    @classmethod
    def referencia_historica(cls):
        """Médias das rotas /api/analise/soma-dezenas e digitos-unicos."""
        ref_d, ref_s = 7, 112
        soma_data = AnaliseSomaDezenasService.analisar_somas()
        if soma_data and not soma_data.get('error'):
            ref_s = int(round(soma_data.get('soma_media', ref_s)))
        dig_data = AnaliseDigitosUnicosService.analisar_digitos_unicos()
        if dig_data and not dig_data.get('error'):
            ref_d = int(round(dig_data.get('quantidade_media', ref_d)))
        return {
            'digitos': ref_d,
            'soma': ref_s,
            'texto': f'{ref_d} / {ref_s}',
        }

    @classmethod
    def distancia_padrao_ideal(cls, numeros, referencia=None):
        if referencia is None:
            referencia = cls.referencia_historica()
        p = cls.padrao_digitos_soma(numeros)
        if p['texto'] == '—':
            return 9999.0
        return abs(p['digitos'] - referencia['digitos']) + abs(
            p['soma'] - referencia['soma']
        ) / 12.0

    @classmethod
    def enriquecer_grid_com_padrao(cls, grid, colunas=None, analises=None):
        del colunas, analises
        for row in grid:
            nums = [
                row['celulas'][p]['dezena']
                for p in range(1, 8)
                if row['celulas'].get(p)
            ]
            padrao = cls.padrao_digitos_soma(nums)
            row['padrao'] = {'padrao_digitos_soma': padrao['texto']}
        return grid
