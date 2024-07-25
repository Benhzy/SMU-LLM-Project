import torch 
from transformers import AutoTokenizer, AutoModelForSequenceClassification 
import nltk
from nltk import sent_tokenize 
nltk.download('punkt')
 
# Load the tokenizer and model from Hugging Face 
model_name = "MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli" 
tokenizer = AutoTokenizer.from_pretrained(model_name) 
model = AutoModelForSequenceClassification.from_pretrained(model_name) 
 
# Define your source document and summary 
source_document = "The small coastal town of Havenport has been known for its vibrant fishing community, which has thrived for centuries. In recent years, however, the local fish populations have seen a significant decline due to overfishing and pollution. Several local initiatives have been launched to address these environmental issues. Efforts include stricter fishing regulations and a significant investment in water purification projects. The town has also seen an increase in tourism, which has brought new challenges and opportunities to the local economy and culture." 
summary = "Havenport faces environmental and economic challenges as overfishing and pollution reduce fish populations, prompting local initiatives and new regulations to restore marine life. The rise in tourism offers potential economic benefits but also presents new difficulties" 
 
# Tokenize sentences 
source_sentences = sent_tokenize(source_document) 
summary_sentences = sent_tokenize(summary) 
 
# Function to classify and print inference 
def check_sentences(source, hypothesis): 
    inputs = tokenizer(source, hypothesis, return_tensors="pt", truncation=True, padding=True) 
    with torch.no_grad():  # No need to calculate gradients 
        outputs = model(**inputs) 
        probabilities = torch.softmax(outputs.logits, dim=-1) 
    return probabilities 
 
# Variables to store entailment scores and coverage counts 
total_entailment = 0 
coverage_hits = [False] * len(source_sentences) 
count = 0 
 
# Compare each summary sentence against each source sentence 
for source_idx, source_sentence in enumerate(source_sentences): 
    source_covered = False 
    for summary_sentence in summary_sentences: 
        result = check_sentences(source_sentence, summary_sentence) 
        print(f"Entailment: {result[0][0].item()*100:.2f}%, Neutral: {result[0][1].item()*100:.2f}%, Contradiction: {result[0][2].item()*100:.2f}%")
        entailment_probability = result[0][0].item()  # Entailment probability 
        total_entailment += entailment_probability 
        count += 1 
 
        if entailment_probability > 0.5: 
            source_covered = True 
     
    coverage_hits[source_idx] = source_covered 
 
average_entailment = total_entailment / count if count else 0 
coverage_percentage = sum(coverage_hits) / len(source_sentences) * 100 
 
print(f"Average Entailment Score: {average_entailment*100:.2f}%") 
print(f"Coverage Percentage: {coverage_percentage:.2f}%")