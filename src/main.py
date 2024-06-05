import json
from prediction_model import ModelPredictor
from system_prompts import sys_prompt


predictor = ModelPredictor(
    project="775367805714",
    endpoint_id="7326375829359820800",
    system_prompt=sys_prompt("ans_tort_qns"),
    location="asia-southeast1"
)

# Load the JSON data from the file
with open('data/processed/extracted_data.json', 'r') as file:
    data = json.load(file)

# Iterate over each file in the JSON data
for item in data:
    file_name = item['file']
    scenario = item['scenario']
    questions = item['questions']
    answers = []

    # For each question, prepare the prompt and get the model's prediction
    for question in questions:
        prompt = f"Scenario: {scenario}\nQuestion: {question}\n\n My answer is:"
        answer = predictor.predict(prompt)
        print(answer)
        answers.append(answer)

    # Add the answers to the data
    item['answers'] = answers

# Save the updated data back to a new JSON file
with open('results/exam_answers.json', 'w') as file:
    json.dump(data, file, indent=4)

print("Processing complete. The updated data is saved in 'data/results/exam_answers.json'.")