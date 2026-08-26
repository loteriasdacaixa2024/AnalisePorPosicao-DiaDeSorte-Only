content = open('templates/gerador_especial.html', 'r', encoding='utf-8').read()

# Find the end of the fatiamento aba content - look for {% endblock %} preceded by </div>
idx_endblock = content.find('{% endblock %}')
# Find the last </div>\n</div>\n before {% endblock %}
# Walk backwards from endblock to find the closing structure
segment = content[:idx_endblock]
# The structure at the end is:
#  </div>  <- closes fatiamento pane
#  </div>  <- closes geradoresTabsContent  
#  </div>  <- closes container
# Then <script> block
# Then {% endblock %}

# Let's just find where the fatiamento aba div ends
# and insert the new aba after it, before the geradoresTabsContent closing </div>

# Find the last occurrence of "        </div>" pattern that closes a top-level aba
# The fatiamento aba starts around 114955 and script is at 157494
# So the fatiamento aba ends somewhere between these

# Let's look for a reasonable closing pattern
# The fatiamento aba's closing: it's a series of </div>s then \n\n    </div> (closes geradoresTabsContent)
# Then \n\n</div> (closes container)
# Then \n\n<script>

idx_fat_div = content.rfind('id="fatiamento"')
idx_script = content.find('<script>', idx_fat_div)

# The geradoresTabsContent closing is the parent div that closes after all abas
# Let's find it by looking for \n\n    </div>\n\n</div>\n\n<script>
pattern = '\n\n    </div>\n\n</div>\n\n<script>'
idx_pattern = content.find(pattern, idx_fat_div)
print("Pattern found at:", idx_pattern)
if idx_pattern > 0:
    print(repr(content[idx_pattern-100:idx_pattern+60]))
else:
    # Try without double newlines
    pattern2 = '\n    </div>\n\n</div>\n\n<script>'
    idx_pattern2 = content.find(pattern2, idx_fat_div)
    print("Pattern2 found at:", idx_pattern2)
    if idx_pattern2 > 0:
        print(repr(content[idx_pattern2-50:idx_pattern2+50]))
    else:
        # Show what's near the script tag
        print("Near script:")
        print(repr(content[idx_script-200:idx_script+50]))
