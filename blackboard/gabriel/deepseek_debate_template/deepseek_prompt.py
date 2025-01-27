# ----- REQUIRED IMPORTS -----

import os
import json
import requests
from dotenv import load_dotenv

# ----- HELPER FUNCTIONS -----

def safe_write_json(filepath, data):
    """
    appends provided json data to a specified json file
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

def query_deepseek(api_url, api_key, query):
    """
    sends a query to the deepseek ai api and returns the response
    """
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
    }
    payload = {
        'query': query
    }
    try:
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status()  
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error querying DeepSeek AI: {e}")
        return None

def log_query_and_response(log_filepath, query, response):
    """
    logs the query and its corresponding response to a json file
    """
    log_data = {
        'query': query,
        'response': response,
    }
    safe_write_json(log_filepath, log_data)

def debate(prompt, api_url, api_key, log_filepath):
    """
    conducts a debate between two responses from DeepSeek AI based on the provided prompt
    """
    print(f"Starting debate on: {prompt}")
    query_a = f"{prompt} (Model A's argument)"
    print(f"Querying Model A: {query_a}")
    response_a = query_deepseek(api_url, api_key, query_a)
    query_b = f"{prompt} (Model B's argument)"
    print(f"Querying Model B: {query_b}")
    response_b = query_deepseek(api_url, api_key, query_b)
    if response_a and response_b:
        debate_log = {
            'prompt': prompt,
            'model_a_response': response_a,
            'model_b_response': response_b,
        }
        log_query_and_response(log_filepath, prompt, debate_log)
        print("Debate responses logged successfully.")
        return {
            "response_a": response_a,
            "response_b": response_b
        }
    else:
        print("Failed to get responses from one or both models.")
        return None

def get_api_key_from_env():
    """
    reads the api key from a .env file
    """
    load_dotenv()
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise ValueError("API key not found in environment variables. Please set DEEPSEEK_API_KEY in your .env file.")
    return api_key

# ----- EXECUTION CODE -----

if __name__ == "__main__":

    API_URL = "https://api.deepseek.ai/v1/query" 
    API_KEY = get_api_key_from_env()  
    LOG_FILEPATH = "./deepseek_log.json"

    debate_prompt = "Why is kindness good and unkindness bad?"

    print(f"Starting debate on prompt: {debate_prompt}")
    responses = debate(debate_prompt, API_URL, API_KEY, LOG_FILEPATH)

    if responses:
        print(f"\nModel A Response:\n{responses['response_a']}")
        print(f"\nModel B Response:\n{responses['response_b']}")