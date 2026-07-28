content = open('templates/gerador_especial.html', 'r', encoding='utf-8').read()

# Check the card-header area around the Raio-X section - the broken replacement
# 'bg-primary text-white' was replaced with 'text-dark" style="background:#D4B31A;'
# This would create: class="card-header text-dark" style="background:#D4B31A; ..."
# But might have originally been: class="card-header d-flex ... bg-primary text-white py-3"
# making it: class="card-header d-flex ... text-dark" style="background:#D4B31A; py-3"

idx = content.find('text-dark" style="background:#D4B31A;')
if idx > 0:
    print(f"BROKEN at {idx}:")
    print(repr(content[idx-100:idx+200]))
else:
    print("No broken text-dark pattern found")
    # Search for the raio-x card header
    idx2 = content.find('Raio-X Hist')
    print(f"Raio-X at {idx2}")
    print(repr(content[idx2-200:idx2+300]))
