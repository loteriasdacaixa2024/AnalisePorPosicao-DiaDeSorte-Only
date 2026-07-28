from models.sorteio import Sorteio, db

class AnaliseDezenasFaixasService:
    @staticmethod
    def obter_distribuicao_faixas():
        total_concursos = Sorteio.query.count()
        
        padroes = {}
        
        concursos = Sorteio.query.order_by(Sorteio.concurso.desc()).all()
        
        for concurso in concursos:
            baixa = 0
            media = 0
            alta = 0
            
            for pos in range(1, 8):
                campo = f'posicao_{pos}'
                numero = getattr(concurso, campo, None)
                
                if numero:
                    if 1 <= numero <= 10:
                        baixa += 1
                    elif 11 <= numero <= 20:
                        media += 1
                    elif 21 <= numero <= 31:
                        alta += 1
            
            chave = f"{baixa}B+{media}M+{alta}A"
            
            if chave not in padroes:
                padroes[chave] = {
                    'descricao': chave,
                    'baixa': baixa,
                    'media': media,
                    'alta': alta,
                    'frequencia': 0,
                    'ultimo_concurso': None,
                    'atraso': 0
                }
            
            padroes[chave]['frequencia'] += 1
            
            if padroes[chave]['ultimo_concurso'] is None:
                padroes[chave]['ultimo_concurso'] = concurso.concurso
        
        lista_padroes = list(padroes.values())
        lista_padroes.sort(key=lambda x: x['frequencia'], reverse=True)
        
        ultimo_concurso_geral = concursos[0].concurso if concursos else 0
        
        for padrao in lista_padroes:
            if padrao['ultimo_concurso']:
                padrao['atraso'] = ultimo_concurso_geral - padrao['ultimo_concurso']
            padrao['percentual'] = f"{(padrao['frequencia'] / total_concursos * 100):.2f}"
        
        total_baixa = sum(
            p['frequencia'] * p['baixa'] for p in lista_padroes
        )
        total_media = sum(
            p['frequencia'] * p['media'] for p in lista_padroes
        )
        total_alta = sum(
            p['frequencia'] * p['alta'] for p in lista_padroes
        )
        
        total_numeros = total_baixa + total_media + total_alta
        
        return {
            'padroes': lista_padroes,
            'total_concursos': total_concursos,
            'media_baixa': f"{(total_baixa / total_concursos):.2f}",
            'media_media': f"{(total_media / total_concursos):.2f}",
            'media_alta': f"{(total_alta / total_concursos):.2f}",
            'perc_baixa': f"{(total_baixa / total_numeros * 100):.2f}",
            'perc_media': f"{(total_media / total_numeros * 100):.2f}",
            'perc_alta': f"{(total_alta / total_numeros * 100):.2f}"
        }