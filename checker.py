import xml.etree.ElementTree as ET

try:
    # Read the file and clean the BOM
    with open('iShares-Core-Dividend-Growth-ETF_fund.xls', 'rb') as f:
        content = f.read()
    
    print(f"Original first 50 bytes: {content[:50]}")
    
    # Remove the double BOM
    if content.startswith(b'\xef\xbb\xbf\xef\xbb\xbf'):
        content = content[6:]  # Remove both BOMs (3 bytes each)
        print("Removed double BOM")
    elif content.startswith(b'\xef\xbb\xbf'):
        content = content[3:]  # Remove single BOM
        print("Removed single BOM")
    
    print(f"Cleaned first 50 bytes: {content[:50]}")
    
    # Try to parse the cleaned content
    content_str = content.decode('utf-8')
    root = ET.fromstring(content_str)
    
    print("SUCCESS! XML parsed correctly")
    print("Root tag:", root.tag)
    print("Root attributes:", root.attrib)
    
    # Look for worksheets
    for child in root:
        print(f"Child: {child.tag}")
        if 'Worksheet' in child.tag:
            print(f"Found worksheet: {child.attrib}")
            
except Exception as e:
    print(f"Error: {e}")
    print(f"Error type: {type(e)}")