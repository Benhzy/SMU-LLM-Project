# SMU LLM Project

## Requirements

This project is developed using Python 3.12.3. To set up the project environment:
- Create a virtual environment.
- Install all the required packages by running:
  ```
  pip install -r requirements.txt 
  ```
  
## Downloading Model
To download the desired model from Hugging Face:
1. Run the following command:

    ```
    python local-deploy/download_model.py --model_id meta-llama/Meta-Llama-3-8B-Instruct --cache  --cache_dir ./.cache
    ```
2. You will be prompted to enter your Hugging Face access token. You can generate this token from [Hugging Face Tokens](https://huggingface.co/settings/tokens).

The script will download and cache the model into the specified cache directory.
