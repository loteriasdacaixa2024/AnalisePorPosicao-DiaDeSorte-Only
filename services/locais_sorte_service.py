import os
import re
import json
import glob
import time
import unicodedata
from datetime import datetime
from sqlalchemy import or_, desc, asc, func
from models.shared import db
from models.locais_sorte import LocaisSorte
from models.sorteio import Sorteio

class LocaisSorteService:
    MODALIDADE = "Dia de Sorte"
    _cache_comparativo = {'dados': None, 'ts': 0}
    _CACHE_TTL_SEG = 120

    @staticmethod
    def pasta_dados():
        from config import Config
        return str(Config.BASE_DIR / "conferencias-locais-da-sorte" / "Dia-de-Sorte")

    @staticmethod
    def normalizar_cabecalho(texto):
        """Remove acentos e padroniza nome de coluna para mapeamento."""
        if not texto:
            return ''
        nfkd = unicodedata.normalize('NFKD', str(texto))
        sem_acento = ''.join(c for c in nfkd if not unicodedata.combining(c))
        return sem_acento.lower().strip()

    @staticmethod
    def limpar_valor_monetario(valor_str):
        """Converte R$ 2.553,17 ou similar em float"""
        if not valor_str:
            return 0.0
        limpo = str(valor_str).replace('R$', '').replace(' ', '').strip()
        if ',' in limpo and '.' in limpo:
            limpo = limpo.replace('.', '').replace(',', '.')
        elif ',' in limpo:
            limpo = limpo.replace(',', '.')
        try:
            return float(limpo)
        except ValueError:
            return 0.0

    @staticmethod
    def identificar_concurso(filename, dados):
        """
        Tenta identificar o concurso de duas maneiras:
        1. Procurando '_conc_(N)' no nome do arquivo.
        2. Cruzando os prêmios do arquivo com a tabela de sorteios no banco de dados.
        """
        # Método 1: Nome do arquivo
        match = re.search(r'_conc_(\d+)', filename)
        if match:
            return int(match.group(1))

        # Método 2: Cruzamento de dados de premiação
        # Procurar no JSON por prêmios de "6 acertos" ou "7 acertos"
        for row in dados:
            if len(row) >= 11:
                faixa = row[3] # Faixa de acertos
                premio_str = row[10] # Prêmio total
                
                # Se for faixa de 6 ou 7 acertos, tenta cruzar com o banco
                if "6 acertos" in faixa or "7 acertos" in faixa:
                    valor = LocaisSorteService.limpar_valor_monetario(premio_str)
                    if valor > 25.0:  # Prêmios de 5 e 4 acertos são fixos, ignorar
                        # Query no banco
                        if "6 acertos" in faixa:
                            sorteio = Sorteio.query.filter(
                                func.abs(Sorteio.valor_premio_6_acertos - valor) < 0.1
                            ).first()
                        else:
                            sorteio = Sorteio.query.filter(
                                func.abs(Sorteio.valor_premio_7_acertos - valor) < 0.1
                            ).first()

                        if sorteio:
                            print(f"[ETL] Concurso {sorteio.concurso} identificado via cruzamento de prêmios ({faixa}: {premio_str})")
                            return sorteio.concurso
        return None

    @staticmethod
    def importar_arquivos_json():
        """
        Varre a pasta de dados Dia-de-Sorte, valida, normaliza e importa para o SQL.
        Retorna estatísticas do processo.
        """
        pasta = LocaisSorteService.pasta_dados()
        if not os.path.exists(pasta):
            os.makedirs(pasta, exist_ok=True)
            return {'arquivos_processados': 0, 'registros_inseridos': 0, 'registros_pulados': 0, 'erros': []}

        busca = os.path.join(pasta, "*.json")
        arquivos = glob.glob(busca)

        total_arquivos = 0
        total_inseridos = 0
        total_pulados = 0
        erros = []

        for arq_path in arquivos:
            filename = os.path.basename(arq_path)
            try:
                with open(arq_path, 'r', encoding='utf-8') as f:
                    dados_json = json.load(f)

                cabecalhos = dados_json.get('cabecalhos', [])
                dados = dados_json.get('dados', [])

                if not cabecalhos or not dados:
                    continue

                # Cria mapa de cabeçalhos normalizados para índices do array
                header_map = {}
                for idx, h in enumerate(cabecalhos):
                    header_map[LocaisSorteService.normalizar_cabecalho(h)] = idx

                # Identifica concurso
                concurso = LocaisSorteService.identificar_concurso(filename, dados)

                if not concurso:
                    erros.append(f"Não foi possível identificar o concurso para o arquivo: {filename}")
                    continue

                total_arquivos += 1

                for row in dados:
                    if len(row) < len(cabecalhos):
                        continue

                    # Extrai dados mapeados
                    cidade = row[header_map['cidade']].strip() if 'cidade' in header_map else ""
                    unidade_loterica = row[header_map['unidade loterica']].strip() if 'unidade loterica' in header_map else ""
                    razao_social = row[header_map['razao social']].strip() if 'razao social' in header_map else ""
                    faixa_acertos = row[header_map['faixa de acertos']].strip() if 'faixa de acertos' in header_map else ""
                    
                    try:
                        qtd_numeros = int(row[header_map['quantidade de numeros apostados']]) if 'quantidade de numeros apostados' in header_map else 7
                    except:
                        qtd_numeros = 7

                    canal_vendas = row[header_map['canal de vendas']].strip() if 'canal de vendas' in header_map else ""
                    teimosinha = row[header_map['teimosinha']].strip() if 'teimosinha' in header_map else ""
                    tipo_aposta_raw = row[header_map['tipo de aposta']].strip() if 'tipo de aposta' in header_map else "Simples"
                    # Normalize tipo_aposta: if it's any variation of "Bolão", set to "Bolão" (using Unicode escape)
                    BOLAO = "Bol\u00E3o"  # This is "Bolão"
                    if tipo_aposta_raw:
                        tipo_aposta_lower = tipo_aposta_raw.lower()
                        if 'bol' in tipo_aposta_lower and 'o' in tipo_aposta_lower:
                            tipo_aposta = BOLAO
                        else:
                            tipo_aposta = tipo_aposta_raw
                    else:
                        tipo_aposta = "Simples"

                    try:
                        cotas = int(row[header_map['cotas']]) if 'cotas' in header_map else 1
                    except:
                        cotas = 1

                    try:
                        qtd_premios = int(row[header_map['quantidade de premios por faixa']]) if 'quantidade de premios por faixa' in header_map else 1
                    except:
                        qtd_premios = 1

                    premio = row[header_map['premio']].strip() if 'premio' in header_map else "R$ 0,00"
                    valor_premio = LocaisSorteService.limpar_valor_monetario(premio)

                    # Valida duplicidade incremental antes de inserir
                    exists = LocaisSorte.query.filter_by(
                        modalidade=LocaisSorteService.MODALIDADE,
                        concurso=concurso,
                        cidade=cidade,
                        unidade_loterica=unidade_loterica,
                        faixa_acertos=faixa_acertos,
                        tipo_aposta=tipo_aposta,
                        valor_premio=valor_premio,
                        cotas=cotas,
                        qtd_premios_faixa=qtd_premios
                    ).first()

                    if exists:
                        total_pulados += 1
                        continue

                    # Insere registro
                    novo_registro = LocaisSorte(
                        modalidade=LocaisSorteService.MODALIDADE,
                        concurso=concurso,
                        cidade=cidade,
                        unidade_loterica=unidade_loterica,
                        razao_social=razao_social,
                        faixa_acertos=faixa_acertos,
                        qtd_numeros_apostados=qtd_numeros,
                        canal_vendas=canal_vendas,
                        teimosinha=teimosinha,
                        tipo_aposta=tipo_aposta,
                        cotas=cotas,
                        qtd_premios_faixa=qtd_premios,
                        premio=premio,
                        valor_premio=valor_premio,
                        arquivo_origem=filename
                    )

                    db.session.add(novo_registro)
                    total_inseridos += 1

                db.session.commit()

            except Exception as e:
                db.session.rollback()
                erros.append(f"Erro ao processar arquivo {filename}: {str(e)}")

        return {
            'arquivos_processados': total_arquivos,
            'registros_inseridos': total_inseridos,
            'registros_pulados': total_pulados,
            'erros': erros
        }

    @staticmethod
    def _aplicar_filtro_numerico(query, coluna, valor_raw):
        """Suporta =123, >100, <50 ou valor exato."""
        if not valor_raw:
            return query
        val = str(valor_raw).strip()
        match = re.match(r'^([><=]+)\s*([\d.,]+)$', val)
        try:
            if match:
                op, num_s = match.groups()
                num = float(num_s.replace('.', '').replace(',', '.')) if ',' in num_s and num_s.count(',') == 1 else float(num_s)
                if '>' in op:
                    return query.filter(coluna > num)
                if '<' in op:
                    return query.filter(coluna < num)
                return query.filter(coluna == num)
            num = float(val.replace('.', '').replace(',', '.')) if ',' in val else float(val)
            return query.filter(coluna == num)
        except (ValueError, TypeError):
            return query

    @staticmethod
    def obter_resumo():
        """Totais e metadados para o painel."""
        q = LocaisSorte.query.filter_by(modalidade=LocaisSorteService.MODALIDADE)
        total = q.count()
        concursos = db.session.query(func.count(func.distinct(LocaisSorte.concurso))).filter_by(
            modalidade=LocaisSorteService.MODALIDADE
        ).scalar() or 0
        ultima = q.order_by(desc(LocaisSorte.data_importacao)).first()
        soma_premios = db.session.query(func.sum(LocaisSorte.valor_premio)).filter_by(
            modalidade=LocaisSorteService.MODALIDADE
        ).scalar() or 0.0
        arquivos_pasta = len(glob.glob(os.path.join(LocaisSorteService.pasta_dados(), "*.json")))
        return {
            'sucesso': True,
            'total_registros': total,
            'total_concursos': concursos,
            'soma_premios': round(float(soma_premios), 2),
            'ultima_importacao': ultima.data_importacao.strftime('%d/%m/%Y %H:%M') if ultima and ultima.data_importacao else None,
            'arquivos_json_pasta': arquivos_pasta,
            'pasta_dados': LocaisSorteService.pasta_dados(),
        }

    @staticmethod
    def obter_relatorio_paginado(filtros=None, pagina=1, por_pagina=50, ordenacao='concurso', ord_dir='desc'):
        """Retorna lista paginada de registros com base em filtros avançados"""
        query = LocaisSorte.query.filter_by(modalidade=LocaisSorteService.MODALIDADE)

        if filtros:
            # Filtro por Concurso
            if 'concurso' in filtros and filtros['concurso']:
                try:
                    val = filtros['concurso'].strip()
                    if val.startswith('>') or val.startswith('<') or val.startswith('='):
                        match = re.match(r'^([><=]+)\s*(\d+)$', val)
                        if match:
                            op, num = match.groups()
                            num = int(num)
                            if '>' in op:
                                query = query.filter(LocaisSorte.concurso > num)
                            elif '<' in op:
                                query = query.filter(LocaisSorte.concurso < num)
                            else:
                                query = query.filter(LocaisSorte.concurso == num)
                    else:
                        query = query.filter(LocaisSorte.concurso == int(val))
                except:
                    pass

            # Filtro por Local (Cidade / Lotérica / Razão Social)
            if 'local' in filtros and filtros['local']:
                local_filter = f"%{filtros['local'].strip()}%"
                query = query.filter(or_(
                    LocaisSorte.cidade.like(local_filter),
                    LocaisSorte.unidade_loterica.like(local_filter),
                    LocaisSorte.razao_social.like(local_filter)
                ))

            # Filtro por Faixa de Acertos
            if 'acertos' in filtros and filtros['acertos']:
                query = query.filter(LocaisSorte.faixa_acertos.like(f"%{filtros['acertos'].strip()}%"))

            # Filtro por Tipo de Aposta (Simples / Bolão)
            if 'tipo_aposta' in filtros and filtros['tipo_aposta']:
                query = query.filter(LocaisSorte.tipo_aposta == filtros['tipo_aposta'].strip())

            # Filtro por Canal de Venda
            if 'canal_vendas' in filtros and filtros['canal_vendas']:
                query = query.filter(LocaisSorte.canal_vendas.like(f"%{filtros['canal_vendas'].strip()}%"))

            # Estratégia = tipo de aposta (Bolão / Simples)
            if 'estrategia' in filtros and filtros['estrategia']:
                query = query.filter(LocaisSorte.tipo_aposta.like(f"%{filtros['estrategia'].strip()}%"))

            if 'unidade_loterica' in filtros and filtros['unidade_loterica']:
                query = query.filter(LocaisSorte.unidade_loterica.like(f"%{filtros['unidade_loterica'].strip()}%"))

            if 'cidade' in filtros and filtros['cidade']:
                query = query.filter(LocaisSorte.cidade.like(f"%{filtros['cidade'].strip()}%"))

            if 'teimosinha' in filtros and filtros['teimosinha']:
                query = query.filter(LocaisSorte.teimosinha.like(f"%{filtros['teimosinha'].strip()}%"))

            if 'valor_premio' in filtros and filtros['valor_premio']:
                query = LocaisSorteService._aplicar_filtro_numerico(
                    query, LocaisSorte.valor_premio, filtros['valor_premio']
                )

            if 'cotas' in filtros and filtros['cotas']:
                query = LocaisSorteService._aplicar_filtro_numerico(
                    query, LocaisSorte.cotas, filtros['cotas']
                )

            if 'qtd_numeros_apostados' in filtros and filtros['qtd_numeros_apostados']:
                query = LocaisSorteService._aplicar_filtro_numerico(
                    query, LocaisSorte.qtd_numeros_apostados, filtros['qtd_numeros_apostados']
                )

            # Busca Global Rápida (tipo Google search)
            if 'busca_global' in filtros and filtros['busca_global']:
                busca = f"%{filtros['busca_global'].strip()}%"
                
                # Se for número, tenta buscar também por concurso exato
                condicoes = [
                    LocaisSorte.cidade.like(busca),
                    LocaisSorte.unidade_loterica.like(busca),
                    LocaisSorte.razao_social.like(busca),
                    LocaisSorte.faixa_acertos.like(busca),
                    LocaisSorte.tipo_aposta.like(busca),
                    LocaisSorte.canal_vendas.like(busca)
                ]
                try:
                    num_val = int(filtros['busca_global'].strip())
                    condicoes.append(LocaisSorte.concurso == num_val)
                except ValueError:
                    pass
                
                query = query.filter(or_(*condicoes))

        # Ordenação
        col_ord = getattr(LocaisSorte, ordenacao, LocaisSorte.concurso)
        if ord_dir == 'asc':
            query = query.order_by(asc(col_ord))
        else:
            query = query.order_by(desc(col_ord))

        # Paginação
        pagination = query.paginate(page=pagina, per_page=por_pagina, error_out=False)

        return {
            'sucesso': True,
            'dados': [item.to_dict() for item in pagination.items],
            'total': pagination.total,
            'paginas': pagination.pages,
            'pagina_atual': pagination.page
        }

    @staticmethod
    def obter_padroes_faixa_acertos():
        """Padrões por faixa de acertos (proxy de posição/performance)."""
        rows = db.session.query(
            LocaisSorte.faixa_acertos,
            LocaisSorte.tipo_aposta,
            func.count(LocaisSorte.id).label('total'),
            func.sum(LocaisSorte.valor_premio).label('soma_premios'),
            func.avg(LocaisSorte.valor_premio).label('media_premio'),
        ).filter_by(modalidade=LocaisSorteService.MODALIDADE).group_by(
            LocaisSorte.faixa_acertos, LocaisSorte.tipo_aposta
        ).order_by(desc('total')).all()

        padroes = []
        for row in rows:
            padroes.append({
                'faixa_acertos': row[0] or '—',
                'tipo_aposta': row[1] or 'Simples',
                'total': row[2],
                'soma_premios': round(float(row[3] or 0), 2),
                'media_premio': round(float(row[4] or 0), 2),
            })
        return {'sucesso': True, 'padroes': padroes}

    @staticmethod
    def obter_comparativo_estratificacao(usar_cache=True):
        """Calcula métricas de comparação inteligente: Bolão vs Simples, etc."""
        agora = time.time()
        if usar_cache and LocaisSorteService._cache_comparativo['dados']:
            if agora - LocaisSorteService._cache_comparativo['ts'] < LocaisSorteService._CACHE_TTL_SEG:
                return LocaisSorteService._cache_comparativo['dados']

        # 1. Bolão vs Simples
        stats_tipos = db.session.query(
            LocaisSorte.tipo_aposta,
            func.count(LocaisSorte.id).label('total_apostas'),
            func.sum(LocaisSorte.valor_premio).label('total_premios'),
            func.avg(LocaisSorte.valor_premio).label('premio_medio')
        ).filter_by(modalidade=LocaisSorteService.MODALIDADE).group_by(LocaisSorte.tipo_aposta).all()

        comparador_aposta = []
        for row in stats_tipos:
            comparador_aposta.append({
                'tipo_aposta': row[0] or "Simples",
                'total_apostas': row[1],
                'total_premios': row[2] or 0.0,
                'premio_medio': row[3] or 0.0
            })

        # 2. Locais mais eficientes (TOP 10 Cidades)
        stats_cidades = db.session.query(
            LocaisSorte.cidade,
            func.count(LocaisSorte.id).label('total_apostas'),
            func.sum(LocaisSorte.valor_premio).label('total_premios')
        ).filter_by(modalidade=LocaisSorteService.MODALIDADE).group_by(LocaisSorte.cidade).order_by(desc('total_apostas')).limit(10).all()

        top_cidades = []
        for row in stats_cidades:
            top_cidades.append({
                'cidade': row[0],
                'total_apostas': row[1],
                'total_premios': row[2] or 0.0
            })

        # 3. Lotéricas pé quente (TOP 10 Unidades)
        stats_lotericas = db.session.query(
            LocaisSorte.unidade_loterica,
            LocaisSorte.cidade,
            func.count(LocaisSorte.id).label('total_apostas'),
            func.sum(LocaisSorte.valor_premio).label('total_premios')
        ).filter_by(modalidade=LocaisSorteService.MODALIDADE).group_by(LocaisSorte.unidade_loterica, LocaisSorte.cidade).order_by(desc('total_apostas')).limit(10).all()

        top_lotericas = []
        for row in stats_lotericas:
            top_lotericas.append({
                'loterica': row[0] or "Canais Eletrônicos",
                'cidade': row[1],
                'total_apostas': row[2],
                'total_premios': row[3] or 0.0
            })

        # 4. Concursos mais lucrativos (Top 10)
        stats_concursos = db.session.query(
            LocaisSorte.concurso,
            func.count(LocaisSorte.id).label('total_apostas'),
            func.sum(LocaisSorte.valor_premio).label('total_premios')
        ).filter_by(modalidade=LocaisSorteService.MODALIDADE).group_by(LocaisSorte.concurso).order_by(desc('total_premios')).limit(10).all()

        top_concursos = []
        for row in stats_concursos:
            top_concursos.append({
                'concurso': row[0],
                'total_apostas': row[1],
                'total_premios': row[2] or 0.0
            })

        resultado = {
            'sucesso': True,
            'comparador_aposta': comparador_aposta,
            'top_cidades': top_cidades,
            'top_lotericas': top_lotericas,
            'top_concursos': top_concursos
        }
        LocaisSorteService._cache_comparativo = {'dados': resultado, 'ts': agora}
        return resultado
