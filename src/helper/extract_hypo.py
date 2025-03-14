import re
import fitz  # PyMuPDF
import json
import os
import argparse

def extract_content(pdf_path):
    # Open the PDF file
    doc = fitz.open(pdf_path)
    num_pages = doc.page_count
    
    scenario = ""
    questions = []

    # Extract qns and scenario
    if num_pages > 1:
        # Get the last page for qns
        last_page_text = doc.load_page(num_pages - 1).get_text()

        # Find all qns on the last page
        questions = re.findall(r'\d+\..*?(?=\d+\.|$)', last_page_text, re.S)

        # Remove redundant text from last qn
        last_qn = questions.pop()
        end_of_qn = last_qn.find('?')
        
        if end_of_qn != -1:
            trimmed_qn = last_qn[:end_of_qn + 1]
        else:
            trimmed_qn = last_qn
        questions.append(trimmed_qn)
        
        scenario_text_pages = []
        for i in range(1, num_pages):  # Starts from the second page
            page_text = doc.load_page(i).get_text()
            # Remove everything before "* * *" if it appears
            cut_index = page_text.find("* * *")
            if cut_index != -1:
                page_text = page_text[cut_index + 5:]  # Skip "* * *" and continue
            scenario_text_pages.append(page_text)

        # Include text from the last page up to the start of the first question if found
        if questions:
            first_question_start = last_page_text.find(questions[0])
            scenario_text_pages.append(last_page_text[:first_question_start])

        scenario = " ".join(scenario_text_pages).strip()

    return scenario, [question.strip() for question in questions]

def main(inpath, outpath):
    pdf_files = [os.path.join(inpath, f) for f in os.listdir(inpath) if f.endswith('.pdf')]
    results = []

    for pdf_file in pdf_files:
        scenario, questions = extract_content(pdf_file)
        data = {
            'file': os.path.basename(pdf_file),
            'scenario': scenario,
            'questions': questions
        }
        results.append(data)

    # Ensure the output directory exists
    os.makedirs(outpath, exist_ok=True)
    output_file_path = os.path.join(outpath, 'extracted_data.json')
    with open(output_file_path, 'w') as f:
        json.dump(results, f, indent=4)

    print(f"Extraction completed. Results saved to {output_file_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract paragraphs from PDF files.")
    parser.add_argument('--inpath', type=str, default='data/raw', help='Input directory containing PDF files.')
    parser.add_argument('--outpath', type=str, default='data/processed', help='Output directory for JSON results.')
    
    args = parser.parse_args()
    
    main(args.inpath, args.outpath)
