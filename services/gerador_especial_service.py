import random
from itertools import combinations
from models.sorteio import Sorteio, db


class GeradorEspecialService:
    """Serviço para geração de apostas com análises estatísticas consolidadas."""
    
    MONTHS_ABBR = {
        1: 'JAN', 2: 'FEV', 3: 'MAR', 4: 'ABR', 5: 'MAI', 6: 'JUN',
        7: 'JUL', 8: 'AGO', 9: 'SET', 10: 'OUT', 11: 'NOV', 12: 'DEZ'
    }
    
    MONTHS_FULL = {
        1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho',
        7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
    }

    @staticmethod
    def get_last_draw():
        """Busca o último sorteio do banco."""
        resultado = Sorteio.query.order_by(Sorteio.id.desc()).first()
        if resultado:
            posicoes = [
                resultado.posicao_1, resultado.posicao_2, resultado.posicao_3,
                resultado.posicao_4, resultado.posicao_5, resultado.posicao_6,
                resultado.posicao_7
            ]
            mes_num = resultado.mes_sorte
            return {
                'concurso': resultado.concurso,
                'data': resultado.data_sorteio.strftime('%d/%m/%Y') if resultado.data_sorteio else 'N/A',
                'dezenas': posicoes,
                'mes_num': mes_num,
                'mes_nome': GeradorEspecialService.MONTHS_FULL.get(mes_num, 'N/A')
            }
        return None

    @staticmethod
    def get_month_stats():
        """Retorna mês mais atrasado e mais frequente."""
        try:
            # 1. Mais Frequente (Total)
            frequencia = db.session.query(
                Sorteio.mes_sorte, db.func.count(Sorteio.mes_sorte)
            ).filter(
                Sorteio.mes_sorte >= 1, 
                Sorteio.mes_sorte <= 12
            ).group_by(Sorteio.mes_sorte).all()
            
            # Ordenar por contagem decrescente
            if frequencia:
                mais_frequente = sorted(frequencia, key=lambda x: x[1], reverse=True)[0][0]
            else:
                mais_frequente = 1 # Fallback Jan

            # 2. Mais Atrasado
            # Busca o último sorteio de cada mês
            ultimos_sorteios = {}
            # Otimização: Pegar todos os resultados ordenados decrescente e parar quando encontrar todos os 12 meses (ou varrer últimos 100)
            sorteios_recentes = Sorteio.query.with_entities(Sorteio.concurso, Sorteio.mes_sorte).order_by(Sorteio.concurso.desc()).limit(200).all()
            
            ultimo_concurso = sorteios_recentes[0].concurso if sorteios_recentes else 0
            
            for concurso, mes in sorteios_recentes:
                if mes not in ultimos_sorteios:
                    ultimos_sorteios[mes] = concurso
                if len(ultimos_sorteios) == 12:
                    break
            
            # Calcular atraso (Concurso Atual - Último Concurso do Mês)
            atrasos = []
            for m in range(1, 13):
                ultimo = ultimos_sorteios.get(m, 0)
                atraso = ultimo_concurso - ultimo
                atrasos.append((m, atraso))
            
            # Ordenar por atraso decrescente
            mais_atrasado = sorted(atrasos, key=lambda x: x[1], reverse=True)[0][0]

            return {
                'atrasado': mais_atrasado,
                'frequente': mais_frequente
            }
        except Exception as e:
            print(f"Erro ao calcular estatísticas de meses: {e}")
            return {'atrasado': 1, 'frequente': 1}

    @staticmethod
    def classify_number(num):
        """Classifica número como baixo (01-10), médio (11-20) ou alto (21-31)."""
        if 1 <= num <= 10:
            return 'baixo'
        elif 11 <= num <= 20:
            return 'medio'
        else:
            return 'alto'

    @staticmethod
    def get_number_digit(num):
        """Retorna o dígito inicial do número."""
        if 1 <= num <= 9:
            return 0
        elif 10 <= num <= 19:
            return 1
        elif 20 <= num <= 29:
            return 2
        else:
            return 3

    @staticmethod
    def _calcular_numeros_quentes(limite_concursos=20, top_k=10):
        """Calcula os números mais frequentes dos últimos N concursos."""
        ultimos = Sorteio.query.order_by(Sorteio.id.desc()).limit(limite_concursos).all()
        frequencia = {i: 0 for i in range(1, 32)}
        
        for sorteio in ultimos:
            for num in [
                sorteio.posicao_1, sorteio.posicao_2, sorteio.posicao_3,
                sorteio.posicao_4, sorteio.posicao_5, sorteio.posicao_6,
                sorteio.posicao_7
            ]:
                frequencia[num] += 1
        
        # Ordenar por frequência (decrescente) e pegar os top_k
        ordenados = sorted(frequencia.items(), key=lambda x: x[1], reverse=True)
        return [num for num, freq in ordenados[:top_k]]

    @staticmethod
    def is_hot_number(num, hot_numbers=None):
        """Verifica se número é 'quente'."""
        if hot_numbers is None:
            # Fallback seguro, mas idealmente deve ser passado
            hot_numbers = GeradorEspecialService._calcular_numeros_quentes()
        return num in hot_numbers

    @staticmethod
    def generate_apostas(quantidade, dezenas_por_jogo, mes_selecionado, faixa, paridade, temperatura, 
                         desdobrar_ultimo=False, usar_nucleo=False, numeros_nucleo='', ordenacao='crescente'):
        """
        Gera apostas com Estratégia em Cascata (3 Níveis):
        1. Rigoroso: Respeita todos os filtros e fonte de números.
        2. Relaxado: Se falhar, ignora filtros estatísticos (Faixa, Paridade, Temp).
        3. Expandido: Se ainda falhar (pool insuficiente), expande para usar números de 1-31.
        """
        if not mes_selecionado:
            return {'sucesso': False, 'mensagem': 'Mês obrigatório não selecionado'}
        
        # --- Preparação dos Pools e Núcleo ---
        
        # 1. Núcleo Fixo
        nucleo = []
        if usar_nucleo and numeros_nucleo:
            try:
                nucleo = [int(n.strip()) for n in numeros_nucleo.split(',') if n.strip().isdigit()]
                nucleo = [n for n in nucleo if 1 <= n <= 31]
                if len(nucleo) >= dezenas_por_jogo:
                   return {'sucesso': False, 'mensagem': f'Núcleo ({len(nucleo)}) maior ou igual ao tamanho do jogo ({dezenas_por_jogo}).'}
            except ValueError:
                return {'sucesso': False, 'mensagem': 'Formato de núcleo inválido.'}

        # 2. Fonte de Dados (Pool)
        pool_geral = list(range(1, 32))
        pool_ultimo = []
        
        if desdobrar_ultimo:
            ultimo = GeradorEspecialService.get_last_draw()
            if ultimo and ultimo['dezenas']:
                pool_ultimo = ultimo['dezenas']
            else:
                 # Se falhar ao pegar último, fallback silencioso ou aviso? 
                 # Melhor avisar.
                 return {'sucesso': False, 'mensagem': 'Não foi possível obter o último sorteio para desdobramento.'}
        
        # 3. Números Quentes (cache)
        numeros_quentes = []
        if temperatura != 'livre':
            # Assumimos que a rota ou script já proveu o contexto
            numeros_quentes = GeradorEspecialService._calcular_numeros_quentes()

        # --- Estratégia de Geração ---

        apostas_finais = []
        assinaturas = set()
        
        # Definição dos Estágios de Tentativa
        # Cada estágio define: (Pool Base, Usar Filtros Estatísticos?)
        estagios = []
        
        # Estágio 1: Rigoroso
        # Se desdobrar_ultimo, usa pool_ultimo. Se não, pool_geral.
        # Filtros ativos.
        pool_s1 = pool_ultimo if desdobrar_ultimo else pool_geral
        estagios.append({'nome': 'Rigoroso', 'pool': pool_s1, 'filtros': True})
        
        # Estágio 2: Relaxado (só se filtros não forem 'livre')
        # Mesmo pool, mas sem filtros.
        tem_filtros = (faixa != 'livre' or paridade != 'livre' or temperatura != 'livre')
        if tem_filtros:
            estagios.append({'nome': 'Relaxado', 'pool': pool_s1, 'filtros': False})
            
        # Estágio 3: Expandido (só se estiver usando desdobramento restrito)
        # Usa pool_geral (1-31), com ou sem filtros?
        # Se chegamos aqui, é porque o pool restrito falhou. Vamos tentar pool geral COM filtros primeiro?
        # Ou direto sem filtros para garantir? Vamos tentar COM filtros, depois SEM.
        if desdobrar_ultimo:
            estagios.append({'nome': 'Expandido (Com Filtros)', 'pool': pool_geral, 'filtros': True})
            if tem_filtros:
                estagios.append({'nome': 'Expandido (Sem Filtros)', 'pool': pool_geral, 'filtros': False})

        # Execução dos Estágios
        for estagio in estagios:
            if len(apostas_finais) >= quantidade:
                break
            
            pool_atual = [n for n in estagio['pool'] if n not in nucleo]
            usar_filtros = estagio['filtros']
            
            # Validação rápida de viabilidade do pool
            if len(pool_atual) + len(nucleo) < dezenas_por_jogo:
                continue # Pool impossível para este estágio, pula
                
            # Tentar gerar o restante das apostas
            tentativas_falhas = 0
            max_falhas = 500 # Se falhar 500x consecutivas em gerar UMA aposta válida, aborta estágio
            
            while len(apostas_finais) < quantidade and tentativas_falhas < max_falhas:
                
                # Construir aposta
                aposta = nucleo[:]
                temp_pool = list(pool_atual)
                random.shuffle(temp_pool) # Misturar para aleatoriedade
                
                sucesso_construcao = True
                
                while len(aposta) < dezenas_por_jogo:
                    if not temp_pool:
                        sucesso_construcao = False
                        break
                    
                    num = temp_pool.pop() # Remove para não repetir na construção
                    
                    # Validar Filtros Individuais (se ativos)
                    valido = True
                    if usar_filtros:
                        # Faixa
                        if faixa != 'livre':
                            c = GeradorEspecialService.classify_number(num)
                            if faixa == 'baixas' and c != 'baixo': valido = False
                            elif faixa == 'medias' and c != 'medio': valido = False
                            elif faixa == 'altas' and c != 'alto': valido = False
                            elif faixa == 'baixas_medias' and c == 'alto': valido = False
                            elif faixa == 'baixas_altas' and c == 'medio': valido = False
                            elif faixa == 'medias_altas' and c == 'baixo': valido = False
                        
                        # Temperatura (apenas se num passou em faixa)
                        if valido and temperatura != 'livre':
                            quente = num in numeros_quentes
                            if temperatura == 'quentes' and not quente: valido = False
                            elif temperatura == 'frias' and quente: valido = False
                    
                    if valido:
                        aposta.append(num)
                
                if not sucesso_construcao:
                    tentativas_falhas += 1
                    continue
                
                # Validar Filtros Globais (Paridade) na aposta completa
                if usar_filtros and paridade != 'livre':
                    pares = sum(1 for n in aposta if n % 2 == 0)
                    impares = len(aposta) - pares
                    valido_p = False
                    if paridade == 'pares' and impares == 0: valido_p = True
                    elif paridade == 'impares' and pares == 0: valido_p = True
                    elif paridade == '4x3' and ((pares==4 and impares==3) or (pares==3 and impares==4)): valido_p = True
                    elif paridade == '3x4' and ((pares==3 and impares==4) or (pares==4 and impares==3)): valido_p = True
                    
                    if not valido_p:
                        tentativas_falhas += 1
                        continue

                # Validar Duplicidade
                aposta_sorted = sorted(aposta)
                assinatura = '-'.join(map(str, aposta_sorted))
                
                if assinatura in assinaturas:
                    tentativas_falhas += 1 # Aposta repetida conta como falha para evitar loop infinito em espaços pequenos
                    continue
                
                # Sucesso! Adiciona
                assinaturas.add(assinatura)
                if ordenacao == 'crescente':
                    apostas_finais.append(aposta_sorted)
                else:
                    apostas_finais.append(aposta) # Ordem de geração (núcleo no inicio)
                
                tentativas_falhas = 0 # Reseta falhas pois conseguimos uma

        # Resultado
        if len(apostas_finais) < quantidade:
             return {
                'sucesso': False,
                'mensagem': f'Não foi possível gerar {quantidade} apostas. Tente reduzir o número de filtros ou o tamanho do núcleo. Geradas: {len(apostas_finais)}'
            }

        return {
            'sucesso': True,
            'apostas': apostas_finais,
            'quantidade': len(apostas_finais),
            'mes': GeradorEspecialService.MONTHS_FULL.get(mes_selecionado, 'N/A'),
            'mes_num': mes_selecionado
        }

    @staticmethod
    def exportar_txt(apostas, mes_abreviado):
        """Exporta apostas em formato TXT: dezenas + mês abreviado."""
        linhas = []
        for aposta in apostas:
            linha = ' '.join(f'{num:02d}' for num in aposta) + f' {mes_abreviado}'
            linhas.append(linha)
        return '\n'.join(linhas)

    @staticmethod
    def exportar_xlsx_data(apostas, mes_num, mes_nome, faixa, paridade, temperatura, valor_unitario, total):
        """Prepara dados para exportação XLSX."""
        return {
            'apostas': apostas,
            'mes': mes_nome,
            'estrategias': {
                'faixa': faixa,
                'paridade': paridade,
                'temperatura': temperatura
            },
            'quantidade': len(apostas),
            'valor_unitario': valor_unitario,
            'valor_total': total
        }

    @staticmethod
    def exportar_html(apostas, mes_nome, faixa, paridade, temperatura, valor_total):
        """Gera HTML para visualização."""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Gerador Especial - Apostas</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #D4B31A; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: center; }}
                th {{ background-color: #D4B31A; color: white; }}
                .info {{ margin: 10px 0; font-size: 14px; }}
            </style>
        </head>
        <body>
            <h1>Gerador Especial de Apostas - Comunidade de Sorte</h1>
            <div class="info">
                <p><strong>Mês:</strong> {mes_nome}</p>
                <p><strong>Estratégias:</strong> Faixa: {faixa} | Paridade: {paridade} | Temperatura: {temperatura}</p>
                <p><strong>Total de Apostas:</strong> {len(apostas)}</p>
                <p><strong>Valor Total:</strong> R$ {valor_total:.2f}</p>
            </div>
            <table>
                <tr>
                    <th>#</th>
                    <th>Dezenas</th>
                </tr>
        """
        for i, aposta in enumerate(apostas, 1):
            dezenas_str = ' '.join(f'{num:02d}' for num in aposta)
            html += f'<tr><td>{i}</td><td>{dezenas_str}</td></tr>'
        
        html += """
            </table>
        </body>
        </html>
        """
        return html
