import json
import logging
from typing import Dict, List, Union


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Load settings from settings.json
with open('settings.json', 'r') as settings_file:
    settings = json.load(settings_file)


class ModelPredictor:
    def __init__(self, system_prompt):
        self.system_prompt = system_prompt
        
        # Load settings from settings.json
        with open('settings.json', 'r') as settings_file:
            settings = json.load(settings_file)
        
        self.pipeline = settings["pipeline"]
        # Load settings of each pipeline below:    
        if self.pipeline == "vertex_ai":
            from google.cloud import aiplatform
            """
            Make sure to run the following commands before running the code: 
            1. pip install google-cloud-aiplatform transformers torch fastapi pydantic
            2. gcloud auth application-default login
            """
            self.project = "775367805714"
            self.endpoint_id = "7326375829359820800"
            self.location = "asia-southeast1"
            self.api_endpoint = "asia-southeast1-aiplatform.googleapis.com"
            self.client_options = {"api_endpoint": self.api_endpoint}
            self.client = aiplatform.gapic.PredictionServiceClient(client_options=self.client_options)
            self.endpoint = self.client.endpoint_path(project=self.project, location=self.location, endpoint=self.endpoint_id)
            self.max_length = 600
        
        elif self.pipeline == "local_model":
            import transformers
            import torch

            cache_dir = "./.cache"
            self.local_model = transformers.AutoModelForCausalLM.from_pretrained(cache_dir, torch_dtype=torch.bfloat16)
            self.local_tokenizer = transformers.AutoTokenizer.from_pretrained(cache_dir)
            print(f"GPU is {torch.cuda.is_available()}")
            self.local_pipeline = transformers.pipeline(
                "text-generation",
                model=self.local_model,
                tokenizer=self.local_tokenizer,
                device=0 if torch.cuda.is_available() else -1,  # Use GPU if available
                pad_token_id=self.local_tokenizer.eos_token_id,
                truncation=True,
                max_length=2000
            )

    def predict(self, user_prompt: str = None) -> str:
        prompt = f"{self.system_prompt} \n{user_prompt}\n"
        
        if self.pipeline == "vertex_ai":
            from google.protobuf import json_format
            from google.protobuf.struct_pb2 import Value

            instances = [{"prompt": prompt, "max_tokens": self.max_length}]
            formatted_instances = [json_format.ParseDict(instance_dict, Value()) for instance_dict in instances]
            parameters_dict = {}
            parameters = json_format.ParseDict(parameters_dict, Value())

            try:
                response = self.client.predict(endpoint=self.endpoint, instances=formatted_instances, parameters=parameters)
                predictions = response.predictions
                cleaned_predictions = []
                for prediction in predictions:
                    parts = prediction.split("My answer is:")
                    cleaned_text = parts[-1] if len(parts) > 1 else prediction
                    cleaned_predictions.append(cleaned_text)
                return cleaned_predictions[0]
            except Exception as e:
                logger.error(f"Prediction failed: {e}")
                return f"Prediction failed: {e}"

        elif self.pipeline == "local_model":
            try:
                predictions = self.local_pipeline(prompt)
                return predictions[0]["generated_text"]
            except Exception as e:
                logger.error(f"Local model prediction failed: {e}")
                return f"Local model prediction failed: {e}"