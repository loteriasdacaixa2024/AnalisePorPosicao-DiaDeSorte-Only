from itertools import combinations
import random
from collections import Counter

def calcular_conec(apostas):
    if not apostas: return 0
    pares = []
    for i, a in enumerate(apostas):
        for j, b in enumerate(apostas):
            if i < j:
                pares.append(len(set(a) & set(b)))
    return sum(pares) / len(pares) if pares else 0

def gerar_apostas_equilibradas():
    # 1. Restrição: Máximo 2 do anterior.
    # Anterior: 6, 8, 13, 19, 22, 24, 26
    anterior = [6, 8, 13, 19, 22, 24, 26]
    
    # Para validar 100% o 2x2 com apenas 2 dezenas por jogo,
    # É OBRIGATÓRIO fazer todas as combinações C(7,2) = 21 jogos.
    pares_obrigatorios = list(combinations(anterior, 2))
    
    # 2. Problema da Conectividade:
    # Se usarmos sempre a base fixa [3, 10, 16, 30, 31],
    # Todos os jogos terão 5 números iguais. Conectividade > 5.0. Impossível baixar.
    
    # 3. Solução: Rotação de Base.
    # Vamos pegar a base do usuário e adicionar uns "amigos" para rotacionar.
    base_favorita = [3, 10, 16, 30, 31]
    # Adicionamos alguns números neutros para permitir rotação (ex: primos ou comuns)
    # Vamos expandir o pool para 10 números para permitir variação
    pool_complementar = base_favorita + [1, 2, 4, 5, 7] 
    
    apostas_finais = []
    
    # Tentativa de balanceamento
    # Para cada par obrigatório, escolhemos 5 do pool de forma a não repetir muito
    random.seed(42) # Reprodutibilidade
    
    for par in pares_obrigatorios:
        # Começamos com o par obrigatório
        aposta = list(par)
        
        # Precisamos de mais 5 números do pool
        # Escolhemos 5 aleatórios do pool, mas tentando garantir presença da base favorita
        # Estratégia: 3 da base favorita + 2 dos extras (mistura)
        
        base_sample = random.sample(base_favorita, 3)
        extras_pool = [x for x in pool_complementar if x not in base_favorita]
        extras_sample = random.sample(extras_pool, 2)
        
        complemento = base_sample + extras_sample
        aposta.extend(complemento)
        aposta.sort()
        apostas_finais.append(aposta)

    # Métricas
    conec = calcular_conec(apostas_finais)
    
    print(f"Total de Apostas: {len(apostas_finais)}")
    print(f"Conectividade Média: {conec:.2f}")
    print(f"Pares Anteriores Cobertos: 21/21 (Garantido pela lógica)")
    
    print("\n--- Apostas Otimizadas (Copiar e Colar) ---")
    for a in apostas_finais:
        print(str(a).replace('[', '').replace(']', '').replace(',', ''))

if __name__ == "__main__":
    gerar_apostas_equilibradas()
