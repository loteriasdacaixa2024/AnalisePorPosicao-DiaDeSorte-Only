from models.sorteio import Sorteio, db

class AnaliseSequenciasService:
    @staticmethod
    def obter_analise_sequencias():
        concursos = Sorteio.query.order_by(Sorteio.concurso.desc()).all()
        
        total_concursos = len(concursos)
        
        # Contadores por tipo de sequência
        duplas = 0
        triplas = 0
        quadruplas = 0
        quintuplas_ou_mais = 0
        concursos_sem_sequencia = 0
        
        # Estatísticas detalhadas
        tamanhos_sequencias = {2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0}
        exemplos_sequencias = []
        
        for concurso in concursos:
            # Obter todos os números do sorteio
            numeros = []
            for pos in range(1, 8):
                campo = f'posicao_{pos}'
                numero = getattr(concurso, campo, None)
                if numero:
                    numeros.append(numero)
            
            # Ordenar números
            numeros.sort()
            
            # Detectar sequências
            sequencias_encontradas = []
            i = 0
            while i < len(numeros):
                tamanho_sequencia = 1
                j = i
                
                # Verificar quantos números consecutivos existem
                while j < len(numeros) - 1 and numeros[j + 1] == numeros[j] + 1:
                    tamanho_sequencia += 1
                    j += 1
                
                # Se encontrou sequência (2 ou mais números consecutivos)
                if tamanho_sequencia >= 2:
                    sequencia = numeros[i:j+1]
                    sequencias_encontradas.append({
                        'tamanho': tamanho_sequencia,
                        'numeros': sequencia,
                        'concurso': concurso.concurso
                    })
                    
                    # Registrar estatísticas
                    if tamanho_sequencia in tamanhos_sequencias:
                        tamanhos_sequencias[tamanho_sequencia] += 1
                    
                    # Guardar exemplos (apenas os primeiros 50)
                    if len(exemplos_sequencias) < 50:
                        exemplos_sequencias.append({
                            'tamanho': tamanho_sequencia,
                            'numeros': '-'.join(map(str, sequencia)),
                            'concurso': concurso.concurso
                        })
                
                i = j + 1
            
            # Classificar o concurso
            if not sequencias_encontradas:
                concursos_sem_sequencia += 1
            else:
                # Pegar a maior sequência do concurso
                maior_seq = max(sequencias_encontradas, key=lambda x: x['tamanho'])
                tamanho = maior_seq['tamanho']
                
                if tamanho == 2:
                    duplas += 1
                elif tamanho == 3:
                    triplas += 1
                elif tamanho == 4:
                    quadruplas += 1
                else:
                    quintuplas_ou_mais += 1
        
        # Calcular percentuais
        perc_duplas = (duplas / total_concursos * 100) if total_concursos > 0 else 0
        perc_triplas = (triplas / total_concursos * 100) if total_concursos > 0 else 0
        perc_quadruplas = (quadruplas / total_concursos * 100) if total_concursos > 0 else 0
        perc_quintuplas = (quintuplas_ou_mais / total_concursos * 100) if total_concursos > 0 else 0
        perc_sem_sequencia = (concursos_sem_sequencia / total_concursos * 100) if total_concursos > 0 else 0
        
        concursos_com_sequencia = total_concursos - concursos_sem_sequencia
        perc_com_sequencia = (concursos_com_sequencia / total_concursos * 100) if total_concursos > 0 else 0
        
        # Preparar dados para retorno
        distribuicao = [
            {
                'tipo': 'Sem Sequência',
                'quantidade': concursos_sem_sequencia,
                'percentual': f"{perc_sem_sequencia:.2f}"
            },
            {
                'tipo': 'Duplas (2 números)',
                'quantidade': duplas,
                'percentual': f"{perc_duplas:.2f}"
            },
            {
                'tipo': 'Triplas (3 números)',
                'quantidade': triplas,
                'percentual': f"{perc_triplas:.2f}"
            },
            {
                'tipo': 'Quádruplas (4 números)',
                'quantidade': quadruplas,
                'percentual': f"{perc_quadruplas:.2f}"
            },
            {
                'tipo': 'Quíntuplas+ (5+ números)',
                'quantidade': quintuplas_ou_mais,
                'percentual': f"{perc_quintuplas:.2f}"
            }
        ]
        
        return {
            'total_concursos': total_concursos,
            'concursos_com_sequencia': concursos_com_sequencia,
            'concursos_sem_sequencia': concursos_sem_sequencia,
            'percentual_com_sequencia': f"{perc_com_sequencia:.2f}",
            'percentual_sem_sequencia': f"{perc_sem_sequencia:.2f}",
            'distribuicao': distribuicao,
            'tamanhos_sequencias': tamanhos_sequencias,
            'exemplos': exemplos_sequencias[:20]  # Retornar apenas os 20 primeiros exemplos
        }