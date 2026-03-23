import sys
try:
    import PyPDF2
    reader = PyPDF2.PdfReader(r'C:\Users\tejpa\Downloads\IEEE_Conference_Paper_TD12_final-r1.pdf')
    text = ''
    for i, page in enumerate(reader.pages):
        text += f'\n===PAGE {i+1}===\n'
        t = page.extract_text()
        if t:
            text += t
    print(text[:40000])
except ImportError:
    try:
        import pdfplumber
        with pdfplumber.open(r'C:\Users\tejpa\Downloads\IEEE_Conference_Paper_TD12_final-r1.pdf') as pdf:
            text = ''
            for i, page in enumerate(pdf.pages):
                text += f'\n===PAGE {i+1}===\n'
                t = page.extract_text()
                if t:
                    text += t
        print(text[:40000])
    except ImportError:
        print("No PDF library available. Trying pypdf...")
        try:
            from pypdf import PdfReader
            reader = PdfReader(r'C:\Users\tejpa\Downloads\IEEE_Conference_Paper_TD12_final-r1.pdf')
            text = ''
            for i, page in enumerate(reader.pages):
                text += f'\n===PAGE {i+1}===\n'
                t = page.extract_text()
                if t:
                    text += t
            print(text[:40000])
        except Exception as e:
            print(f"Error: {e}")
