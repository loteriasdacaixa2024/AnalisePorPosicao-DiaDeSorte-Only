content = open('templates/gerador_especial.html', 'r', encoding='utf-8').read()

# Find the closing of geradoresTabsContent - look for the pattern before script tag
# The structure is:  </div> (closes geradoresTabsContent) + \n\n + </div> (closes container) + \n\n + <script>
# Let's find the last </div> before </div>\n\n</div>\n\n<script

idx_script = content.find('\n</script>\n{% endblock %}')
print("script endblock at:", idx_script)
print(repr(content[idx_script-50:idx_script+30]))

# Find where the fatiamento aba closes - look backwards from script
idx_fatiamento_end = content.rfind('</div>\n\n    </div>\n\n</div>', 0, idx_script)
print("fatiamento end at:", idx_fatiamento_end)
print(repr(content[idx_fatiamento_end-30:idx_fatiamento_end+60]))
