"""
# Relevant papers:
https://ar5iv.labs.arxiv.org/html/2212.01326
https://ar5iv.labs.arxiv.org/html/2401.16212

# Next steps:
1. Include a database of legal rules and retrieve using vector similarity
2. Use actual Tort exam answers for few shot prompting 
3. Train model using actual Tort exam answers using LORA (but need relatively large amount of data)
"""
import json

class SystemPrompts:
    def __init__(self):
        self.filepath = "system_prompts.json"
        # Load existing prompts or create a new file with an empty dictionary if it doesn't exist
        try:
            with open(self.filepath, 'r') as file:
                self.prompts = json.load(file)
        except FileNotFoundError:
            self.prompts = {}
            with open(self.filepath, 'w') as file:
                json.dump(self.prompts, file)

    def retrieve(self, key):
        """Retrieve a prompt based on the provided key."""
        return self.prompts.get(key, "Prompt not found")

    def store(self, key, prompt):
        """Store or update a prompt. If the key exists, it updates the prompt; otherwise, it adds a new one."""
        self.prompts[key] = prompt
        with open(self.filepath, 'w') as file:
            json.dump(self.prompts, file, indent=4)