content = open('templates/gerador_especial.html', 'r', encoding='utf-8').read()

start = content.find('<!-- GUIA DE DECIS')
# Find the end - it's right before the ABA 10 comment
end = content.find('<!-- ==========================================', start)

if start > 0 and end > start:
    removed = content[start:end]
    print(f"Removing {len(removed)} chars")
    print("Starts with:", repr(removed[:80]))
    print("Ends with:", repr(removed[-80:]))
    content = content[:start] + content[end:]
    open('templates/gerador_especial.html', 'w', encoding='utf-8').write(content)
    print("OK - block removed")
else:
    print(f"NOT FOUND: start={start}, end={end}")
