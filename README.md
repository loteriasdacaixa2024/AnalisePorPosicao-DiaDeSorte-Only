

RESPOSTA:
O usuário deve usar a página: "Configurações do Sistema"
🎯 Caminho: localhost:5010/sistema/configuracoes
✅ Por quê "Configurações do Sistema"?
Propósito específico: Esta página foi criada ESPECIFICAMENTE para gerenciar as configurações globais do sistema
Interface clara: Foco único em alterar o valor da aposta
Feedback visual: Mostra "Valor atual: R$ 2.50" antes de salvar
Centralização: Todas as configurações do sistema ficam em um só lugar
Tabela de auditoria: Mostra todas as configurações salvas no banco com data de atualização
⚠️ Observação importante:
AMBAS as páginas tecnicamente salvam o valor no banco de dados:

✅ Configurações do Sistema → Salva via botão "Salvar Valor da Aposta"
✅ Valores e Probabilidades → Salva via botão "Calcular Valores"
PORÉM, a página "Valores e Probabilidades" tem como função PRINCIPAL calcular e exibir tabelas de preços e probabilidades. O salvamento do valor é uma função SECUNDÁRIA nesta página.

🎯 RECOMENDAÇÃO FINAL:
Use "Configurações do Sistema" (/sistema/configuracoes) para alterar o valor da aposta mínima, pois esta é a página oficial e dedicada para este propósito.