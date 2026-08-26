import zipfile
import xml.etree.ElementTree as ET

def get_docx_text(path):
    with zipfile.ZipFile(path) as docx:
        xml_content = docx.read('word/document.xml')
    tree = ET.XML(xml_content)
    WORD_NAMESPACE = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
    PARA = WORD_NAMESPACE + 'p'
    TEXT = WORD_NAMESPACE + 't'
    
    paragraphs = []
    for paragraph in tree.iter(PARA):
        texts = [node.text for node in paragraph.iter(TEXT) if node.text]
        if texts:
            paragraphs.append("".join(texts))
    return "\n".join(paragraphs)

with open('out.txt', 'w', encoding='utf-8') as f:
    f.write(get_docx_text("Estrategia_dos_Mestres-MATRIZ-VALIDADA.docx"))
