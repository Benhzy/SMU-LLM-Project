from typing import Dict, List, Union

from google.cloud import aiplatform
from google.protobuf import json_format
from google.protobuf.struct_pb2 import Value

"""
make sure to run the following cmd before running the code: 
1. pip install google-cloud-aiplatform
2. gcloud auth application-default login
"""

class ModelPredictor:
    def __init__(self, project: str, endpoint_id: str, system_prompt: str, max_length: int = 600, location: str = "asia-southeast1", api_endpoint: str = "asia-southeast1-aiplatform.googleapis.com"):
        # Configure client options
        self.max_length = max_length
        self.client_options = {"api_endpoint": api_endpoint}
        self.client = aiplatform.gapic.PredictionServiceClient(client_options=self.client_options)
        self.endpoint = self.client.endpoint_path(project=project, location=location, endpoint=endpoint_id)
        self.system_prompt = system_prompt  # Store system prompt
        
    def predict(self, user_prompt: str = None) -> List[Dict]:
        # Combine system prompt with user prompt if provided
        prompt = f"{self.system_prompt} \n{user_prompt}\n"
        instances = [{"prompt": prompt, "max_tokens": self.max_length}]

        # Prepare instances and parameters for the prediction request
        formatted_instances = [json_format.ParseDict(instance_dict, Value()) for instance_dict in instances]
        parameters_dict = {}
        parameters = json_format.ParseDict(parameters_dict, Value())

        # Make prediction request
        response = self.client.predict(endpoint=self.endpoint, instances=formatted_instances, parameters=parameters)

        predictions = response.predictions
        cleaned_predictions = []
        for prediction in predictions:
            parts = prediction.split("Output:")
            cleaned_text = parts[-1] if len(parts) > 1 else prediction
            cleaned_predictions.append(cleaned_text)

        return cleaned_predictions[0]


# # test
# if __name__ == "__main__":
#     system_prompt = "You are SkyNet."

#     predictor = ModelPredictor(775367805714, 7326375829359820800, system_prompt)


#     user_prompt = "What do you think about humanity?"
#     predictions = predictor.predict(user_prompt)
#     print(predictions)
