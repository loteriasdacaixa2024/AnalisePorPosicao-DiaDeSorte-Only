import os, glob

bat_files = glob.glob('DiaDeSorte*.bat')
count = 0
for file in bat_files:
    if file == 'iniciar_servidores_boloes.bat': continue
    with open(file, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # 1. Manter a janela aberta se houver erro (cmd /k)
    content = content.replace('start "" python app.py', 'start "Servidor Principal" cmd /k "python app.py"')
    
    # 2. Usar o navegador padrao do Windows ao inves de forcar o Chrome
    content = content.replace('set CHROME="C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"', ':: Usando o navegador padrao do Windows')
    content = content.replace('start "" %CHROME% --new-tab ', 'start "" ')
    content = content.replace('start "" %CHROME% ', 'start "" ')
    
    with open(file, 'w', encoding='utf-8') as f:
        f.write(content)
    count += 1
print(f'Modificados {count} arquivos .bat com sucesso!')
