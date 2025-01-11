# ----- REQUIRED IMPORT -----

import os
import json
import ollama  

# ----- HELPER FUNCTIONS -----

def safe_write_json(filepath, data):
    """
    appends provided JSON  data to a specified JSON file
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    if not os.path.isfile(filepath):
        with open(filepath, 'w') as f:
            json.dump([], f)
    with open(filepath, 'r') as f:
        existing_data = json.load(f)
    if isinstance(existing_data, list):
        existing_data.append(data)
    else:
        raise ValueError("Error: The existing JSON data should be a list.")
    with open(filepath, 'w') as f:
        json.dump(existing_data, f, indent=4)

def start_model():
    """
    attempts to start and return an ollama model client 
    """
    try:
        client = ollama.Client()
        return client
    except Exception as e:
        print(f"Error starting model: {e}")
        return None

def generate_response(client, model_name, raw_prompt):
    """
    generates a response from the specified ollama model based on the provided prompt
    """
    try:
        response = client.generate(prompt=raw_prompt, model=model_name)
        print("------")
        print("Complete response from model:")
        print(response)
        response_text = response["response"].strip()
        return response_text
    except Exception as e:
        print(f"Error generating response: {e}")
        return None

def debate(prompt, model_a_type , model_b_type, model_a_client=None, model_b_client=None):
    """
    conducts a debate between two models based on the provided prompt
    """
    model_a_client = start_model()
    model_b_client = start_model()
    if model_a_client is None or model_b_client is None:
        print("Error: Failed to start one or both models")
        return (False, None)
    print(f"STARTING DEBATE ON:\n{prompt}")
    response_a = generate_response(model_a_client, model_a_type, f"{prompt} (Model A's argument)")
    response_b = generate_response(model_b_client, model_b_type, f"{prompt} (Model B's argument)")
    return (True, {
        "response_a": response_a, 
        "response_b": response_b
    })

# ----- EXECUTION CODE -----

if __name__ == "__main__":

    debate_prompt = "Why is kind good and unkind bad?"

    LOG_FILEPATH = "./chat_log.json"
    MODEL_A_TYPE = "llama2:7b"
    MODEL_B_TYPE = "llama2:7b"

    responses_tuple = debate(debate_prompt, MODEL_A_TYPE, MODEL_B_TYPE)
    
    if responses_tuple[0]:
        safe_write_json(LOG_FILEPATH, responses_tuple[1])
        response_a, response_b = responses_tuple[1]["response_a"], responses_tuple[1]["response_b"]
        print(f"MODEL A:\n{response_a}")
        print(f"MODEL B:\n{response_b}")
