import PyPDF2

def extract():
    with open('Plan of action -Unisync infosystems private limited.pdf', 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"

    with open('pdf_content.txt', 'w') as out:
        out.write(text)
    print("PDF extracted successfully!")

if __name__ == '__main__':
    extract()
