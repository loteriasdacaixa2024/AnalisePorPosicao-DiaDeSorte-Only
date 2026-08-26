# Sistema: Análise por Posição - Dia de Sorte
# Desenvolvido para: Márcio Fernando Maia

from datetime import datetime
from models.shared import db


class Configuracao(db.Model):
    """
    Modelo para armazenar configurações do sistema
    """

    __tablename__ = 'configuracoes'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    chave = db.Column(db.String(100), unique=True, nullable=False, index=True)
    valor = db.Column(db.String(500), nullable=False)
    tipo = db.Column(db.String(50), nullable=False, default='string')  # string, float, int, boolean
    descricao = db.Column(db.String(500), nullable=True)

    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Configuracao {self.chave} = {self.valor}>'

    def to_dict(self):
        return {
            'id': self.id,
            'chave': self.chave,
            'valor': self.get_valor_convertido(),
            'valor_raw': self.valor,
            'tipo': self.tipo,
            'descricao': self.descricao,
            'criado_em': self.criado_em.strftime('%d/%m/%Y %H:%M:%S') if self.criado_em else None,
            'atualizado_em': self.atualizado_em.strftime('%d/%m/%Y %H:%M:%S') if self.atualizado_em else None
        }

    def get_valor_convertido(self):
        """Converte o valor string para o tipo apropriado"""
        if self.tipo == 'float':
            return float(self.valor)
        elif self.tipo == 'int':
            return int(self.valor)
        elif self.tipo == 'boolean':
            return self.valor.lower() in ('true', '1', 'yes', 'sim')
        else:
            return self.valor

    @staticmethod
    def criar_configuracoes_padrao():
        """Cria as configurações padrão do sistema se não existirem"""
        configuracoes_padrao = [
            {
                'chave': 'valor_aposta_minima',
                'valor': '2.50',
                'tipo': 'float',
                'descricao': 'Valor da aposta mínima (7 números) em reais'
            },
            {
                'chave': 'sistema_nome',
                'valor': 'Análise Dia de Sorte',
                'tipo': 'string',
                'descricao': 'Nome do sistema'
            },
            {
                'chave': 'sistema_versao',
                'valor': '2.0.0',
                'tipo': 'string',
                'descricao': 'Versão do sistema'
            },

            # ========================================================================
            # ANÁLISES PARA GERAR FECHAMENTO - ESTATÍSTICAS BÁSICAS (8)
            # ========================================================================
            {
                'chave': 'analise_atrasados',
                'valor': 'true',
                'tipo': 'boolean',
                'descricao': 'Números que estão há mais tempo sem sair'
            },
            {
                'chave': 'analise_quentes_frios',
                'valor': 'true',
                'tipo': 'boolean',
                'descricao': 'Números mais e menos sorteados recentemente'
            },
            {
                'chave': 'analise_numeros_devidos',
                'valor': 'true',
                'tipo': 'boolean',
                'descricao': 'Números com atraso acima da média'
            },
            {
                'chave': 'analise_frequencia',
                'valor': 'true',
                'tipo': 'boolean',
                'descricao': 'Análise de frequência geral de cada número'
            },
            {
                'chave': 'analise_probabilidade',
                'valor': 'true',
                'tipo': 'boolean',
                'descricao': 'Cálculo de probabilidades de saída'
            },
            {
                'chave': 'analise_media_atrasos',
                'valor': 'true',
                'tipo': 'boolean',
                'descricao': 'Cálculo da média de atrasos por número'
            },
            {
                'chave': 'analise_desvio_padrao',
                'valor': 'false',
                'tipo': 'boolean',
                'descricao': 'Análise de variância nos atrasos'
            },
            {
                'chave': 'analise_tendencias',
                'valor': 'true',
                'tipo': 'boolean',
                'descricao': 'Identificação de tendências de alta/baixa'
            },

            # ========================================================================
            # ANÁLISES PARA GERAR FECHAMENTO - PADRÕES NUMÉRICOS (10)
            # ========================================================================
            {
                'chave': 'analise_pares_impares',
                'valor': 'true',
                'tipo': 'boolean',
                'descricao': 'Proporção e padrões de números pares e ímpares'
            },
            {
                'chave': 'analise_primos_compostos',
                'valor': 'false',
                'tipo': 'boolean',
                'descricao': 'Análise de números primos vs compostos'
            },
            {
                'chave': 'analise_digito_inicial',
                'valor': 'true',
                'tipo': 'boolean',
                'descricao': 'Padrão do primeiro dígito dos números'
            },
            {
                'chave': 'analise_digito_final',
                'valor': 'true',
                'tipo': 'boolean',
                'descricao': 'Padrão do último dígito dos números'
            },
            {
                'chave': 'analise_soma_dezenas',
                'valor': 'true',
                'tipo': 'boolean',
                'descricao': 'Análise da soma total das dezenas'
            },
            {
                'chave': 'analise_faixas_numericas',
                'valor': 'true',
                'tipo': 'boolean',
                'descricao': 'Distribuição por faixas (1-10, 11-20, 21-31)'
            },
            {
                'chave': 'analise_extremos',
                'valor': 'true',
                'tipo': 'boolean',
                'descricao': 'Análise de números muito altos ou muito baixos'
            },
            {
                'chave': 'analise_numeros_juntos',
                'valor': 'true',
                'tipo': 'boolean',
                'descricao': 'Pares que aparecem juntos frequentemente'
            },
            {
                'chave': 'analise_duplicatas_triplas',
                'valor': 'false',
                'tipo': 'boolean',
                'descricao': 'Números com dígitos repetidos (11, 22, etc)'
            },
            {
                'chave': 'analise_padroes_extremos',
                'valor': 'true',
                'tipo': 'boolean',
                'descricao': 'Combinações com números nos extremos'
            },

            # ========================================================================
            # ANÁLISES PARA GERAR FECHAMENTO - DISTRIBUIÇÃO E ESPAÇAMENTO (8)
            # ========================================================================
            {
                'chave': 'analise_gaps',
                'valor': 'true',
                'tipo': 'boolean',
                'descricao': 'Análise de distâncias entre números sorteados'
            },
            {
                'chave': 'analise_consecutivos',
                'valor': 'true',
                'tipo': 'boolean',
                'descricao': 'Identificação de números consecutivos'
            },
            {
                'chave': 'analise_quadrantes',
                'valor': 'false',
                'tipo': 'boolean',
                'descricao': 'Distribuição em 4 quadrantes (1-7, 8-15, 16-23, 24-31)'
            },
            {
                'chave': 'analise_dezenas',
                'valor': 'true',
                'tipo': 'boolean',
                'descricao': 'Distribuição por dezenas (unidades, 10s, 20s, 30)'
            },
            {
                'chave': 'analise_espacamento',
                'valor': 'true',
                'tipo': 'boolean',
                'descricao': 'Análise do espaçamento médio entre números'
            },
            {
                'chave': 'analise_distribuicao_geral',
                'valor': 'true',
                'tipo': 'boolean',
                'descricao': 'Análise geral da distribuição numérica'
            },
            {
                'chave': 'analise_concentracao',
                'valor': 'true',
                'tipo': 'boolean',
                'descricao': 'Identificação de regiões com maior concentração'
            },
            {
                'chave': 'analise_dispersao',
                'valor': 'false',
                'tipo': 'boolean',
                'descricao': 'Medida de dispersão dos números'
            },

            # ========================================================================
            # ANÁLISES PARA GERAR FECHAMENTO - RELACIONAMENTO E SEQUÊNCIAS (6)
            # ========================================================================
            {
                'chave': 'analise_repeticoes',
                'valor': 'true',
                'tipo': 'boolean',
                'descricao': 'Números que se repetem entre sorteios'
            },
            {
                'chave': 'analise_sequencias',
                'valor': 'true',
                'tipo': 'boolean',
                'descricao': 'Padrões de sequências numéricas'
            },
            {
                'chave': 'analise_persistencia',
                'valor': 'true',
                'tipo': 'boolean',
                'descricao': 'Números que persistem em sorteios consecutivos'
            },
            {
                'chave': 'analise_alternancia',
                'valor': 'false',
                'tipo': 'boolean',
                'descricao': 'Padrões de alternância entre sorteios'
            },
            {
                'chave': 'analise_correlacao_numeros',
                'valor': 'false',
                'tipo': 'boolean',
                'descricao': 'Correlação entre diferentes números'
            },
            {
                'chave': 'analise_grupos_frequentes',
                'valor': 'true',
                'tipo': 'boolean',
                'descricao': 'Grupos de 3+ números que saem juntos'
            },

            # ========================================================================
            # ANÁLISES PARA GERAR FECHAMENTO - TEMPORAIS E SAZONAIS (8)
            # ========================================================================
            {
                'chave': 'analise_meses',
                'valor': 'true',
                'tipo': 'boolean',
                'descricao': 'Análise de distribuição por mês do sorteio'
            },
            {
                'chave': 'analise_dias_semana',
                'valor': 'false',
                'tipo': 'boolean',
                'descricao': 'Padrões por dia da semana'
            },
            {
                'chave': 'analise_trimestres',
                'valor': 'false',
                'tipo': 'boolean',
                'descricao': 'Análise por trimestre do ano'
            },
            {
                'chave': 'analise_sazonal',
                'valor': 'true',
                'tipo': 'boolean',
                'descricao': 'Identificação de padrões sazonais'
            },
            {
                'chave': 'analise_transicao_meses',
                'valor': 'true',
                'tipo': 'boolean',
                'descricao': 'Como números transitam entre meses'
            },
            {
                'chave': 'analise_correlacao_mes_dezenas',
                'valor': 'true',
                'tipo': 'boolean',
                'descricao': 'Relação entre mês e dezenas sorteadas'
            },
            {
                'chave': 'analise_acumulos_mes',
                'valor': 'true',
                'tipo': 'boolean',
                'descricao': 'Acúmulos e padrões mensais'
            },
            {
                'chave': 'analise_ciclos_temporais',
                'valor': 'false',
                'tipo': 'boolean',
                'descricao': 'Identificação de ciclos ao longo do tempo'
            },

            # ========================================================================
            # ANÁLISES PARA GERAR FECHAMENTO - AVANÇADAS E PREDITIVAS (8)
            # ========================================================================
            {
                'chave': 'analise_probabilidade_condicional',
                'valor': 'true',
                'tipo': 'boolean',
                'descricao': 'Probabilidade baseada em condições específicas'
            },
            {
                'chave': 'analise_ciclos_intervalos',
                'valor': 'true',
                'tipo': 'boolean',
                'descricao': 'Análise de ciclos de repetição'
            },
            {
                'chave': 'analise_frequencia_premios',
                'valor': 'true',
                'tipo': 'boolean',
                'descricao': 'Análise baseada em sorteios premiados'
            },
            {
                'chave': 'analise_tendencia_futura',
                'valor': 'false',
                'tipo': 'boolean',
                'descricao': 'Projeção de tendências futuras'
            },
            {
                'chave': 'analise_regressao',
                'valor': 'false',
                'tipo': 'boolean',
                'descricao': 'Análise de regressão estatística'
            },
            {
                'chave': 'analise_clusters',
                'valor': 'false',
                'tipo': 'boolean',
                'descricao': 'Agrupamento de padrões similares'
            },
            {
                'chave': 'analise_machine_learning',
                'valor': 'false',
                'tipo': 'boolean',
                'descricao': 'Previsões baseadas em ML (futuro)'
            },
            {
                'chave': 'analise_neural_network',
                'valor': 'false',
                'tipo': 'boolean',
                'descricao': 'Previsões com redes neurais (futuro)'
            },

            # ========================================================================
            # CORES SEMÂNTICAS PARA ANÁLISES (7)
            # ========================================================================
            {
                'chave': 'cor_analise_repetidos',
                'valor': '#6f42c1',
                'tipo': 'string',
                'descricao': 'Cor para números repetidos do concurso anterior'
            },
            {
                'chave': 'cor_analise_sequencia_1',
                'valor': '#000000',
                'tipo': 'string',
                'descricao': 'Cor para a primeira sequência encontrada'
            },
            {
                'chave': 'cor_analise_sequencia_2',
                'valor': '#555555',
                'tipo': 'string',
                'descricao': 'Cor para a segunda sequência encontrada'
            },
            {
                'chave': 'cor_analise_sequencia_3',
                'valor': '#999999',
                'tipo': 'string',
                'descricao': 'Cor para a terceira sequência (ou mais) encontrada'
            },
            {
                'chave': 'cor_analise_pares',
                'valor': '#28a745',
                'tipo': 'string',
                'descricao': 'Cor para números pares'
            },
            {
                'chave': 'cor_analise_impares',
                'valor': '#17a2b8',
                'tipo': 'string',
                'descricao': 'Cor para números ímpares'
            },
            {
                'chave': 'cor_analise_finais_iguais',
                'valor': '#ffc107',
                'tipo': 'string',
                'descricao': 'Cor para números com finais iguais'
            }
        ]

        for config_data in configuracoes_padrao:
            # Verifica se já existe
            existe = Configuracao.query.filter_by(chave=config_data['chave']).first()
            if not existe:
                config = Configuracao(
                    chave=config_data['chave'],
                    valor=config_data['valor'],
                    tipo=config_data['tipo'],
                    descricao=config_data['descricao']
                )
                db.session.add(config)

        try:
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao criar configurações padrão: {str(e)}")
            return False
