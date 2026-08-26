
// ==========================
// BUSCAR DADOS DO CONCURSO PARA O CARD DA LOTÉRICA
// ==========================
function buscarDadosConcursoCard(idLot, concursoId) {
    if (!concursoId) return;

    fetch(`/api/sorteios/${concursoId}`)
        .then(r => r.json())
        .then(d => {
            if (d.concurso) {
                // Atualizar Mês de Sorte
                const selectMes = document.getElementById(`mes-${idLot}`);
                if (selectMes && d.mes_sorte) {
                    selectMes.value = d.mes_sorte;
                }

                // Atualizar Prêmio (Estimativa ou Pago)
                const inputPremio = document.getElementById(`premio-${idLot}`);
                if (inputPremio) {
                    // Tenta pegar o valor do prêmio de 7 acertos ou acumulado
                    let valor = 0;
                    if (d.premiacao && d.premiacao['7_acertos']) {
                        valor = d.premiacao['7_acertos'].valor_premio;
                    }

                    // Se zero, tenta estimativa
                    if (!valor && d.valor_estimado_proximo_concurso) {
                        valor = d.valor_estimado_proximo_concurso;
                    }

                    if (valor) {
                        inputPremio.value = valor.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
                    }
                }
            }
        })
        .catch(err => console.error('Erro ao buscar dados do concurso para o card:', err));
}
