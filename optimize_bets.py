from itertools import combinations
import random

def calcular_conec(apostas):
    if not apostas: return 0
    pares = []
    for i, a in enumerate(apostas):
        for j, b in enumerate(apostas):
            if i < j:
                pares.append(len(set(a) & set(b)))
    return sum(pares) / len(pares) if pares else 0

def validar_2x2(apostas, anterior):
    pares_ant = list(combinations(anterior, 2))
    cobertos = set()
    for par in pares_ant:
        for aposta in apostas:
            if par[0] in aposta and par[1] in aposta:
                cobertos.add(par)
                break
    return len(cobertos), len(pares_ant)

def gerar_otimizacao():
    # Baseado nos dados do usuário
    # Base Fixa (5 nums): 3, 10, 16, 30, 31
    # Variáveis (7 nums - anterior): 6, 8, 13, 19, 22, 24, 26
    # O usuário atual usa 1 par de variáveis + 5 fixas por aposta. (21 apostas)
    
    base = [3, 10, 16, 30, 31]
    anterior = [6, 8, 13, 19, 22, 24, 26]
    
    # ESTRATÉGIA: Aumentar a densidade de números do anterior por aposta.
    # Em vez de 2 por aposta (que exige 21 jogos), vamos tentar 3 ou 4.
    # Se usarmos 3 do anterior por aposta, sobram 4 vagas para a base.
    # A base tem 5 números. C(5,4) = 5 variações. Isso já gera rotação.
    
    print("--- Tentativa com 3 números do anterior por aposta ---")
    # Gerar todas as combinações de 3 números do anterior (C(7,3) = 35)
    # Isso é muito. Precisamos escolher um subconjunto que cubra todos os pares (Covering Design 2-(7,3,1) -> C(7,2) cobertos por blocos de 3)
    # O sistema de Steiner S(2,3,7) tem 7 blocos e cobre todos os pares exatamente uma vez. PERFEITO.
    # Os blocos de Fano Plane (S(2,3,7)) mapeados para os n°s do anterior.
    
    # Steiner Triple System para 0-6:
    # (0,1,2), (0,3,4), (0,5,6), (1,3,5), (1,4,6), (2,3,6), (2,4,5)
    
    mapa = {i: n for i, n in enumerate(anterior)}
    steiner_idxs = [
        (0,1,2), (0,3,4), (0,5,6), 
        (1,3,5), (1,4,6), 
        (2,3,6), (2,4,5)
    ]
    
    apostas_geradas = []
    
    # Para cada trio de Steiner (que cobre todos os pares do anterior), completamos com 4 da base.
    # Para rodar a base, vamos usar um shift simples.
    # Base tem 5. Precisamos de 4.
    
    idx_base = 0
    for trio in steiner_idxs:
        nums_ant = [mapa[i] for i in trio]
        
        # Pega 4 da base rotacionando
        nums_base = []
        for k in range(4):
            nums_base.append(base[(idx_base + k) % 5])
        
        aposta = sorted(nums_ant + nums_base)
        apostas_geradas.append(aposta)
        idx_base += 1 # Roda a base
        
    # Verificar métricas
    cob, total_pares = validar_2x2(apostas_geradas, anterior)
    conec = calcular_conec(apostas_geradas)
    
    print(f"Total de Apostas: {len(apostas_geradas)}")
    print(f"Cobertura Pares Anterior: {cob}/{total_pares}")
    print(f"Conectividade Média: {conec:.2f}")
    
    print("\n--- Apostas Sugeridas ---")
    for a in apostas_geradas:
        print(str(a).replace('[', '').replace(']', ''))

if __name__ == "__main__":
    gerar_otimizacao()
