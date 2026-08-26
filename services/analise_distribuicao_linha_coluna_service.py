"""
Service de Análise de Distribuição por Linha e Coluna
Sistema Dia de Sorte - Análise completa com clusters, probabilidades e recomendações
+ Análise do Volante com filtros personalizados
"""

from models.sorteio import Sorteio
from collections import defaultdict, Counter
import statistics


class AnaliseDistribuicaoLinhaColuna:
    """
    Análise completa de distribuição de dezenas por linha e coluna
    LINHA: Grupos de 1-7, 8-14, 15-21, 22-28, 29-31
    COLUNA: Posições verticais 1-5 no volante
    """

    # Mapeamento de dezenas para LINHAS (horizontal no volante)
    LINHAS = {
        1: list(range(1, 8)),    # Linha 1: 01-07
        2: list(range(8, 15)),   # Linha 2: 08-14
        3: list(range(15, 22)),  # Linha 3: 15-21
        4: list(range(22, 29)),  # Linha 4: 22-28
        5: list(range(29, 32))   # Linha 5: 29-31
    }

    # Mapeamento de dezenas para COLUNAS (vertical no volante)
    COLUNAS = {
        1: [1, 8, 15, 22, 29],   # Coluna 1
        2: [2, 9, 16, 23, 30],   # Coluna 2
        3: [3, 10, 17, 24, 31],  # Coluna 3
        4: [4, 11, 18, 25],      # Coluna 4
        5: [5, 12, 19, 26],      # Coluna 5
        6: [6, 13, 20, 27],      # Coluna 6
        7: [7, 14, 21, 28]       # Coluna 7
    }

    @staticmethod
    def obter_linha(dezena):
        """Retorna o número da linha (1-5) onde a dezena está localizada"""
        for linha, dezenas in AnaliseDistribuicaoLinhaColuna.LINHAS.items():
            if dezena in dezenas:
                return linha
        return None

    @staticmethod
    def obter_coluna(dezena):
        """Retorna o número da coluna (1-7) onde a dezena está localizada"""
        for coluna, dezenas in AnaliseDistribuicaoLinhaColuna.COLUNAS.items():
            if dezena in dezenas:
                return coluna
        return None

    @staticmethod
    def calcular_distribuicao_historica(tipo='linha'):
        """
        Calcula distribuição histórica completa
        tipo: 'linha' ou 'coluna'
        """
        sorteios = Sorteio.query.order_by(Sorteio.concurso.desc()).all()

        distribuicao = defaultdict(int)
        total_sorteios = len(sorteios)

        for sorteio in sorteios:
            dezenas = sorteio.get_posicoes_lista()

            posicoes_encontradas = set()
            for dezena in dezenas:
                if tipo == 'linha':
                    pos = AnaliseDistribuicaoLinhaColuna.obter_linha(dezena)
                else:
                    pos = AnaliseDistribuicaoLinhaColuna.obter_coluna(dezena)

                if pos:
                    posicoes_encontradas.add(pos)

            for pos in posicoes_encontradas:
                distribuicao[pos] += 1

        # Formatar resultado
        dados = []
        for pos in sorted(distribuicao.keys()):
            dados.append({
                'posicao': pos,
                'frequencia': distribuicao[pos],
                'percentual': round((distribuicao[pos] / total_sorteios) * 100, 2) if total_sorteios > 0 else 0
            })

        return {
            'tipo': tipo,
            'total_sorteios': total_sorteios,
            'distribuicao': dados,
            'frequencias': {str(item['posicao']): item['frequencia'] for item in dados}
        }

    @staticmethod
    def obter_top3(tipo='linha'):
        """Retorna TOP 3 linhas ou colunas mais frequentes"""
        dados = AnaliseDistribuicaoLinhaColuna.calcular_distribuicao_historica(tipo)
        distribuicao = sorted(dados['distribuicao'], key=lambda x: x['frequencia'], reverse=True)

        return {
            'tipo': tipo,
            'top3': distribuicao[:3]
        }

    @staticmethod
    def calcular_insight_por_periodo(tipo='linha', ultimos=100):
        """Gera insight inteligente baseado em período recente"""
        sorteios = Sorteio.query.order_by(Sorteio.concurso.desc()).limit(ultimos).all()

        distribuicao_recente = defaultdict(int)

        for sorteio in sorteios:
            dezenas = sorteio.get_posicoes_lista()
            posicoes_encontradas = set()

            for dezena in dezenas:
                pos = AnaliseDistribuicaoLinhaColuna.obter_linha(dezena) if tipo == 'linha' else AnaliseDistribuicaoLinhaColuna.obter_coluna(dezena)
                if pos:
                    posicoes_encontradas.add(pos)

            for pos in posicoes_encontradas:
                distribuicao_recente[pos] += 1

        if not distribuicao_recente:
            return {
                'tipo': tipo,
                'periodo': ultimos,
                'insight': 'Nenhum dado disponível',
                'mais_frequente': None,
                'menos_frequente': None
            }

        mais_frequente = max(distribuicao_recente, key=distribuicao_recente.get)
        menos_frequente = min(distribuicao_recente, key=distribuicao_recente.get)

        tipo_nome = "Linha" if tipo == 'linha' else "Coluna"

        insight = f"{tipo_nome} {mais_frequente} apareceu {distribuicao_recente[mais_frequente]} vezes nos últimos {len(sorteios)} sorteios ({round((distribuicao_recente[mais_frequente]/len(sorteios))*100, 1)}%). "
        insight += f"{tipo_nome} {menos_frequente} está menos ativa com apenas {distribuicao_recente[menos_frequente]} aparições."

        return {
            'tipo': tipo,
            'periodo': ultimos,
            'insight': insight,
            'mais_frequente': mais_frequente,
            'menos_frequente': menos_frequente
        }

    @staticmethod
    def identificar_regioes_quentes(tipo='linha'):
        """Identifica regiões quentes baseado nos últimos 50 sorteios"""
        sorteios = Sorteio.query.order_by(Sorteio.concurso.desc()).limit(50).all()

        distribuicao = defaultdict(int)

        for sorteio in sorteios:
            dezenas = sorteio.get_posicoes_lista()
            posicoes_encontradas = set()

            for dezena in dezenas:
                pos = AnaliseDistribuicaoLinhaColuna.obter_linha(dezena) if tipo == 'linha' else AnaliseDistribuicaoLinhaColuna.obter_coluna(dezena)
                if pos:
                    posicoes_encontradas.add(pos)

            for pos in posicoes_encontradas:
                distribuicao[pos] += 1

        if not distribuicao:
            return {'tipo': tipo, 'quentes': [], 'frias': [], 'detalhes': []}

        media = statistics.mean(distribuicao.values())
        quentes = [pos for pos, freq in distribuicao.items() if freq > media]
        frias = [pos for pos, freq in distribuicao.items() if freq < media]

        return {
            'tipo': tipo,
            'quentes': sorted(quentes),
            'frias': sorted(frias),
            'detalhes': [{'posicao': pos, 'frequencia': freq} for pos, freq in sorted(distribuicao.items())]
        }

    @staticmethod
    def gerar_mapa_calor(tipo='linha'):
        """Gera dados para mapa de calor"""
        dados = AnaliseDistribuicaoLinhaColuna.calcular_distribuicao_historica(tipo)

        mapa = []
        for item in dados['distribuicao']:
            intensidade = min(100, int((item['frequencia'] / dados['total_sorteios']) * 1000)) if dados['total_sorteios'] > 0 else 0
            mapa.append({
                'posicao': item['posicao'],
                'valor': item['frequencia'],
                'intensidade': intensidade
            })

        return {'tipo': tipo, 'mapa': mapa}

    @staticmethod
    def analise_comparativa():
        """Análise comparativa completa Linha x Coluna"""
        linhas = AnaliseDistribuicaoLinhaColuna.calcular_distribuicao_historica('linha')
        colunas = AnaliseDistribuicaoLinhaColuna.calcular_distribuicao_historica('coluna')

        # Correlação
        freq_linhas = [item['frequencia'] for item in linhas['distribuicao']]
        freq_colunas = [item['frequencia'] for item in colunas['distribuicao']]

        # Presença cruzada
        sorteios = Sorteio.query.all()

        combinacoes = defaultdict(int)
        for sorteio in sorteios:
            dezenas = sorteio.get_posicoes_lista()
            linhas_presentes = set()
            colunas_presentes = set()

            for dezena in dezenas:
                linha = AnaliseDistribuicaoLinhaColuna.obter_linha(dezena)
                coluna = AnaliseDistribuicaoLinhaColuna.obter_coluna(dezena)
                if linha:
                    linhas_presentes.add(linha)
                if coluna:
                    colunas_presentes.add(coluna)

            for l in linhas_presentes:
                for c in colunas_presentes:
                    combinacoes[f"L{l}_C{c}"] += 1

        top_combinacoes = sorted(combinacoes.items(), key=lambda x: x[1], reverse=True)[:5]

        return {
            'linhas': linhas,
            'colunas': colunas,
            'top_combinacoes': [{'combinacao': k, 'frequencia': v} for k, v in top_combinacoes]
        }

    @staticmethod
    def analise_desvio_padrao(tipo='linha'):
        """Análise de desvio padrão e comportamento esperado"""
        dados = AnaliseDistribuicaoLinhaColuna.calcular_distribuicao_historica(tipo)
        frequencias = [item['frequencia'] for item in dados['distribuicao']]

        if not frequencias:
            return {'tipo': tipo, 'media': 0, 'desvio_padrao': 0, 'anomalias': []}

        media = statistics.mean(frequencias)
        desvio = statistics.stdev(frequencias) if len(frequencias) > 1 else 0

        anomalias = []
        for item in dados['distribuicao']:
            z_score = (item['frequencia'] - media) / desvio if desvio > 0 else 0
            if abs(z_score) > 2:
                anomalias.append({
                    'posicao': item['posicao'],
                    'frequencia': item['frequencia'],
                    'z_score': round(z_score, 2),
                    'status': 'Acima do esperado' if z_score > 0 else 'Abaixo do esperado'
                })

        return {
            'tipo': tipo,
            'media': round(media, 2),
            'desvio_padrao': round(desvio, 2),
            'anomalias': anomalias
        }

    @staticmethod
    def clusterizar_padroes(n_clusters=3):
        """Clusterização de padrões de sorteios"""
        sorteios = Sorteio.query.limit(500).all()

        if not sorteios:
            return {'clusters': [], 'total_analisados': 0}

        # Criar matriz de features: contagem de linhas e colunas
        X = []
        for sorteio in sorteios:
            dezenas = sorteio.get_posicoes_lista()

            contagem_linhas = [0] * 5
            contagem_colunas = [0] * 7

            for dezena in dezenas:
                linha = AnaliseDistribuicaoLinhaColuna.obter_linha(dezena)
                coluna = AnaliseDistribuicaoLinhaColuna.obter_coluna(dezena)

                if linha:
                    contagem_linhas[linha - 1] += 1
                if coluna:
                    contagem_colunas[coluna - 1] += 1

            X.append(contagem_linhas + contagem_colunas)

        import numpy as np
        from sklearn.cluster import KMeans

        X = np.array(X)
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        labels = kmeans.fit_predict(X)

        clusters = defaultdict(list)
        for idx, label in enumerate(labels):
            clusters[int(label)].append(idx)

        resultado = []
        for cluster_id, indices in clusters.items():
            resultado.append({
                'cluster': cluster_id,
                'tamanho': len(indices),
                'percentual': round((len(indices) / len(labels)) * 100, 2)
            })

        return {'clusters': resultado, 'total_analisados': len(sorteios)}

    @staticmethod
    def calcular_probabilidade_proxima(tipo='linha'):
        """Probabilidade da próxima composição"""
        dados = AnaliseDistribuicaoLinhaColuna.calcular_distribuicao_historica(tipo)
        total = sum(item['frequencia'] for item in dados['distribuicao'])

        probabilidades = []
        for item in dados['distribuicao']:
            prob = (item['frequencia'] / total) * 100 if total > 0 else 0
            probabilidades.append({
                'posicao': item['posicao'],
                'probabilidade': round(prob, 2)
            })

        return {
            'tipo': tipo,
            'probabilidades': sorted(probabilidades, key=lambda x: x['probabilidade'], reverse=True)
        }

    @staticmethod
    def gerar_alertas_anomalias():
        """Detecta e alerta sobre anomalias"""
        alertas = []

        # Verificar linhas
        desvio_linhas = AnaliseDistribuicaoLinhaColuna.analise_desvio_padrao('linha')
        for anomalia in desvio_linhas['anomalias']:
            alertas.append({
                'tipo': 'Linha',
                'posicao': anomalia['posicao'],
                'mensagem': f"Linha {anomalia['posicao']}: {anomalia['status']} (Z-score: {anomalia['z_score']})",
                'severidade': 'alta' if abs(anomalia['z_score']) > 3 else 'media'
            })

        # Verificar colunas
        desvio_colunas = AnaliseDistribuicaoLinhaColuna.analise_desvio_padrao('coluna')
        for anomalia in desvio_colunas['anomalias']:
            alertas.append({
                'tipo': 'Coluna',
                'posicao': anomalia['posicao'],
                'mensagem': f"Coluna {anomalia['posicao']}: {anomalia['status']} (Z-score: {anomalia['z_score']})",
                'severidade': 'alta' if abs(anomalia['z_score']) > 3 else 'media'
            })

        return {'alertas': alertas, 'total': len(alertas)}

    @staticmethod
    def gerar_recomendacao_final():
        """Recomendação final baseada em todas as análises"""
        insight_linha = AnaliseDistribuicaoLinhaColuna.calcular_insight_por_periodo('linha', 50)
        insight_coluna = AnaliseDistribuicaoLinhaColuna.calcular_insight_por_periodo('coluna', 50)

        quentes_linha = AnaliseDistribuicaoLinhaColuna.identificar_regioes_quentes('linha')
        quentes_coluna = AnaliseDistribuicaoLinhaColuna.identificar_regioes_quentes('coluna')

        recomendacao = f"**Recomendação Estratégica:**\n\n"
        recomendacao += f"📍 **Linhas prioritárias:** {', '.join(map(str, quentes_linha['quentes']))}\n"
        recomendacao += f"📍 **Colunas prioritárias:** {', '.join(map(str, quentes_coluna['quentes']))}\n\n"

        if insight_linha.get('mais_frequente'):
            recomendacao += f"🔥 Linha {insight_linha['mais_frequente']} está em alta tendência recente.\n"
        if insight_coluna.get('mais_frequente'):
            recomendacao += f"🔥 Coluna {insight_coluna['mais_frequente']} mostra forte presença.\n\n"

        recomendacao += f"**Sugestão:** Combine dezenas das linhas e colunas quentes para maximizar chances baseadas em padrões históricos."

        return {
            'recomendacao': recomendacao,
            'linhas_recomendadas': quentes_linha['quentes'],
            'colunas_recomendadas': quentes_coluna['quentes']
        }

    @staticmethod
    def obter_analise_completa():
        """Retorna análise completa consolidada"""
        return {
            'distribuicao_linha': AnaliseDistribuicaoLinhaColuna.calcular_distribuicao_historica('linha'),
            'distribuicao_coluna': AnaliseDistribuicaoLinhaColuna.calcular_distribuicao_historica('coluna'),
            'top3_linhas': AnaliseDistribuicaoLinhaColuna.obter_top3('linha'),
            'top3_colunas': AnaliseDistribuicaoLinhaColuna.obter_top3('coluna'),
            'insight_linha': AnaliseDistribuicaoLinhaColuna.calcular_insight_por_periodo('linha'),
            'insight_coluna': AnaliseDistribuicaoLinhaColuna.calcular_insight_por_periodo('coluna'),
            'regioes_quentes_linha': AnaliseDistribuicaoLinhaColuna.identificar_regioes_quentes('linha'),
            'regioes_quentes_coluna': AnaliseDistribuicaoLinhaColuna.identificar_regioes_quentes('coluna'),
            'mapa_calor_linha': AnaliseDistribuicaoLinhaColuna.gerar_mapa_calor('linha'),
            'mapa_calor_coluna': AnaliseDistribuicaoLinhaColuna.gerar_mapa_calor('coluna'),
            'comparativa': AnaliseDistribuicaoLinhaColuna.analise_comparativa(),
            'desvio_linha': AnaliseDistribuicaoLinhaColuna.analise_desvio_padrao('linha'),
            'desvio_coluna': AnaliseDistribuicaoLinhaColuna.analise_desvio_padrao('coluna'),
            'clusters': AnaliseDistribuicaoLinhaColuna.clusterizar_padroes(),
            'probabilidade_linha': AnaliseDistribuicaoLinhaColuna.calcular_probabilidade_proxima('linha'),
            'probabilidade_coluna': AnaliseDistribuicaoLinhaColuna.calcular_probabilidade_proxima('coluna'),
            'alertas': AnaliseDistribuicaoLinhaColuna.gerar_alertas_anomalias(),
            'recomendacao': AnaliseDistribuicaoLinhaColuna.gerar_recomendacao_final()
        }

    # =========================================================================
    # NOVO: MÉTODO PARA ANÁLISE DO VOLANTE COM FILTROS PERSONALIZADOS
    # =========================================================================

    @staticmethod
    def obter_analise_volante(modo='coluna', filtro_tipo='todos', concurso_unico=None,
                              intervalo_inicio=None, intervalo_fim=None, concursos_ids=None):
        """
        Análise do volante com filtros personalizados

        Args:
            modo: 'linha' ou 'coluna'
            filtro_tipo: 'todos', 'unico', 'intervalo', 'multiplos'
            concurso_unico: Número do concurso único (quando filtro_tipo='unico')
            intervalo_inicio: Concurso inicial (quando filtro_tipo='intervalo')
            intervalo_fim: Concurso final (quando filtro_tipo='intervalo')
            concursos_ids: Lista de IDs de concursos (quando filtro_tipo='multiplos')

        Returns:
            dict: Análise completa do volante
        """
        # Construir query de acordo com o filtro
        query = Sorteio.query

        if filtro_tipo == 'unico' and concurso_unico:
            query = query.filter(Sorteio.concurso == concurso_unico)
        elif filtro_tipo == 'intervalo' and intervalo_inicio and intervalo_fim:
            query = query.filter(Sorteio.concurso.between(intervalo_inicio, intervalo_fim))
        elif filtro_tipo == 'multiplos' and concursos_ids:
            query = query.filter(Sorteio.concurso.in_(concursos_ids))

        sorteios = query.order_by(Sorteio.concurso).all()

        if not sorteios:
            return {'erro': 'Nenhum sorteio encontrado com os filtros fornecidos'}

        # Estruturas de análise
        frequencia_por_posicao = defaultdict(int)
        frequencia_por_dezena = Counter()
        dezenas_por_posicao = defaultdict(list)
        concursos_analisados = []

        # Processar sorteios
        for sorteio in sorteios:
            concursos_analisados.append(sorteio.concurso)
            dezenas = sorteio.get_posicoes_lista()

            # Contar frequência de cada dezena
            for dezena in dezenas:
                frequencia_por_dezena[dezena] += 1

            # Mapear para linha ou coluna
            posicoes_encontradas = set()
            for dezena in dezenas:
                if modo == 'linha':
                    posicao = AnaliseDistribuicaoLinhaColuna.obter_linha(dezena)
                else:
                    posicao = AnaliseDistribuicaoLinhaColuna.obter_coluna(dezena)

                if posicao:
                    posicoes_encontradas.add(posicao)
                    dezenas_por_posicao[posicao].append(dezena)

            # Contar frequência de cada posição
            for posicao in posicoes_encontradas:
                frequencia_por_posicao[posicao] += 1

        # TOP 3 posições mais utilizadas
        top3_posicoes = sorted(
            frequencia_por_posicao.items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]

        # TOP 3 dezenas de cada TOP 3 posição
        top3_dezenas_por_posicao = {}
        for posicao, freq in top3_posicoes:
            dezenas_nesta_posicao = dezenas_por_posicao[posicao]
            contagem = Counter(dezenas_nesta_posicao)
            top3_dez = contagem.most_common(3)
            top3_dezenas_por_posicao[posicao] = [
                {'dezena': dez, 'frequencia': freq_dez}
                for dez, freq_dez in top3_dez
            ]

        # Mais e menos destacadas
        mais_destacada = max(frequencia_por_posicao.items(), key=lambda x: x[1]) if frequencia_por_posicao else (None, 0)
        menos_destacada = min(frequencia_por_posicao.items(), key=lambda x: x[1]) if frequencia_por_posicao else (None, 0)

        # Frequências para o volante visual
        volante_frequencias = {dez: frequencia_por_dezena[dez] for dez in range(1, 32)}

        # Gerar volante visual (estrutura 3x10 para o frontend)
        volante_visual = AnaliseDistribuicaoLinhaColuna.gerar_volante_visual_3x10(volante_frequencias)

        # Insights inteligentes
        insights = AnaliseDistribuicaoLinhaColuna.gerar_insights_volante(
            modo=modo,
            top3_posicoes=top3_posicoes,
            total_sorteios=len(sorteios),
            mais_destacada=mais_destacada,
            menos_destacada=menos_destacada
        )

        return {
            'modo': modo,
            'filtro_aplicado': filtro_tipo,
            'total_sorteios_analisados': len(sorteios),
            'primeiro_concurso': concursos_analisados[0] if concursos_analisados else None,
            'ultimo_concurso': concursos_analisados[-1] if concursos_analisados else None,
            'volante_visual': volante_visual,
            'volante_frequencias': volante_frequencias,
            'top3_posicoes': [
                {
                    'posicao': pos,
                    'frequencia': freq,
                    'percentual': round((freq / len(sorteios)) * 100, 2),
                    'top3_dezenas': top3_dezenas_por_posicao.get(pos, [])
                }
                for pos, freq in top3_posicoes
            ],
            'mais_destacada': {
                'posicao': mais_destacada[0],
                'frequencia': mais_destacada[1],
                'percentual': round((mais_destacada[1] / len(sorteios)) * 100, 2) if len(sorteios) > 0 else 0
            } if mais_destacada[0] is not None else None,
            'menos_destacada': {
                'posicao': menos_destacada[0],
                'frequencia': menos_destacada[1],
                'percentual': round((menos_destacada[1] / len(sorteios)) * 100, 2) if len(sorteios) > 0 else 0
            } if menos_destacada[0] is not None else None,
            'insights': insights
        }

    @staticmethod
    def gerar_volante_visual_3x10(frequencias):
        """
        Gera estrutura visual do volante 3x10 (formato do frontend)
        Linha 1: 01-10
        Linha 2: 11-20
        Linha 3: 21-30
        Linha 4: 31 + 9 vazios
        """
        volante = []

        # Linha 1: 01-10
        volante.append([
            {'numero': i, 'frequencia': frequencias.get(i, 0)}
            for i in range(1, 11)
        ])

        # Linha 2: 11-20
        volante.append([
            {'numero': i, 'frequencia': frequencias.get(i, 0)}
            for i in range(11, 21)
        ])

        # Linha 3: 21-30
        volante.append([
            {'numero': i, 'frequencia': frequencias.get(i, 0)}
            for i in range(21, 31)
        ])

        # Linha 4: 31 + 9 células vazias
        linha_4 = [{'numero': 31, 'frequencia': frequencias.get(31, 0)}]
        linha_4.extend([{'numero': None, 'frequencia': 0} for _ in range(9)])
        volante.append(linha_4)

        return volante

    @staticmethod
    def gerar_insights_volante(modo, top3_posicoes, total_sorteios, mais_destacada, menos_destacada):
        """Gera insights inteligentes para a análise do volante"""
        insights = []
        tipo_nome = "Linha" if modo == 'linha' else "Coluna"

        # Insight 1: Análise baseada no total
        insights.append(f"Análise baseada em {total_sorteios} sorteio(s) histórico(s).")

        # Insight 2: TOP 1 posição
        if top3_posicoes:
            top1_pos, top1_freq = top3_posicoes[0]
            percent = round((top1_freq / total_sorteios) * 100, 2) if total_sorteios > 0 else 0
            insights.append(
                f"🏆 {tipo_nome} {top1_pos} é a mais frequente com {percent}% de aparições."
            )

        # Insight 3: Distribuição equilibrada ou concentrada
        if len(top3_posicoes) >= 3:
            top1_freq = top3_posicoes[0][1]
            top3_freq = top3_posicoes[2][1]
            if top1_freq > top3_freq * 1.5:
                insights.append(
                    f"⚠️ Distribuição CONCENTRADA: {tipo_nome} {top3_posicoes[0][0]} domina fortemente."
                )
            else:
                insights.append(
                    f"✅ Distribuição EQUILIBRADA entre as principais {tipo_nome.lower()}s."
                )

        # Insight 4: Diferença entre mais e menos destacada
        if mais_destacada[0] is not None and menos_destacada[0] is not None:
            diferenca = mais_destacada[1] - menos_destacada[1]
            insights.append(
                f"📊 Diferença de {diferenca} aparições entre a {tipo_nome.lower()} mais ativa ({mais_destacada[0]}) e menos ativa ({menos_destacada[0]})."
            )

        return insights
