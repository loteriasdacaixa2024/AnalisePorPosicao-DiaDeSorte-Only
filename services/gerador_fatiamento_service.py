import random
from models.sorteio import Sorteio, db
from collections import defaultdict

class GeradorFatiamentoService:
    # Definição oficial dos grupos da Matriz Associativa
    GRUPOS = {
        '0': [10, 20, 30],
        '1': [1, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 21, 31],
        '2': [2, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29],
        '3': [3, 13, 23, 30, 31],
        '4': [4, 14, 24],
        '5': [5, 15, 25],
        '6': [6, 16, 26],
        '7': [7, 17, 27],
        '8': [8, 18, 28],
        '9': [9, 19, 29],
        'gemeas': [11, 22]
    }

    @staticmethod
    def validar_limites_associativos(combinacao, limites, modos=None):
        """Valida se a combinação respeita os limites de cada grupo da Matriz Associativa.
        
        modos: dict com 'max' (≤) ou 'min' (≥) por chave de grupo.
               Padrão é 'max' para todos quando não informado.
        """
        if not limites:
            return True

        if modos is None:
            modos = {}

        contagem = {chave: 0 for chave in GeradorFatiamentoService.GRUPOS.keys()}

        for num in combinacao:
            for chave, dezenas_grupo in GeradorFatiamentoService.GRUPOS.items():
                if num in dezenas_grupo:
                    contagem[chave] += 1

        for chave, limit_str in limites.items():
            if limit_str and str(limit_str).strip() != '':
                limite_val = int(limit_str)
                modo = modos.get(chave, 'max')
                if modo == 'min':
                    # Modo mínimo: a aposta DEVE ter pelo menos X dezenas deste grupo
                    if contagem[chave] < limite_val:
                        return False
                else:
                    # Modo máximo (padrão): a aposta não pode ter MAIS que X dezenas
                    if contagem[chave] > limite_val:
                        return False
        return True

    @staticmethod
    def gerar_apostas(qtd_apostas, dezenas_por_jogo, limites_fatiamento, mes_selecionado, modos_fatiamento=None):
        todas_dezenas = list(range(1, 32))
        apostas_geradas = []
        tentativas = 0
        max_tentativas = 500000
        
        meses_nomes = ['', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']

        # Para facilitar a verificação de duplicidade, usar set
        apostas_set = set()

        while len(apostas_geradas) < qtd_apostas and tentativas < max_tentativas:
            tentativas += 1
            aposta_teste = tuple(sorted(random.sample(todas_dezenas, dezenas_por_jogo)))
            
            # Filtro: Limites da Matriz Associativa
            if not GeradorFatiamentoService.validar_limites_associativos(aposta_teste, limites_fatiamento, modos_fatiamento):
                continue
            
            if aposta_teste not in apostas_set:
                apostas_set.add(aposta_teste)
                
                if str(mes_selecionado) == 'aleatorio':
                    mes_num = random.randint(1, 12)
                elif str(mes_selecionado) == 'sequencial':
                    # Distribui os meses de 1 a 12 ciclicamente entre as apostas
                    mes_num = (len(apostas_geradas) % 12) + 1
                else:
                    mes_num = int(mes_selecionado)
                
                apostas_geradas.append({
                    'dezenas': list(aposta_teste),
                    'mes_num': mes_num,
                    'mes_nome': meses_nomes[mes_num]
                })

        return {
            'sucesso': True if len(apostas_geradas) > 0 else False,
            'apostas': apostas_geradas,
            'qtd_gerada': len(apostas_geradas),
            'tentativas': tentativas,
            'mensagem': 'Apostas geradas com sucesso' if len(apostas_geradas) > 0 else 'Filtro muito restritivo. Nenhuma aposta gerada.'
        }
        
    @staticmethod
    def analisar_historico_associativo(limite=50):
        """Analisa os últimos N sorteios e conta quantas dezenas vieram de cada grupo associativo."""
        query = Sorteio.query.order_by(Sorteio.concurso.desc())
        if str(limite).lower() != 'todos':
            query = query.limit(int(limite))
        sorteios = query.all()
        
        if not sorteios:
            return {'error': 'Nenhum sorteio encontrado'}
            
        historico_detalhado = []
        
        # Para estatística global no período
        media_grupos = {chave: 0 for chave in GeradorFatiamentoService.GRUPOS.keys()}
        
        for sorteio in sorteios:
            numeros = sorteio.get_posicoes_lista()
            contagem_sorteio = {chave: 0 for chave in GeradorFatiamentoService.GRUPOS.keys()}
            
            for num in numeros:
                for chave, dezenas_grupo in GeradorFatiamentoService.GRUPOS.items():
                    if num in dezenas_grupo:
                        contagem_sorteio[chave] += 1
                        media_grupos[chave] += 1
                        
            historico_detalhado.append({
                'concurso': sorteio.concurso,
                'data': sorteio.data_sorteio.strftime('%d/%m/%Y') if sorteio.data_sorteio else '',
                'dezenas': numeros,
                'contagem': contagem_sorteio,
                'mes_nome': sorteio.get_nome_mes()
            })
            
        for k in media_grupos.keys():
            media_grupos[k] = round(media_grupos[k] / len(sorteios), 2)
            
        top_3 = sorted(media_grupos.items(), key=lambda x: x[1], reverse=True)[:3]
        top_3_formatado = [{"grupo": k, "media": v} for k, v in top_3]

        return {
            'total_analisado': len(sorteios),
            'medias': media_grupos,
            'top_3': top_3_formatado,
            'historico': historico_detalhado
        }
