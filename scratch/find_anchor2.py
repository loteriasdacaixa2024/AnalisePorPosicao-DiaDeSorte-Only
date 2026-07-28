content = open('templates/gerador_especial.html', 'r', encoding='utf-8').read()

# Find the fatiamento div id to locate where the last aba ends
idx_fat_div = content.rfind('id="fatiamento"')
print("fatiamento div at:", idx_fat_div)
# From there, find the closing - it's a long section, let's look for the script tag before endblock
idx_script = content.find('<script>', idx_fat_div)
print("script at:", idx_script)
# The tabs content ends just before the <script> tag
# Let's find the last </div> before the script
end_of_tabs = content.rfind('\n    </div>\n\n', 0, idx_script)
print("end_of_tabs at:", end_of_tabs)
print(repr(content[end_of_tabs:end_of_tabs+30]))

# Insert the new aba BEFORE the closing of geradoresTabsContent
# That means: insert BEFORE "    </div>\n\n" that closes geradoresTabsContent
