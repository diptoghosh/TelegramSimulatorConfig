from lxml import etree

root = etree.parse(r'HeaderType.xsbt.xml')
# Print the loaded XML
#print(etree.tostring(root))

for tags in root.iter('Telegram'):
    for tag in tags:
        print(tag.tag)