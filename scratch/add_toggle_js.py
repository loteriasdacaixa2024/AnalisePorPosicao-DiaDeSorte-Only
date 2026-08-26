content = open('templates/gerador_especial.html', 'r', encoding='utf-8').read()

# 1. Replace gerarFatiamento payload to include modos
old_payload = """        const payload = {
            quantidade: document.getElementById('fat_qtd_apostas').value,
            dezenas_por_jogo: document.getElementById('fat_dezenas').value,
            mes_tipo: document.getElementById('fat_mes').value,
            limites: {
                '0': document.getElementById('fat_dig_0').value,
                '1': document.getElementById('fat_dig_1').value,
                '2': document.getElementById('fat_dig_2').value,
                '3': document.getElementById('fat_dig_3').value,
                '4': document.getElementById('fat_dig_4').value,
                '5': document.getElementById('fat_dig_5').value,
                '6': document.getElementById('fat_dig_6').value,
                '7': document.getElementById('fat_dig_7').value,
                '8': document.getElementById('fat_dig_8').value,
                '9': document.getElementById('fat_dig_9').value,
                'gemeas': document.getElementById('fat_gemeas').value
            }
        };"""

new_payload = """        // Coleta limites e modos (max=\u2264 / min=\u2265) de cada grupo
        const grupoIds = ['0','1','2','3','4','5','6','7','8','9','gemeas'];
        const limitesObj = {};
        const modosObj = {};
        grupoIds.forEach(k => {
            const inputId = k === 'gemeas' ? 'fat_gemeas' : 'fat_dig_' + k;
            limitesObj[k] = document.getElementById(inputId).value;
            const btnModo = document.getElementById('fat_modo_' + k);
            modosObj[k] = btnModo ? btnModo.dataset.modo : 'max';
        });

        const payload = {
            quantidade: document.getElementById('fat_qtd_apostas').value,
            dezenas_por_jogo: document.getElementById('fat_dezenas').value,
            mes_tipo: document.getElementById('fat_mes').value,
            limites: limitesObj,
            modos: modosObj
        };"""

if old_payload in content:
    content = content.replace(old_payload, new_payload, 1)
    print("Payload updated OK")
else:
    print("Payload NOT FOUND")

# 2. Add toggleFatModo function + aplicarLimitesPelaAnalise update
# Find the existing aplicarLimitesPelaAnalise function to add the toggle function before it
old_aplic = "    function aplicarLimitesPelaAnalise() {"
new_aplic = """    // Toggle entre modo MAX (≤) e MIN (≥) para cada grupo
    function toggleFatModo(groupId) {
        const btn = document.getElementById('fat_modo_' + groupId);
        if (!btn) return;
        if (btn.dataset.modo === 'max') {
            btn.dataset.modo = 'min';
            btn.textContent = '\u2265';
            btn.classList.remove('btn-outline-danger');
            btn.classList.add('btn-outline-success');
            btn.title = 'Modo M\u00ednimo: exige pelo menos X dezenas deste grupo';
        } else {
            btn.dataset.modo = 'max';
            btn.textContent = '\u2264';
            btn.classList.remove('btn-outline-success');
            btn.classList.add('btn-outline-danger');
            btn.title = 'Modo M\u00e1ximo: permite no m\u00e1ximo X dezenas deste grupo';
        }
    }

    function aplicarLimitesPelaAnalise() {"""

if old_aplic in content:
    content = content.replace(old_aplic, new_aplic, 1)
    print("toggleFatModo added OK")
else:
    print("aplicarLimitesPelaAnalise NOT FOUND")

open('templates/gerador_especial.html', 'w', encoding='utf-8').write(content)
print("Done")
