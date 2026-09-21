"""Exportação XLSX do relatório de conferência (não altera apostas.json)."""

from collections import Counter
from io import BytesIO
from itertools import combinations

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

MESES_NOME = {
    1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
    5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
    9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro',
}
MESES_ABREV = {
    1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr', 5: 'Mai', 6: 'Jun',
    7: 'Jul', 8: 'Ago', 9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez',
}

OURO = '6B5710'
OURO_CLARO = 'C9A227'
BRANCO = 'FFFFFF'
ZEBRA = 'F7F3E8'
VERDE = '1B7A4E'
VERMELHO = 'A33B3B'
CINZA = 'F3F4F6'


def _border():
    side = Side(style='thin', color='D0D0D0')
    return Border(left=side, right=side, top=side, bottom=side)


def _fill(hex_color):
    return PatternFill('solid', fgColor=hex_color)


def analisar_resultado(resultado):
    """Monta o parecer a partir do JSON já processado da conferência."""
    apostas = [
        a for a in resultado.get('apostas') or []
        if not a.get('erro_ocr') and not a.get('dados_incompletos')
    ]
    sorteio = resultado.get('resultado_sorteio') or {}
    resumo = resultado.get('resumo') or {}
    concurso = resultado.get('concurso')

    freq = Counter()
    meses = Counter()
    pares = Counter()
    tamanhos = Counter()
    acertos_lista = []
    constantes = {}

    for a in apostas:
        extra = a.get('dados_extraidos') or {}
        nums = list(extra.get('numeros_apostados') or [])
        mes = extra.get('mes_apostado')
        res = a.get('resultado') or {}
        tamanhos[len(nums)] += 1
        meses[str(mes)] += 1
        freq.update(nums)
        acertos_lista.append(int(res.get('acertos') or 0))
        for par in combinations(sorted(nums), 2):
            pares[par] += 1

    nunca = [n for n in range(1, 32) if freq.get(n, 0) == 0]
    sorteados = list(sorteio.get('numeros') or [])
    sorteados_nao_apostados = sorted(set(sorteados) & set(nunca))
    n = max(len(apostas), 1)
    media_acertos = sum(acertos_lista) / n if apostas else 0

    colunas_constantes = []
    arquivos = {a.get('arquivo') for a in apostas}
    if len(arquivos) == 1:
        colunas_constantes.append(('Arquivo', next(iter(arquivos))))
    meses_ok = {a.get('resultado', {}).get('acertou_mes') for a in apostas}
    if len(meses_ok) == 1:
        colunas_constantes.append(
            ('Acertou Mês', 'Sim' if next(iter(meses_ok)) else 'Não')
        )
    faixas = {(a.get('resultado') or {}).get('faixa') or 'Sem prêmio' for a in apostas}
    if len(faixas) == 1:
        colunas_constantes.append(('Faixa', next(iter(faixas))))

    constantes['colunas'] = colunas_constantes
    constantes['todos_7'] = tamanhos.get(7, 0) == len(apostas) and len(apostas) > 0

    dist = resumo.get('distribuicao_acertos') or {}
    dist_int = {int(k): int(v) for k, v in dist.items()}

    return {
        'concurso': concurso,
        'sorteio': sorteio,
        'resumo': resumo,
        'apostas': apostas,
        'freq': freq,
        'nunca': nunca,
        'meses': meses,
        'pares': pares,
        'tamanhos': tamanhos,
        'media_acertos': media_acertos,
        'sorteados_nao_apostados': sorteados_nao_apostados,
        'colunas_constantes': colunas_constantes,
        'dist_acertos': dist_int,
        'n': len(apostas),
        'mais_usados': freq.most_common(5),
        'menos_usados': sorted(
            [(n, c) for n, c in freq.items()],
            key=lambda x: (x[1], x[0]),
        )[:5],
        'top_pares': pares.most_common(8),
    }


def _parecer_linhas(an):
    s = an['sorteio']
    r = an['resumo']
    mes_sorte = MESES_NOME.get(s.get('mes_sorte'), s.get('mes_sorte'))
    nums_s = ' '.join(f'{n:02d}' for n in (s.get('numeros') or []))
    dist = ', '.join(f'{k} acerto(s): {v}' for k, v in sorted(an['dist_acertos'].items()))
    vicio = an['mais_usados'][0] if an['mais_usados'] else (None, 0)
    pares_txt = ', '.join(
        f'{a:02d}-{b:02d} ({c}/{an["n"]})' for (a, b), c in an['top_pares'][:5]
    ) or 'nenhum'
    n = an['n']
    linhas = [
        ('TÍTULO', f'PARECER TÉCNICO — Concurso {an["concurso"]}'),
        ('SEÇÃO', 'Resumo executivo'),
        ('P', (
            f'{n} apostas conferidas (origem {an["sorteio"] and "apostas.json"}), '
            f'sorteio {nums_s}, mês da sorte {mes_sorte}. '
            f'Investido R$ {r.get("total_investido", 0):.2f}; ganho R$ {r.get("total_ganho", 0):.2f}; '
            f'ROI {r.get("roi", 0):.1f}%. Premiadas: {r.get("apostas_premiadas", 0)}.'
        )),
        ('P', (
            f'Média de {an["media_acertos"]:.2f} acertos por aposta. Distribuição: {dist or "sem dados"}. '
            f'Nenhum acerto de mês.' if r.get('apostas_premiadas', 0) == 0 and an['n']
            else f'Média de {an["media_acertos"]:.2f} acertos por aposta. Distribuição: {dist or "sem dados"}.'
        )),
        ('P', (
            f'Dezena mais usada: {vicio[0]:02d} em {vicio[1]}/{n} apostas ({100 * vicio[1] / n:.0f}%). '
            f'{len(an["nunca"])} números de 1–31 nunca saíram nestes jogos. '
            f'Sorteados que não foram apostados: '
            f'{", ".join(f"{x:02d}" for x in an["sorteados_nao_apostados"]) or "nenhum"}.'
        )),
        ('SEÇÃO', 'Estrutura do arquivo'),
        ('P', (
            'Colunas conferidas: Aposta, Arquivo, dezenas, Mês Apostado, Acertos, '
            'Acertou Mês, Faixa, Valor Ganho. Sem valores nulos nas apostas válidas. '
            'Tipos consistentes (inteiros 1–31 nas dezenas; mês abreviado; valores monetários).'
        )),
        ('P', (
            'Colunas constantes neste concurso: ' +
            ('; '.join(f'{k} = {v}' for k, v in an['colunas_constantes']) or 'nenhuma') +
            '. Manter Faixa/Valor/Acertou Mês mesmo quando zerados — viram sinal de ausência de prêmio. '
            'Arquivo pode ser omitido no Excel se for sempre apostas.json, e permanece no JSON de origem.'
        )),
        ('SEÇÃO', 'Frequência das dezenas'),
        ('P', 'Mais usadas: ' + ', '.join(f'{n:02d} ({c}x)' for n, c in an['mais_usados'])),
        ('P', 'Menos usadas (entre as que aparecem): ' +
         ', '.join(f'{n:02d} ({c}x)' for n, c in an['menos_usados'])),
        ('P', 'Nunca apostadas (1–31): ' +
         (', '.join(f'{n:02d}' for n in an['nunca']) or 'nenhuma')),
        ('SEÇÃO', 'Vícios e duplas'),
        ('P', (
            f'Pares que mais andam juntos: {pares_txt}. '
            'Isso não aumenta chance no sorteio aleatório; só mostra hábito de montagem. '
            'Se a dezena da esquerda entrar no jogo, a da direita costuma entrar também — '
            'e o contrário: números fora desse núcleo quase não são cobertos.'
        )),
        ('SEÇÃO', 'Resultados'),
        ('P', (
            f'Acertos por aposta: {dist or "—"}. '
            f'Acerto de mês: não. Premiação: '
            f'{"nenhuma faixa paga" if not r.get("apostas_premiadas") else str(r.get("apostas_premiadas")) + " aposta(s) premiada(s)"}. '
            f'Taxa média: {an["media_acertos"]:.2f} acertos / 7 dezenas '
            f'({100 * an["media_acertos"] / 7:.1f}% das dezenas do volante, por jogo).'
        )),
        ('SEÇÃO', 'Meses apostados'),
        ('P', 'Distribuição: ' + ', '.join(f'{m}: {c}' for m, c in an['meses'].most_common())),
        ('P', f'Mês sorteado: {mes_sorte}. ' + (
            'Nenhuma aposta deste arquivo usou esse mês.'
            if MESES_ABREV.get(s.get('mes_sorte')) not in an['meses']
            else 'Há aposta(s) no mês sorteado — conferir coluna Acertou Mês.'
        )),
        ('SEÇÃO', 'Sugestões (sem promessa de 7 acertos)'),
        ('P', (
            'O sorteio é aleatório: nenhum recorte de dezenas “crava” 7 acertos. '
            'O que o arquivo mostra é cobertura: dezenas sorteadas que sequer estavam nos jogos '
            'não podem acertar. Priorize preencher buracos do 1–31 antes de repetir o mesmo núcleo.'
        )),
        ('P', (
            'Continuar só com 7 dezenas (R$ 2,50 / 1 combinação) é coerente para volume. '
            'Juntar caixa para 8–9 dezenas aumenta combinações na mesma cartela, com custo bem maior '
            '(8 dezenas = R$ 20; 9 = R$ 90). Faz mais sentido como jogo pontual em acumulado, '
            'não como substituto de dezenas que hoje nem são apostadas.'
        )),
        ('P', (
            'Diversificar 10 jogos simples de 7, com menos sobreposição, cobre mais o volante '
            'do que um salto para 15 dezenas (R$ 16.302) na expectativa de “acertar os 7 de uma vez”.'
        )),
        ('SEÇÃO', 'Inconsistências / lacunas'),
        ('P', (
            f'Apostas com erro OCR: {r.get("apostas_com_erro", 0)}. '
            f'Incompletas: {r.get("apostas_incompletas", 0)}. '
            'Fonte única (apostas.json). '
            + (
                'Nenhuma inconsistência de tipo ou nulo nas linhas válidas.'
                if r.get('apostas_com_erro', 0) == 0
                else 'Há linhas com erro — conferir o JSON de origem, sem alterar o arquivo original.'
            )
        )),
    ]
    return linhas


def gerar_xlsx_relatorio(resultado) -> BytesIO:
    an = analisar_resultado(resultado)
    wb = Workbook()
    ws = wb.active
    ws.title = 'Relatório'

    title_font = Font(bold=True, color=BRANCO, size=16, name='Calibri')
    sub_font = Font(bold=True, color=OURO, size=11, name='Calibri')
    head_font = Font(bold=True, color=BRANCO, size=10, name='Calibri')
    body = Font(name='Calibri', size=10)
    section_font = Font(bold=True, color=OURO, size=12, name='Calibri')
    wrap = Alignment(wrap_text=True, vertical='center')
    center = Alignment(horizontal='center', vertical='center')
    left = Alignment(horizontal='left', vertical='center', wrap_text=True)

    headers = [
        'Aposta', 'Arquivo',
        'D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7',
        'Mês Apostado', 'Acertos', 'Números Acertados',
        'Acertou Mês', 'Faixa', 'Valor Aposta (R$)', 'Valor Ganho (R$)',
    ]
    last_col = len(headers)
    last_letter = get_column_letter(last_col)

    ws.merge_cells(f'A1:{last_letter}1')
    c = ws['A1']
    c.value = 'DIA DE SORTE — Relatório de Conferência de Apostas'
    c.font = title_font
    c.fill = _fill(OURO)
    c.alignment = Alignment(horizontal='center', vertical='center')
    ws.row_dimensions[1].height = 28

    s = an['sorteio']
    nums_s = ' '.join(f'{n:02d}' for n in (s.get('numeros') or []))
    mes_s = MESES_NOME.get(s.get('mes_sorte'), s.get('mes_sorte'))
    ws.merge_cells(f'A2:{last_letter}2')
    c = ws['A2']
    c.value = (
        f'Concurso {an["concurso"]}  |  Data {s.get("data") or "—"}  |  '
        f'Sorteio {nums_s or "—"}  |  Mês da sorte: {mes_s}'
    )
    c.font = sub_font
    c.alignment = Alignment(horizontal='center', vertical='center')
    ws.row_dimensions[2].height = 20

    ws.merge_cells(f'A3:{last_letter}3')
    ws['A3'] = (
        'Arquivo de origem: apostas.json (não modificado). '
        'O parecer técnico está na sequência, abaixo da tabela e do rodapé.'
    )
    ws['A3'].font = Font(italic=True, name='Calibri', size=9, color='666666')

    header_row = 5
    for col, h in enumerate(headers, 1):
        cell = ws.cell(header_row, col, h)
        cell.font = head_font
        cell.fill = _fill(OURO)
        cell.alignment = center
        cell.border = _border()
    ws.auto_filter.ref = f'A{header_row}:{last_letter}{header_row + max(an["n"], 1)}'
    ws.freeze_panes = f'A{header_row + 1}'

    for i, a in enumerate(an['apostas']):
        row = header_row + 1 + i
        extra = a.get('dados_extraidos') or {}
        res = a.get('resultado') or {}
        nums = list(extra.get('numeros_apostados') or [])
        nums = (nums + [''] * 7)[:7]
        acertados = ' '.join(f'{n:02d}' for n in (res.get('numeros_acertados') or []))
        valores = [
            a.get('numero_aposta'),
            a.get('arquivo'),
            *nums,
            extra.get('mes_apostado'),
            res.get('acertos'),
            acertados or '—',
            'Sim' if res.get('acertou_mes') else 'Não',
            res.get('faixa') or 'Sem prêmio',
            float(a.get('valor_aposta') or 0),
            float(a.get('valor_ganho') or 0),
        ]
        fill = _fill(ZEBRA) if i % 2 else _fill(BRANCO)
        for col, val in enumerate(valores, 1):
            cell = ws.cell(row, col, val)
            cell.font = body
            cell.fill = fill
            cell.border = _border()
            cell.alignment = center if col != 12 else left
            if col in (15, 16) and isinstance(val, (int, float)):
                cell.number_format = '"R$" #,##0.00'
            if col == 11:
                ac = res.get('acertos') or 0
                if ac >= 4:
                    cell.font = Font(bold=True, color=VERDE, name='Calibri', size=10)
                elif ac == 0:
                    cell.font = Font(color=VERMELHO, name='Calibri', size=10)

    rodape = header_row + 1 + an['n'] + 1
    r = an['resumo']
    ws.merge_cells(f'A{rodape}:{last_letter}{rodape}')
    ws[f'A{rodape}'] = (
        f'RODAPÉ  ·  Apostas: {r.get("total_apostas", an["n"])}  ·  '
        f'Investido: R$ {r.get("total_investido", 0):.2f}  ·  '
        f'Ganho: R$ {r.get("total_ganho", 0):.2f}  ·  '
        f'Lucro: R$ {r.get("lucro", 0):.2f}  ·  '
        f'ROI: {r.get("roi", 0):.1f}%  ·  '
        f'Premiadas: {r.get("apostas_premiadas", 0)}  ·  '
        f'Média de acertos: {an["media_acertos"]:.2f}'
    )
    ws[f'A{rodape}'].font = Font(bold=True, name='Calibri', size=10, color=BRANCO)
    ws[f'A{rodape}'].fill = _fill(OURO_CLARO)
    ws[f'A{rodape}'].alignment = Alignment(horizontal='left', vertical='center', wrap_text=True)
    ws.row_dimensions[rodape].height = 22

    parecer_ini = rodape + 2
    ws.merge_cells(f'A{parecer_ini}:{last_letter}{parecer_ini}')
    for i, (tipo, texto) in enumerate(_parecer_linhas(an)):
        row = parecer_ini + i
        ws.merge_cells(f'A{row}:{last_letter}{row}')
        cell = ws[f'A{row}']
        cell.value = texto
        cell.alignment = left
        if tipo == 'TÍTULO':
            cell.font = title_font
            cell.fill = _fill(OURO)
            cell.alignment = Alignment(horizontal='center', vertical='center')
            ws.row_dimensions[row].height = 26
        elif tipo == 'SEÇÃO':
            cell.font = section_font
            cell.fill = _fill(CINZA)
            ws.row_dimensions[row].height = 20
        else:
            cell.font = body
            ws.row_dimensions[row].height = 36

    widths = {
        'A': 10, 'B': 16, 'C': 7, 'D': 7, 'E': 7, 'F': 7, 'G': 7, 'H': 7, 'I': 7,
        'J': 14, 'K': 10, 'L': 22, 'M': 14, 'N': 16, 'O': 18, 'P': 18,
    }
    for col, w in widths.items():
        ws.column_dimensions[col].width = w
    ws.page_setup.orientation = 'landscape'
    ws.page_setup.fitToPage = True
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.print_title_rows = '1:5'
    ws.sheet_properties.pageSetUpPr.fitToPage = True

    wf = wb.create_sheet('Frequência')
    wf['A1'] = f'Frequência das dezenas — concurso {an["concurso"]}'
    wf.merge_cells('A1:D1')
    wf['A1'].font = title_font
    wf['A1'].fill = _fill(OURO)
    wf['A1'].alignment = Alignment(horizontal='center', vertical='center')
    wf.row_dimensions[1].height = 24
    for col, h in enumerate(['Dezena', 'Vezes apostada', '% das apostas', 'Saiu no sorteio?'], 1):
        cell = wf.cell(3, col, h)
        cell.font = head_font
        cell.fill = _fill(OURO)
        cell.alignment = center
        cell.border = _border()
    sorteados_set = set(s.get('numeros') or [])
    for n in range(1, 32):
        row = 3 + n
        c = an['freq'].get(n, 0)
        vals = [f'{n:02d}', c, round(100 * c / max(an['n'], 1), 1), 'Sim' if n in sorteados_set else 'Não']
        for col, val in enumerate(vals, 1):
            cell = wf.cell(row, col, val)
            cell.border = _border()
            cell.alignment = center
            cell.font = body
            if n in sorteados_set:
                cell.fill = _fill('D4EDDA')
            elif c == 0:
                cell.fill = _fill('F8D7DA')
            elif c >= (an['mais_usados'][0][1] if an['mais_usados'] else 99):
                cell.fill = _fill(ZEBRA)
    wf.column_dimensions['A'].width = 12
    wf.column_dimensions['B'].width = 18
    wf.column_dimensions['C'].width = 16
    wf.column_dimensions['D'].width = 18
    wf['A36'] = 'Linha verde = dezena sorteada. Linha vermelha = nunca apostada neste arquivo.'
    wf.merge_cells('A36:D36')
    wf['A36'].font = Font(italic=True, name='Calibri', size=9, color='666666')

    buf = BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf
