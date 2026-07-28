# Sistema: Análise por Posição - Dia de Sorte
# Desenvolvido para: Márcio Fernando Maia

from reportlab.lib.pagesizes import A4, letter
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.pdfgen import canvas
import pandas as pd
from datetime import datetime
import os
from config import Config
from models.sorteio import Sorteio
from services.estatistica_service import EstatisticaService

class RelatorioService:
    """
    Serviço para geração de relatórios em PDF e Excel
    """
    
    RELATORIOS_DIR = Config.RELATORIOS_DIR
    COR_PRIMARIA = colors.HexColor(Config.COR_PRIMARIA)
    
    @staticmethod
    def _criar_cabecalho_pdf(canvas_obj, doc):
        """
        Cria cabeçalho padrão para PDFs
        """
        canvas_obj.saveState()
        
        # Título
        canvas_obj.setFont('Helvetica-Bold', 16)
        canvas_obj.setFillColor(RelatorioService.COR_PRIMARIA)
        canvas_obj.drawString(2*cm, A4[1] - 2*cm, 'Análise por Posição - Dia de Sorte')
        
        # Data
        canvas_obj.setFont('Helvetica', 10)
        canvas_obj.setFillColor(colors.gray)
        data_atual = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        canvas_obj.drawRightString(A4[0] - 2*cm, A4[1] - 2*cm, f'Gerado em: {data_atual}')
        
        # Linha divisória
        canvas_obj.setStrokeColor(RelatorioService.COR_PRIMARIA)
        canvas_obj.setLineWidth(2)
        canvas_obj.line(2*cm, A4[1] - 2.5*cm, A4[0] - 2*cm, A4[1] - 2.5*cm)
        
        canvas_obj.restoreState()
    
    @staticmethod
    def _criar_rodape_pdf(canvas_obj, doc):
        """
        Cria rodapé padrão para PDFs
        """
        canvas_obj.saveState()
        
        # Número da página
        canvas_obj.setFont('Helvetica', 9)
        canvas_obj.setFillColor(colors.gray)
        pagina = f'Página {doc.page}'
        canvas_obj.drawCentredString(A4[0] / 2, 1.5*cm, pagina)
        
        # Desenvolvedor
        canvas_obj.setFont('Helvetica', 8)
        canvas_obj.drawCentredString(A4[0] / 2, 1*cm, f'Desenvolvido para: {Config.DESENVOLVEDOR}')
        
        canvas_obj.restoreState()
    
    @staticmethod
    def gerar_relatorio_sorteios_pdf(sorteios, nome_arquivo=None):
        """
        Gera relatório PDF com lista de sorteios
        """
        try:
            if not nome_arquivo:
                nome_arquivo = f'relatorio_sorteios_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
            
            caminho_completo = os.path.join(RelatorioService.RELATORIOS_DIR, nome_arquivo)
            
            # Criar documento
            doc = SimpleDocTemplate(caminho_completo, pagesize=A4)
            elementos = []
            
            # Estilos
            styles = getSampleStyleSheet()
            titulo_style = ParagraphStyle(
                'TituloCustom',
                parent=styles['Heading1'],
                fontSize=14,
                textColor=RelatorioService.COR_PRIMARIA,
                spaceAfter=20,
                alignment=TA_CENTER
            )
            
            # Título
            elementos.append(Spacer(1, 1*cm))
            elementos.append(Paragraph('Relatório de Sorteios', titulo_style))
            elementos.append(Spacer(1, 0.5*cm))
            
            # Tabela de sorteios
            dados_tabela = [['Concurso', 'Pos 1', 'Pos 2', 'Pos 3', 'Pos 4', 'Pos 5', 'Pos 6', 'Pos 7', 'Mês', 'Data']]
            
            for sorteio in sorteios:
                linha = [
                    str(sorteio.concurso),
                    str(sorteio.posicao_1),
                    str(sorteio.posicao_2),
                    str(sorteio.posicao_3),
                    str(sorteio.posicao_4),
                    str(sorteio.posicao_5),
                    str(sorteio.posicao_6),
                    str(sorteio.posicao_7),
                    sorteio.get_nome_mes(),
                    sorteio.data_sorteio.strftime('%d/%m/%Y')
                ]
                dados_tabela.append(linha)
            
            # Criar tabela
            tabela = Table(dados_tabela, repeatRows=1)
            tabela.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), RelatorioService.COR_PRIMARIA),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
            ]))
            
            elementos.append(tabela)
            
            # Construir PDF
            doc.build(elementos, onFirstPage=RelatorioService._criar_cabecalho_pdf, 
                     onLaterPages=RelatorioService._criar_cabecalho_pdf)
            
            return {
                'sucesso': True,
                'mensagem': 'Relatório PDF gerado com sucesso',
                'arquivo': nome_arquivo,
                'caminho': caminho_completo,
                'total_registros': len(sorteios)
            }
            
        except Exception as e:
            return {
                'sucesso': False,
                'erro': f'Erro ao gerar PDF: {str(e)}'
            }
    
    @staticmethod
    def gerar_relatorio_estatisticas_pdf(nome_arquivo=None):
        """
        Gera relatório PDF com estatísticas completas
        """
        try:
            if not nome_arquivo:
                nome_arquivo = f'relatorio_estatisticas_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
            
            caminho_completo = os.path.join(RelatorioService.RELATORIOS_DIR, nome_arquivo)
            
            doc = SimpleDocTemplate(caminho_completo, pagesize=A4)
            elementos = []
            styles = getSampleStyleSheet()
            
            titulo_style = ParagraphStyle(
                'TituloCustom',
                parent=styles['Heading1'],
                fontSize=14,
                textColor=RelatorioService.COR_PRIMARIA,
                spaceAfter=20,
                alignment=TA_CENTER
            )
            
            subtitulo_style = ParagraphStyle(
                'SubtituloCustom',
                parent=styles['Heading2'],
                fontSize=12,
                textColor=RelatorioService.COR_PRIMARIA,
                spaceAfter=10
            )
            
            # Título
            elementos.append(Spacer(1, 1*cm))
            elementos.append(Paragraph('Relatório de Estatísticas', titulo_style))
            elementos.append(Spacer(1, 0.5*cm))
            
            # Frequência Geral
            elementos.append(Paragraph('Frequência Geral (Top 10)', subtitulo_style))
            frequencias = EstatisticaService.frequencia_geral()[:10]
            
            dados_freq = [['Posição', 'Número', 'Frequência', 'Percentual']]
            for i, freq in enumerate(frequencias, 1):
                dados_freq.append([
                    str(i),
                    str(freq['numero']),
                    str(freq['frequencia']),
                    f"{freq['percentual']}%"
                ])
            
            tabela_freq = Table(dados_freq)
            tabela_freq.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), RelatorioService.COR_PRIMARIA),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elementos.append(tabela_freq)
            elementos.append(Spacer(1, 0.5*cm))
            
            # Números Atrasados
            elementos.append(Paragraph('Números Mais Atrasados (Top 10)', subtitulo_style))
            atrasados_dados = EstatisticaService.numeros_atrasados(limite=10)
            
            if atrasados_dados and 'numeros_atrasados' in atrasados_dados:
                dados_atraso = [['Posição', 'Número', 'Atraso (concursos)', 'Última Aparição']]
                for i, atraso in enumerate(atrasados_dados['numeros_atrasados'], 1):
                    dados_atraso.append([
                        str(i),
                        str(atraso['numero']),
                        str(atraso['atraso']),
                        atraso['ultima_data']
                    ])
                
                tabela_atraso = Table(dados_atraso)
                tabela_atraso.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), RelatorioService.COR_PRIMARIA),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                elementos.append(tabela_atraso)
                elementos.append(Spacer(1, 0.5*cm))
            
            # Mês da Sorte
            elementos.append(PageBreak())
            elementos.append(Paragraph('Estatísticas do Mês da Sorte', subtitulo_style))
            stats_mes = EstatisticaService.estatisticas_mes_sorte()
            
            if stats_mes and 'meses' in stats_mes:
                dados_mes = [['Posição', 'Mês', 'Frequência', 'Percentual']]
                for i, mes in enumerate(stats_mes['meses'], 1):
                    dados_mes.append([
                        str(i),
                        mes['nome'],
                        str(mes['frequencia']),
                        f"{mes['percentual']}%"
                    ])
                
                tabela_mes = Table(dados_mes)
                tabela_mes.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), RelatorioService.COR_PRIMARIA),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                elementos.append(tabela_mes)
            
            doc.build(elementos, onFirstPage=RelatorioService._criar_cabecalho_pdf,
                     onLaterPages=RelatorioService._criar_cabecalho_pdf)
            
            return {
                'sucesso': True,
                'mensagem': 'Relatório de estatísticas gerado com sucesso',
                'arquivo': nome_arquivo,
                'caminho': caminho_completo
            }
            
        except Exception as e:
            return {
                'sucesso': False,
                'erro': f'Erro ao gerar PDF: {str(e)}'
            }
    
    @staticmethod
    def gerar_relatorio_sorteios_excel(sorteios, nome_arquivo=None):
        """
        Gera relatório Excel com lista de sorteios
        """
        try:
            if not nome_arquivo:
                nome_arquivo = f'relatorio_sorteios_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
            
            caminho_completo = os.path.join(RelatorioService.RELATORIOS_DIR, nome_arquivo)
            
            # Preparar dados
            dados = []
            for sorteio in sorteios:
                dados.append({
                    'Concurso': sorteio.concurso,
                    'Posição 1': sorteio.posicao_1,
                    'Posição 2': sorteio.posicao_2,
                    'Posição 3': sorteio.posicao_3,
                    'Posição 4': sorteio.posicao_4,
                    'Posição 5': sorteio.posicao_5,
                    'Posição 6': sorteio.posicao_6,
                    'Posição 7': sorteio.posicao_7,
                    'Mês da Sorte': sorteio.get_nome_mes(),
                    'Data': sorteio.data_sorteio.strftime('%d/%m/%Y')
                })
            
            # Criar DataFrame
            df = pd.DataFrame(dados)
            
            # Salvar Excel
            with pd.ExcelWriter(caminho_completo, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Sorteios', index=False)
                
                # Ajustar largura das colunas
                worksheet = writer.sheets['Sorteios']
                for column in worksheet.columns:
                    max_length = 0
                    column = [cell for cell in column]
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(cell.value)
                        except:
                            pass
                    adjusted_width = (max_length + 2)
                    worksheet.column_dimensions[column[0].column_letter].width = adjusted_width
            
            return {
                'sucesso': True,
                'mensagem': 'Relatório Excel gerado com sucesso',
                'arquivo': nome_arquivo,
                'caminho': caminho_completo,
                'total_registros': len(sorteios)
            }
            
        except Exception as e:
            return {
                'sucesso': False,
                'erro': f'Erro ao gerar Excel: {str(e)}'
            }
    
    @staticmethod
    def gerar_relatorio_estatisticas_excel(nome_arquivo=None):
        """
        Gera relatório Excel com estatísticas completas
        """
        try:
            if not nome_arquivo:
                nome_arquivo = f'relatorio_estatisticas_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
            
            caminho_completo = os.path.join(RelatorioService.RELATORIOS_DIR, nome_arquivo)
            
            with pd.ExcelWriter(caminho_completo, engine='openpyxl') as writer:
                # Aba 1: Frequência Geral
                frequencias = EstatisticaService.frequencia_geral()
                df_freq = pd.DataFrame(frequencias)
                df_freq.to_excel(writer, sheet_name='Frequência Geral', index=False)
                
                # Aba 2: Números Atrasados
                atrasados_dados = EstatisticaService.numeros_atrasados(limite=31)
                if atrasados_dados and 'numeros_atrasados' in atrasados_dados:
                    df_atraso = pd.DataFrame(atrasados_dados['numeros_atrasados'])
                    df_atraso.to_excel(writer, sheet_name='Números Atrasados', index=False)
                
                # Aba 3: Mês da Sorte
                stats_mes = EstatisticaService.estatisticas_mes_sorte()
                if stats_mes and 'meses' in stats_mes:
                    df_mes = pd.DataFrame(stats_mes['meses'])
                    df_mes.to_excel(writer, sheet_name='Mês da Sorte', index=False)
                
                # Ajustar largura das colunas em todas as abas
                for sheet_name in writer.sheets:
                    worksheet = writer.sheets[sheet_name]
                    for column in worksheet.columns:
                        max_length = 0
                        column = [cell for cell in column]
                        for cell in column:
                            try:
                                if len(str(cell.value)) > max_length:
                                    max_length = len(cell.value)
                            except:
                                pass
                        adjusted_width = (max_length + 2)
                        worksheet.column_dimensions[column[0].column_letter].width = adjusted_width
            
            return {
                'sucesso': True,
                'mensagem': 'Relatório de estatísticas Excel gerado com sucesso',
                'arquivo': nome_arquivo,
                'caminho': caminho_completo
            }
            
        except Exception as e:
            return {
                'sucesso': False,
                'erro': f'Erro ao gerar Excel: {str(e)}'
            }