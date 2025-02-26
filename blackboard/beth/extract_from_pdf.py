import pymupdf

file_name = "ssrn-4945566.pdf"

def extract_text_from_pdf(pdf_path):
    doc = pymupdf.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text

#later on bring file dump to the same level as this file or amend the code accordingly
print(extract_text_from_pdf("./blackboard/beth/file_dump/" + file_name)) #works! :D