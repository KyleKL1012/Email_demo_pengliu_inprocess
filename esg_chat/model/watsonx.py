import requests
import os
import json

from config import config, logger


class Watsonx:
    def __init__(self):
        self._api_key = os.getenv("WATSONX_API_KEY")
        self._project_id = os.getenv("WATSONX_PROJECT_ID")
        self._access_token = self._generate_iam_token()

    def _generate_iam_token(self) -> str:
        response = requests.post(config["settings"]["iam_url"], 
                                headers={"Content-Type": "application/x-www-form-urlencoded"}, 
                                data=f"grant_type=urn:ibm:params:oauth:grant-type:apikey&apikey={self._api_key}")
        return response.json()["access_token"]


    def call_watsonx(
        self,
        input_str: str,
        task: str = "qa",
    ) -> dict:
        """Call watsonx RESTAPI.

        Args:
            input_str (str): The input text to the model.
            project_id (str): The watsonx project id.
            task (str): The task to perform, such as qa, summarization.
            model_id (str): The model to use. Default is google/flan-ul2.
            
        Returns:
            (dict): The watsonx output.
            
        Raises:
            requests.RequestException: If there is an error making the API request.
            ValueError: If the url and watsonx_access_token are not provided.

        """
        try:
            url = config["model"]["watsonx"]["url"]
        except:
            raise ValueError("url must be provided or set in config file.")

        parameter = config["model"]["watsonx"][task]["param"]
        watsonx_input = {
            "model_id": parameter["model_id"],
            "input": input_str,
            "parameters":{
                "decoding_method": parameter["decoding_method"],
                "temperature": parameter["temperature"],
                "top_p": parameter["top_p"],
                "top_k": parameter["top_k"],
                "repetition_penalty": parameter["repetition_penalty"],
                "min_new_tokens":parameter["min_new_tokens"],
                "max_new_tokens": parameter["max_new_tokens"]
            },
            "project_id": self._project_id
        }
        logger.info(f"WATSONX input: {json.dumps(watsonx_input)}")
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self._access_token}"
            }
            response = requests.post(
                url,
                headers=headers,
                json=watsonx_input
            )
            response.raise_for_status()
            result = response.json()
            return result
        except requests.exceptions.RequestException as e:
            logger.error(f"Error occurred during API call of watsonx: {str(e)}")
            return {}
