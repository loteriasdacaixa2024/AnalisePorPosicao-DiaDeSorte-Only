# Como diminuir o ABS — Variância Nominal

Guia prático para gerar apostas mais próximas do sorteio na métrica **ABS** da Central de Conferências (`/central-conferencias`, aba **Variância Nominal**).

---

## O que o ABS mede

ABS é a soma das distâncias **depois de ordenar** aposta e sorteio:

```
ABS = |P1−S1| + |P2−S2| + … + |P7−S7|
```

- **Delta**: desvio com sinal (+ jogou acima, − jogou abaixo). `0` é acerto perfeito na posição.
- **ABS**: distância pura, sem sinal. **Quanto menor, melhor.**

| Faixa   | Cor    | Leitura                                      |
|---------|--------|----------------------------------------------|
| ABS ≤ 7 | Verde  | Excelente — em média ±1 por posição          |
| 8–14    | Amarelo| Bom — erro médio de até 2 por posição        |
| > 14    | Neutro | Comum — formato distante do sorteio          |

Verde (≤ 7) quase sempre é **±1 ou ±2 por posição**. Um único salto grande (P3 com −8, P1 com +10) já joga o jogo para amarelo/neutro, mesmo com 4–5 acertos de dezena.

O **mês da sorte** não entra no ABS das dezenas. O X da coluna M é outro problema.

---

## Leitura do resumo histórico

Na pasta de conferências, um recorte típico é:

**486 de 1912 apostas · 134 concursos** com ABS ≤ 20 (~25%).

Isso é a **cauda boa**, não o jogo típico. Grande parte do topo da tabela costuma ser um concurso com muitas variações do **mesmo esqueleto** (ex.: 1166). Isso infla o resumo sem significar que o gerador está preciso.

---

## Envelope posicional

O ABS baixo não vem de “adivinhar dezena”. Vem de **acertar o formato do jogo ordenado**.

Envelope típico do Dia de Sorte (7 dezenas de 1–31), em torno da média das posições ordenadas:

```
04 · 08 · 12 · 16 · 20 · 24 · 28
```

Jogo com P1 = 9–12 ou P7 = 21–23 só fica com ABS baixo se o sorteio vier **comprimido**. Exemplo: concurso 1286 (`02 04 08 10 12 17 23`) puniu jogos “abertos” no alto.

Filtro de sanidade antes de enviar à conferência:

- P1 acima de ~8 → descarte (salvo sorteio claramente comprimido)
- P7 abaixo de ~22 → descarte
- soma muito baixa/alta → descarte
- 5+ dezenas no miolo (11–20) → descarte

---

## O que usar (nesta ordem)

### 1. Análise: Posição Mínima × Máxima

Rota: `/posicao-minima-maxima`

É a análise **alinhada com o ABS** (usa dezenas ordenadas, igual à aba Variância Nominal).

Olhe **média** e **mais frequente** de cada posição. Não use o min–max histórico como alvo: ele é largo demais e quase não corta ABS.

### 2. Gerador: Atraso Posicional — aba 6 original

Rota: `/gerador-especial` → **Atraso Posicional** → sub aba **6 — Original**

Parte do último concurso e desloca pouco. É o gerador que mais produz vizinhança de baixo ABS.

- Use **7 dezenas**
- Salto implícito de **±1**
- Evite a **6A (salto 6 / 15 / 30)**: esses saltos aumentam o ABS de propósito

### 3. Ajuste fino: Laboratório de Alterações

Rota: `/analise-visual` → aba **Laboratório de Alterações**

Importe o esqueleto (último sorteio **ordenado**, ou o envelope `04 08 12 16 20 24 28`) e gere alteradas com **delta ±1 / ±2**.

Não use o viés **“nova”** se o objetivo for baixar ABS: ele troca por dezena longe e estoura a posição.

### 4. Filtro complementar

- `/estatisticas` — frequência **por posição, modo crescente** (não ordem de sorteio)
- `/analise/dezenas-faixas` — baixa / média / alta + soma

---
http://localhost:5151//posicao-minima-maxima
http://localhost:5151/gerador-especial/
http://localhost:5151/analise-visual/#pane-laboratorio-alteracoes
http://localhost:5151//estatisticas
http://localhost:5151//analise/dezenas-faixas


## O que não usar se a meta é ABS

| Ferramenta                         | Por quê                                                                 |
|------------------------------------|-------------------------------------------------------------------------|
| Ciclo Posicional (aba 8)           | Trabalha ordem do sorteio (`sorteio_1…7`), não posição crescente        |
| Híbrido Colunas / Precisão / Dígitos | Otimizam coluna, escape e dígito; empurram 18 em P3 ou 31 cedo        |
| Aba 6A com salto grande            | Distância posicional grande = ABS grande                                |
| Laboratório modo “nova”            | Substitui por número fora da vizinhança                                 |

---

## Receita para o próximo concurso

1. Pegue o último sorteio **ordenado** e o envelope médio `04 08 12 16 20 24 28`.
2. Na aba **6**, gere uma leva curta (10–20) em volta do último.
3. No Laboratório, clone os 3–4 melhores esqueletos com só **±1 / ±2**.
4. Jogue fora qualquer linha com um desvio único **> 5** numa posição.
5. Trate o mês à parte: o X da coluna M não entra no ABS das dezenas.

---

## Exemplo de aderência (1286 → 1287)

Sorteio 1286 ordenado: `02 04 08 10 12 17 23`

Jogos do 1287 que puxam P1 para 9–10 (`09 10 16…`) nascem com ABS alto contra um sorteio clássico.

Mais aderente ao formato do 1286:

```
03 05 09 10 16 17 23
```

Delta vs 1286: `+1 +1 +1 0 +4 0 0` → ABS 7 contra o concurso anterior (persistência de formato).

---

## Referência no código

Cálculo do ABS histórico (apostas JSON na pasta `conferencia_apostas/`):

- Serviço: `services/conferencia_apostas_ocr_service.py` → `resumo_abs_historico_pasta`
- UI: `templates/central_conferencias.html` → aba Variância Nominal (`ABS_LIMITE_RESUMO = 20`)
- Rota: `GET /api/conferencia-ocr/resumo-abs-historico?max_abs=20`
