import math
import random
from models.sorteio import Sorteio, db

class GeradorDigitosService:

    @staticmethod
    def get_top_combinations(limite=3):
        """
        Analisa o histórico inteiro e encontra os conjuntos de dígitos mais frequentes
        usados nos sorteios do Dia de Sorte.
        """
        sorteios = Sorteio.query.all()
        combinacoes_freq = {}
        
        for sorteio in sorteios:
            dezenas = [
                sorteio.posicao_1, sorteio.posicao_2, sorteio.posicao_3,
                sorteio.posicao_4, sorteio.posicao_5, sorteio.posicao_6,
                sorteio.posicao_7
            ]
            
            # Extrair dígitos únicos dessa combinação
            digitos_unico = set()
            for num in dezenas:
                s = f"{num:02d}"
                digitos_unico.add(s[0])
                digitos_unico.add(s[1])
                
            # Ordenar para criar chave única
            chave = tuple(sorted(list(digitos_unico)))
            
            if chave not in combinacoes_freq:
                combinacoes_freq[chave] = 0
            combinacoes_freq[chave] += 1
            
        # Ordenar pelas combinações que mais saíram
        ordenado = sorted(combinacoes_freq.items(), key=lambda x: x[1], reverse=True)
        
        resultado = []
        total_sorteios = len(sorteios) if sorteios else 1
        
        for idx, (comb, freq) in enumerate(ordenado[:limite]):
            pct = (freq / total_sorteios) * 100
            resultado.append({
                'rank': idx + 1,
                'combinacao': ','.join(comb),
                'lista': list(comb),
                'frequencia': freq,
                'percentual': round(pct, 2)
            })
            
        return resultado

    @staticmethod
    def get_digit_frequencies():
        """
        Consulta todos os resultados do Dia de Sorte e calcula a frequência 
        de cada dígito (0-9) nas dezenas sorteadas.
        """
        sorteios = Sorteio.query.all()
        frequencias = {str(i): 0 for i in range(10)}
        
        for sorteio in sorteios:
            dezenas = [
                sorteio.posicao_1, sorteio.posicao_2, sorteio.posicao_3,
                sorteio.posicao_4, sorteio.posicao_5, sorteio.posicao_6,
                sorteio.posicao_7
            ]
            for num in dezenas:
                # Transforma a dezena em string formatada (ex: '01', '31')
                dezena_str = f"{num:02d}"
                for digito in dezena_str:
                    frequencias[digito] += 1
                    
        # Ordenar do mais frequente para o menos
        ordenado = sorted(frequencias.items(), key=lambda x: x[1], reverse=True)
        return [{'digito': k, 'total': v} for k, v in ordenado]

    @staticmethod
    def gerar_pool_valido(digitos_selecionados):
        """
        Dada uma lista de dígitos (ex: ['1', '2', '3']), 
        gera todas as dezenas válidas (01-31) possíveis compostas Apenas por esses dígitos.
        """
        pool = []
        digitos_set = set(str(d) for d in digitos_selecionados)
        for i in range(1, 32):
            dezena_str = f"{i:02d}"
            # Verifica se TODOS os dígitos da dezena_str estão nos dígitos escolhidos
            if dezena_str[0] in digitos_set and dezena_str[1] in digitos_set:
                pool.append(i)
        return pool

    @staticmethod
    def gerar_apostas_por_digitos(digitos, qtd_dezenas_por_aposta, qtd_apostas, dezenas_excluidas=None, mes_input='aleatorio', filtros=None):
        """
        Gera as apostas a partir do pool de dígitos, aplicando quantidade, 
        dezenas excluídas e garantindo combinações únicas.
        Aplica os 'Filtros Estratégicos' se fornecidos em `filtros`.
        """
        if not dezenas_excluidas:
            dezenas_excluidas = []
            
        pool_completo = GeradorDigitosService.gerar_pool_valido(digitos)
        pool_valido = [n for n in pool_completo if n not in dezenas_excluidas]
        
        # Validações
        tamanho_pool = len(pool_valido)
        if tamanho_pool < qtd_dezenas_por_aposta:
            return {
                'sucesso': False, 
                'mensagem': f'O pool gerado possui apenas {tamanho_pool} dezenas, o que é insuficiente para criar apostas de {qtd_dezenas_por_aposta} dezenas.'
            }
        
        # Limite teórico de combinações
        max_comb = math.comb(tamanho_pool, qtd_dezenas_por_aposta)
        if qtd_apostas > max_comb:
            return {
                'sucesso': False, 
                'mensagem': f'Impossível gerar {qtd_apostas} apostas únicas. Com {tamanho_pool} dezenas no pool, só é possível formar {max_comb} combinações.'
            }
            
        apostas = set()
        tentativas = 0
        max_tentativas = max_comb * 50 # Aumentado por causa dos filtros
        
        # Filtros extraídos
        f_frq = filtros.get('f_frq', '') if filtros else ''
        f_par = filtros.get('f_par', '') if filtros else ''
        f_som = filtros.get('f_som', '') if filtros else ''
        f_seq = filtros.get('f_seq', '') if filtros else ''
        f_rep = filtros.get('f_rep', '') if filtros else ''
        f_lin = filtros.get('f_lin', '') if filtros else ''
        
        quentes = filtros.get('quentes', []) if filtros else []
        frias = filtros.get('frias', []) if filtros else []
        ultimo_sorteio = filtros.get('ultimo_sorteio', []) if filtros else []
        
        while len(apostas) < qtd_apostas and tentativas < max_tentativas:
            tentativas += 1
            # Selecionar aleatoriamente e ordenar
            aposta = tuple(sorted(random.sample(pool_valido, qtd_dezenas_por_aposta)))
            
            if apostas and aposta in apostas:
                continue
                
            # --- VALIDAÇÕES DOS FILTROS ESTRATÉGICOS ---
            
            # 1. Repetições do concurso anterior (ex: '2')
            if f_rep and f_rep != '' and f_rep != 'manual':
                maxRep = int(f_rep)
                rep = sum(1 for n in aposta if n in ultimo_sorteio)
                if rep != maxRep:
                    continue
                    
            # 2. Frequência (ex: '3Q-2M-2F')
            if f_frq and f_frq != '' and f_frq != 'manual' and 'Q' in f_frq:
                qMax = int(f_frq.split('Q')[0])
                mMax = int(f_frq.split('-')[1].split('M')[0])
                fMax = int(f_frq.split('-')[2].split('F')[0])
                q = m = f = 0
                for n in aposta:
                    if n in quentes: q += 1
                    elif n in frias: f += 1
                    else: m += 1
                if q != qMax or m != mMax or f != fMax:
                    continue
                    
            # 2. Pares e Ímpares
            if f_par and f_par != '' and f_par != 'manual' and 'P' in f_par:
                maxP = int(f_par.split('P')[0])
                maxI = int(f_par.split('-')[1].split('I')[0])
                p = sum(1 for n in aposta if n % 2 == 0)
                if p != maxP or (len(aposta) - p) != maxI:
                    continue
                    
            # 3. Somas (Ex: '70-90')
            if f_som and f_som != '' and f_som != 'manual':
                try:
                    s_min, s_max = map(int, f_som.split('-'))
                    soma_total = sum(aposta)
                    if not (s_min <= soma_total <= s_max):
                        continue
                except:
                    pass
                    
            # 6. Sequências (Ex: 'Nenhuma', '2', '3')
            if f_seq and f_seq != '' and f_seq != 'manual':
                maior_seq = 1
                seq_atual = 1
                for i in range(1, len(aposta)):
                    if aposta[i] == aposta[i-1] + 1:
                        seq_atual += 1
                        if seq_atual > maior_seq:
                            maior_seq = seq_atual
                    else:
                        seq_atual = 1
                
                if str(f_seq).lower() == 'nenhuma' or str(f_seq) == '1':
                    if maior_seq > 1:
                        continue
                else:
                    try:
                        max_seq_permitida = int(f_seq)
                        if maior_seq != max_seq_permitida:
                            continue
                    except:
                        pass
            
            # 7. Distância de Linhas (ex: '3-2-1-1')
            if f_lin and f_lin != '' and f_lin != 'manual' and '-' in f_lin:
                l = [0, 0, 0, 0]
                for n in aposta:
                    if n <= 10: l[0] += 1
                    elif n <= 20: l[1] += 1
                    elif n <= 30: l[2] += 1
                    else: l[3] += 1
                # Formatando a linha sorteada em ex: '3-2-1-1'
                l_filtered = sorted([x for x in l if x > 0], reverse=True)
                lin_str = '-'.join(map(str, l_filtered))
                if lin_str != f_lin:
                    continue
                        
            apostas.add(aposta)
            
        meses_nomes = ['', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
        
        # Converte set de tuples para list de dicts formatado para o frontend (igual Aba 2)
        resultado_apostas = []
        for a in apostas:
            mes_n = random.randint(1, 12) if str(mes_input) == 'aleatorio' else int(mes_input)
            resultado_apostas.append({
                'dezenas': list(a),
                'mes_num': mes_n,
                'mes_nome': meses_nomes[mes_n]
            })
            
        return {
            'sucesso': True,
            'apostas': resultado_apostas,
            'pool_tamanho': tamanho_pool,
            'pool_dezenas': pool_valido,
            'combinacoes_possiveis': max_comb
        }
